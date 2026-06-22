# Free-Dooms Agent — Context

## Goal
Build a free LLM chat API + web UI that routes to multiple free backends.

## Architecture
- **Backend**: FastAPI (`app.py`) — proxies to GitHub Models (Llama 405B, GPT-4o, GPT-4o mini) + Cerebras (gpt-oss-120b with CoT/reasoning)
- **Frontend**: Glassmorphic SPA (`static/index.html`) — model selector, file upload, settings panel, dark/light mode, glow effects, typing animation
- **Hosting**: HuggingFace Spaces (free CPU tier) at `https://dacdoyx13-free-dooms.hf.space`
- **GitHub**: `dacdoyx/Free-Dooms_Agent`

## Key Info
- **Secrets**: CEREBRAS_KEY, GH_MODELS_TOKEN (set as HF Space secrets, NOT in code)
- **API key prefix**: `free-dooms_` — generated via `POST /api/v1/api-keys/generate`
- **Remotes**: `origin` → GitHub, `hf` → HF Space
- **HF Space URL**: `https://dacdoyx13-free-dooms.hf.space` (rebuilds after push, ~60-90s)

## Current State
- ✅ Glassmorphic UI connected to real API backend
- ✅ One API key works across all models
- ✅ Model selection, file upload, token tracking, settings
- ✅ Responsive UI — desktop, tablet (768px), mobile (480px) breakpoints
- ✅ Deployed on HF Space + GitHub
- ⏳ PR for `freedooms.is-a.dev` → https://github.com/is-a-dev/register/pull/41533
- ❌ Custom domain requires HF Pro ($9/mo)
- ❌ **Not** for commercial resale — uses free tier APIs (GitHub Models, Cerebras) which forbid reselling
- ❌ No finetune, RAG, or vector DB — pure proxy/gateway

## Usage
- User generates API key from Settings → Generate Key
- Sends chat with `Authorization: Bearer <key>`
- Models: Llama 3.1 405B (default), gpt-oss-120b (Cerebras/reasoning), GPT-4o, GPT-4o mini
- gpt-oss-120b returns CoT reasoning from Cerebras

## Models & Pricing (for future monetization)
- Open source models allowed for commercial use: Llama 3.1, Qwen2.5, DeepSeek-V3, Mistral
- Official APIs (legal for resale): OpenAI, Anthropic, Google Gemini, Groq, Together AI
- Self-host inference: vLLM, Ollama, llama.cpp (requires GPU)

## Suggestions discussed
- Add Gemini backend for free multimodal (image + video + audio)
- Add Ollama backend for truly self-hosted "free forever"
- Build CLI agent (like OpenCode/Claude Code) using GPT-4o function calling
- Pivot to premium tier (rate limits, exclusive models, priority support)
- For real business: host own model (vLLM) or wrap paid API with markup

## Commands
- Deploy: `git push origin main && git push hf main`
- Secrets: Set on HF Space dashboard → Settings → Repository Secrets
