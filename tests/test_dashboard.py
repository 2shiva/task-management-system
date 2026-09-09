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


def test_admin_dashboard():
    token = login(
        "admin@example.com",
        "admin12345",
    )

    response = client.get(
        "/dashboard/admin",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "users" in data
    assert "tasks" in data


def test_user_dashboard():
    token = login(
        "pytestuser@example.com",
        "TestPassword123",
    )

    response = client.get(
        "/dashboard/user",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "user" in data
    assert "tasks" in data