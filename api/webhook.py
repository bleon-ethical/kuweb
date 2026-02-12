import os
import time
import jwt
import httpx
from fastapi import FastAPI, Request, HTTPException

app = FastAPI()

# Configuración desde Vercel Environment Variables
APP_ID = os.getenv("GITHUB_APP_ID")
PRIVATE_KEY = os.getenv("GITHUB_PRIVATE_KEY")

def generate_jwt():
    """Crea un token JWT para que GitHub sepa que somos KuVuln Bot"""
    actual_time = int(time.time())
    payload = {
        "iat": actual_time - 60,
        "exp": actual_time + (10 * 60),
        "iss": APP_ID,
    }
    # Formateamos la llave si viene como una sola línea con \n
    key = PRIVATE_KEY.replace('\\n', '\n')
    return jwt.encode(payload, key, algorithm="RS256")

async def get_installation_token(installation_id):
    """Obtiene un token temporal para interactuar con el repo"""
    token_jwt = generate_jwt()
    headers = {
        "Authorization": f"Bearer {token_jwt}",
        "Accept": "application/vnd.github.v3+json",
    }
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers)
        return response.json().get("token")

@app.post("/api/webhook")
async def webhook(request: Request):
    payload = await request.json()
    event = request.headers.get("X-GitHub-Event")

    # Si alguien abre un Pull Request...
    if event == "pull_request" and payload.get("action") == "opened":
        installation_id = payload["installation"]["id"]
        repo_name = payload["repository"]["full_name"]
        pr_number = payload["pull_request"]["number"]
        
        # Conseguir permiso para hablar en el PR
        token = await get_installation_token(installation_id)
        
        # Publicar comentario de bienvenida
        comment_url = f"https://api.github.com/repos/{repo_name}/issues/{pr_number}/comments"
        comment_body = {
            "body": "🤖 **KuVuln Security Bot is active!**\n\nI am currently analyzing your Kubernetes manifests and secrets. Check the 'Checks' tab for details."
        }
        
        async with httpx.AsyncClient() as client:
            await client.post(
                comment_url, 
                json=comment_body, 
                headers={"Authorization": f"token {token}"}
            )

    return {"status": "ok"}
