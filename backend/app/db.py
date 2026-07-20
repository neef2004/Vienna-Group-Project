import sqlite3
from flask import g, current_app

DATABASE = "app.db"

# open a sqlite connection for this request (reuse if already open) and return rows as dict-like objects
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row

    return g.db

# close the request's db connection if one was opened
def close_db(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()

# create the database tables by running schema.sql
def init_db():
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))

# register close_db to run automatically when each request/app context ends
def init_app(app):
    app.teardown_appcontext(close_db)