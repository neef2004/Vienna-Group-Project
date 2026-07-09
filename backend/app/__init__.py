from flask import Flask
from flask_jwt_extended import JWTManager
from app.routes.auth import auth_bp
from app.routes.trips import trips_bp
from app.routes.itineraries import itineraries_bp
from app.routes.reminders import reminders_bp
from app.routes.collaborators import collaborators_bp
from app import db as db_module


def create_app():
    app = Flask(__name__)

    app.config["JWT_SECRET_KEY"] = "change-this-to-a-real-secret"
    app.config["DATABASE"] = "app.db"

    JWTManager(app)

    db_module.init_app(app)

    app.register_blueprint(auth_bp, url_prefix="/api")

    return app