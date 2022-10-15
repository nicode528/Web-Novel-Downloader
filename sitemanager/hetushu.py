import asyncio
import re
import urllib.request
from typing import List

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from sitemanager.site import SiteInterface


class Hetushu(SiteInterface):
    def __init__(self, url) -> None:
        self.url = url
        if self.url[-1] == "/":
            self.url = self.url[:-1]
        self.initializeBrowser()

    def initializeBrowser(self) -> None:
        options = Options()
        options.add_argument('headless')
        options.add_argument('--no-sandbox')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_experimental_option(
            "prefs", {"profile.default_content_settings.cookies": 2})
        self.browser = webdriver.Chrome(
            options=options, executable_path='./Selenium/chromedriver.exe')

    def parseHtmlPage(self, url) -> BeautifulSoup:
        request = urllib.request.Request(
            url, headers={'User-Agent': 'Mozilla/5.0'})
        html_page = urllib.request.urlopen(request).read()
        return self.soupify(html_page)

    def soupify(self, html) -> BeautifulSoup:
        soup = BeautifulSoup(html, features='html.parser')
        return soup

    def getBookCode(self) -> str:
        book_code = self.url.split("/")[-2]
        return book_code

    def getBookName(self, soup) -> str:
        book_name = soup.find('div', attrs={'class': 'book_info'})\
            .find('h2')\
            .string
        return book_name

    def getBookAuthor(self, soup) -> str:
        book_author = soup.find('div', attrs={'class': 'book_info'})\
            .find('a')\
            .string
        return book_author

    def getBookInfo(self, soup) -> str:
        book_info = soup.find('div', attrs={'class': 'intro'})\
            .stripped_strings
        book_info_string = ''

        for content in book_info:
            if (re.search('<\w+\/?>', content, re.MULTILINE)):
                continue
            book_info_string += content

        return book_info_string

    def getChapterUrls(self, soup) -> List[str]:
        content_page = soup.find('dl', attrs={'id': 'dir'}).findAll('dd')
        domain = '/'.join(self.url.split('/')[:3])
        chapters = []

        for content in content_page:
            try:
                chapter = domain + content.find('a')['href']
            except:
                continue
            chapters.append(chapter)

        chapter_set = set(chapters)
        chapters = sorted(chapter_set)

        return chapters

    def getChapterName(self, soup) -> str:
        try:
            chapter_name = soup.find('div', attrs={'id': 'content'})\
                .find('h2', attrs={'class': 'h2'})\
                .string
        except:
            print(soup.prettify())
        return chapter_name

    async def getChapterContent(self, session, url) -> tuple[str, str]:
        self.browser.get(url)
        html = self.browser.page_source.encode('utf-8')
        soup = self.soupify(html)

        # prevent cloudflare ddos block
        while soup.find('span', attrs={'class': 'cf-error-code'}) is not None:
            self.browser.close()
            asyncio.sleep(10)
            self.initializeBrowser()
            self.browser.get(url)
            html = self.browser.page_source.encode('utf-8')
            soup = self.soupify(html)

        chapter_name = self.getChapterName(soup)

        chapter_content = soup.find('div', attrs={'id': 'content'})

        # remove random texts within the main body
        [a.extract() for a in chapter_content.findAll(re.compile("^((?!div).)*$"))]

        chapter_content_string = '<h2>' + chapter_name + '</h2>'

        for content in chapter_content.stripped_strings:
            chapter_content_string += '<p>' + content + '</p>'

        return chapter_name, chapter_content_string
