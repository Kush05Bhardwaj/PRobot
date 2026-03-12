import os
from github import Github
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

g = Github(GITHUB_TOKEN)


def get_pr_diff(repo_name, pr_number):
    """
    Fetch all changed files and their patches from a PR
    """

    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)

    files = pr.get_files()

    diff_data = []

    for file in files:
        diff_data.append({
            "filename": file.filename,
            "patch": file.patch
        })

    return diff_data