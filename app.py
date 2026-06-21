import secrets, time, os, httpx
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import uvicorn
from typing import List, Optional

VALID_KEYS = {}
BACKENDS = []

GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6KJpCXQmxKeomCw52w8PIqCY664EjWkZqUElEfoB7Epvg")
GH_MODELS_TOKEN = os.environ.get("GH_MODELS_TOKEN", "")

app = FastAPI(title="free-dooms_ddkdkdketc")

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

# ─── Backend routers ───────────────────────────────────────────

async def gemini_chat(messages, max_tokens, temperature):
    """Free Google Gemini API. Get key: https://aistudio.google.com/apikey"""
    if not GEMINI_KEY:
        return None
    model = "gemini-2.5-flash"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_KEY}"
    contents = []
    sys_inst = None
    for m in messages:
        if m.role == "system":
            sys_inst = m.content
        else:
            contents.append({"role": m.role, "parts": [{"text": m.content}]})
    body = {"contents": contents, "generationConfig": {"maxOutputTokens": max_tokens, "temperature": temperature}}
    if sys_inst:
        body["systemInstruction"] = {"parts": [{"text": sys_inst}]}
    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.post(url, json=body)
    if r.status_code != 200:
        return None
    data = r.json()
    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        return text
    except (KeyError, IndexError):
        return None

async def gh_models_chat(messages, max_tokens, temperature):
    """Free GitHub Models. Get token: https://github.com/settings/tokens (no scopes needed)"""
    if not GH_MODELS_TOKEN:
        return None
    url = "https://models.inference.ai.azure.com/chat/completions"
    body = {
        "model": "gpt-4o-free",
        "messages": [m.model_dump() for m in messages],
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    async with httpx.AsyncClient(timeout=60) as c:
        r = await c.post(url, json=body, headers={"Authorization": f"Bearer {GH_MODELS_TOKEN}"})
    if r.status_code != 200:
        return None
    data = r.json()
    return data["choices"][0]["message"]["content"]

BACKENDS = [gemini_chat, gh_models_chat]

# ─── Endpoints ──────────────────────────────────────────────────

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
    models = [{"id": "free-dooms", "object": "model", "owned_by": "freedooms"}]
    if GEMINI_KEY:
        models.append({"id": "gemini-2.5-flash", "object": "model", "owned_by": "google"})
    if GH_MODELS_TOKEN:
        models.append({"id": "gpt-4o-free", "object": "model", "owned_by": "github"})
    return {"object": "list", "data": models}

@app.post("/v1/chat/completions")
async def chat_completions(req: ChatRequest, authorization: Optional[str] = Header(None)):
    check_auth(authorization)

    for backend in BACKENDS:
        text = await backend(req.messages, req.max_tokens, req.temperature)
        if text:
            return {
                "id": f"chatcmpl-{secrets.token_hex(6)}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": req.model or "free-dooms",
                "choices": [{"index": 0, "message": {"role": "assistant", "content": text.strip()}, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            }
    raise HTTPException(503, {"error": "all backends exhausted."})

if __name__ == "__main__":
    print("╔══════════════════════════════════════════════╗")
    print("║      free-dooms_ddkdkdketc API v1           ║")
    print("╠══════════════════════════════════════════════╣")
    if GEMINI_KEY:
        print("║  ✓ Gemini backend  (free, ~60 req/min)      ║")
    else:
        print("║  ✗ Gemini backend — set GEMINI_API_KEY      ║")
    if GH_MODELS_TOKEN:
        print("║  ✓ GitHub Models backend (free)              ║")
    else:
        print("║  ✗ GitHub Models — set GH_MODELS_TOKEN       ║")
    print("╚══════════════════════════════════════════════╝")
    uvicorn.run(app, host="0.0.0.0", port=7860)
