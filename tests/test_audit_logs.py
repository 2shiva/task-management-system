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


def test_admin_can_get_audit_logs():
    token = login(
        "admin@example.com",
        "admin12345",
    )

    response = client.get(
        "/audit-logs/",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_normal_user_cannot_get_audit_logs():
    token = login(
        "pytestuser@example.com",
        "TestPassword123",
    )

    response = client.get(
        "/audit-logs/",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 403