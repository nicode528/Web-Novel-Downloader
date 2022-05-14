import re
import urllib.request
from typing import List

from bs4 import BeautifulSoup

from sitemanager.site import SiteInterface


class Xbiquge(SiteInterface):
    def __init__(self, url) -> None:
        self.url = url
        if self.url[-1] == "/":
            self.url = self.url[:-1]

    def parseHtmlPage(self, url) -> BeautifulSoup:
        html_page = urllib.request.urlopen(url)
        return self.soupify(html_page)

    def soupify(self, html) -> BeautifulSoup:
        soup = BeautifulSoup(html, features='html.parser')
        return soup

    def getBookCode(self) -> str:
        book_code = self.url.split("/")[-1]
        return book_code

    def getBookName(self, soup) -> str:
        book_name = soup.find('div', attrs={'id': 'info'})\
            .find('h1')\
                .string
        return book_name

    def getBookAuthor(self, soup) -> str:
        book_author = soup.find('div', attrs={'id': 'info'})\
            .find('a', attrs={'href': re.compile('author')})\
                .string
        return book_author

    def getBookInfo(self, soup) -> str:
        book_info = soup.find('div', attrs={'id': 'intro'})\
            .stripped_strings
        book_info_string = ''

        for content in book_info:
            if (re.search('<\w+\/?>', content, re.MULTILINE)):
                continue
            book_info_string += content

        return book_info_string

    def getChapterUrls(self, soup) -> List[str]:
        content_page = soup.findAll('dd')
        chapter_url_list = []
        chapter_num_list = []

        for content in content_page:
            try:
                chapter = int(content.find('a')['href'].replace('.html',''))
            except:
                continue
            chapter_num_list.append(chapter)

        chapter_set = set(chapter_num_list)
        sorted_chapter_num_list = sorted(chapter_set)
        chapter_url_list = ['/'.join([self.url, str(x) + ".html"]) for x in sorted_chapter_num_list]

        return chapter_url_list

    def getChapterName(self, soup) -> str:
        chapter_name = soup.find('div', attrs={'class': 'bookname'})\
            .find('h1')\
                .string
        return chapter_name

    async def getChapterContent(self, session, url) -> tuple[str, str]:
        async with session.get(url) as response:
            html = await response.read()
            soup = self.soupify(html)
            chapter_name = self.getChapterName(soup)

            chapter_content = soup.find('div', attrs={'id': 'content'}).stripped_strings
            chapter_content_string = '<h2>' + chapter_name + '</h2>'

            for content in chapter_content:
                chapter_content_string += '<p>' + content + '</p>'

            return chapter_name, chapter_content_string
