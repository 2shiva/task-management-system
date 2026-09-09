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
            "title": "Comment Test Task",
            "description": "Task for testing comments",
            "priority": "Medium",
        },
    )

    assert response.status_code == 201

    return response.json()


def test_create_comment():
    token = login(
        "pytestuser@example.com",
        "TestPassword123",
    )

    task = create_task(token)

    response = client.post(
        f"/tasks/{task['id']}/comments",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "content": "This is a pytest comment",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["task_id"] == task["id"]
    assert data["content"] == "This is a pytest comment"


def test_get_comments():
    token = login(
        "pytestuser@example.com",
        "TestPassword123",
    )

    task = create_task(token)

    client.post(
        f"/tasks/{task['id']}/comments",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "content": "Comment for retrieval",
        },
    )

    response = client.get(
        f"/tasks/{task['id']}/comments",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 1


def test_update_comment():
    token = login(
        "pytestuser@example.com",
        "TestPassword123",
    )

    task = create_task(token)

    comment_response = client.post(
        f"/tasks/{task['id']}/comments",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "content": "Original comment",
        },
    )

    assert comment_response.status_code == 201

    comment = comment_response.json()

    response = client.put(
        f"/tasks/comments/{comment['id']}",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "content": "Updated comment",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["content"] == "Updated comment"


def test_delete_comment():
    token = login(
        "pytestuser@example.com",
        "TestPassword123",
    )

    task = create_task(token)

    comment_response = client.post(
        f"/tasks/{task['id']}/comments",
        headers={
            "Authorization": f"Bearer {token}",
        },
        json={
            "content": "Comment to delete",
        },
    )

    assert comment_response.status_code == 201

    comment = comment_response.json()

    response = client.delete(
        f"/tasks/comments/{comment['id']}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Comment deleted successfully"