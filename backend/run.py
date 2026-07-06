# run.py
# The entry point for starting the Flask development server.
# This is the file you actually execute: python3 run.py

from app import create_app

# Build the app using our factory function from app/__init__.py
app = create_app()

# Only run the server if this file is executed directly
# (not if it's imported by something else, like a test file).
if __name__ == "__main__":
    app.run(debug=True, port=5001)