from abc import ABC, abstractmethod
from typing import List

from bs4 import BeautifulSoup


class SiteInterface(ABC):
    @abstractmethod
    def parseHtmlPage(self, url) -> BeautifulSoup:
        pass

    @abstractmethod
    def soupify(self, html) -> BeautifulSoup:
        pass

    @abstractmethod
    def getBookCode(self) -> str:
        pass

    @abstractmethod
    def getBookName(self, soup) -> str:
        pass

    @abstractmethod
    def getBookAuthor(self, soup) -> str:
        pass

    @abstractmethod
    def getBookInfo(self, soup) -> str:
        pass

    @abstractmethod
    def getChapterUrls(self, soup) -> List[str]:
        pass

    @abstractmethod
    def getChapterName(self, soup) -> str:
        pass

    @abstractmethod
    def getChapterContent(self, session, url) -> tuple[str, str]:
        pass
