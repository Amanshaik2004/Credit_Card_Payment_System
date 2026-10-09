import os
import tempfile
from decimal import Decimal
from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient
import jwt
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from fastapi_payment.database import Base, get_db
from fastapi_payment.main import app, SECRET_KEY, ALGORITHM
from fastapi_payment.models import User, Card, Transaction, AuditLog

# Create a temporary SQLite database for testing
tmp_db_file = tempfile.NamedTemporaryFile(suffix="_test.sqlite3", delete=False)
TEST_DATABASE_URL = f"sqlite:///{tmp_db_file.name}"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Create schema
Base.metadata.create_all(bind=test_engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_and_seed_database():
    db = TestingSessionLocal()

    # Clear old data
    db.query(AuditLog).delete()
    db.query(Transaction).delete()
    db.query(Card).delete()
    db.query(User).delete()
    db.commit()

    # Create test user
    user = User(
        id=1,
        username="fastapi_user",
        email="fastapi_user@example.com",
        password="hashed_dummy_password",
        is_active=True
    )
    db.add(user)
    db.commit()

    # Create active valid card
    card = Card(
        id=10,
        user_id=1,
        card_holder_name="FastAPI Test Card",
        card_type="CREDIT",
        card_brand="Visa",
        masked_card_number="**** **** **** 4242",
        last_4_digits="4242",
        expiry_month=12,
        expiry_year=2030,
        is_active=True
    )
    # Create expired card
    expired_card = Card(
        id=11,
        user_id=1,
        card_holder_name="Expired Card",
        card_type="DEBIT",
        card_brand="MasterCard",
        masked_card_number="**** **** **** 5555",
        last_4_digits="5555",
        expiry_month=1,
        expiry_year=2020,
        is_active=True
    )
    db.add(card)
    db.add(expired_card)
    db.commit()
    db.close()

    yield


def create_test_token(user_id=1):
    payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc).timestamp() + 3600
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Payment Processing Engine"
    assert data["status"] == "online"


def test_payment_unauthorized_without_token():
    payload = {
        "card_id": 10,
        "amount": 100.00,
        "currency": "USD",
        "cvv": "123",
        "description": "Test"
    }
    response = client.post("/api/payments/pay", json=payload)
    assert response.status_code in (401, 403)


def test_payment_success():
    token = create_test_token(user_id=1)
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "card_id": 10,
        "amount": 150.50,
        "currency": "USD",
        "cvv": "123",
        "description": "Dinner Payment"
    }
    response = client.post("/api/payments/pay", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert float(data["amount"]) == 150.50
    assert data["failure_reason"] is None
    assert "TXN-" in data["transaction_id"]

    # Verify transaction in DB and no CVV stored
    db = TestingSessionLocal()
    txn = db.query(Transaction).filter(Transaction.transaction_id == data["transaction_id"]).first()
    assert txn is not None
    assert txn.status == "SUCCESS"
    assert not hasattr(txn, "cvv")

    # Verify audit log
    audit = db.query(AuditLog).filter(AuditLog.action == "PAYMENT_SUCCESS").first()
    assert audit is not None
    assert str(txn.user_id) in audit.details or "SUCCEEDED" in audit.details
    db.close()


def test_payment_failed_cvv_simulation():
    # CVV '000' triggers simulated bank decline
    token = create_test_token(user_id=1)
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "card_id": 10,
        "amount": 75.00,
        "currency": "USD",
        "cvv": "000",
        "description": "Failed payment simulation"
    }
    response = client.post("/api/payments/pay", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "FAILED"
    assert "CVV" in data["failure_reason"] or "Declined" in data["failure_reason"]

    # Verify audit log recorded failure
    db = TestingSessionLocal()
    audit = db.query(AuditLog).filter(AuditLog.action == "PAYMENT_FAILED").first()
    assert audit is not None
    db.close()


def test_payment_failed_expired_card():
    token = create_test_token(user_id=1)
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "card_id": 11,  # Expired card
        "amount": 50.00,
        "currency": "USD",
        "cvv": "321",
        "description": "Payment on expired card"
    }
    response = client.post("/api/payments/pay", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "FAILED"
    assert "expired" in data["failure_reason"].lower()


def test_payment_failed_amount_limit():
    token = create_test_token(user_id=1)
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "card_id": 10,
        "amount": 99999.00,  # Exceeds limit
        "currency": "USD",
        "cvv": "123",
        "description": "Limit test"
    }
    response = client.post("/api/payments/pay", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "FAILED"
    assert "limit" in data["failure_reason"].lower()


def test_payment_invalid_card_id():
    token = create_test_token(user_id=1)
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "card_id": 9999,  # Does not exist
        "amount": 25.00,
        "currency": "USD",
        "cvv": "123",
        "description": "Invalid card"
    }
    response = client.post("/api/payments/pay", json=payload, headers=headers)
    assert response.status_code == 400


def test_get_payment_status():
    token = create_test_token(user_id=1)
    headers = {"Authorization": f"Bearer {token}"}

    # Make payment first
    pay_resp = client.post("/api/payments/pay", json={
        "card_id": 10,
        "amount": 40.00,
        "currency": "USD",
        "cvv": "123",
        "description": "Status query test"
    }, headers=headers)
    txn_id = pay_resp.json()["transaction_id"]

    # Check status
    status_resp = client.get(f"/api/payments/status/{txn_id}", headers=headers)
    assert status_resp.status_code == 200
    assert status_resp.json()["transaction_id"] == txn_id
    assert status_resp.json()["status"] == "SUCCESS"
