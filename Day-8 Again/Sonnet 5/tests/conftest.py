"""Shared pytest fixtures.

Each test gets a fresh application backed by its own temporary SQLite file, so
tests are fully isolated and never touch the real dev database.
"""

import sys
from pathlib import Path

import pytest

BACKEND = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app import create_app  # noqa: E402
from app.extensions import db as _db  # noqa: E402


@pytest.fixture
def app(tmp_path):
    db_file = tmp_path / "test.db"
    application = create_app(
        "testing", SQLALCHEMY_DATABASE_URI=f"sqlite:///{db_file.as_posix()}"
    )
    yield application
    with application.app_context():
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def make_task(client):
    """Factory that creates a task via the API and returns its JSON."""

    def _make(**overrides):
        payload = {"title": "Sample task", "priority": "medium", "status": "pending"}
        payload.update(overrides)
        res = client.post("/api/tasks", json=payload)
        assert res.status_code == 201, res.get_json()
        return res.get_json()

    return _make
