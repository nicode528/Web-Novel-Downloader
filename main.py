#!/usr/bin/env python3

from sitemanager.xxbiquge import Xxbiquge
from sitemanager.xbiquge import Xbiquge
from bookmanager.book import Book
import re
import os

if __name__ == "__main__":
    os.chdir(os.path.expanduser('~'))

    url = (input('Paste URL: '))
    # while not re.match('https?:\/\/www\.xbiquge\.so\/book\/\d+\/', book_main_url):
    #     print('Invalid URL: Format should be https://www.xbiquge.so/book/\{book_code\}/')
    #     book_main_url = (input('Paste 笔趣阁 URL: '))

    if re.match('https?:\/\/www\.xbiquge\.so\/book\/\d+\/?', url):
        site = Xbiquge(url)
    elif re.match('https?:\/\/www\.xxbiquge\.net\/\d+\/?', url):
        site = Xxbiquge(url)
    else: 
        print("invalid url format")
        exit(1)

    book = Book(site)
    book.build()
    book.export(os.path.expanduser("~") + "/Downloads/")
    exit(0)