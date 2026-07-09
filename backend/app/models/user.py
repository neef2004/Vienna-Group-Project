from werkzeug.security import generate_password_hash, check_password_hash
from app.db import get_db
from datetime import datetime, timedelta
import secrets


def create_user(email, password):
    db = get_db()

    hashed_password = generate_password_hash(password, method="pbkdf2:sha256")

    db.execute(
        "INSERT INTO users (email, password_hash) VALUES (?, ?)",
        (email, hashed_password),
    )

    db.commit()


def get_user_by_email(email):
    db = get_db()

    return db.execute(
        "SELECT * FROM users WHERE email = ?", (email,)
    ).fetchone()


def verify_password(user, password):
    return check_password_hash(user["password_hash"], password)

def create_password_reset_token(user_id):
    db = get_db()
    
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=24)
    
    db.execute(
        "INSERT INTO password_reset_token (user_id, token, expires_at) VALUES (?, ?, ?)",
        (user_id, token, expires_at)
    )
    
    db.commit()
    
    return token


def get_password_reset_token(token):
    db = get_db()
    
    return db.execute(
        "SELECT * FROM password_reset_token WHERE token = ? AND used = 0 AND expires_at > ?",
        (token, datetime.utcnow())
    ).fetchone()


def update_password(user_id, new_password):
    db = get_db()
    
    hashed_password = generate_password_hash(new_password, method="pbkdf2:sha256")
    
    db.execute(
        "UPDATE users SET password_hash = ? WHERE id = ?",
        (hashed_password, user_id)
    )
    
    db.commit()


def mark_reset_token_used(token):
    db = get_db()
    
    db.execute(
        "UPDATE password_reset_token SET used = 1 WHERE token = ?",
        (token,)
    )
    
    db.commit()