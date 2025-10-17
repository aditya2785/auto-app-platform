import os
import json
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv
from pydantic import BaseModel
import logging

from student_api.generator import generate_app
from student_api.github_helper import create_and_push_to_repo
from student_api.utils import process_attachments
from database.db_utils import execute, main as init_db

load_dotenv()

API_SECRET = os.getenv("API_SECRET")
if not API_SECRET:
    raise ValueError("API_SECRET not found in .env file")

app = FastAPI()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TaskRequest(BaseModel):
    email: str
    secret: str
    task: str
    round: int
    nonce: str
    brief: str
    checks: list[str]
    evaluation_url: str
    attachments: list[dict]

def notify_evaluation_service(url: str, payload: dict):
    """Notifies the evaluation service with a given payload."""
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        backoff_factor=1
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)
    http.mount("http://", adapter)
    try:
        response = http.post(url, json=payload, timeout=30)
        response.raise_for_status()
        logging.info(f"Successfully notified evaluation service for task: {payload.get('task')}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to notify evaluation service for task: {payload.get('task')}: {e}")

@app.on_event("startup")
async def startup_event():
    """Initializes the database on startup."""
    init_db()

@app.get("/")
def read_root():
    """A welcome message for the API."""
    return {"message": "Welcome to the Student API"}

@app.post("/api-endpoint")
async def api_endpoint(request: Request):
    """The main endpoint for processing tasks."""
    try:
        data = await request.json()
        task_request = TaskRequest(**data)

        if task_request.secret != API_SECRET:
            raise HTTPException(status_code=403, detail="Invalid secret")

        logging.info(f"Received task: {task_request.task} for email: {task_request.email}")

        processed_data = process_attachments(task_request.attachments)
        app_code = generate_app(task_request.brief, processed_data)

        if "error" in app_code:
            raise HTTPException(status_code=500, detail=app_code["error"])

        repo_url, commit_sha, pages_url = create_and_push_to_repo(
            task_request.email, task_request.task, app_code, task_request.round
        )

        evaluation_payload = {
            "email": task_request.email,
            "task": task_request.task,
            "round": task_request.round,
            "nonce": task_request.nonce,
            "repo_url": repo_url,
            "commit_sha": commit_sha,
            "pages_url": pages_url,
        }
        notify_evaluation_service(task_request.evaluation_url, evaluation_payload)

        execute(
            "INSERT INTO tasks (email, task, round, nonce, brief, attachments, checks, evaluation_url, endpoint, statuscode, secret, repo_url, commit_sha, pages_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (task_request.email, task_request.task, task_request.round, task_request.nonce, task_request.brief, json.dumps(task_request.attachments), json.dumps(task_request.checks), task_request.evaluation_url, str(request.url), 200, task_request.secret, repo_url, commit_sha, pages_url)
        )

        return {
            "status": "success",
            "repo_url": repo_url,
            "pages_url": pages_url,
            "commit_sha": commit_sha
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")