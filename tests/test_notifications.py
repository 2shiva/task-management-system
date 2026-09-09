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


def test_get_notifications():
    token = login(
        "pytestuser@example.com",
        "TestPassword123",
    )

    response = client.get(
        "/notifications/",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_mark_notification_as_read():
    token = login(
        "pytestuser@example.com",
        "TestPassword123",
    )

    notifications_response = client.get(
        "/notifications/",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert notifications_response.status_code == 200

    notifications = notifications_response.json()

    if not notifications:
        return

    notification_id = notifications[0]["id"]

    response = client.put(
        f"/notifications/{notification_id}/read",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200
    assert response.json()["is_read"] is True


def test_mark_all_notifications_as_read():
    token = login(
        "pytestuser@example.com",
        "TestPassword123",
    )

    response = client.put(
        "/notifications/read-all",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200
    assert "message" in response.json()