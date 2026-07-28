# tests/test_user.py
import pytest
import sqlite3
from datetime import datetime, timedelta
from app.db import get_db
from app.models.user import (
    create_user,
    get_user_by_email,
    verify_password,
    create_password_reset_token,
    get_password_reset_token,
    update_password,
    mark_reset_token_used,
)


# ---------- create_user / get_user_by_email ----------

# creating a user should let us find them again by email
def test_create_and_get_user(app):
    with app.app_context():
        create_user("bob@example.com", "SecurePass123!")
        user = get_user_by_email("bob@example.com")

        assert user is not None
        assert user["email"] == "bob@example.com"

# looking up an email that was never created should return nothing
def test_get_user_by_email_not_found(app):
    with app.app_context():
        user = get_user_by_email("ghost@example.com")
        assert user is None

# the email column is UNIQUE — creating the same email twice should fail loudly
# rather than silently creating a duplicate account
def test_create_user_duplicate_email_raises(app):
    with app.app_context():
        create_user("bob@example.com", "SecurePass123!")

        with pytest.raises(sqlite3.IntegrityError):
            create_user("bob@example.com", "DifferentPass456!")

# stored password should never be the plaintext password — confirms hashing
# actually happened and isn't accidentally bypassed
def test_create_user_password_is_hashed(app):
    with app.app_context():
        create_user("bob@example.com", "SecurePass123!")
        user = get_user_by_email("bob@example.com")

        assert user["password_hash"] != "SecurePass123!"
        assert user["password_hash"].startswith("pbkdf2:sha256")


# ---------- verify_password ----------

# correct password should verify successfully against the stored hash
def test_verify_password_correct(app):
    with app.app_context():
        create_user("bob@example.com", "SecurePass123!")
        user = get_user_by_email("bob@example.com")

        assert verify_password(user, "SecurePass123!") is True

# wrong password should be rejected, not just silently pass
def test_verify_password_incorrect(app):
    with app.app_context():
        create_user("bob@example.com", "SecurePass123!")
        user = get_user_by_email("bob@example.com")

        assert verify_password(user, "WrongPassword") is False

# an empty string should never accidentally verify as correct
def test_verify_password_empty_string(app):
    with app.app_context():
        create_user("bob@example.com", "SecurePass123!")
        user = get_user_by_email("bob@example.com")

        assert verify_password(user, "") is False

# passwords should be checked case-sensitively — "securepass123!" != "SecurePass123!"
def test_verify_password_case_sensitive(app):
    with app.app_context():
        create_user("bob@example.com", "SecurePass123!")
        user = get_user_by_email("bob@example.com")

        assert verify_password(user, "securepass123!") is False


# ---------- create_password_reset_token ----------

# creating a reset token should return a non-empty, sufficiently random-looking string
def test_create_password_reset_token(app):
    with app.app_context():
        create_user("bob@example.com", "SecurePass123!")
        user = get_user_by_email("bob@example.com")

        token = create_password_reset_token(user["id"])

        assert token is not None
        assert len(token) > 20  # secrets.token_urlsafe(32) should generate a long string

# calling this twice for the same user currently creates two valid tokens —
# this test documents that behavior so it's a deliberate choice, not an accident
def test_create_password_reset_token_allows_multiple_active_tokens(app):
    with app.app_context():
        create_user("bob@example.com", "SecurePass123!")
        user = get_user_by_email("bob@example.com")

        token_one = create_password_reset_token(user["id"])
        token_two = create_password_reset_token(user["id"])

        assert token_one != token_two
        assert get_password_reset_token(token_one) is not None
        assert get_password_reset_token(token_two) is not None

# two tokens generated back-to-back should never collide
def test_create_password_reset_token_is_unique(app):
    with app.app_context():
        create_user("bob@example.com", "SecurePass123!")
        user = get_user_by_email("bob@example.com")

        tokens = {create_password_reset_token(user["id"]) for _ in range(20)}
        assert len(tokens) == 20


# ---------- get_password_reset_token ----------

