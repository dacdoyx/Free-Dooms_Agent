import secrets, time, os, httpx
from fastapi import FastAPI, HTTPException, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn
from typing import List, Optional

VALID_KEYS = {}

GH_TOKEN = os.environ.get("GH_MODELS_TOKEN", "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")
GH_MODEL = "Meta-Llama-3.1-405B-Instruct"
GH_BASE = "https://models.inference.ai.azure.com"
AVAILABLE_MODELS = ["Meta-Llama-3.1-405B-Instruct", "gpt-4o", "Meta-Llama-3.1-8B-Instruct", "gpt-4o-mini"]

app = FastAPI(title="free-dooms_ddkdkdketc")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/index.html")

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: Optional[str] = "free-dooms"
    messages: List[Message]
    max_tokens: Optional[int] = 1024
    temperature: Optional[float] = 0.7

class KeyGenerateRequest(BaseModel):
    name: Optional[str] = "default"

def gen_key():
    return f"free-dooms_{secrets.token_hex(16)}"

def check_auth(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(401, {"error": "missing api key. get one at /v1/api-keys/generate"})
    key = authorization.replace("Bearer ", "")
    if not key.startswith("free-dooms_"):
        raise HTTPException(401, {"error": "invalid api key"})
    if key not in VALID_KEYS:
        raise HTTPException(401, {"error": "unknown api key. generate one at /v1/api-keys/generate"})
    return key

# ─── GitHub Models backend (free GPT-4o) ──────────────────

async def gh_chat(model, messages, max_tokens, temperature):
    m = model if model in AVAILABLE_MODELS else GH_MODEL
    body = {
        "model": m,
        "messages": [msg.model_dump() for msg in messages],
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.post(f"{GH_BASE}/chat/completions", json=body,
            headers={"Authorization": f"Bearer {GH_TOKEN}", "Content-Type": "application/json"})
    if r.status_code != 200:
        return None
    data = r.json()
    return data["choices"][0]["message"]["content"]

BACKENDS = [gh_chat]

# ─── Endpoints ─────────────────────────────────────────────

@app.get("/v1/api-keys")
async def list_keys():
    return {"object": "list", "data": [{"id": k, "created": v["created"], "name": v["name"]} for k, v in VALID_KEYS.items()]}

@app.post("/v1/api-keys/generate")
async def generate_key(req: Optional[KeyGenerateRequest] = None):
    name = req.name if req else "default"
    key = gen_key()
    VALID_KEYS[key] = {"created": int(time.time()), "name": name}
    return {"id": key, "name": name, "created": VALID_KEYS[key]["created"], "message": "free forever. zero cost."}

@app.delete("/v1/api-keys/{key}")
async def delete_key(key: str):
    VALID_KEYS.pop(key, None)
    return {"deleted": key}

@app.get("/v1/models")
async def list_models():
    return {"object": "list", "data": [{"id": m, "object": "model", "owned_by": "github/freedooms"} for m in AVAILABLE_MODELS]}

@app.post("/v1/chat/completions")
async def chat_completions(req: ChatRequest, authorization: Optional[str] = Header(None)):
    check_auth(authorization)
    for backend in BACKENDS:
        text = await backend(req.model, req.messages, req.max_tokens, req.temperature)
        if text:
            return {
                "id": f"chatcmpl-{secrets.token_hex(6)}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": req.model or "free-dooms",
                "choices": [{"index": 0, "message": {"role": "assistant", "content": text.strip()}, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            }
    raise HTTPException(503, {"error": "backend unavailable."})

if __name__ == "__main__":
    print("╔══════════════════════════════════════════════╗")
    print("║      free-dooms_ddkdkdketc API v1           ║")
    print("╠══════════════════════════════════════════════╣")
    print(f"║  ✓ GitHub Models backend (free GPT-4o)     ║")
    print("╚══════════════════════════════════════════════╝")
    uvicorn.run(app, host="0.0.0.0", port=7860)
