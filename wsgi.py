"""WSGI entrypoint for gunicorn.

Importing this module initialises the DB connection pool once per worker and
exposes the Flask ``app`` object as ``wsgi:app``.
"""

from app import app, init_pool

init_pool()
