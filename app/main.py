from fastapi import FastAPI, Request, HTTPException
from app.github_handler import get_pr_diff, post_pr_comment
from app.ollama_reviewer import review_code
import hmac, hashlib
import logging
import sqlite3
import json
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")

app = FastAPI()

DB_FILE = "seen_prs.db"

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS seen (pr_id TEXT PRIMARY KEY)")

init_db()

@app.post("/webhook")

def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    expected = "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

async def github_webhook(request: Request):
    raw_body = await request.body()
    signature = request.headers.get("X-Hub-Signature-256", "")
    
    if not verify_signature(raw_body, signature, WEBHOOK_SECRET):
        raise HTTPException(status_code=403, detail="Invalid webhook signature")
    
    payload = json.loads(raw_body)

    if payload.get("action") != "opened":
        return {"message": "Ignored"}

    repo_name = payload["repository"]["full_name"]
    pr_number = payload["pull_request"]["number"]
    
    pr_id = f"{repo_name}#{pr_number}"
    
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.execute("SELECT 1 FROM seen WHERE pr_id = ?", (pr_id,))
        already_seen = cursor.fetchone() is not None
        
    if already_seen:
        logger.info(f"Skipping already processed PR {pr_id}")
        return {"message": "Already processed"}
        
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("INSERT OR IGNORE INTO seen VALUES (?)", (pr_id,))
    
    logger.info(f"Received PR opened event for {repo_name}#{pr_number}")

    try:
        diff = get_pr_diff(repo_name, pr_number)
        
        if not diff:
            logger.warning(f"No diff found for {repo_name}#{pr_number}")
            return {"message": "No diff found"}

        review = review_code(diff)
        
        post_pr_comment(repo_name, pr_number, review)

        return {"message": "Review posted"}
    except Exception as e:
        logger.error(f"Failed to process PR {repo_name}#{pr_number}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")