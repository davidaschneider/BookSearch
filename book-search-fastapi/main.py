import concurrent
from typing import Annotated
from fastapi import FastAPI, Query
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from book import Book, add_covers_to_books, enrich_fields_books_async
from pydantic_settings import BaseSettings

import book_api

class Settings(BaseSettings):
    books_per_page: int = 10
    model: str = 'llama3.2'

settings = Settings()
app = FastAPI()

@app.get("/search")
def search(title: str =Query ('', description="Search query, which is assumed to be part of the title."), 
           page: int = Query(1, description='Which page of search results should be returned.')):
    '''Search for books in the OpenLibrary API.'''
    [booksData, total_available] = book_api.search(title, settings.books_per_page, page)
    for i, b in enumerate(booksData):
        if 'isbn' in b and len(b['isbn']) > 0 and Book.get_by_isbn(b['isbn'][0]):
             book = Book.get_by_isbn(b['isbn'][0])
        else:
             book = Book(b)
        booksData[i] = book
    # Ideally, there'd a single pool, rather than this, which won't scale at all well.
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor: #push this higher in the file so there's just one.
        executor.submit(book_api.search, title, page + 1)
    return {'books': [b.toDict() for b in booksData],
            'total_available': total_available}

@app.get('/book')
async def book(isbn: Annotated[list[str], Query(description='ISBN numbers of books to retrieve')] = [], 
               field: Annotated[list[str], Query(description='Any fields that should be added to the book description.  Current valid values are "cover_url" and "summary".')] = []):
    """Gathers data about specific books, based on the ISBN numbers sent in.  This currently assumes that the books have already been found
       by a search.  If an ISBN number has not already been found in a call to /search, this service may return nothing for the book.
    ---
    responses:
        200:
            description: The book, with any enriched fields.
            examples:
                application/json: [{'title': 'Lord of the rings',
                                   'cover_url': 'http://whatever',
                                   'summary': 'A very well known book'}]
        500:
            description: 
            examples:
                application.json: {error: 'Unable to find a book with the ISBN 1234567890'}
    """
    books = []
    for isbn_num in isbn:
        b = Book.get_by_isbn(isbn_num)
        if b :
            books.append(b)
    if field == ['cover_url']:
        await add_covers_to_books(books)
    else :    
        for b in books:
            await enrich_fields_books_async(books, field)
    return [b.toDict() for b in books]

@app.get('/')
async def redirect():
    return RedirectResponse(url='/index.html')


app.mount("/", StaticFiles(directory="static"), name="static")