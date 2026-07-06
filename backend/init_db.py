# init_db.py
# A one-time setup script that creates app.db and builds the users
# table inside it, using the SQL defined in app/schema.sql.
#
# Run this ONCE manually:
#     python3 init_db.py
#
# Do NOT run this again after you have real signups you care about —
# schema.sql starts with "DROP TABLE IF EXISTS users", which means
# re-running this will WIPE all existing user data.

from app import create_app
from app.db import init_db

# Build a Flask app instance using our factory function.
app = create_app()

# init_db() needs access to current_app (used inside db.py to find
# schema.sql), which only works inside an "app context." Using
# `with app.app_context():` temporarily activates that context just
# long enough to run init_db(), then cleans it up automatically.
with app.app_context():
    init_db()
    print("Database initialized.")