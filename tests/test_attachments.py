from io import BytesIO

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


def create_task(token):
    response = client.post(
        "/tasks/",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "title": "Attachment Test Task",
            "description": "Task for testing attachments",
            "priority": "Medium",
        },
    )

    assert response.status_code == 201

    return response.json()


def test_upload_attachment():
    token = login(
        "pytestuser@example.com",
        "TestPassword123",
    )

    task = create_task(token)

    response = client.post(
        f"/tasks/{task['id']}/attachments",
        headers={
            "Authorization": f"Bearer {token}",
        },
        files={
            "file": (
                "test.txt",
                BytesIO(b"pytest attachment content"),
                "text/plain",
            )
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["task_id"] == task["id"]
    assert data["filename"] == "test.txt"


def test_get_attachments():
    token = login(
        "pytestuser@example.com",
        "TestPassword123",
    )

    task = create_task(token)

    upload_response = client.post(
        f"/tasks/{task['id']}/attachments",
        headers={
            "Authorization": f"Bearer {token}",
        },
        files={
            "file": (
                "list_test.txt",
                BytesIO(b"attachment for list test"),
                "text/plain",
            )
        },
    )

    assert upload_response.status_code == 201

    response = client.get(
        f"/tasks/{task['id']}/attachments",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 1


def test_delete_attachment():
    token = login(
        "pytestuser@example.com",
        "TestPassword123",
    )

    task = create_task(token)

    upload_response = client.post(
        f"/tasks/{task['id']}/attachments",
        headers={
            "Authorization": f"Bearer {token}",
        },
        files={
            "file": (
                "delete_test.txt",
                BytesIO(b"attachment to delete"),
                "text/plain",
            )
        },
    )

    assert upload_response.status_code == 201

    attachment = upload_response.json()

    response = client.delete(
    f"/tasks/attachments/{attachment['id']}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Attachment deleted successfully"


def test_invalid_attachment_type():
    token = login(
        "pytestuser@example.com",
        "TestPassword123",
    )

    task = create_task(token)

    response = client.post(
        f"/tasks/{task['id']}/attachments",
        headers={
            "Authorization": f"Bearer {token}",
        },
        files={
            "file": (
                "malware.exe",
                BytesIO(b"invalid file type"),
                "application/octet-stream",
            )
        },
    )

    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]


def test_large_attachment():
    token = login(
        "pytestuser@example.com",
        "TestPassword123",
    )

    task = create_task(token)

    large_file = b"x" * (11 * 1024 * 1024)

    response = client.post(
        f"/tasks/{task['id']}/attachments",
        headers={
            "Authorization": f"Bearer {token}",
        },
        files={
            "file": (
                "large_test.txt",
                BytesIO(large_file),
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert "10 MB" in response.json()["detail"]