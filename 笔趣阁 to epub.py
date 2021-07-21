#!/usr/bin/env python3

from bs4 import BeautifulSoup, Doctype
from ebooklib import epub
from tqdm import tqdm
import urllib.request
import re
import os

def soupify(url):
    html_page = urllib.request.urlopen(url)
    soup = BeautifulSoup(html_page, features='html.parser')
    return soup

def getBookName(soup):
    book_name = soup.find('div', attrs={'id': 'info'})\
        .find('h1')\
            .string
    return book_name

def getBookAuthor(soup):
    book_author = soup.find('div', attrs={'id': 'info'})\
        .find('a', attrs={'href': re.compile('author')})\
            .string
    return book_author

def getBookInfo(soup):
    book_info = soup.find('div', attrs={'id': 'intro'})\
        .stripped_strings
    book_info_string = ''

    for content in book_info:
        if (re.search('<\w+\/?>', content, re.MULTILINE)):
            continue
        book_info_string += content

    return book_info_string

def getChapters(soup):
    content_page = soup.findAll('dd')
    chapters = []

    for content in content_page:
        try:
            chapter = content.find('a')['href']
        except:
            continue
        chapters.append(chapter)

    return chapters

def getChapterName(soup):
    chapter_name = soup.find('div', attrs={'class': 'bookname'})\
        .find('h1')\
            .string
    return chapter_name

def getChapterContent(soup, chapter_name):
    chapter_content = soup.find('div', attrs={'id': 'content'}).stripped_strings
    chapter_content_string = '<h2>' + chapter_name + '</h2>'

    for content in chapter_content:
        chapter_content_string += '<p>' + content + '</p>'

    return chapter_content_string

def initializeBook(book_code, book_name, book_author):
    book_epub = epub.EpubBook()
    book_epub.set_identifier(book_code)
    book_epub.set_title(book_name)
    book_epub.set_language('zh')
    book_epub.add_author(book_author)
    book_epub.toc = []
    book_epub.spine = ['nav']
    return book_epub

def createAboutPage(book, book_name, book_author, book_info, default_css):
    about = epub.EpubHtml(uid='title',\
        title='内容简介',\
        file_name='titlepage.xhtml')
    about.set_content('<h1>' + book_name + '</h1>' +\
        '<h1>' + '作者：' + book_author + '</h1>' +\
            '<p>' + '内容简介：' + book_info + '</p>')
    about.add_item(default_css)
    book_epub.add_item(about)
    book_epub.spine.insert(0, about)


def createEpubChapter(chapter_name, chapter_number, chapter_content, default_css):
    epub_chapter = epub.EpubHtml(uid=str(chapter_number),\
        title=chapter_name,\
        file_name=(str(chapter_number) + '.xhtml'))
    epub_chapter.set_content(chapter_content)
    epub_chapter.add_item(default_css)
    book_epub.add_item(epub_chapter)
    book_epub.toc.append(epub_chapter)
    book_epub.spine.append(epub_chapter)

if __name__ == "__main__":
    os.chdir(os.path.expanduser('~') + '/Downloads/')

    book_main_url = (input('Paste 笔趣阁 URL: '))
    while not re.match('https?:\/\/www\.xbiquge\.so\/book\/\d+\/', book_main_url):
        print('Invalid URL: Format should be https://www.xbiquge.cc/book/\{book_code\}/')
        book_main_url = (input('Paste 笔趣阁 URL: '))

    book_code = book_main_url[book_main_url.rfind('/', 0, -2):].replace('/', '')
    book_main_soup = soupify(book_main_url)
    book_name = getBookName(book_main_soup)
    book_author = getBookAuthor(book_main_soup)
    book_info = getBookInfo(book_main_soup)
    print('==================================================')
    print('书名：' + book_name)
    print('作者：' + book_author)
    print('内容简介：' + book_info)
    print('==================================================')

    book_epub = initializeBook(book_code, book_name, book_author)

    style = '''
        body {
            margin: 10px;
            font-size: 1em;
            word-wrap: break-word;
        }
        ul, li {
            list-style-type: none;
            margin: 0;
            padding: 0;
        }
        p {
            text-indent: 2em;
            line-height: 1.5em;
            margin-top: 0;
            margin-bottom: 1.5em;
        }
        .catalog {
            padding: 1.5em 0;
            font-size: 0.8em;
        }
        li {
            border-bottom: 1px solid #D5D5D5;
        }
        h1 {
            font-size: 1.6em;
            font-weight: bold;
        }
        h2 {
            display: block;
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 1.5em;
            margin-left: 0;
            margin-right: 0;
            margin-top: 1em;
            border-bottom: 1px solid;
        }
        .mbppagebreak {
            display: block;
            margin-bottom: 0;
            margin-left: 0;
            margin-right: 0;
            margin-top: 0;
        }
        a {
            color: inherit;
            text-decoration: none;
            cursor: default;
        }
        a[href] {
            color: blue;
            text-decoration: none;
            cursor: pointer;
        }
        .italic {
            font-style: italic;
        }
        '''
    default_css = epub.EpubItem(uid="style_default", file_name="style/default.css", media_type="text/css", content=style)
    book_epub.add_item(default_css)

    createAboutPage(book_epub, book_name, book_author, book_info, default_css)

    chapter_number = 0
    chapters = getChapters(book_main_soup)
    for chapter in tqdm(chapters):
        chapter_url = book_main_url + chapter
        chapter_soup = soupify(chapter_url)
        chapter_name = getChapterName(chapter_soup)
        chapter_number += 1
        chapter_content = getChapterContent(chapter_soup, chapter_name)
        createEpubChapter(chapter_name, chapter_number, chapter_content, default_css)
    print(str(chapter_number) + ' chapters downloaded')

    book_epub.add_item(epub.EpubNcx())
    book_epub.add_item(epub.EpubNav())
    filename = book_name + ' - ' + book_author + '.epub'
    epub.write_epub(filename, book_epub)
    print(filename + ' saved to ' + os.getcwd())
    exit(0)
