# validators.py
# Pure validation logic — no Flask, no database, no side effects.
# These functions just take a string and return whether it passes
# our rules. Keeping validation separate from auth.py means we can
# test these functions on their own, and reuse them anywhere else
# in the app that needs the same checks (e.g. a "change password" route later).

import re  # Python's built-in regular expressions module


# A regex pattern for a "good enough" email format check.
# This is NOT a fully RFC-compliant email validator (that's notoriously
# complex), but it catches the common mistakes: missing "@", missing
# domain, or whitespace inside the address.
#
# Breaking the pattern down:
#   ^              start of string
#   [^@\s]+        one or more characters that are NOT "@" and NOT whitespace
#                  (this is the "local part" before the @, e.g. "john.doe")
#   @              a literal "@" symbol
#   [^@\s]+        one or more non-@, non-whitespace characters
#                  (the domain, e.g. "gmail")
#   \.             a literal "." character
#   [^@\s]+        one or more non-@, non-whitespace characters
#                  (the TLD, e.g. "com")
#   $              end of string
EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_valid_email(email: str) -> bool:
    """
    Returns True if the email matches our basic format requirements,
    False otherwise.

    .match() checks the pattern starting from the beginning of the string.
    bool(...) converts the match object (or None) into a clean True/False.
    """
    return bool(EMAIL_REGEX.match(email))


def is_valid_password(password: str):
    """
    Checks a password against our strength rules, one rule at a time.

    Returns a tuple: (is_valid, error_message)
        - (True, None)              if the password passes every check
        - (False, "some message")   on the FIRST rule it fails

    We check rules in order and return immediately on the first failure
    rather than checking everything and returning a list of all problems —
    this keeps the function simple, though you could change this later
    if you want to show the user every issue at once instead of one at a time.
    """

    # Rule 1: minimum length
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    # Rule 2: at least one uppercase letter (A-Z)
    # re.search() scans the WHOLE string looking for a match anywhere,
    # unlike re.match() which only checks the start of the string.
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"

    # Rule 3: at least one lowercase letter (a-z)
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"

    # Rule 4: at least one digit (0-9)
    # \d is shorthand for "any digit character"
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit"

    # Rule 5: at least one special character.
    # The character class below lists out common special characters.
    # Note: inside a [...] character class, most characters lose their
    # special regex meaning, so this is treated as a literal list of
    # allowed characters, not a complex pattern. The backslashes before
    # certain characters (like \- and \") are just to avoid ambiguity.
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=]", password):
        return False, "Password must contain at least one special character"

    # If we made it through every check above without returning early,
    # the password is valid.
    return True, None