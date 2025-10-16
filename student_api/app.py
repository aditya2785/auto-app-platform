import os
import json
import requests
from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv
from pydantic import BaseModel
import logging

from student_api.generator import generate_app
from student_api.github_helper import create_and_push_to_repo
from database.db_utils import execute

load_dotenv()

API_SECRET = os.getenv("API_SECRET")

app = FastAPI()

# Configure logging to write to a file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='student_api.log',
    filemode='w'
)
logger = logging.getLogger(__name__)

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

@app.post("/api-endpoint")
async def api_endpoint(request: Request):
    try:
        data = await request.json()
        task_request = TaskRequest(**data)

        if task_request.secret != API_SECRET:
            logger.error("Invalid secret")
            raise HTTPException(status_code=403, detail="Invalid secret")

        logger.info(f"Received task: {task_request.task} for email: {task_request.email}")

        execute(
            "INSERT INTO tasks (email, task, round, nonce, brief, attachments, checks, evaluation_url, endpoint, statuscode, secret) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (task_request.email, task_request.task, task_request.round, task_request.nonce, task_request.brief, json.dumps(task_request.attachments), json.dumps(task_request.checks), task_request.evaluation_url, str(request.url), 200, task_request.secret)
        )
        logger.info("Task logged to database")


        # Generate app code
        logger.info("Generating app code...")
        app_code = generate_app(task_request.brief, task_request.attachments)
        logger.info("App code generated")

        # Create repo and push code
        logger.info("Creating and pushing to repo...")
        repo_url, commit_sha, pages_url = create_and_push_to_repo(
            task_request.email, task_request.task, app_code, task_request.round
        )
        logger.info("Repo created and code pushed")

        # Notify evaluation service
        evaluation_payload = {
            "email": task_request.email,
            "task": task_request.task,
            "round": task_request.round,
            "nonce": task_request.nonce,
            "repo_url": repo_url,
            "commit_sha": commit_sha,
            "pages_url": pages_url,
        }
        try:
            logger.info("Notifying evaluation service...")
            requests.post(task_request.evaluation_url, json=evaluation_payload)
            logger.info(f"Successfully notified evaluation service for task: {task_request.task}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to notify evaluation service for task: {task_request.task}: {e}")

        return {"status": "success", "message": "Task received and is being processed."}
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == "__main__":
    import uvicorn
    import sys
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        print(f"Error running uvicorn: {e}", file=sys.stderr)