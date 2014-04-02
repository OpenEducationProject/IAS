from flask import g
import os
import sqlite3

def get_connection():
    if getattr(g, 'db', None) is None:
        g.db = sqlite3.connect(os.getenv("FLASK_DB_PATH", "database"))
    return g.db

def query_db(query, args=(), one=False):
    cur = get_connection().execute(query, args)
    rv = [dict((cur.description[idx][0], value)
          for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    get_connection().execute(query, args)
    get_connection().commit()
