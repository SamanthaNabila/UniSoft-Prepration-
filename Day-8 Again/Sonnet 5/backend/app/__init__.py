"""Application factory."""

from pathlib import Path

from flask import Flask

from config import get_config

from .errors import register_error_handlers
from .extensions import db
from .logging_config import configure_logging

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"


def create_app(config_name=None, **overrides):
    app = Flask(
        __name__,
        static_folder=str(FRONTEND_DIR),
        static_url_path="",
    )
    app.config.from_object(get_config(config_name))
    app.config.update(overrides)

    configure_logging(app)
    _ensure_sqlite_dir(app)

    db.init_app(app)

    from . import models  # noqa: F401  - register models with SQLAlchemy

    with app.app_context():
        db.create_all()

    from .routes import api

    app.register_blueprint(api, url_prefix="/api")
    register_error_handlers(app)

    @app.get("/")
    def index():
        return app.send_static_file("index.html")

    app.logger.info("Task Manager application initialised")
    return app


def _ensure_sqlite_dir(app):
    uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if uri.startswith("sqlite:///") and ":memory:" not in uri:
        db_path = Path(uri.replace("sqlite:///", "", 1))
        db_path.parent.mkdir(parents=True, exist_ok=True)
