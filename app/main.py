from fastapi import FastAPI, Request
import json

app = FastAPI()

@app.get("/")
def home():
    return {"status": "PRobot running"}

@app.post("/webhook")
async def github_webhook(request: Request):
    payload = await request.json()

    print("Received webhook:")
    print(json.dumps(payload, indent=2))

    return {"message": "Webhook received"}