# tests/test_auth.py
import pytest
from flask_jwt_extended import decode_token
from app.models.user import create_password_reset_token, get_user_by_email


# ---------- POST /api/signup ----------

# a valid signup should create the user and return 201
def test_signup_success(client):
    response = client.post("/api/signup", json={
        "email": "bob@example.com",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!",
    })

    assert response.status_code == 201
    assert response.get_json()["success"] is True
    assert response.get_json()["user"]["email"] == "bob@example.com"

# missing body entirely should return 400, not crash
def test_signup_missing_json_body(client):
    response = client.post("/api/signup")
    assert response.status_code == 400

# a JSON body that isn't a dict (e.g. a list) should return 400, not a 500 crash
def test_signup_non_dict_json_body(client):
    response = client.post("/api/signup", json=["not", "a", "dict"])
    assert response.status_code == 400

# missing a required field should return 400
def test_signup_missing_password(client):
    response = client.post("/api/signup", json={
        "email": "bob@example.com",
        "confirm_password": "SecurePass123!",
    })
    assert response.status_code == 400

# mismatched password/confirm_password should return 400
def test_signup_passwords_dont_match(client):
    response = client.post("/api/signup", json={
        "email": "bob@example.com",
        "password": "SecurePass123!",
        "confirm_password": "DifferentPass456!",
    })
    assert response.status_code == 400
    assert "match" in response.get_json()["error"].lower()

# malformed email should return 400
def test_signup_invalid_email(client):
    response = client.post("/api/signup", json={
        "email": "not-an-email",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!",
    })
    assert response.status_code == 400

# weak password should return 400 with a helpful message
def test_signup_weak_password(client):
    response = client.post("/api/signup", json={
        "email": "bob@example.com",
        "password": "weak",
        "confirm_password": "weak",
    })
    assert response.status_code == 400

# signing up with an email that's already registered should return 409, not 500
def test_signup_duplicate_email(client):
    client.post("/api/signup", json={
        "email": "bob@example.com",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!",
    })

    response = client.post("/api/signup", json={
        "email": "bob@example.com",
        "password": "AnotherPass456!",
        "confirm_password": "AnotherPass456!",
    })

    assert response.status_code == 409

# duplicate check should be case-insensitive — "Bob@" and "bob@" are the same account
def test_signup_duplicate_email_different_case(client):
    client.post("/api/signup", json={
        "email": "bob@example.com",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!",
    })

    response = client.post("/api/signup", json={
        "email": "BOB@EXAMPLE.COM",
        "password": "AnotherPass456!",
        "confirm_password": "AnotherPass456!",
    })

    assert response.status_code == 409


# ---------- POST /api/login ----------

# correct credentials should return 200 with a token
def test_login_success(client):
    client.post("/api/signup", json={
        "email": "bob@example.com",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!",
    })

    response = client.post("/api/login", json={
        "email": "bob@example.com",
        "password": "SecurePass123!",
    })

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert "token" in body

# the JWT returned should actually encode the correct user's id — confirms
# create_access_token() is wired to the right user, not just that a token exists
def test_login_token_contains_correct_user_id(client, app):
    client.post("/api/signup", json={
        "email": "bob@example.com",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!",
    })

    response = client.post("/api/login", json={
        "email": "bob@example.com",
        "password": "SecurePass123!",
    })
    token = response.get_json()["token"]

    with app.app_context():
        decoded = decode_token(token)
        user = get_user_by_email("bob@example.com")
        assert decoded["sub"] == str(user["id"])

# wrong password should return 401
def test_login_wrong_password(client):
    client.post("/api/signup", json={
        "email": "bob@example.com",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!",
    })

    response = client.post("/api/login", json={
        "email": "bob@example.com",
        "password": "WrongPassword!",
    })

    assert response.status_code == 401

# unknown email should return 401 — same status/message as wrong password,
# so an attacker can't tell which emails are registered
def test_login_unknown_email(client):
    response = client.post("/api/login", json={
        "email": "ghost@example.com",
        "password": "SomePassword123!",
    })

    assert response.status_code == 401

# unknown-email and wrong-password responses should be identical,
# confirming no user-enumeration leak between the two cases
def test_login_error_messages_dont_leak_which_emails_exist(client):
    client.post("/api/signup", json={
        "email": "bob@example.com",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!",
    })

    wrong_password_response = client.post("/api/login", json={
        "email": "bob@example.com",
        "password": "WrongPassword!",
    })
    unknown_email_response = client.post("/api/login", json={
        "email": "ghost@example.com",
        "password": "WrongPassword!",
    })

    assert wrong_password_response.status_code == unknown_email_response.status_code
    assert wrong_password_response.get_json()["error"] == unknown_email_response.get_json()["error"]

# missing fields should return 400
def test_login_missing_password(client):
    response = client.post("/api/login", json={"email": "bob@example.com"})
    assert response.status_code == 400

# login should work even if the email was typed with different casing/whitespace
def test_login_email_case_and_whitespace_normalized(client):
    client.post("/api/signup", json={
        "email": "bob@example.com",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!",
    })

    response = client.post("/api/login", json={
        "email": "  BOB@Example.com  ",
        "password": "SecurePass123!",
    })

    assert response.status_code == 200


# ---------- POST /api/forgot-password ----------

# a known email should return 200 and include a reset token
def test_forgot_password_known_email(client):
    client.post("/api/signup", json={
        "email": "bob@example.com",
        "password": "SecurePass123!",
        "confirm_password": "SecurePass123!",
    })

    response = client.post("/api/forgot-password", json={"email": "bob@example.com"})

    assert response.status_code == 200
    assert "reset_token" in response.get_json()

