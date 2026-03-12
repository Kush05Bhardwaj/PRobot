from fastapi import FastAPI, Request
from app.github_handler import get_pr_diff, post_pr_comment
from app.ollama_reviewer import review_code

app = FastAPI()


@app.post("/webhook")
async def github_webhook(request: Request):

    payload = await request.json()

    if payload["action"] != "opened":
        return {"message": "Ignored"}

    repo_name = payload["repository"]["full_name"]
    pr_number = payload["pull_request"]["number"]

    diff = get_pr_diff(repo_name, pr_number)

    review = review_code(diff)

    post_pr_comment(repo_name, pr_number, review)

    return {"message": "Review generated"}