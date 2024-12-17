import asyncio
import importlib
import json

from aiohttp import ClientSession
from summarize_api import summarize_async, summarize_multiple_async

class Book:
    main = importlib.import_module('main')
    book_api = importlib.import_module("book_api") # name could be pulled from config.  A step towards dependency injection of different ways to find books.

    # a cache for books.  In production, this would be something more sophisticated, like a redis cache, or at least an LRU cache.
    books_by_isbn = {}

    def __init__(self, book_dict) :
        self.authors = book_dict['author_name'] if 'author_name' in book_dict else []
        self.title = book_dict['title']
        self.isbn = book_dict['isbn'][0] if 'isbn' in book_dict else None
        self.publish_year = book_dict['first_publish_year'] if 'first_publish_year' in book_dict else None
        self.formats = book_dict['format'] if 'format' in book_dict else None
        self.cover_url = book_dict['cover_url'] if 'cover_url' in book_dict else None
        self.summary = book_dict['summary'] if 'summary' in book_dict else None
        self.fully_enriched = False
        if self.isbn:
            Book.books_by_isbn[self.isbn] = self

    def toJSON(self, fieldsToOmit = []):
        return json.dumps(
            self.toDict(fieldsToOmit),
            sort_keys=True,
            indent=2
        )
    
    def toDict(self, fieldsToOmit = []):
        return dictExceptFields(self.__dict__, fieldsToOmit)


    def set_cover_url(self, url: str):
        self.cover_url = url

    def set_summary(self, summary: str):
        self.summary = summary  
    
    async def add_summary(self, model:str):
        summary = await summarize_async(self.toJSON(['cover_url', 'summary', 'isbn']), model)
        self.summary = summary

    async def enrich_fields(self, fields = ['cover_url', 'summary']):
        '''Add the requested fields to self.'''
        fields = await self.gather_fields(fields)
        if fields[0] != None:
            self.cover_url = fields[0]
        if fields[1] != None: #this could overwrite, but that's OK. This value should be as good as the previous one.
            self.summary = fields[1]
        self.fully_enriched = len(fields) == 2 or (self.summary and self.cover_url)

    async def gather_fields(self, fields: list[str]) :
        '''Gather the requested fields simultaneously.'''
        tasks = []
        async with ClientSession() as session:
            if 'cover_url' in fields and self.cover_url == None:
                tasks.append(self.book_api.cover_url_async(self.isbn, session )) #Config.get_client_session()))             
            else:
                tasks.append(do_nothing_async())

            if 'summary' in fields and self.summary == None: # the omitted fields just produce nonsense from the LLM
                tasks.append(self.add_summary(Book.main.settings.model))
            else:
                tasks.append(do_nothing_async())
            result = await asyncio.gather(*tasks)
        return result
    
    @classmethod
    def get_by_isbn(cls, isbn):
        result = cls.books_by_isbn[isbn] if isbn in Book.books_by_isbn else None
        return result


## These functions operate on lists of books, not individual books.

async def add_covers_to_books(books: list[Book]):
    filtered_books = [b for b in books if b.cover_url == None]
    isbns = [ b.isbn for b in filtered_books]
    urls = await Book.book_api.cover_urls_async(isbns)
    for i, url in enumerate(urls):
        if filtered_books[i].cover_url == None: # just in case something else retrieved it while this was running
            filtered_books[i].cover_url = url

async def enrich_fields_books_async(books, fields):
    '''Enrich all elements of books with the relevant fields.  Note that the will all run simultaneously,
       so if they're not I/O bound, you might have to wait a long time to get any answers.  For non-I/O bound
       tasks like generating summaries, it's better to send them one at a time, so they can return as soon
       as each individual task is completed.'''
    async with asyncio.TaskGroup () as tg:
        for book in books:
            tg.create_task(book.enrich_fields(fields))
    return books


async def add_summaries_to_books(books: list[Book]):
    filtered_books = [b for b in books if b.summary == None]    
    jsons = [b.toJSON() for b in filtered_books]
    summaries = await summarize_multiple_async(jsons)
    for i, summary in enumerate(summaries):
        if filtered_books[i].summary == None: # just in case something else retrieved it while this was running
            filtered_books[i].summary = summary



## Utilities
def dictExceptFields(dict, fieldsToOmit: list[str], dropEmptyFields = True): 
    dict = {k:v for k, v in dict.items() if v} # remove empty fields
    return {k: dict[k] for k in set(list(dict.keys())) - set(fieldsToOmit)}

async def do_nothing_async():
    return