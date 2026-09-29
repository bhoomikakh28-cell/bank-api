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


def get_auth_headers(client, email="alice@example.com", password="strongpass123"):
    response = client.post(
        "/api/auth/register",
        json={"name": "Alice Johnson", "email": email, "password": password},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_get_own_account(client):
    headers = get_auth_headers(client)
    response = client.get("/api/accounts/me", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["account_number"]
    assert data["balance"] == "0.00"


def test_deposit_and_withdraw(client):
    headers = get_auth_headers(client)
    deposit = client.post("/api/accounts/deposit", json={"amount": "50.00"}, headers=headers)
    assert deposit.status_code == 200, deposit.text
    assert deposit.json()["balance"] == "50.00"

    withdraw = client.post("/api/accounts/withdraw", json={"amount": "10.00"}, headers=headers)
    assert withdraw.status_code == 200, withdraw.text
    assert withdraw.json()["balance"] == "40.00"


def test_insufficient_balance_rejected(client):
    headers = get_auth_headers(client)
    response = client.post("/api/accounts/withdraw", json={"amount": "100.00"}, headers=headers)
    assert response.status_code == 400, response.text


def test_invalid_amount_rejected(client):
    headers = get_auth_headers(client)
    response = client.post("/api/accounts/deposit", json={"amount": "0.00"}, headers=headers)
    assert response.status_code == 422, response.text


def test_transfer_works_and_updates_balances(client):
    alice_headers = get_auth_headers(client, "alice@example.com", "strongpass123")
    bob_headers = get_auth_headers(client, "bob@example.com", "strongpass123")

    alice_before = client.get("/api/accounts/me", headers=alice_headers).json()
    assert alice_before["balance"] == "0.00"

    client.post("/api/accounts/deposit", json={"amount": "100.00"}, headers=alice_headers)
    invalid_transfer = client.post(
        "/api/accounts/transfer",
        json={"destination_account_number": "", "amount": "25.00"},
        headers=alice_headers,
    )
    assert invalid_transfer.status_code == 422, invalid_transfer.text

    missing_transfer = client.post(
        "/api/accounts/transfer",
        json={"destination_account_number": "ACC-NOT-EXIST", "amount": "25.00"},
        headers=alice_headers,
    )
    assert missing_transfer.status_code == 404, missing_transfer.text

    bob_account = client.get("/api/accounts/me", headers=bob_headers).json()
    transfer = client.post(
        "/api/accounts/transfer",
        json={"destination_account_number": bob_account["account_number"], "amount": "25.00"},
        headers=alice_headers,
    )
    assert transfer.status_code == 200, transfer.text
    data = transfer.json()
    assert data["source_account"]["balance"] == "75.00"
    assert data["destination_account"]["balance"] == "25.00"
    assert len(data["transactions"]) == 2
    assert data["transactions"][0]["reference_id"] == data["transactions"][1]["reference_id"]


def test_same_account_transfer_rejected(client):
    headers = get_auth_headers(client)
    account = client.get("/api/accounts/me", headers=headers).json()
    response = client.post(
        "/api/accounts/transfer",
        json={"destination_account_number": account["account_number"], "amount": "10.00"},
        headers=headers,
    )
    assert response.status_code == 400, response.text


def test_transaction_history_is_private(client):
    alice_headers = get_auth_headers(client, "alice@example.com", "strongpass123")
    bob_headers = get_auth_headers(client, "bob@example.com", "strongpass123")

    client.post("/api/accounts/deposit", json={"amount": "80.00"}, headers=alice_headers)
    response = client.get("/api/accounts/transactions", headers=alice_headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert len(data) >= 1

    response = client.get("/api/accounts/transactions", headers=bob_headers)
    assert response.status_code == 200, response.text
    assert response.json() == []


def test_users_cannot_access_other_account_data(client):
    alice_headers = get_auth_headers(client, "alice@example.com", "strongpass123")
    bob_headers = get_auth_headers(client, "bob@example.com", "strongpass123")

    alice_account = client.get("/api/accounts/me", headers=alice_headers).json()
    bob_account = client.get("/api/accounts/me", headers=bob_headers).json()
    assert alice_account["account_number"] != bob_account["account_number"]
