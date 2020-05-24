import requests
from os import cpu_count, mkdir, rmdir
from threading import Thread, Lock
from bs4 import BeautifulSoup
from sys import argv
from urllib.parse import urlparse, unquote
from os.path import basename, splitext, join
from multiprocessing import Process, Manager
from time import sleep
from shutil import copyfileobj

if not(len(argv) > 1):
    print("Please enter the no of books to crawl.")
    exit(1)

noOfBookstoCrawl = int(argv[1])

if noOfBookstoCrawl % cpu_count() != 0:
    print("Please enter a number divisible by {0}.".format(cpu_count()))
    exit(1)

startPoint = int(argv[2])

if startPoint is None:
    startPoint = 0

print("Starting from {0}...".format(startPoint))

noOfBookstoCrawl = int(noOfBookstoCrawl / cpu_count())

crawlThreads = []
linkTemplate = "https://pdfstop.com/get-download/?file="
discoveredLinks = Manager().Queue()

observerProcessStarted = False



def crawlLinks(threadId, printLock):
    while not observerProcessStarted:
        
        print("[{0}] - Waiting for the observer process to start...".format(threadId))
        
        sleep(2)

    loopStopFlag = 0
    crawlRange = list(range(startPoint + (threadId * noOfBookstoCrawl), startPoint + (threadId * noOfBookstoCrawl + noOfBookstoCrawl)))
    
    print("[{0}] - Crawling from {1} to {2}.".format(threadId, crawlRange[0], crawlRange[-1]))
    
    for i in crawlRange:
        response = requests.get(linkTemplate + str(i))
        soup = BeautifulSoup(response.text, "html.parser")
        link = soup.find(class_="entry-content").a
        if link is None:
            
            print("[{0}] - Found invalid ebook. {1} more to go.".format(threadId, 80 - loopStopFlag))
            
            if loopStopFlag >= 80:
                break
            loopStopFlag += 1
        else:
            
            print("[{0}] - Found valid ebook.".format(threadId))
            
            loopStopFlag = 0
            ebookLink = link['href']
            ebookName = " ".join([word.capitalize() for word in splitext(basename(unquote(urlparse(ebookLink).path)))[0].split("-")])
            discoveredLinks.put({"name":ebookName, "link":ebookLink})
        
        print("[{0}] - {1}% of work is complete.".format(threadId, round(crawlRange.index(i) / len(crawlRange) * 100)))
        
    
    print("[{0}] - Died...".format(threadId))


def downloadEbooks(dataQueue, printLock):
    
    print("Observer process started.")
    
    def observerWork(printLock):
        while True:
            print("Observer job started.")

            ebookDetails = dataQueue.get()

            if ebookDetails is None:
                break

            ebookName, ebookLink = ebookDetails["name"], ebookDetails["link"]

            try:
                
                print("Creating directory...")
                
                mkdir(ebookName)
            except (FileExistsError, FileNotFoundError):
                
                print("Skipping...")
                
                continue

            filePath = join("./", ebookName, basename(urlparse(ebookLink).path))
            
            print("Writing {0} to {1}.".format(ebookName, filePath))
            
            try:
                with requests.get(ebookLink, stream=True) as request:
                    
                    print("Downloading {0}...".format(ebookName))
                    
                    with open(filePath, 'wb') as f:
                        copyfileobj(request.raw, f)
                    
                    print("Downloading {0} finished.".format(ebookName))
                    
            except Exception as e:
                
                print("An unknown error occured " + str(e))
                
                rmdir(ebookName)
            finally:
                
                print("Observer job finished.")
        print("Observer thread died.")
                

    observeThreads = []

    for i in range(cpu_count()):
        t = Thread(target=observerWork, args=(printLock,))
        t.setDaemon(True)
        observeThreads.append(t)
        t.start()
    
    print("Waiting for threads...")
    

    for t in observeThreads:
        t.join()
        observeThreads.remove(t)
    
    print("Observer threads finished, stopping observer...")
    print("Observer process stopped.")
    


if __name__ == "__main__":

    print("Starting crawling ebooks.")
    printLock = Lock()
    for i in range(cpu_count()):
        print("Initiating thread no. " + str(i))
        t = Thread(target=crawlLinks, args=(i, printLock,))
        t.setDaemon(True)
        crawlThreads.append(t)
        t.start()

    p = Process(target=downloadEbooks, args=(discoveredLinks,printLock,))
    p.start()

    observerProcessStarted = True

    for t in crawlThreads:
        t.join()
        crawlThreads.remove(t)

    for i in range(cpu_count()):
        discoveredLinks.put(None)

    print("All work finished. Waiting for observer...")

    p.join()

    print("Finished crawling ebooks.")
