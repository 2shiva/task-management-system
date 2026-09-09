from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def login(email, password):
    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def test_normal_user_cannot_list_users():
    token = login(
        "pytestuser@example.com",
        "TestPassword123",
    )

    response = client.get(
        "/users/",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 403


def test_admin_can_list_users():
    token = login(
        "admin@example.com",
        "admin12345",
    )

    response = client.get(
        "/users/",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_admin_can_create_user():
    token = login(
        "admin@example.com",
        "admin12345",
    )

    email = f"admin_test_{uuid4().hex}@example.com"

    response = client.post(
        "/users/",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "name": "Admin Created User",
            "email": email,
            "password": "TestPassword123",
            "role": "user",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Admin Created User"
    assert data["email"] == email
    assert data["role"] == "user"
    assert data["is_active"] is True