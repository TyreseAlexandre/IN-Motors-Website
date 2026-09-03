"""Entry point for traditional WSGI hosts (gunicorn, Render, Railway, etc.).

    gunicorn wsgi:app
"""
from app import app

if __name__ == "__main__":
    app.run()
