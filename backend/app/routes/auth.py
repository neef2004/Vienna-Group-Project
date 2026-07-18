from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token

from app.models.user import create_user, get_user_by_email, verify_password
from app.utils.validators import is_valid_email, is_valid_password


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=['POST'])
def login():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"success": False, "error": "Invalid or missing JSON body"}), 400

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"success": False, "error": "Email and password are required"}), 400

    user = get_user_by_email(email)

    if user is None or not verify_password(user, password):
        return jsonify({"success": False, "error": "Invalid Login"}), 401

    token = create_access_token(identity=str(user["id"]))

    return jsonify({
        "success": True,
        "user": {"id": user["id"], "email": user["email"]},
        "token": token
    }), 200


@auth_bp.route("/signup", methods=['POST']) # /register 
def signup():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"success": False, "error": "Invalid or missing JSON body"}), 400

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    confirm_password = data.get("confirm_password", "")

    if not email or not password or not confirm_password:
        return jsonify({
            "success": False,
            "error": "Email, password, and confirm password are required"
        }), 400

    if password != confirm_password:
        return jsonify({"success": False, "error": "Passwords do not match"}), 400

    if not is_valid_email(email):
        return jsonify({"success": False, "error": "Invalid email format"}), 400

    valid, msg = is_valid_password(password)
    if not valid:
        return jsonify({"success": False, "error": msg}), 400

    if get_user_by_email(email):
        return jsonify({"success": False, "error": "Email is already registered"}), 409

    create_user(email, password)

    user = get_user_by_email(email)

    return jsonify({"success": True, "user": {"id": user["id"], "email": email}}), 201

@auth_bp.route("/forgot-password", methods=['POST'])
def forgot_password():
    data = request.get_json(silent=True)
    
    if not data:
        return jsonify({"success": False, "error": "Invalid or missing JSON body"}), 400
    
    email = data.get("email", "").strip().lower()
    
    if not email:
        return jsonify({"success": False, "error": "Email is required"}), 400
    
    user = get_user_by_email(email)
    
    if not user:
        return jsonify({"success": True, "message": "If email exists, reset link sent"}), 200
    
    from app.models.user import create_password_reset_token
    token = create_password_reset_token(user['id'])
    
    return jsonify({
        "success": True,
        "reset_token": token,
        "message": "Password reset token created"
    }), 200


@auth_bp.route("/reset-password", methods=['POST'])
def reset_password():
    data = request.get_json(silent=True)
    
    if not data:
        return jsonify({"success": False, "error": "Invalid or missing JSON body"}), 400
    
    token = data.get("token")
    new_password = data.get("new_password")
    confirm_password = data.get("confirm_password")
    
    if not token or not new_password or not confirm_password:
        return jsonify({"success": False, "error": "Token and passwords are required"}), 400
    
    if new_password != confirm_password:
        return jsonify({"success": False, "error": "Passwords do not match"}), 400
    
    from app.models.user import get_password_reset_token, update_password, mark_reset_token_used
    
    reset_token = get_password_reset_token(token)
    
    if not reset_token:
        return jsonify({"success": False, "error": "Invalid or expired token"}), 400
    
    valid, msg = is_valid_password(new_password)
    if not valid:
        return jsonify({"success": False, "error": msg}), 400
    
    update_password(reset_token['user_id'], new_password)
    mark_reset_token_used(token)
    
    return jsonify({"success": True, "message": "Password reset successful"}), 200