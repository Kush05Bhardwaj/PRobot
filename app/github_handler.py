import os
import logging
from github import Github
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

g = Github(GITHUB_TOKEN)


def get_pr_diff(repo_name, pr_number):
    """
    Fetch all changed files and their patches from a PR
    """
    try:
        repo = g.get_repo(repo_name)
        pr = repo.get_pull(pr_number)

        files = pr.get_files()

        diff_text = ""

        for file in files:

            diff_text += f"\nFile: {file.filename}\n"

            if file.patch:
                diff_text += file.patch

        if len(diff_text) > 12000:
            logger.warning(f"Diff size exceeds 12,000 characters for PR #{pr_number}, truncating...")
            diff_text = diff_text[:12000] + "\n\n...[DIFF TRUNCATED TO 12,000 CHARACTERS DUE TO CONTEXT LIMIT]..."

        logger.info(f"Fetched diff for PR #{pr_number}, size: {len(diff_text)} bytes")
        return diff_text
    except Exception as e:
        logger.error(f"Error fetching PR diff for {repo_name}#{pr_number}: {e}")
        raise

def post_pr_comment(repo_name, pr_number, review_text):
    try:
        repo = g.get_repo(repo_name)
        pr = repo.get_pull(pr_number)

        pr.create_issue_comment(review_text)
        logger.info(f"Successfully posted review comment to PR #{pr_number}")
    except Exception as e:
        logger.error(f"Error posting PR comment for {repo_name}#{pr_number}: {e}")
        raise