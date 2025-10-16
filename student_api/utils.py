import base64
import os

def verify_secret(secret, shared_secret):
    return secret == shared_secret

def parse_request(data):
    task_info = {
        "task": data["task"],
        "brief": data["brief"],
        "attachments": data.get("attachments", []),
        "checks": data.get("checks", [])
    }

    # Save attachments locally
    for attach in task_info["attachments"]:
        name = attach["name"]
        b64 = attach["url"].split(",")[1]
        with open(os.path.join("student_apps", name), "wb") as f:
            f.write(base64.b64decode(b64))
    
    return task_info
