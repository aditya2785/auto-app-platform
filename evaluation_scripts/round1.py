import csv, json, uuid, hashlib, requests, random
from database.db_utils import execute, fetchall

# Load submissions.csv
with open("submissions.csv") as f:
    reader = csv.DictReader(f)
    submissions = list(reader)

# Load task templates
with open("task_templates/sum-of-sales.json") as f:
    template = json.load(f)

for sub in submissions:
    email = sub["email"]
    secret = sub["secret"]
    endpoint = sub["endpoint"]

    # Skip if already processed
    rows = fetchall("SELECT * FROM tasks WHERE email=? AND round=1", (email,))
    if rows:
        continue

    # Generate unique task id
    task_hash = hashlib.md5((template["brief"] + email).encode()).hexdigest()[:5]
    task_id = f"{template['id']}-{task_hash}"
    nonce = str(uuid.uuid4())

    # Prepare payload
    payload = {
        "email": email,
        "secret": secret,
        "task": task_id,
        "round": 1,
        "nonce": nonce,
        "brief": template["brief"],
        "checks": template["checks"],
        "attachments": template["attachments"],
        "evaluation_url": "http://localhost:8001/evaluation-url"  # Instructor API
    }

    # POST to student API
    try:
        r = requests.post(endpoint, json=payload, timeout=600)
        status = r.status_code
    except Exception as e:
        status = 0

    # Log in tasks table
    execute("""
        INSERT INTO tasks(email, task, round, nonce, brief, attachments, checks, evaluation_url, endpoint, statuscode, secret)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (email, task_id, 1, nonce, template["brief"], json.dumps(template["attachments"]),
          json.dumps(template["checks"]), payload["evaluation_url"], endpoint, status, secret))
