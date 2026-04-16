import os
import logging
import requests
from dotenv import load_dotenv
from app.prompts import REVIEW_PROMPT

load_dotenv()

logger = logging.getLogger(__name__)

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")
OLLAMA_URL = "http://localhost:11434/api/generate"


def review_code(diff):
    prompt = REVIEW_PROMPT.format(diff=diff)

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )
        response.raise_for_status()
        
        result = response.json()
        review_text = result["response"]
        
        logger.info(f"Received review from Ollama, length: {len(review_text)} characters")
        return review_text
    except Exception as e:
        logger.error(f"Error communicating with Ollama: {e}")
        raise