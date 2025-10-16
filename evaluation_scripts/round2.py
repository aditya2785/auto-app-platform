import json
import uuid
import requests
import logging
from database.db_utils import fetchall, execute, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """
    Generates and sends round 2 tasks based on the results of the evaluation.
    """
    init_db()

    # Get all repos that have been evaluated in round 1
    repos = fetchall("SELECT * FROM repos WHERE round=1")

    for repo in repos:
        email = repo["email"]
        task_name = repo["task"]

        # Skip if round 2 task already exists
        if fetchall("SELECT * FROM tasks WHERE email=? AND task=? AND round=2", (email, task_name)):
            logger.info(f"Round 2 task for {email} and {task_name} already exists. Skipping.")
            continue

        # This is a placeholder for generating a more specific round 2 brief
        # based on the evaluation results.
        brief = f"Round 2: Improve the UI and add error handling for the {task_name} task."
        checks = [
            "UI has been improved with CSS.",
            "Error handling is implemented for user inputs.",
            "All previous functionality is still working."
        ]

        nonce = str(uuid.uuid4())
        task_info = fetchall("SELECT * FROM tasks WHERE task=? AND round=1", (task_name,))[0]


        payload = {
            "email": email,
            "secret": task_info["secret"],
            "task": task_name,
            "round": 2,
            "nonce": nonce,
            "brief": brief,
            "checks": checks,
            "evaluation_url": task_info["evaluation_url"],
            "attachments": [], # No new attachments for round 2 in this example
        }

        endpoint = "http://localhost:8000/api-endpoint"
        logger.info(f"Sending round 2 task {payload['task']} to {email} at {endpoint}")

        try:
            r = requests.post(endpoint, json=payload, timeout=30)
            status = r.status_code
            if status != 200:
                logger.error(f"Failed to send round 2 task to {email}: {r.text}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send round 2 task to {email}: {e}")
            status = 0

        execute(
            "INSERT INTO tasks (email, task, round, nonce, brief, attachments, checks, evaluation_url, endpoint, statuscode, secret) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (payload["email"], payload["task"], payload["round"], payload["nonce"], payload["brief"], json.dumps(payload["attachments"]), json.dumps(payload["checks"]), payload["evaluation_url"], endpoint, status, payload["secret"])
        )
        logger.info(f"Round 2 task for {email} logged to database with status {status}.")

if __name__ == "__main__":
    main()
