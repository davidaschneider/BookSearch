import logging
import requests
import asyncio
from aiohttp import ClientSession

def search(title, limit: int, page = 1 ): 
    fields = ['author_name', 'format', 'isbn', 'first_publish_year','title', 'first_sentence']
    headers = {'Content-Type': 'application/json'}
    params = 'q={}&page={}&limit={}&fields={}'.format(title, page, limit, ','.join(fields))
    r = requests.get('https://openlibrary.org/search.json', params, headers=headers) 
    res = r.json()
    books = res['docs']
    return books, res['numFound'] 

def cover_url(isbn):
    """Given an ISBN number, fetch the URL of the cover of that book."""
    try :  
        r = requests.get('https://openlibrary.org/api/books', f'bibkeys=ISBN:{isbn}&format=json')
        json = r.json()[f'ISBN:{isbn}']
        url = json['thumbnail_url'] if 'thumbnail_url' in json else None
        return url
    except: 
        logging.exception(f'Unable to retrieve cover for {isbn}.')
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
        logging.exception(f"Exception looking for cover for {isbn}:")
        return None

async def cover_urls_async(isbns): 
    async with ClientSession() as session:
        tasks = []
        for isbn in isbns:
            tasks.append(
                cover_url_async(isbn, session)
            )
        result = await asyncio.gather(*tasks) 
    return result
