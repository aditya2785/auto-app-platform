import json, hashlib, uuid, requests
from database.db_utils import fetchall, execute

tasks = fetchall("SELECT * FROM repos WHERE round=1")  # Round 2 tasks based on round1

with open("task_templates/sum-of-sales.json") as f:
    template = json.load(f)

for task_row in tasks:
    email = task_row["email"]
    secret = "student_shared_secret"
    endpoint = "http://student-api:8000/api-endpoint"

    # Skip if round2 already done
    rows = fetchall("SELECT * FROM tasks WHERE email=? AND round=2", (email,))
    if rows:
        continue

    task_hash = hashlib.md5((template["brief"] + email).encode()).hexdigest()[:5]
    task_id = f"{template['id']}-{task_hash}"
    nonce = str(uuid.uuid4())

    # Choose round2 brief
    round2_task = template["round2"][0]

    payload = {
        "email": email,
        "secret": secret,
        "task": task_id,
        "round": 2,
        "nonce": nonce,
        "brief": round2_task["brief"],
        "checks": round2_task["checks"],
        "attachments": template.get("attachments", []),
        "evaluation_url": "http://localhost:8001/evaluation-url"
    }

    try:
        r = requests.post(endpoint, json=payload)
        status = r.status_code
    except:
        status = 0

    # Log in tasks
    execute("""
        INSERT INTO tasks(email, task, round, nonce, brief, attachments, checks, evaluation_url, endpoint, statuscode, secret)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (email, task_id, 2, nonce, payload["brief"], json.dumps(payload["attachments"]),
          json.dumps(payload["checks"]), payload["evaluation_url"], endpoint, status, secret))
