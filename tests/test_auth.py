from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api import accounts as accounts_api
from app.api import auth as auth_api
from app.api import deps as deps_api
from app.db.base import Base
from app.db.session import get_db
from app.main import app


@pytest.fixture
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[auth_api.get_db] = override_get_db
    app.dependency_overrides[accounts_api.get_db] = override_get_db
    app.dependency_overrides[deps_api.get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_registration_success(client):
    payload = {"name": "Alice Johnson", "email": "alice@example.com", "password": "strongpass123"}
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["user"]["email"] == "alice@example.com"
    assert data["account"]["account_number"]
    assert data["access_token"]
    assert data["token_type"] == "bearer"


def test_duplicate_email_rejected(client):
    payload = {"name": "Alice Johnson", "email": "alice@example.com", "password": "strongpass123"}
    client.post("/api/auth/register", json=payload)
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 409, response.text


def test_login_success(client):
    client.post(
        "/api/auth/register",
        json={"name": "Alice Johnson", "email": "alice@example.com", "password": "strongpass123"},
    )
    response = client.post(
        "/api/auth/login",
        json={"email": "alice@example.com", "password": "strongpass123"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["access_token"]
    assert data["token_type"] == "bearer"


def test_invalid_login(client):
    client.post(
        "/api/auth/register",
        json={"name": "Alice Johnson", "email": "alice@example.com", "password": "strongpass123"},
    )
    response = client.post(
        "/api/auth/login",
        json={"email": "alice@example.com", "password": "wrongpass"},
    )
    assert response.status_code == 401, response.text


def test_protected_route_requires_token(client):
    response = client.get("/api/accounts/me")
    assert response.status_code == 401, response.text


def test_invalid_token_rejected(client):
    response = client.get("/api/accounts/me", headers={"Authorization": "Bearer invalid.token.value"})
    assert response.status_code == 401, response.text


def test_logout_blacklists_token(client):
    register = client.post(
        "/api/auth/register",
        json={"name": "Alice Johnson", "email": "alice@example.com", "password": "strongpass123"},
    )
    token = register.json()["access_token"]

    logout = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert logout.status_code == 200, logout.text

    response = client.get("/api/accounts/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401, response.text
