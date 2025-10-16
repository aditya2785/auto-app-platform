import os
import json
from unittest.mock import patch
from fastapi.testclient import TestClient
from student_api.app import app
from database.db_utils import init_db
from dotenv import load_dotenv

load_dotenv()

client = TestClient(app)

API_SECRET = os.getenv("API_SECRET")

def test_invalid_secret():
    """
    Tests that the API returns a 403 error when an invalid secret is provided.
    """
    response = client.post(
        "/api-endpoint",
        json={
            "email": "test@example.com",
            "secret": "invalid_secret",
            "task": "test-task",
            "round": 1,
            "nonce": "test-nonce",
            "brief": "Test brief",
            "checks": [],
            "evaluation_url": "http://example.com/evaluate",
            "attachments": [],
        },
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Invalid secret"}

@patch("student_api.app.generate_app")
@patch("student_api.app.create_and_push_to_repo")
def test_valid_request(mock_create_and_push_to_repo, mock_generate_app):
    """
    Tests that the API returns a 200 OK status when a valid request is sent.
    """
    init_db()
    mock_generate_app.return_value = {
        "index.html": "<html></html>",
        "README.md": "README",
        "LICENSE": "LICENSE",
    }
    mock_create_and_push_to_repo.return_value = (
        "https://github.com/user/repo",
        "commit_sha",
        "https://user.github.io/repo/",
    )

    response = client.post(
        "/api-endpoint",
        json={
            "email": "test@example.com",
            "secret": API_SECRET,
            "task": "test-task",
            "round": 1,
            "nonce": "test-nonce",
            "brief": "Test brief",
            "checks": [],
            "evaluation_url": "http://example.com/evaluate",
            "attachments": [],
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json["status"] == "success"
    assert response_json["repo_url"] == "https://github.com/user/repo"
    assert response_json["pages_url"] == "https://user.github.io/repo/"