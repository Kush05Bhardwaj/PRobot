from fastapi import FastAPI, Request, HTTPException
from app.github_handler import get_pr_diff, post_pr_comment
from app.ollama_reviewer import review_code
import hmac, hashlib
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

seen_pr_ids = set()

@app.post("/webhook")

def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    expected = "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

async def github_webhook(request: Request):

    payload = await request.json()

    if payload.get("action") != "opened":
        return {"message": "Ignored"}

    repo_name = payload["repository"]["full_name"]
    pr_number = payload["pull_request"]["number"]
    
    pr_id = f"{repo_name}#{pr_number}"
    if pr_id in seen_pr_ids:
        logger.info(f"Skipping already processed PR {pr_id}")
        return {"message": "Already processed"}
        
    seen_pr_ids.add(pr_id)
    
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