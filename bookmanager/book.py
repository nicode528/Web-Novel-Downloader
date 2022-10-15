#!/usr/bin/env python3

import asyncio

import aiohttp
from ebooklib import epub
from tqdm.asyncio import tqdm
from tqdm import tqdm as tq


class Book:
    def __init__(self, siteManager) -> None:
        self.siteManager = siteManager
        self.code = self.siteManager.getBookCode()
        soup = self.siteManager.parseHtmlPage(self.siteManager.url)
        self.name = self.siteManager.getBookName(soup)
        try:
            self.author = self.siteManager.getBookAuthor(soup)
        except:
            self.author = "unknown"
        self.info = self.siteManager.getBookInfo(soup)
        self.chapter_urls = self.siteManager.getChapterUrls(soup)
        self.chapters = []
        self.style = '''
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
        print('==================================================')
        print('书名：' + self.name)
        print('作者：' + self.author)
        print('内容简介：' + self.info)
        print('==================================================')

    def _initialize_book(self):
        self.book = epub.EpubBook()
        self.book.set_identifier(self.code)
        self.book.set_title(self.name)
        self.book.set_language('zh')
        self.book.add_author(self.author)
        self.book.toc = []
        self.book.spine = ['nav']
        self.css = epub.EpubItem(
            uid="style_default", file_name="style/default.css", media_type="text/css", content=self.style)
        self.book.add_item(self.css)

    def _create_about_page(self):
        about = epub.EpubHtml(uid='title',
                              title='内容简介',
                              file_name='titlepage.xhtml')
        about.set_content('<h1>' + self.name + '</h1>' +
                          '<h1>' + '作者：' + self.author + '</h1>' +
                          '<p>' + '内容简介：' + self.info + '</p>')
        about.add_item(self.css)
        self.book.add_item(about)
        self.book.spine.insert(0, about)

    async def _create_chapters(self):
        async with aiohttp.ClientSession() as session:
            tasks = []
            chapter_number = 0
            pbar = tq(total=len(self.chapter_urls))
            for url in self.chapter_urls:
                chapter_number += 1
                tasks.append(self._create_chapter(
                    session, url, chapter_number, pbar))
            for task in asyncio.as_completed(tasks):
                await task

        pbar.close()
        self.chapters = sorted(self.chapters, key=lambda c: list(c.keys()))
        for chapter in self.chapters:
            chapter_content = list(chapter.values())[0]
            self.book.add_item(chapter_content)
            self.book.toc.append(chapter_content)
            self.book.spine.append(chapter_content)
        print('\n{} chapters downloaded'.format(chapter_number))

    async def _create_chapter(self, session, url, chapter_number, pbar):
        chapter_name, chapter_content = await self.siteManager.getChapterContent(session, url)
        chapter = epub.EpubHtml(uid=str(chapter_number),
                                title=chapter_name,
                                file_name=('{}.xhtml'.format(chapter_number)))
        chapter.set_content(chapter_content)
        chapter.add_item(self.css)
        self.chapters.append({chapter_number: chapter})
        pbar.update(1)

    def build(self):
        self._initialize_book()
        self._create_about_page()
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(self._create_chapters())

    def export(self, destination):
        filename = '{}{} - {}.epub'.format(destination, self.name, self.author)
        epub.write_epub(filename, self.book)
        print("exported to " + filename)
