from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["message"] == "Task Management System API is running"


def test_register_user():
    email = f"pytest_{uuid4().hex}@example.com"

    response = client.post(
        "/auth/register",
        json={
            "name": "Pytest New User",
            "email": email,
            "password": "TestPassword123",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Pytest New User"
    assert data["email"] == email
    assert data["role"] == "user"
    assert data["is_active"] is True


def test_login_user():
    response = client.post(
        "/auth/login",
        json={
            "email": "pytestuser@example.com",
            "password": "TestPassword123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"