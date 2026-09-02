"""Application configuration.

Configuration is selected by name ("development", "testing", "production") or via
the FLASK_ENV environment variable. Individual values can also be overridden with
environment variables so the app stays easy to run in different setups.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
LOG_DIR = PROJECT_ROOT / "logs"

_DEFAULT_SQLITE_URI = f"sqlite:///{(DATA_DIR / 'tasks.db').as_posix()}"


class BaseConfig:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False

    # Validation limits (kept in config so they are easy to tune / test).
    MAX_TITLE_LENGTH = 200
    MAX_DESCRIPTION_LENGTH = 2000

    LOG_DIR = str(LOG_DIR)
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", _DEFAULT_SQLITE_URI)


class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = True
    # conftest overrides this with a per-test temp file.
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    LOG_LEVEL = "CRITICAL"


class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", _DEFAULT_SQLITE_URI)


CONFIG_MAP = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(name=None):
    """Return a config class by name, falling back to development."""
    name = name or os.environ.get("FLASK_ENV", "development")
    return CONFIG_MAP.get(name, DevelopmentConfig)
