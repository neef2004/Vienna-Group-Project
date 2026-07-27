from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt

from app.models.user import create_user, get_user_by_email, verify_password
from app.utils.validators import is_valid_email, is_valid_password

# setup for revoked tokens. Used for signout
jwt_blocklist = set()  

# auth routes
auth_bp = Blueprint("auth", __name__)

# POST /login, check email & password, give back a login token.
# method: POST
# header: Content-Type: application/json
# body(json): email(str, required), password(str, required)
# return {"success":true, "user":{email}, "token": <jwt>} (200),
#        400 if bad/missing json or missing fields, 401 if wrong login
@auth_bp.route("/login", methods=['POST'])
# Authenticate a user by looking them up by email, checking the password, return a JWT.
def login():
    data = request.get_json(silent=True)

    if not data:
        # body was missing or not valid JSON
        return jsonify({"success": False, "error": "Invalid or missing JSON body"}), 400

    # normalize email (trim spaces, lowercase) so lookups are consistent
    # password must be provided as-is (case-sensitive)
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        # both fields must be present and non-empty
        return jsonify({"success": False, "error": "Email and password are required"}), 400

    user = get_user_by_email(email)

    # same error whether the email is unknown OR the password is wrong,
    # so an attacker can't tell which emails exist
    if user is None or not verify_password(user, password):
        return jsonify({"success": False, "error": "Invalid Login"}), 401

    # identity must be a string for the JWT; store the user id inside the token
    token = create_access_token(identity=str(user["id"]))

    return jsonify({
        "success": True,
        "user": {"id": user["id"], "email": user["email"]},
        "token": token
    }), 200

# POST /signup, make a new account. (also known as /register)
# method: POST
# header: Content-Type: application/json
# body(json): email(str, required), password(str, required), confirm_password(str, required)
# return {"success":true, "user":{email}} (201),
#        400 if missing fields / passwords don't match / bad email / weak password,
#        409 if email already registered
@auth_bp.route("/signup", methods=['POST']) # /register 
# Register a new account after validating email format, password strength, and uniqueness.
def signup():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "error": "Invalid or missing JSON body"}), 400

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    confirm_password = data.get("confirm_password", "") # second entry to catch typos

    if not email or not password or not confirm_password:
        # the two password entries must match
        return jsonify({
            "success": False,
            "error": "Email, password, and confirm password are required"
        }), 400

    if password != confirm_password:
        # the two password entries must match
        return jsonify({"success": False, "error": "Passwords do not match"}), 400

    if not is_valid_email(email):
        # reject bad email shape before touching the db
        return jsonify({"success": False, "error": "Invalid email format"}), 400

    # is_valid_password returns (bool, message); msg explains why it failed
    valid, msg = is_valid_password(password)
    if not valid:
        return jsonify({"success": False, "error": msg}), 400

    if get_user_by_email(email):
        # email already taken -> 409 conflict
        return jsonify({"success": False, "error": "Email is already registered"}), 409

    create_user(email, password) # model handles hashing the password

    user = get_user_by_email(email)

    return jsonify({"success": True, "user": {"id": user["id"], "email": email}}), 201

# POST /forgot-password, start a password reset. always says ok even if email is unknown (so no one can guess which emails exist).
# method: POST
# header: Content-Type: application/json
# body(json): email(str, required)
# return {"success":true, "reset_token": <token>, "message":...} (200) if email exists,
#        {"success":true, "message":"If email exists, reset link sent"} (200) if it doesn't,
#        400 if bad/missing json or no email
@auth_bp.route("/forgot-password", methods=['POST'])
# Start a password reset: create a reset token for a known email.
# Always reports success so outsiders can't discover which emails are registered.
def forgot_password():
    data = request.get_json(silent=True)
    
    if not data:
        return jsonify({"success": False, "error": "Invalid or missing JSON body"}), 400
    
    email = data.get("email", "").strip().lower()
    
    if not email:
        return jsonify({"success": False, "error": "Email is required"}), 400
    
    user = get_user_by_email(email)
    
    if not user:
        # unknown email will return the SAME success message, but do NOT create a token
        return jsonify({"success": True, "message": "If email exists, reset link sent"}), 200
    
    # imported here (not at top) to avoid a circular import with app.models.user
    from app.models.user import create_password_reset_token
    token = create_password_reset_token(user['id'])
    
    return jsonify({
        "success": True,
        "reset_token": token,
        "message": "Password reset token created"
    }), 200

# POST /reset-password, set a new password using the token from /forgot-password.
# method: POST
# header: Content-Type: application/json
# body(json): token(str, required), new_password(str, required), confirm_password(str, required)
# return {"success":true, "message":"Password reset successful"} (200),
#        400 if missing fields / passwords don't match / invalid or expired token / weak password
@auth_bp.route("/reset-password", methods=['POST'])
# Finish a password reset: validate the token + new password, then update it.
def reset_password():
    data = request.get_json(silent=True)
    
    if not data:
        return jsonify({"success": False, "error": "Invalid or missing JSON body"}), 400
    
    token = data.get("token") # the token issued by forgot_password
    new_password = data.get("new_password")
    confirm_password = data.get("confirm_password")
    
    if not token or not new_password or not confirm_password:
        # all three required
        return jsonify({"success": False, "error": "Token and passwords are required"}), 400
    
    if new_password != confirm_password:
        # the two new-password entries must match
        return jsonify({"success": False, "error": "Passwords do not match"}), 400
    
    # imported here to avoid circular imports
    from app.models.user import get_password_reset_token, update_password, mark_reset_token_used
    
    reset_token = get_password_reset_token(token)
    
    if not reset_token:
        # token doesn't exist, already used, or expired
        return jsonify({"success": False, "error": "Invalid or expired token"}), 400
    
    # check strength only after the token is confirmed valid
    valid, msg = is_valid_password(new_password)
    if not valid:
        return jsonify({"success": False, "error": msg}), 400
    
    # reset_token['user_id'] tells us whose password to change
    update_password(reset_token['user_id'], new_password)
    mark_reset_token_used(token) # burn the token so it can't be reused
    
    return jsonify({"success": True, "message": "Password reset successful"}), 200

# POST /signout, revoke the current JWT so it can no longer be used.
# method: POST
# header: Authorization: Bearer <jwt>
# return {"success":true, "message":"Successfully signed out"} (200),
#        401 if missing/invalid/expired token
@auth_bp.route("/signout", methods=['POST'])
@jwt_required()
# Revoke the current access token by adding its jti to the blocklist.
def signout():
    jti = get_jwt()["jti"]
    jwt_blocklist.add(jti)
    print("Blocklist after signout:", jwt_blocklist)

    return jsonify({"success": True, "message": "Successfully signed out"}), 200