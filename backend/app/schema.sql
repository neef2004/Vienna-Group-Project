-- schema.sql
-- Defines the structure of our database tables.
-- This file is run ONCE by init_db() (in db.py) to set up app.db
-- from scratch. Running it again will WIPE any existing data,
-- because of the DROP TABLE statement below — so don't re-run this
-- once you have real users you care about.

-- "IF EXISTS" prevents an error if the table doesn't exist yet
-- (e.g. the very first time you ever run this).
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    -- A unique numeric ID for each user, automatically generated
    -- and incremented by SQLite (1, 2, 3, ...). This is our primary
    -- key — the value we use internally to refer to "this exact user"
    -- (e.g. it's what gets stored inside the JWT identity claim).
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- The user's email address. TEXT is SQLite's generic string type.
    -- UNIQUE means the database itself will reject any INSERT that
    -- tries to use an email already in the table — this is our real
    -- safety net against duplicate accounts, backing up the
    -- application-level check in signup(). NOT NULL means this field
    -- can never be left empty.
    email TEXT UNIQUE NOT NULL,

    -- The HASHED password — never the raw password. This column stores
    -- the output of generate_password_hash() from user.py, which looks
    -- something like "pbkdf2:sha256:600000$somesalt$somehash".
    -- NOT NULL means every user must have a password set.
    password_hash TEXT NOT NULL,

    -- Automatically records when each user row was created.
    -- CURRENT_TIMESTAMP is a SQLite built-in that fills this in for you —
    -- you never need to set this manually when inserting a new user.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);