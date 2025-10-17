import os
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from student_api.app import app
from database.db_utils import init_db, DB_PATH
from dotenv import load_dotenv

load_dotenv()

client = TestClient(app)

API_SECRET = os.getenv("API_SECRET")

@patch("student_api.app.requests.Session.post")
@patch("student_api.app.create_and_push_to_repo")
@patch("student_api.app.generate_app")
def test_end_to_end_flow(mock_generate_app, mock_create_and_push, mock_post):
    """
    Tests the full end-to-end flow of the API using TestClient and mocks.
    """
    # Clean up database before test
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db()

    # 1. Setup mocks
    mock_generate_app.return_value = {
        "index.html": "<html></html>",
        "README.md": "README",
        "LICENSE": "LICENSE",
    }
    mock_create_and_push.return_value = (
        "https://github.com/user/repo",
        "mock_commit_sha",
        "https://user.github.io/repo/",
    )
    # Mock the response from the evaluation service
    mock_post.return_value = MagicMock(status_code=200)

    # 2. Send request to the API
    response = client.post(
        "/api-endpoint",
        json={
            "email": "test@example.com",
            "secret": API_SECRET,
            "task": "test-task-e2e",
            "round": 1,
            "nonce": "test-nonce-e2e",
            "brief": "Test brief for e2e test.",
            "checks": [],
            "evaluation_url": "http://example.com/evaluate",
            "attachments": [],
        },
    )

    # 3. Assertions
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["status"] == "success"
    assert response_json["repo_url"] == "https://github.com/user/repo"
    assert response_json["pages_url"] == "https://user.github.io/repo/"

    # Check if mocks were called
    mock_generate_app.assert_called_once()
    mock_create_and_push.assert_called_once()
    mock_post.assert_called_once()

    # Clean up database after test
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)