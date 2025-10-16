import os
from github import Github, GithubException
from dotenv import load_dotenv
import logging

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
# A mock for the Github object when no token is provided
if GITHUB_TOKEN == "your_github_token":
    g = None
else:
    g = Github(GITHUB_TOKEN)

logger = logging.getLogger(__name__)

def create_and_push_to_repo(email: str, task_name: str, files: dict[str, str], round_num: int) -> tuple[str, str, str]:
    """
    Creates a GitHub repository, pushes files to it, and enables GitHub Pages.
    If the repo exists, it updates the files.
    """
    repo_name = f"{task_name}-{email.split('@')[0]}"

    # Mock functionality if no token is provided
    if g is None:
        logger.warning("No GITHUB_TOKEN found, mocking GitHub API calls.")
        user_login = "mockuser"
        repo_url = f"https://github.com/{user_login}/{repo_name}"
        commit_sha = "mock_commit_sha"
        pages_url = f"https://{user_login}.github.io/{repo_name}/"

        # Create a dummy directory to simulate the repo
        dummy_repo_path = f"temp/{repo_name}"
        os.makedirs(dummy_repo_path, exist_ok=True)
        for path, content in files.items():
            with open(os.path.join(dummy_repo_path, path), "w") as f:
                f.write(content)

        return repo_url, commit_sha, pages_url

    try:
        user = g.get_user()
        repo = user.get_repo(repo_name)
        logger.info(f"Repo {repo_name} already exists. Updating files.")
    except GithubException:
        logger.info(f"Creating repo {repo_name}.")
        repo = user.create_repo(repo_name, private=False)

    commit_message = f"Round {round_num} submission"

    try:
        main_ref = repo.get_git_ref('heads/main')
        latest_commit_sha = main_ref.object.sha
        tree = repo.get_git_tree(latest_commit_sha, recursive=True)
        file_shas = {item.path: item.sha for item in tree.tree}
    except GithubException:
        latest_commit_sha = None
        file_shas = {}

    for path, content in files.items():
        if path in file_shas:
            repo.update_file(path, commit_message, content, file_shas[path], branch="main")
        else:
            repo.create_file(path, commit_message, content, branch="main")

    try:
        source = {"branch": "main", "path": "/"}
        repo.enable_pages(source=source)
    except GithubException as e:
        logger.error(f"Failed to enable GitHub Pages for {repo_name}: {e}")

    main_ref = repo.get_git_ref('heads/main')
    commit_sha = main_ref.object.sha
    pages_url = f"https://{user.login}.github.io/{repo_name}/"

    return repo.html_url, commit_sha, pages_url
