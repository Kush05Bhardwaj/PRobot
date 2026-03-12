# PRobot — Local AI PR Reviewer

An automated pull request reviewer that runs entirely on your local machine. When a PR is opened on GitHub, PRobot fetches the diff, sends it to a local LLM via [Ollama](https://ollama.com), and posts the AI-generated review back as a PR comment.

---

## How It Works

```
GitHub PR opened
      │
      ▼
GitHub Webhook (HTTP POST)
      │
      ▼
ngrok (tunnels to localhost)
      │
      ▼
FastAPI server (/webhook)
      │
      ├── Fetch PR diff via GitHub API
      │
      ├── Send diff to Ollama (local LLM)
      │
      └── Post AI review as PR comment
```

---

## Tech Stack

| Component | Tool |
|---|---|
| Web server | FastAPI + Uvicorn |
| GitHub integration | PyGitHub |
| Local LLM | Ollama (`qwen2.5-coder:7b`) |
| Tunnel (dev) | ngrok |
| Config | python-dotenv |

---

## Project Structure

```
probot/
├── app/
│   ├── main.py              # FastAPI app & webhook handler
│   ├── github_handler.py    # Fetch PR diff, post PR comment
│   ├── ollama_reviewer.py   # Send diff to Ollama, return review
│   └── prompts.py           # LLM prompt template
├── .env                     # Secrets (not committed)
├── requirements.txt
└── README.md
```

---

## Setup

### 1. Clone & install dependencies

```bash
git clone https://github.com/Kush05Bhardwaj/PRobot.git
cd PRobot/probot
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 2. Configure environment variables

Create a `.env` file in the `probot/` directory:

```env
GITHUB_TOKEN=your_github_pat_here
WEBHOOK_SECRET=your_webhook_secret
OLLAMA_MODEL=qwen2.5-coder:7b
```

- **`GITHUB_TOKEN`** — A GitHub Personal Access Token with `repo` scope.
- **`WEBHOOK_SECRET`** — A secret string; set the same value in your GitHub webhook config.
- **`OLLAMA_MODEL`** — Any code-capable model pulled in Ollama.

### 3. Pull the Ollama model

```bash
ollama pull qwen2.5-coder:7b
```

### 4. Start the server

```bash
uvicorn app.main:app --reload --port 8000
```

### 5. Expose localhost with ngrok

```bash
ngrok http 8000
```

Copy the HTTPS URL (e.g. `https://xxxx.ngrok-free.app`).

### 6. Configure GitHub Webhook

In your GitHub repo → **Settings → Webhooks → Add webhook**:

| Field | Value |
|---|---|
| Payload URL | `https://xxxx.ngrok-free.app/webhook` |
| Content type | `application/json` |
| Secret | value from `WEBHOOK_SECRET` in `.env` |
| Events | `Pull requests` |

---

## Usage

Open a pull request in your GitHub repo. PRobot will automatically:

1. Receive the `pull_request` opened event
2. Fetch the changed files and diffs
3. Run the diff through the local LLM
4. Post a structured review comment on the PR

### Example review output

```
🤖 PRobot Review

📋 Summary:
Adds basic Express authentication middleware and a login endpoint.

🐛 Bugs:
- Hardcoded credentials ('admin'/'secret') should never be used in production.

⚡ Performance:
- No issues for this scope.

🔒 Security:
- Plaintext password comparison is a critical vulnerability; use bcrypt or similar.
- JWT token is hardcoded ('fake-jwt-token'); replace with a real signing library.

📝 PR Description Feedback:
Consider documenting the expected request/response schema for the login route.
```

---

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com) running locally
- ngrok (for local development tunneling)
