# user.py
# Handles all database operations related to users:
# creating new users, fetching by email, and verifying passwords.
# This file is the only place in the app that should know SQL syntax
# for the "users" table — everything else just calls these functions.

from werkzeug.security import generate_password_hash, check_password_hash
from app.db import get_db


def create_user(email, password):
    """
    Insert a new user into the database.

    We NEVER store the raw password — only a one-way hash of it.
    Even if someone steals the database, they can't recover the
    original password from the hash.
    """
    db = get_db()

    # generate_password_hash() does two things automatically:
    # 1. Generates a random "salt" (extra random data mixed into the hash
    #    so two users with the same password don't get the same hash)
    # 2. Hashes the password + salt together using the specified algorithm
    # The salt is stored INSIDE the returned string, so we don't need
    # a separate column for it.
    hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

    # "?" placeholders prevent SQL injection — never insert user input
    # directly into a SQL string with f-strings or string concatenation.
    db.execute(
        "INSERT INTO users (email, password_hash) VALUES (?, ?)",
        (email, hashed_password),
    )

    # commit() actually saves the change to the database file on disk.
    # Without this, the insert would be rolled back / lost.
    db.commit()


def get_user_by_email(email):
    """
    Look up a single user row by their email address.

    Returns:
        - A sqlite3.Row object (acts like a dict: row["email"], row["id"])
          if a matching user is found
        - None if no user with this email exists
    """
    db = get_db()

    # fetchone() returns just the first matching row, or None if there
    # were no matches at all. Since email is UNIQUE in our schema,
    # there will never be more than one match anyway.
    return db.execute(
        "SELECT * FROM users WHERE email = ?", (email,)
    ).fetchone()


def verify_password(user, password):
    """
    Checks whether a plaintext password attempt matches the hash
    stored for this user.

    check_password_hash() re-hashes the attempt using the same
    algorithm and salt embedded in the stored hash, then compares
    the two hashes. Returns True if they match, False otherwise.
    """
    return check_password_hash(user["password_hash"], password)