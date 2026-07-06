# db.py
# Manages the SQLite database connection lifecycle for the app.
# This file is the ONLY place that knows how to open/close a raw
# database connection. Everything else (like models/user.py) just
# calls get_db() to get a working connection — it never opens one itself.

import sqlite3
from flask import g, current_app

# The filename of our SQLite database file. SQLite stores the entire
# database as a single file on disk — no separate server process needed,
# which makes it great for small projects and local development.
DATABASE = "app.db"


def get_db():
    """
    Returns a database connection for the CURRENT request.

    `g` is a special Flask object that's unique to each individual
    request — anything stored on `g` during a request disappears once
    that request finishes. We use it here to make sure we only open
    ONE database connection per request, even if get_db() gets called
    multiple times during that same request (e.g. once in get_user_by_email,
    once in create_user).
    """

    # "db" not in g  ->  we haven't already opened a connection this request
    if "db" not in g:
        # sqlite3.connect() opens (or creates, if it doesn't exist yet)
        # the database file and returns a connection object.
        g.db = sqlite3.connect(DATABASE)

        # By default, sqlite3 returns rows as plain tuples, meaning you'd
        # have to access fields by position: row[0], row[1], etc.
        # Setting row_factory to sqlite3.Row lets us access fields by
        # NAME instead, like row["email"] or row["password_hash"] —
        # which is exactly what auth.py and user.py expect.
        g.db.row_factory = sqlite3.Row

    # Whether we just created it above, or it already existed from
    # earlier in this same request, return the connection.
    return g.db


def close_db(e=None):
    """
    Closes the database connection at the end of a request, if one
    was opened. Flask calls this automatically — we never call it
    directly ourselves (see init_app() below).

    The `e` parameter receives any exception that occurred during the
    request, if there was one. We don't use it here, but Flask's
    teardown system always passes it in, so the parameter must exist.
    """

    # g.pop("db", None) removes "db" from `g` if it exists, and returns
    # its value — or returns None if it was never set. This is safer
    # than g.db, which would raise an error if no connection was ever opened.
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    """
    Creates all tables from scratch by running schema.sql.
    This is a ONE-TIME setup function — you run it once to create
    app.db with the correct table structure, not on every server start.
    Running it again would WIPE existing data, because schema.sql
    starts with "DROP TABLE IF EXISTS users".
    """

    db = get_db()

    # current_app.open_resource() opens a file relative to the app's
    # root folder — this is the standard Flask way to read bundled
    # files like schema.sql, rather than using plain open().
    with current_app.open_resource("schema.sql") as f:
        # executescript() runs multiple SQL statements at once
        # (schema.sql has both a DROP and a CREATE statement).
        # .decode("utf8") converts the file's raw bytes into a string,
        # since open_resource() opens files in binary mode by default.
        db.executescript(f.read().decode("utf8"))


def init_app(app):
    """
    Registers close_db() to run automatically whenever a Flask
    application context ends (i.e. after every request finishes).
    This is called once, from the app factory in __init__.py.
    """
    app.teardown_appcontext(close_db)