# an unknown email should still return 200 with the same generic message —
# this prevents attackers from using this endpoint to discover valid emails
def test_forgot_password_unknown_email_still_returns_200(client):
    response = client.post("/api/forgot-password", json={"email": "ghost@example.com"})

    assert response.status_code == 200
    assert "reset_token" not in response.get_json()

# missing email should return 400
def test_forgot_password_missing_email(client):
    response = client.post("/api/forgot-password", json={})
    assert response.status_code == 400


# ---------- POST /api/reset-password ----------

# a valid token + matching new password should succeed and actually update the password
def test_reset_password_success(client, app):
    client.post("/api/signup", json={
        "email": "bob@example.com",
        "password": "OldPassword123!",
        "confirm_password": "OldPassword123!",
    })

    with app.app_context():
        user = get_user_by_email("bob@example.com")
        token = create_password_reset_token(user["id"])

    response = client.post("/api/reset-password", json={
        "token": token,
        "new_password": "NewPassword456!",
        "confirm_password": "NewPassword456!",
    })

    assert response.status_code == 200

    # confirm the new password actually works via login
    login_response = client.post("/api/login", json={
        "email": "bob@example.com",
        "password": "NewPassword456!",
    })
    assert login_response.status_code == 200

# an invalid/nonexistent token should return 400
def test_reset_password_invalid_token(client):
    response = client.post("/api/reset-password", json={
        "token": "fake-token-does-not-exist",
        "new_password": "NewPassword456!",
        "confirm_password": "NewPassword456!",
    })

    assert response.status_code == 400

# a token that's already been used once should be rejected on second use
def test_reset_password_token_cannot_be_reused(client, app):
    client.post("/api/signup", json={
        "email": "bob@example.com",
        "password": "OldPassword123!",
        "confirm_password": "OldPassword123!",
    })

    with app.app_context():
        user = get_user_by_email("bob@example.com")
        token = create_password_reset_token(user["id"])

    # first use should succeed
    client.post("/api/reset-password", json={
        "token": token,
        "new_password": "NewPassword456!",
        "confirm_password": "NewPassword456!",
    })

    # second use of the same token should fail
    response = client.post("/api/reset-password", json={
        "token": token,
        "new_password": "AnotherPassword789!",
        "confirm_password": "AnotherPassword789!",
    })

    assert response.status_code == 400

# mismatched new_password/confirm_password should return 400
def test_reset_password_passwords_dont_match(client, app):
    client.post("/api/signup", json={
        "email": "bob@example.com",
        "password": "OldPassword123!",
        "confirm_password": "OldPassword123!",
    })

    with app.app_context():
        user = get_user_by_email("bob@example.com")
        token = create_password_reset_token(user["id"])

    response = client.post("/api/reset-password", json={
        "token": token,
        "new_password": "NewPassword456!",
        "confirm_password": "DifferentPassword789!",
    })

    assert response.status_code == 400

# a weak new password should be rejected even with a valid token
def test_reset_password_weak_new_password(client, app):
    client.post("/api/signup", json={
        "email": "bob@example.com",
        "password": "OldPassword123!",
        "confirm_password": "OldPassword123!",
    })

    with app.app_context():
        user = get_user_by_email("bob@example.com")
        token = create_password_reset_token(user["id"])

    response = client.post("/api/reset-password", json={
        "token": token,
        "new_password": "weak",
        "confirm_password": "weak",
    })

    assert response.status_code == 400

# a reset token belonging to one user should never affect a different user's password —
# guards against a bug like accidentally using the wrong user_id when updating
def test_reset_password_only_affects_correct_user(client, app):
    client.post("/api/signup", json={
        "email": "bob@example.com",
        "password": "BobPass123!",
        "confirm_password": "BobPass123!",
    })
    client.post("/api/signup", json={
        "email": "alice@example.com",
        "password": "AlicePass123!",
        "confirm_password": "AlicePass123!",
    })

    with app.app_context():
        bob = get_user_by_email("bob@example.com")
        token = create_password_reset_token(bob["id"])

    client.post("/api/reset-password", json={
        "token": token,
        "new_password": "NewBobPass456!",
        "confirm_password": "NewBobPass456!",
    })

    # alice's password should be completely untouched
    alice_login = client.post("/api/login", json={
        "email": "alice@example.com",
        "password": "AlicePass123!",
    })
    assert alice_login.status_code == 200

# password missing uppercase, length, AND special char should report ALL three,
def test_signup_reports_all_password_errors_pop1234(client):
    response = client.post("/api/signup", json={
        "email": "example@user.com",
        "password": "pop1234",
        "confirm_password": "pop1234",
    })

    assert response.status_code == 400
    errors = response.get_json()["errors"]

    assert any("uppercase" in e.lower() for e in errors)
    assert any("8 characters" in e for e in errors)
    assert any("special character" in e.lower() for e in errors)

# password missing uppercase AND special char should report both
def test_signup_reports_all_password_errors_pop12345(client):
    response = client.post("/api/signup", json={
        "email": "example@user.com",
        "password": "pop12345",
        "confirm_password": "pop12345",
    })

    assert response.status_code == 400
    errors = response.get_json()["errors"]

    assert any("uppercase" in e.lower() for e in errors)
    assert any("special character" in e.lower() for e in errors)
    # "pop12345" is 8 characters
    assert not any("8 characters" in e for e in errors)