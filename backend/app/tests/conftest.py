import os
import tempfile
import pytest
from app import create_app
from app.db import get_db


"""
Sets up a temporary database for testing
Provides fixtures for the Flask app and test client.

Creates a temporary SQLite database
Initializes the schema
Yields the app and client for use in tests.
"""

# path to schema.sql relative to THIS file, so it works no matter where the tests are run from
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "schema.sql")


# Creates a fresh Flask app with a temporary, empty test database
# runs before every test that uses it
@pytest.fixture
def app():
    db_fd, db_path = tempfile.mkstemp()
    app = create_app({
        "TESTING": True,
        "DATABASE": db_path,
    })
    with app.app_context():
        db = get_db()
        with open(SCHEMA_PATH) as f:
            db.executescript(f.read())
        db.commit()
        yield app
    os.close(db_fd)
    os.unlink(db_path)


# Fake HTTP client for the Flask app, used to make requests in tests
@pytest.fixture
def client(app):
    return app.test_client()


# creates a test user via /api/signup and returns headers with a real JWT,
# for tests that need to hit routes behind require_auth
@pytest.fixture
def auth_headers(client):
    client.post("/api/signup", json={
        "email": "user1@example.com",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!",
    })
    login_response = client.post("/api/login", json={
        "email": "user1@example.com",
        "password": "SecurePass123!",
    })
    token = login_response.get_json()["token"]
    return {"Authorization": f"Bearer {token}"}


# a second, separate test user — for tests that check cross-user access control
@pytest.fixture
def auth_headers_2(client):
    client.post("/api/signup", json={
        "email": "user2@example.com",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!",
    })
    login_response = client.post("/api/login", json={
        "email": "user2@example.com",
        "password": "SecurePass123!",
    })
    token = login_response.get_json()["token"]
    return {"Authorization": f"Bearer {token}"}