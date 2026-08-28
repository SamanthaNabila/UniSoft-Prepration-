from app.core.whitelist import MOCK_EMPLOYEE_WHITELIST

EMPLOYEE = next(e for e in MOCK_EMPLOYEE_WHITELIST if e["role"] == "employee")
AGENT = next(e for e in MOCK_EMPLOYEE_WHITELIST if e["role"] == "support_agent")

VALID_PASSWORD = "Passw0rd!"


def _register_payload(entry: dict, **overrides) -> dict:
    payload = {
        "name": entry["name"],
        "email": entry["email"],
        "password": VALID_PASSWORD,
        "role": entry["role"],
    }
    payload.update(overrides)
    return payload


def test_register_success_with_valid_whitelisted_employee(client):
    response = client.post("/api/v1/auth/register", json=_register_payload(EMPLOYEE))

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == EMPLOYEE["email"].lower()
    assert body["role"] == "employee"
    assert "password" not in body
    assert "password_hash" not in body


def test_register_success_with_valid_whitelisted_agent(client):
    response = client.post("/api/v1/auth/register", json=_register_payload(AGENT))

    assert response.status_code == 201
    assert response.json()["role"] == "support_agent"


def test_register_is_case_insensitive_and_trims_whitespace(client):
    payload = _register_payload(
        EMPLOYEE,
        name=f"  {EMPLOYEE['name'].upper()}  ",
        email=EMPLOYEE["email"].upper(),
    )

    response = client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 201


def test_register_rejects_name_not_in_whitelist(client):
    payload = _register_payload(EMPLOYEE, name="Eve Hacker")

    response = client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "Registration denied: Name or email not found in company records."
    )


def test_register_rejects_email_not_in_whitelist(client):
    payload = _register_payload(EMPLOYEE, email="not.on.list@unidesk.com")

    response = client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "Registration denied: Name or email not found in company records."
    )


def test_register_rejects_role_mismatched_with_whitelist(client):
    payload = _register_payload(EMPLOYEE, role="support_agent")

    response = client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 400


def test_register_rejects_duplicate_email(client):
    first = client.post("/api/v1/auth/register", json=_register_payload(EMPLOYEE))
    assert first.status_code == 201

    second = client.post("/api/v1/auth/register", json=_register_payload(EMPLOYEE))

    assert second.status_code == 409


def test_register_rejects_weak_password(client):
    payload = _register_payload(EMPLOYEE, password="weak")

    response = client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 422


def test_login_success_returns_jwt(client):
    client.post("/api/v1/auth/register", json=_register_payload(EMPLOYEE))

    response = client.post(
        "/api/v1/auth/login",
        json={"email": EMPLOYEE["email"], "password": VALID_PASSWORD},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert len(body["access_token"]) > 0


def test_login_rejects_invalid_password(client):
    client.post("/api/v1/auth/register", json=_register_payload(EMPLOYEE))

    response = client.post(
        "/api/v1/auth/login",
        json={"email": EMPLOYEE["email"], "password": "WrongPass1"},
    )

    assert response.status_code == 401


def test_login_rejects_unknown_email(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "ghost@unidesk.com", "password": VALID_PASSWORD},
    )

    assert response.status_code == 401


def test_get_me_returns_current_user_with_valid_token(client):
    client.post("/api/v1/auth/register", json=_register_payload(EMPLOYEE))
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": EMPLOYEE["email"], "password": VALID_PASSWORD},
    )
    token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == EMPLOYEE["email"].lower()
    assert body["role"] == "employee"


def test_get_me_rejects_missing_token(client):
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401


def test_get_me_rejects_invalid_token(client):
    response = client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer not-a-real-token"}
    )

    assert response.status_code == 401
