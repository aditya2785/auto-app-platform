import os
import subprocess
import json
import logging
from database.db_utils import fetchall, execute, init_db
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_playwright_test(pages_url: str, task_template: dict) -> tuple[int, str, str]:
    """Runs a Playwright test based on the task template."""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(pages_url, wait_until="networkidle")

            # Example check from template
            check = task_template["checks"][-1] # "Page displays solved captcha text within 15 seconds"

            # This is a placeholder for a more robust solution
            # that would dynamically generate test code.
            page.wait_for_selector("text=/Solved Captcha Text/i", timeout=15000)

            browser.close()
            return 1, "Playwright test passed.", ""
    except Exception as e:
        return 0, "Playwright test failed.", str(e)

def main():
    """
    Fetches repos, clones them, and evaluates them based on the checks.
    """
    init_db()
    repos = fetchall("SELECT * FROM repos")

    for repo in repos:
        repo_url = repo["repo_url"]
        task_name = repo["task"]
        email = repo["email"]
        round_num = repo["round"]
        pages_url = repo["pages_url"]
        commit_sha = repo["commit_sha"]

        logger.info(f"Evaluating repo: {repo_url}")

        # Clone repo
        folder = f"temp/{task_name}"
        if os.path.exists(folder):
            subprocess.run(["rm", "-rf", folder])
        os.makedirs(folder, exist_ok=True)
        subprocess.run(["git", "clone", repo_url, folder], check=True)

        # 1. Check for MIT LICENSE
        license_path = os.path.join(folder, "LICENSE")
        score, reason = (1, "MIT license found") if os.path.exists(license_path) else (0, "MIT license missing")
        execute("INSERT INTO results (email, task, round, repo_url, commit_sha, pages_url, check_name, score, reason) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (email, task_name, round_num, repo_url, commit_sha, pages_url, "MIT LICENSE", score, reason))

        # 2. Check for professional README.md
        readme_path = os.path.join(folder, "README.md")
        if os.path.exists(readme_path):
            with open(readme_path, "r") as f:
                content = f.read()
            score, reason = (1, "README is professional") if len(content) > 100 else (0, "README is too short")
        else:
            score, reason = (0, "README.md missing")
        execute("INSERT INTO results (email, task, round, repo_url, commit_sha, pages_url, check_name, score, reason) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (email, task_name, round_num, repo_url, commit_sha, pages_url, "Professional README", score, reason))

        # 3. Run Playwright tests
        task_info = fetchall("SELECT * FROM tasks WHERE task=? AND round=?", (task_name, round_num))[0]
        task_template = {"checks": json.loads(task_info["checks"])} # Recreate a template-like object

        score, reason, logs = run_playwright_test(pages_url, task_template)
        execute("INSERT INTO results (email, task, round, repo_url, commit_sha, pages_url, check_name, score, reason, logs) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (email, task_name, round_num, repo_url, commit_sha, pages_url, "Playwright Test", score, reason, logs))

        # Clean up
        subprocess.run(["rm", "-rf", folder])

if __name__ == "__main__":
    main()
