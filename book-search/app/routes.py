import json
from flask import Response, jsonify, render_template, redirect, request
from app import app, book_api
from app.book import Book

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
    page = request.args.get('page')
    [books, total_available] = book_api.search(title, page)
    for i, b in enumerate(books):
        if b.isbn in Book.books_by_isbn:
            books[i] = Book.books_by_isbn[b.isbn]
    return jsonify({'books': [b.toDict() for b in books],
                    'total_available': total_available})

@app.route('/book', methods=['GET'])
def book():
    """Gathers data about a specific book, based on the ISBN number sent in.
    ---
    parameters:
      - isbn: the ISBN number of the book
        fields: list<str> a list of the fields that should be added to the standard description of the book
                Currently, 'cover_url' and 'summary' are supported.  If 'fields' is not provided, those two
                fields will be enriched.
    responses:
        200:
            description: The book, with any enriched fields.
            examples:
                application/json: {'title': 'Lord of the rings',
                                   'cover_url': 'http://whatever',
                                   'summary': 'A very well known book'}
        500:
            description: 
            examples:
                application.json: {error: 'Unable to find a book with the ISBN 1234567890'}
    """
    isbn = request.args.get('isbn', default=None)
    fields = json.loads(request.args.get('fields', default='["cover_url", "summary"]'))
    book = Book.get_by_isbn(isbn)
    if book == None :
        return Response(json.dumps({'error': f'Unable to find a book with the isbn {isbn}.'}), 500)
    book.enrich_fields(fields)
    return jsonify(book.toDict())
