import json
import concurrent
from flask import Response, jsonify, render_template, redirect, request
from app import app, book_api
from app.book import Book, add_covers, enrich_fields_books

@app.route('/')
def index():
    return redirect('/index.html')


@app.route('/search', methods=['GET'])
def search():
    """Gathers data about books, based on what open library returns from the 'title' parameter.
    ---
    parameters:
      - title: the title to search for
        page: integer; which page of the results should be returned.
    responses:
        200:
            description: An array of book objects, along with the total number of search results.
            examples:
                application/json: {'books': [{'title': 'Lord of the rings'}],
                                   'total_available': 38}
    """
    title = request.args.get('title')
    page = request.args.get('page', '1')
    page = int(page) if page.isdigit() else 1
    [books, total_available] = book_api.search(title, page)
    for i, b in enumerate(books):
        if b.isbn in Book.books_by_isbn:
            books[i] = Book.books_by_isbn[b.isbn]
    # Ideally, there'd a single pool, rather than this, which won't scale at all well.
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        executor.submit(book_api.search, title, page + 1)
    return jsonify({'books': [b.toDict() for b in books],
                    'total_available': total_available})

@app.route('/book', methods=['GET'])
def book():
    """Gathers data about a specific book, based on the ISBN number sent in.
    ---
    parameters:
      - isbn: an array of ISBN numbers
        fields: list<str> a list of the fields that should be added to the standard description of each book
                Currently, 'cover_url' and 'summary' are supported.  If 'fields' is not provided, those two
                fields will be enriched.
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
    isbn = request.args.get('isbn', default='[]')
    fields= request.args.get('fields', default='["cover_url", "summary"]')
    fields = json.loads(fields)
    books = []
    if isbn and isbn.isdigit():
        b = Book.get_by_isbn(isbn)
        if b:
            books.append(b)
    elif isbn:
        for isbn_num in json.loads(isbn):
            b = Book.get_by_isbn(isbn_num)
            if b :
                books.append(b)
    if fields == ['cover_url']:
        add_covers(books)
    else :    
        for b in books:
            enrich_fields_books(books, fields)
    return jsonify( [b.toDict() for b in books] )
