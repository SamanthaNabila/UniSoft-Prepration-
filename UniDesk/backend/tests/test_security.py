import os
import subprocess
import sys
from datetime import timedelta
from pathlib import Path

from jose import jwt

from app.core.config import settings
from app.core.security import create_access_token
from app.core.whitelist import MOCK_EMPLOYEE_WHITELIST
from app.models import User
from tests.conftest import TestingSessionLocal

BACKEND_DIR = Path(__file__).resolve().parents[1]
EMPLOYEE = next(e for e in MOCK_EMPLOYEE_WHITELIST if e["role"] == "employee")
AGENT = next(e for e in MOCK_EMPLOYEE_WHITELIST if e["role"] == "support_agent")
VALID_PASSWORD = "Passw0rd!"


def _register_and_login(client, entry: dict) -> tuple[dict, int]:
    client.post(
        "/api/v1/auth/register",
        json={
            "name": entry["name"],
            "email": entry["email"],
            "password": VALID_PASSWORD,
            "role": entry["role"],
        },
    )
    response = client.post(
        "/api/v1/auth/login",
        json={"email": entry["email"], "password": VALID_PASSWORD},
    )
    token = response.json()["access_token"]
    user_id = jwt.get_unverified_claims(token)["sub"]
    return {"Authorization": f"Bearer {token}"}, int(user_id)


def _assert_rejected(client, token: str):
    response = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


def test_rejects_malformed_token(client):
    _assert_rejected(client, "this-is-not-a-jwt")


def test_rejects_token_with_missing_subject(client):
    token = create_access_token(data={"role": "employee"})
    _assert_rejected(client, token)


def test_rejects_token_with_non_integer_subject(client):
    token = create_access_token(data={"sub": "not-an-integer", "role": "employee"})
    _assert_rejected(client, token)


def test_rejects_token_with_negative_subject(client):
    token = create_access_token(data={"sub": "-1", "role": "employee"})
    _assert_rejected(client, token)


def test_rejects_expired_token(client):
    token = create_access_token(
        data={"sub": "1", "role": "employee"}, expires_delta=timedelta(seconds=-1)
    )
    _assert_rejected(client, token)


def test_rejects_token_signed_with_invalid_secret(client):
    token = jwt.encode(
        {"sub": "1", "role": "employee"}, "a-completely-different-secret",
        algorithm=settings.ALGORITHM,
    )
    _assert_rejected(client, token)


def test_rejects_token_for_nonexistent_user(client):
    token = create_access_token(data={"sub": "99999", "role": "employee"})
    _assert_rejected(client, token)


def test_rejects_missing_token(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_database_role_is_authoritative_over_stale_token_claim(client):
    headers, user_id = _register_and_login(client, EMPLOYEE)

    db = TestingSessionLocal()
    try:
        user = db.get(User, user_id)
        user.role = "support_agent"
        db.commit()
    finally:
        db.close()

    # The token still carries the old "employee" claim, but /auth/me and any
    # role check must reflect the current database role.
    me_response = client.get("/api/v1/auth/me", headers=headers)
    assert me_response.status_code == 200
    assert me_response.json()["role"] == "support_agent"

    ticket = client.post(
        "/api/v1/tickets",
        json={
            "title": "Printer is jammed",
            "description": "The printer on floor 3 is jammed.",
            "priority": "low",
        },
        headers=headers,
    )
    assert ticket.status_code == 403


def test_stale_token_cannot_use_now_revoked_agent_powers(client):
    headers, user_id = _register_and_login(client, AGENT)

    db = TestingSessionLocal()
    try:
        user = db.get(User, user_id)
        user.role = "employee"
        db.commit()
    finally:
        db.close()

    response = client.patch(
        "/api/v1/tickets/1/status",
        json={"status": "in_progress"},
        headers=headers,
    )
    assert response.status_code == 403
    assert (
        response.json()["detail"]
        == "Access denied: Only Support Agents can update ticket status or priority."
    )


def _run_config_import(env_overrides: dict) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env.update(env_overrides)
    return subprocess.run(
        [sys.executable, "-c", "import app.core.config"],
        cwd=str(BACKEND_DIR),
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )


def test_startup_fails_when_secret_key_missing():
    result = _run_config_import({"SECRET_KEY": ""})
    assert result.returncode != 0
    assert "SECRET_KEY" in result.stderr


def test_startup_fails_when_secret_key_is_placeholder():
    result = _run_config_import({"SECRET_KEY": "dev-secret-key-change-me"})
    assert result.returncode != 0
    assert "SECRET_KEY" in result.stderr


def test_startup_fails_when_secret_key_too_short():
    result = _run_config_import({"SECRET_KEY": "short-secret"})
    assert result.returncode != 0
    assert "SECRET_KEY" in result.stderr


def test_startup_fails_when_secret_key_is_unfilled_template_placeholder():
    result = _run_config_import(
        {"SECRET_KEY": "<generate-a-random-secret-with-at-least-32-characters>"}
    )
    assert result.returncode != 0
    assert "SECRET_KEY" in result.stderr


def test_startup_succeeds_with_valid_secret_key():
    result = _run_config_import({"SECRET_KEY": "x" * 32})
    assert result.returncode == 0
