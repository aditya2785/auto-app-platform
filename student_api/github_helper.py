import subprocess
import os

GITHUB_USER = "your_username"
GITHUB_TOKEN = "ghp_xxx"

def create_repo(app_path, task):
    repo_name = task
    subprocess.run(["gh", "repo", "create", repo_name, "--public", "--confirm"], check=True)
    return f"https://github.com/{GITHUB_USER}/{repo_name}.git", "initial_commit_sha", f"https://{GITHUB_USER}.github.io/{repo_name}/"

def push_to_github(app_path, repo_url):
    os.chdir(app_path)
    subprocess.run(["git", "init"])
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", "Initial commit"])
    subprocess.run(["git", "branch", "-M", "main"])
    subprocess.run(["git", "remote", "add", "origin", repo_url])
    subprocess.run(["git", "push", "-u", "origin", "main"])

def enable_pages(repo_url):
    # Enable GitHub Pages via CLI
    subprocess.run(["gh", "pages", "enable"], check=True)
