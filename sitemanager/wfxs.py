import asyncio
import re
import urllib.request
from typing import List

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from sitemanager.site import SiteInterface


class Wfxs(SiteInterface):

    def __init__(self, url) -> None:
        self.url = url
        if self.url[-1] == "/":
            self.url = self.url[:-1]
        self.initializeBrowser()
        self.code = self.getBookCode()

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
        request = urllib.request.Request(url,
                                         headers={'User-Agent': 'Mozilla/5.0'})
        html_page = urllib.request.urlopen(request).read()
        return self.soupify(html_page)

    def soupify(self, html) -> BeautifulSoup:
        soup = BeautifulSoup(html, features='html.parser')
        return soup

    def getBookCode(self) -> str:
        book_code = self.url.split("/")[-1]
        return book_code

    def getBookName(self, soup) -> str:
        book_name = soup.find('div', attrs={'class': 'book'})\
            .find('h1')\
            .string
        return book_name

    def getBookAuthor(self, soup) -> str:
        book_author = soup.find('div', attrs={'class': 'book'})\
            .find('p')\
            .find('span')\
            .string
        return book_author

    def getBookInfo(self, soup) -> str:
        book_info = soup.find('div', attrs={'class': 'description w'})\
            .find('p')\
            .string

        return book_info

    def getChapterUrls(self, soup) -> List[str]:
        content_page = soup.find('div', attrs={'class': 'list w'}).find(
            'ul', attrs={'class': 'list'}).findAll('li')
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
            chapter_name = soup.find('div', attrs={'class': 'main w'})\
                .find('h1')\
                .string.split("(")[0]
        except:
            print(soup.prettify())
        return chapter_name

    async def getChapterContent(self, session, url) -> tuple[str, str]:
        self.browser.get(url)
        html = self.browser.page_source.encode('utf-8')
        soup = self.soupify(html)

        chapter_name = '<h2>{}</h2>'.format(self.getChapterName(soup))

        chapter_content_string = self._getChapterContent(url)

        chapter_content_string = chapter_name + chapter_content_string

        return chapter_name, chapter_content_string

    def _getChapterContent(self, url) -> str:
        self.browser.get(url)
        html = self.browser.page_source.encode('utf-8')
        soup = self.soupify(html)

        next_part_path = self._getNextPart(soup)

        if not next_part_path:
            # last page in chapter, get current page content and return
            current_part_content_string = self._getCurrentPartContent(url, soup)

            return current_part_content_string

        # get next page content
        next_part_url = self.url + '/' + \
            '/'.join(next_part_path.split('/')
                     [next_part_path.split('/').index(self.code)+1:])

        next_part_content_string = self._getChapterContent(next_part_url)
        
        # append next page content to current page content and return
        current_part_content_string = self._getCurrentPartContent(url, soup)

        current_part_content_string += next_part_content_string

        return current_part_content_string

    def _getCurrentPartContent(self, url, soup) -> str:
        # prevent cloudflare ddos block
        while soup.find('span', attrs={'class': 'cf-error-code'}) is not None:
            self.browser.close()
            asyncio.sleep(10)
            self.initializeBrowser()
            self.browser.get(url)
            html = self.browser.page_source.encode('utf-8')
            soup = self.soupify(html)

        current_part_content = soup.find('div', attrs={'class': 'articlebody', 'id': 'content'})\
            .findAll('p')

        cleaned_current_part_content = []
        for content in current_part_content:
            if content.string.startswith('本章尚未完結'):
                continue
            cleaned_current_part = content.string.replace(
                '\xa0', '').replace('本章已閱讀完畢(請點擊下一章繼續閱讀!)', '')
            cleaned_current_part_content.append('<p>{}</p>'.format(cleaned_current_part))

        current_part_content_string = ''.join(cleaned_current_part_content)
        return current_part_content_string

    def _getNextPart(self, soup) -> str:
        try:
            nav_links = soup.find('div', attrs={'class': 'list_page'})\
                .findAll('span')
            for span in nav_links:
                if span.find('a').string == '下一頁':
                    next_part_path = span.find('a')['href']
                    return next_part_path
        except:
            return ""
        
        return ""
