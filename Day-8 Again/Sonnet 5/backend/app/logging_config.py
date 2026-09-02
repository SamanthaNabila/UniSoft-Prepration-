"""Logging setup.

Logs go to stdout always, and to a rotating file (``logs/app.log``) outside of
tests. Only operational data (task ids, actions, statuses) is logged - never full
task content.
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


def configure_logging(app):
    level = getattr(
        logging, str(app.config.get("LOG_LEVEL", "INFO")).upper(), logging.INFO
    )
    formatter = logging.Formatter(_FORMAT)

    app.logger.handlers.clear()

    stream = logging.StreamHandler()
    stream.setFormatter(formatter)
    app.logger.addHandler(stream)

    if not app.config.get("TESTING"):
        log_dir = Path(app.config["LOG_DIR"])
        log_dir.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            log_dir / "app.log", maxBytes=1_000_000, backupCount=3, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)

    app.logger.setLevel(level)
    app.logger.propagate = False
