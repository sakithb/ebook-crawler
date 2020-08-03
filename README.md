# EbookCrawler

A free program that crawls http://pdfstop.com and automatically downloads ebooks, written in python.

## Prerequisites

* Python 3+
* Requests package
* Beautiful Soup package

## Usage

`python downloader.py [No. of links to crawl] [Starting point to crawl]`

This will download the `No. of links to crawl` from the `Starting point to crawl` and save them to automatically created folders(With the name of the ebook) in the directory that this file exists.

> Note that argument `Starting point to crawl` is optional. If no `Starting point to crawl` is given, it will default to 0.

## Examples

To download all books from book id 0 to 800.

`python downloader.py 800`

To download all books from 1000 to 1800

`python downloader.py 800 1000`

###### Disclaimer

I hold no responsibility for whatever you do with this tool.