# a freshly created, unused, non-expired token should be found in the database
def test_get_password_reset_token_valid(app):
    with app.app_context():
        create_user("bob@example.com", "SecurePass123!")
        user = get_user_by_email("bob@example.com")
        token = create_password_reset_token(user["id"])

        result = get_password_reset_token(token)

        assert result is not None
        assert result["token"] == token

# a token that was never created should not be found
def test_get_password_reset_token_invalid(app):
    with app.app_context():
        result = get_password_reset_token("fake-token-that-does-not-exist")
        assert result is None

# a token whose expires_at is in the past should never be returned as valid —
# this is the most security-critical check in the whole file
def test_get_password_reset_token_expired(app):
    with app.app_context():
        create_user("bob@example.com", "SecurePass123!")
        user = get_user_by_email("bob@example.com")

        # manually insert an already-expired token, since create_password_reset_token
        # only ever generates tokens 24h in the future
        db = get_db()
        expired_time = datetime.utcnow() - timedelta(hours=1)
        db.execute(
            "INSERT INTO password_reset_token (user_id, token, expires_at) VALUES (?, ?, ?)",
            (user["id"], "expired-test-token", expired_time)
        )
        db.commit()

        result = get_password_reset_token("expired-test-token")
        assert result is None

# a token expiring exactly "now" is a boundary case — confirms the ">" comparison
# in the SQL doesn't accidentally allow a token expiring this exact instant
def test_get_password_reset_token_at_expiry_boundary(app):
    with app.app_context():
        create_user("bob@example.com", "SecurePass123!")
        user = get_user_by_email("bob@example.com")

        db = get_db()
        now = datetime.utcnow()
        db.execute(
            "INSERT INTO password_reset_token (user_id, token, expires_at) VALUES (?, ?, ?)",
            (user["id"], "boundary-token", now)
        )
        db.commit()

        result = get_password_reset_token("boundary-token")
        assert result is None

# an empty string token should not match anything or raise an error
def test_get_password_reset_token_empty_string(app):
    with app.app_context():
        result = get_password_reset_token("")
        assert result is None


# ---------- update_password ----------

# updating the password should change the stored hash so old password fails and new one works
def test_update_password_changes_hash(app):
    with app.app_context():
        create_user("bob@example.com", "OldPassword123!")
        user = get_user_by_email("bob@example.com")

        update_password(user["id"], "NewPassword456!")
        updated_user = get_user_by_email("bob@example.com")

        assert verify_password(updated_user, "NewPassword456!") is True
        assert verify_password(updated_user, "OldPassword123!") is False

# calling update_password with a user_id that doesn't exist should not error —
# SQL UPDATE on zero matching rows is a silent no-op, so this documents that
def test_update_password_nonexistent_user_id_is_noop(app):
    with app.app_context():
        # should not raise, even though no row matches
        update_password(9999, "SomePassword123!")

        result = get_user_by_email("nobody@example.com")
        assert result is None


# ---------- mark_reset_token_used ----------

# once a reset token is marked as used, it should no longer be returned as valid
def test_mark_reset_token_used(app):
    with app.app_context():
        create_user("bob@example.com", "SecurePass123!")
        user = get_user_by_email("bob@example.com")
        token = create_password_reset_token(user["id"])

        mark_reset_token_used(token)

        # get_password_reset_token filters out used=1, so this should come back empty
        result = get_password_reset_token(token)
        assert result is None

# marking an already-used token as used again should not error
def test_mark_reset_token_used_twice_is_noop(app):
    with app.app_context():
        create_user("bob@example.com", "SecurePass123!")
        user = get_user_by_email("bob@example.com")
        token = create_password_reset_token(user["id"])

        mark_reset_token_used(token)
        mark_reset_token_used(token)  # should not raise

        result = get_password_reset_token(token)
        assert result is None

# marking a token that was never created should not error — silent no-op
def test_mark_reset_token_used_nonexistent_token_is_noop(app):
    with app.app_context():
        mark_reset_token_used("token-that-does-not-exist")  # should not raise