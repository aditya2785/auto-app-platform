import csv
import json
import uuid
import requests
import logging
from database.db_utils import execute, fetchall, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """
    Reads submissions from submissions.csv, generates tasks,
    and POSTs them to the student API endpoints.
    """
    init_db()

    with open("submissions.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row["email"]
            endpoint = "http://localhost:8000/api-endpoint" # Assuming the student API is running locally

            # Skip if already processed
            if fetchall("SELECT * FROM tasks WHERE email=? AND round=1", (email,)):
                logger.info(f"Task for {email} already exists. Skipping.")
                continue

            nonce = str(uuid.uuid4())
            payload = {
                "email": email,
                "secret": row["secret"],
                "task": row["task"],
                "round": int(row["round"]),
                "nonce": nonce,
                "brief": row["brief"],
                "checks": row["checks"].split(','),
                "evaluation_url": row["evaluation_url"],
                "attachments": json.loads(row["attachments"]),
            }

            logger.info(f"Sending task {payload['task']} to {email} at {endpoint}")

            try:
                r = requests.post(endpoint, json=payload, timeout=30)
                status = r.status_code
                if status != 200:
                    logger.error(f"Failed to send task to {email}: {r.text}")
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to send task to {email}: {e}")
                status = 0

            execute(
                "INSERT INTO tasks (email, task, round, nonce, brief, attachments, checks, evaluation_url, endpoint, statuscode, secret) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (payload["email"], payload["task"], payload["round"], payload["nonce"], payload["brief"], json.dumps(payload["attachments"]), json.dumps(payload["checks"]), payload["evaluation_url"], endpoint, status, payload["secret"])
            )
            logger.info(f"Task for {email} logged to database with status {status}.")

if __name__ == "__main__":
    main()
