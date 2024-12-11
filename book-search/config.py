import asyncio
import os

from aiohttp import ClientSession

class Config:
    # boilerplate params
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret-keys-should-not-be-default-values'
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['book-errors@example.com']
    # book-search specific params
    BOOKS_PER_PAGE = 10
    MODEL = 'llama3.2'
