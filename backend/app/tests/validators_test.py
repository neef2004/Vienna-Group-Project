# tests/test_validators.py
import pytest
from app.utils.validators import is_valid_email, is_valid_password


# ---------- is_valid_email ----------

# a properly formatted email should return True
def test_is_valid_email_valid():
    assert is_valid_email("bob@example.com") is True

# missing @ symbol should be rejected
def test_is_valid_email_missing_at_symbol():
    assert is_valid_email("bobexample.com") is False

# missing domain extension (e.g. ".com") should be rejected
def test_is_valid_email_missing_domain():
    assert is_valid_email("bob@example") is False

# empty string should be rejected
def test_is_valid_email_empty_string():
    assert is_valid_email("") is False

# whitespace inside the email should be rejected
def test_is_valid_email_has_whitespace():
    assert is_valid_email("bob @example.com") is False


# ---------- is_valid_password ----------

# a password meeting all rules should return (True, None)
def test_is_valid_password_valid():
    valid, errors = is_valid_password("SecurePass123!")
    assert valid is True
    assert errors == []

# too short, even with all the right character types
def test_is_valid_password_too_short():
    valid, msg = is_valid_password("Sh0rt!")
    assert valid is False
    assert "8 characters" in msg

# missing an uppercase letter
def test_is_valid_password_no_uppercase():
    valid, msg = is_valid_password("securepass123!")
    assert valid is False
    assert "uppercase" in msg

# missing a lowercase letter
def test_is_valid_password_no_lowercase():
    valid, errors = is_valid_password("SECUREPASS123!")
    assert valid is False
    assert any("lowercase" in e for e in errors)

# missing a digit
def test_is_valid_password_no_digit():
    valid, errors = is_valid_password("SecurePassword!")
    assert valid is False
    assert any("digit" in e for e in errors)

# missing a special character
def test_is_valid_password_no_special_char():
    valid, errors = is_valid_password("SecurePass123")
    assert valid is False
    assert any("special character" in e for e in errors)

# empty string should fail on the length check first
def test_is_valid_password_empty_string():
    valid, errors = is_valid_password("")
    assert valid is False
    assert any("8 characters" in e for e in errors)

# is_valid_password doesn't guard against None — this documents that it currently
# raises a raw TypeError rather than returning (False, "some message")
def test_is_valid_password_none_raises_typeerror():
    with pytest.raises(TypeError):
        is_valid_password(None)

# each test now checks the message is IN the list, not equal to a single string
def test_is_valid_password_too_short():
    valid, errors = is_valid_password("Sh0rt!")
    assert valid is False
    assert any("8 characters" in e for e in errors)

def test_is_valid_password_no_uppercase():
    valid, errors = is_valid_password("securepass123!")
    assert valid is False
    assert any("uppercase" in e for e in errors)