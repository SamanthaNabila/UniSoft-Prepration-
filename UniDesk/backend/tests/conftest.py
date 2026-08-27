import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401 - ensures all models are registered on Base.metadata
from app.core.whitelist import MOCK_EMPLOYEE_WHITELIST
from app.database import Base, get_db
from app.main import app

VALID_PASSWORD = "Passw0rd!"
EMPLOYEES = [e for e in MOCK_EMPLOYEE_WHITELIST if e["role"] == "employee"]
AGENTS = [e for e in MOCK_EMPLOYEE_WHITELIST if e["role"] == "support_agent"]

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db


@pytest.fixture(autouse=True)
def _reset_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def register_and_login(client: TestClient, entry: dict) -> dict:
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
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def employee_a(client):
    return register_and_login(client, EMPLOYEES[0])


@pytest.fixture
def employee_b(client):
    return register_and_login(client, EMPLOYEES[1])


@pytest.fixture
def agent_a(client):
    return register_and_login(client, AGENTS[0])


@pytest.fixture
def agent_b(client):
    return register_and_login(client, AGENTS[1])
