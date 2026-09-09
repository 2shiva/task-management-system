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


def create_task(token, title="Pytest Task"):
    response = client.post(
        "/tasks/",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "title": title,
            "description": "Task created through pytest",
            "priority": "High",
        },
    )

    assert response.status_code == 201

    return response.json()


def test_create_task():
    token = login(
        "pytestuser@example.com",
        "TestPassword123",
    )

    task = create_task(token)

    assert task["title"] == "Pytest Task"
    assert task["description"] == "Task created through pytest"
    assert task["priority"] == "High"
    assert task["status"] == "Todo"
    assert task["created_by"] is not None


def test_get_tasks():
    token = login(
        "pytestuser@example.com",
        "TestPassword123",
    )

    response = client.get(
        "/tasks/",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


def test_update_task():
    token = login(
        "pytestuser@example.com",
        "TestPassword123",
    )

    task = create_task(token, "Task To Update")

    response = client.put(
        f"/tasks/{task['id']}",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "title": "Updated Pytest Task",
            "description": "Updated description",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "Updated Pytest Task"
    assert data["description"] == "Updated description"


def test_task_status_transition():
    token = login(
        "pytestuser@example.com",
        "TestPassword123",
    )

    task = create_task(token, "Status Test Task")

    response = client.put(
        f"/tasks/{task['id']}/status",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "status": "In Progress",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "In Progress"


def test_invalid_task_status_transition():
    token = login(
        "pytestuser@example.com",
        "TestPassword123",
    )

    task = create_task(token, "Invalid Status Test")

    response = client.put(
        f"/tasks/{task['id']}/status",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "status": "Completed",
        },
    )

    assert response.status_code == 400