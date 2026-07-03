# __init__.py
# This file defines the "application factory" — a function that builds
# and configures a brand-new Flask app instance every time it's called.
#
# Why a factory function instead of just creating `app = Flask(__name__)`
# at the top level? It avoids issues with circular imports, and makes it
# easy to create multiple app instances later (e.g. one for testing with
# a different database, one for production) without duplicating setup code.

from flask import Flask
from flask_jwt_extended import JWTManager

# Import the blueprint containing our /login and /signup routes.
from app.routes.auth import auth_bp

# Import our db.py file as db_module (renamed to avoid any naming
# collisions with other things called "db" elsewhere in the app).
from app import db as db_module


def create_app():
    """
    Builds, configures, and returns a fully ready Flask app.
    Called once by run.py to start the server, and can also be called
    by test files to spin up a fresh app instance for testing.
    """

    # Create the core Flask application object.
    # __name__ tells Flask the import name of this module, which it uses
    # internally to locate resources like templates/static files relative
    # to this file. Not heavily used in a pure JSON API, but it's the
    # standard, expected pattern.
    app = Flask(__name__)

    # --- Configuration ---
    # JWT_SECRET_KEY is used to cryptographically SIGN every access token
    # this app issues. Anyone who has this key could forge valid tokens
    # and impersonate any user, so in a real deployment this MUST come
    # from an environment variable (e.g. os.environ.get("JWT_SECRET_KEY"))
    # and never be committed to source control. It's hardcoded here only
    # as a placeholder to get things running locally.
    app.config["JWT_SECRET_KEY"] = "change-this-to-a-real-secret"

    # Just stores the database filename in Flask's config dictionary.
    # db.py can read this if it wants to, instead of hardcoding the
    # filename in two different places.
    app.config["DATABASE"] = "app.db"

    # --- Extensions ---
    # JWTManager "attaches" all the JWT functionality (token creation,
    # verification, the @jwt_required() decorator, etc.) to this specific
    # app instance. Without this line, calling create_access_token() in
    # auth.py would raise a runtime error, since nothing would have
    # configured JWT for this app yet.
    JWTManager(app)

    # init_app() (defined in db.py) registers a "teardown" function with
    # Flask, telling it to automatically close the database connection
    # after every request finishes — whether that request succeeded or
    # raised an error. This prevents leaking open database connections.
    db_module.init_app(app)

    # --- Blueprints ---
    # Registering the blueprint actually "turns on" the routes defined
    # inside auth.py. url_prefix="/api" means every route inside auth_bp
    # gets prefixed with /api — so /login becomes /api/login, and
    # /signup becomes /api/signup.
    app.register_blueprint(auth_bp, url_prefix="/api")

    # Hand back the fully configured app object. run.py will use this
    # to actually start the server.
    return app