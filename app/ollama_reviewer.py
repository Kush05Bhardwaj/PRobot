import os
import requests
from dotenv import load_dotenv
from app.prompts import REVIEW_PROMPT

load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")

OLLAMA_URL = "http://localhost:11434/api/generate"


def review_code(diff):

    prompt = REVIEW_PROMPT.format(diff=diff)

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False
        }
    )

    result = response.json()

    return result["response"]