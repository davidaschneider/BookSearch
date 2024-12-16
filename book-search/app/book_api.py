from threading import Lock
from cachetools import LRUCache, cached
import requests
import asyncio
from aiohttp import ClientSession

from flask import current_app as app
from app.book import Book
from config import Config

@cached(cache=LRUCache(maxsize=1024, getsizeof=len), info=True, lock=Lock())
def search(title, page = 1, limit = Config.BOOKS_PER_PAGE): 
    fields = ['author_name', 'format', 'isbn', 'first_publish_year','title', 'first_sentence']
    headers = {'Content-Type': 'application/json'}
    params = 'q={}&page={}&limit={}&fields={}'.format(title, page, limit, ','.join(fields))
    r = requests.get('https://openlibrary.org/search.json', params, headers=headers) 
    res = r.json()
    books = []
    for b in res['docs']:
        # use cached books if we have them, since they might already be enriched.
        if 'isbn' in b and len(b['isbn']) > 0 and Book.get_by_isbn(b['isbn'][0]):
            books.append(Book.get_by_isbn(b['isbn'][0]))
        else:
            books.append(Book(b))
    return books, res['numFound'] 

def cover_url(isbn):
    try :  
        r = requests.get('https://openlibrary.org/api/books', f'bibkeys=ISBN:{isbn}&format=json')
        json = r.json()[f'ISBN:{isbn}']
        url = json['thumbnail_url'] if 'thumbnail_url' in json else None
        return url
    except: 
        app.logger.exception(f'Unable to retrieve cover for {isbn}.')
        return None

async def cover_url_async(isbn, session: ClientSession):
    """Given an ISBN number, fetch the URL of the cover of that book."""
    try: 
        resp = await(session.request(method='GET', url=f'https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json'))
        resp.raise_for_status()
        data = await(resp.json())
        data = data[f'ISBN:{isbn}']
        return data['thumbnail_url'] if 'thumbnail_url' in data else None
    except:
        app.logger.exception(f"Exception looking for cover for {isbn}:")
        return None

async def cover_urls_async(isbns): 
    session = ClientSession() #Config.get_client_session()
    tasks = []
    for isbn in isbns:
        tasks.append(
            cover_url_async(isbn, session)
        )
    result = await asyncio.gather(*tasks) 
    await session.close()
    return result
