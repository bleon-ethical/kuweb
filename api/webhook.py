from fastapi import FastAPI, Request
import httpx
import os

app = FastAPI()

@app.post("/api/webhook")
async def handle_webhook(request: Request):
    payload = await request.json()
    event_type = request.headers.get("X-GitHub-Event")

    if event_type == "pull_request":
        action = payload.get("action")
        # Trigger on new PRs or new code pushes
        if action in ["opened", "synchronize"]:
            repo_name = payload["repository"]["full_name"]
            installation_id = payload["installation"]["id"]
            
            # Logic: KuVuln reads your config
            # to verify if 'secrets' or 'kubernetes' scans are enabled
            return {"status": f"🤖 KuVuln is analyzing {repo_name}"}

    return {"status": "Event ignored"}
