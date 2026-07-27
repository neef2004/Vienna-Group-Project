from flask import Flask
from flask_jwt_extended import JWTManager
from app.routes.auth import auth_bp
from app.routes.trips import trips_bp
from app.routes.itineraries import itineraries_bp
from app.routes.reminders import reminders_bp
from app.routes.collaborators import collaborators_bp
from app import db as db_module

# create and configure the Flask app
# JWT auth, database, and /api routes
def create_app(test_config=None):
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = "change-this-to-a-real-secret"
    app.config["DATABASE"] = "app.db"
    if test_config is not None:
        app.config.update(test_config)
    JWTManager(app)
    db_module.init_app(app)

    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(trips_bp)
    app.register_blueprint(itineraries_bp)
    app.register_blueprint(reminders_bp)
    app.register_blueprint(collaborators_bp)

    return app