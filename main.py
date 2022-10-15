#!/usr/bin/env python3

import os
import re

import click

from bookmanager.book import Book
from sitemanager.hetushu import Hetushu
from sitemanager.wfxs import Wfxs
from sitemanager.xbiquge import Xbiquge
from sitemanager.xxbiquge import Xxbiquge


@click.command()
@click.option('-u', '--url', type=str, prompt="Paste URL", help='web novel url, check readme.md for available sites and url formats')
@click.option('-o', '--output-dir', type=str, default=os.path.expanduser("~") + "/Downloads/", help='output directory')
def main(url, output_dir):
    """Download web novels as epub"""

    url = url.strip()

    if re.match('https?:\/\/www\.xbiquge\.so\/book\/\d+\/?', url):
        site = Xbiquge(url)
    elif re.match('https?:\/\/m\.xbiquge\.so\/book\/\d+\/?', url):
        site = Xbiquge(url.replace("/m.", "/www."))
    elif re.match('https?:\/\/www\.xxbiquge\.net\/\d+\/?', url):
        site = Xxbiquge(url)
    elif re.match('https?:\/\/www\.hetushu\.com\/book\/\d+\/index.html', url):
        site = Hetushu(url)
    elif re.match('https?:\/\/hetushu\.com\/book\/\d+\/index.html', url):
        site = Hetushu(url)
    elif re.match('https?:\/\/m\.wfxs\.tw\/xs-\d+\/?', url):
        site = Wfxs(url)
    else:
        print("error invalid url format, url={}".format(url))
        exit(1)

    if not os.path.isdir(output_dir):
        print("directory {} does not exist".format(output_dir))
        exit(1)

    book = Book(site)
    book.build()
    book.export(output_dir)
    exit(0)


if __name__ == "__main__":
    main()
