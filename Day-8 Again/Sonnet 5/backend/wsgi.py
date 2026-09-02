"""Entry point for running the Task Manager.

    python backend/wsgi.py

or with a WSGI server:

    gunicorn --chdir backend wsgi:app
"""

import os

from app import create_app

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="127.0.0.1", port=port, debug=app.config.get("DEBUG", False))
