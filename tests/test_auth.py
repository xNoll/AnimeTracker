"""
Tests for authentication endpoints.
Run with:  pytest tests/ -v
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

# ── Test database setup (isolated SQLite in memory) ───────────────────────────
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_db():
    """Create fresh tables before each test, drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def registered_user(client):
    """Helper fixture: a user that's already registered."""
    client.post("/auth/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "securepass123",
    })
    return {"username": "testuser", "password": "securepass123"}



# ── Tests ─────────────────────────────────────────────────────────────────────
def test_register_success(client):
    response = client.post("/auth/register", json={
        "username": "alejandro",
        "email": "alex@example.com",
        "password": "DummyPassword05193",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "alejandro"
    assert "hashed_password" not in data  # never expose this


def test_register_duplicate_username(client, registered_user):
    response = client.post("/auth/register", json={
        "username": "testuser",
        "email": "other@example.com",
        "password": "AnotherPass123",
    })
    assert response.status_code == 409
    assert "Username already taken" in response.json()["detail"]


def test_register_invalid_password_too_short(client):
    response = client.post("/auth/register", json={
        "username": "validuser",
        "email": "valid@example.com",
        "password": "short",  # less than 8 chars
    })
    assert response.status_code == 422  # Pydantic validation error


def test_login_success(client, registered_user):
    response = client.post("/auth/login", json=registered_user)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, registered_user):
    response = client.post("/auth/login", json={
        "username": "testuser",
        "password": "wrongpassword",
    })
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    response = client.post("/auth/login", json={
        "username": "nobody",
        "password": "doesntmatter",
    })
    assert response.status_code == 401


def test_protected_route_without_token(client):
    response = client.get("/list/")
    assert response.status_code == 401


def test_protected_route_with_token(client, registered_user):
    login = client.post("/auth/login", json=registered_user)
    token = login.json()["access_token"]

    response = client.get("/list/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == []  # empty list for new user
