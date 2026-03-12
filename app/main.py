from fastapi import FastAPI, Request
import json
from app.github_handler import get_pr_diff

app = FastAPI()

@app.get("/")
def home():
    return {"status": "PRobot running"}

@app.post("/webhook")
async def github_webhook(request: Request):

    payload = await request.json()

    # Only trigger on PR opened
    if payload.get("action") != "opened" or "pull_request" not in payload:
        return {"message": "Ignored event"}

    repo_name = payload["repository"]["full_name"]
    pr_number = payload["pull_request"]["number"]

    diff = get_pr_diff(repo_name, pr_number)

    print("PR Diff:")
    print(diff)

    return {"message": "PR processed"}