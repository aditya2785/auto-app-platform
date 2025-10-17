import os
import time
from github import Github, Auth, GithubException
from dotenv import load_dotenv
import logging

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
# A mock for the Github object when no token is provided
if GITHUB_TOKEN == "your_github_token":
    g = None
else:
    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)

logger = logging.getLogger(__name__)

def create_and_push_to_repo(email: str, task_name: str, files: dict[str, str], round_num: int) -> tuple[str, str, str]:
    """
    Creates a GitHub repository, pushes files to it, and enables GitHub Pages.
    If the repo already exists, it updates the files in the existing repository, making this function suitable for both Round 1 and Round 2.
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

        logger.info(f"Mocked GitHub pages URL: {pages_url}")
        return repo_url, commit_sha, pages_url

    try:
        user = g.get_user()
        repo = user.get_repo(repo_name)
        logger.info(f"Repo {repo_name} already exists. Updating files.")
    except GithubException:
        logger.info(f"Creating repo {repo_name}.")
        repo = user.create_repo(repo_name, private=False)

    commit_message = f"Round {round_num} submission"
    logger.info(f"Using commit message: {commit_message}")

    try:
        main_ref = repo.get_git_ref('heads/main')
        latest_commit_sha = main_ref.object.sha
        tree = repo.get_git_tree(latest_commit_sha, recursive=True)
        file_shas = {item.path: item.sha for item in tree.tree}
        logger.info(f"Found existing files in repo {repo_name}: {list(file_shas.keys())}")
    except GithubException:
        latest_commit_sha = None
        file_shas = {}
        logger.info(f"No existing files found in repo {repo_name}")

    if not files:
        logger.error(f"No files generated for task {task_name}. Aborting.")
        return None, None, None

    for path, content in files.items():
        try:
            if path in file_shas:
                logger.info(f"Updating file {path} in repo {repo_name}")
                repo.update_file(path, commit_message, content, file_shas[path], branch="main")
            else:
                logger.info(f"Creating file {path} in repo {repo_name}")
                repo.create_file(path, commit_message, content, branch="main")
        except GithubException as e:
            logger.error(f"Failed to commit file {path} to repo {repo_name}: {e}")
            # Continue to the next file
            pass

    for i in range(3):
        try:
            source = {"branch": "main", "path": "/"}
            repo.enable_pages(source=source)
            logger.info(f"Successfully enabled GitHub Pages for {repo_name}")
            break
        except GithubException as e:
            logger.error(f"Failed to enable GitHub Pages for {repo_name} (attempt {i+1}/3): {e}")
            time.sleep(2)

    main_ref = repo.get_git_ref('heads/main')
    commit_sha = main_ref.object.sha
    pages_url = f"https://{user.login}.github.io/{repo_name}/"

    return repo.html_url, commit_sha, pages_url
