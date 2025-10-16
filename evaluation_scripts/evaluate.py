import os, requests, subprocess, json
from database.db_utils import fetchall, execute

repos = fetchall("SELECT * FROM repos WHERE round=1")  # Check round=1 repos

for repo in repos:
    repo_url = repo["repo_url"]
    commit_sha = repo["commit_sha"]
    pages_url = repo["pages_url"]
    email = repo["email"]
    task = repo["task"]

    # Clone repo
    folder = f"temp/{task}"
    os.makedirs(folder, exist_ok=True)
    subprocess.run(["git", "clone", repo_url, folder])

    # Check MIT LICENSE
    license_path = os.path.join(folder, "LICENSE")
    score, reason = (1, "MIT license found") if os.path.exists(license_path) else (0, "MIT license missing")

    # Store results
    execute("""
        INSERT INTO results(email, task, round, repo_url, commit_sha, pages_url, check_name, score, reason)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (email, task, 1, repo_url, commit_sha, pages_url, "MIT LICENSE", score, reason))
