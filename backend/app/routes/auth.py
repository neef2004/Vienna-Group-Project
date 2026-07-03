# auth.py
# Defines the authentication endpoints for the app: signup and login.
# This file handles HTTP request/response logic ONLY — it does not talk
# to the database directly. All database work is delegated to functions
# imported from app.models.user, and validation rules live in
# app.utils.validators. Keeping these separated makes each file easier
# to test and reason about on its own.

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token

# These three functions are the only way this file touches the database.
# create_user()        -> inserts a new row into the users table
# get_user_by_email()  -> fetches a single user row, or None if not found
# verify_password()    -> compares a plaintext attempt against the stored hash
from app.models.user import create_user, get_user_by_email, verify_password

# These two functions check that submitted data meets our rules
# (valid email format, strong enough password) before we touch the database.
from app.utils.validators import is_valid_email, is_valid_password


# A Blueprint groups related routes together so they can be registered
# on the main Flask app as a single unit. "auth" is just a name Flask
# uses internally to refer to this group of routes.
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=['POST'])
def login():
    """
    POST /api/login
    Expects JSON body: { "email": "...", "password": "..." }

    On success: returns a JWT access token the frontend can use to
    authenticate future requests.
    On failure: returns a generic "Invalid Login" error (we don't say
    whether the email or the password specifically was wrong, since
    that would help an attacker guess which emails are registered).
    """

    # get_json(silent=True) parses the incoming JSON body.
    # silent=True means: if the body is missing or malformed,
    # return None instead of throwing an exception and crashing the server.
    data = request.get_json(silent=True)

    if not data:
        # No JSON body at all, or it wasn't valid JSON.
        # 400 = Bad Request: the client sent something we can't process.
        return jsonify({"success": False, "error": "Invalid or missing JSON body"}), 400

    # .get(key, default) avoids a KeyError if the field is missing.
    # We also normalize the email: strip() removes accidental
    # leading/trailing whitespace, lower() ensures "User@Mail.com"
    # and "user@mail.com" are treated as the same account.
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        # Either field was empty/missing after extraction.
        return jsonify({"success": False, "error": "Email and password are required"}), 400

    # Look the user up in the database. Returns None if no match.
    user = get_user_by_email(email)

    # Combined check: either the user doesn't exist, OR the password
    # doesn't match. We deliberately use ONE error message for both
    # cases (see docstring above) — this is a security best practice
    # to avoid leaking which emails are registered.
    if user is None or not verify_password(user, password):
        # 401 = Unauthorized: credentials are invalid.
        return jsonify({"success": False, "error": "Invalid Login"}), 401

    # At this point, the user is verified. Create a signed JWT containing
    # their user ID as the "identity" claim. str() is used because
    # flask_jwt_extended expects identity to be a string, not a raw int.
    token = create_access_token(identity=str(user["id"]))

    # 200 = OK: everything succeeded. Send back the token and basic
    # (non-sensitive) user info. NEVER send back the password_hash.
    return jsonify({
        "success": True,
        "user": {"email": user["email"]},
        "token": token
    }), 200


@auth_bp.route("/signup", methods=['POST'])
def signup():
    """
    POST /api/signup
    Expects JSON body:
    {
        "email": "...",
        "password": "...",
        "confirm_password": "..."
    }

    Creates a new user account if all validation passes.
    """

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "error": "Invalid or missing JSON body"}), 400

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    confirm_password = data.get("confirm_password", "")

    # Step 1: Make sure nothing required is missing.
    if not email or not password or not confirm_password:
        return jsonify({
            "success": False,
            "error": "Email, password, and confirm password are required"
        }), 400

    # Step 2: Make sure the two password fields match.
    # This check should ALSO happen on the frontend for instant feedback,
    # but we never trust the frontend alone — always re-check on the backend.
    if password != confirm_password:
        return jsonify({"success": False, "error": "Passwords do not match"}), 400

    # Step 3: Validate email format (e.g. must contain "@" and a domain).
    if not is_valid_email(email):
        return jsonify({"success": False, "error": "Invalid email format"}), 400

    # Step 4: Validate password strength (length, uppercase, lowercase,
    # digit, special character — see validators.py for exact rules).
    # is_valid_password returns a tuple: (True/False, error message or None)
    valid, msg = is_valid_password(password)
    if not valid:
        return jsonify({"success": False, "error": msg}), 400

    # Step 5: Check for an existing account with this email.
    # This is a friendly early check — the real safety net is the
    # UNIQUE constraint on the email column in the database itself,
    # which prevents duplicates even under race conditions.
    if get_user_by_email(email):
        # 409 = Conflict: the resource (this email) already exists.
        return jsonify({"success": False, "error": "Email is already registered"}), 409

    # Step 6: All checks passed — create the user.
    # create_user() handles hashing the password internally;
    # this file never sees or stores the raw password beyond this point.
    create_user(email, password)

    # 201 = Created: a new resource (the user account) was successfully made.
    return jsonify({"success": True, "user": {"email": email}}), 201