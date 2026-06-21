# free-dooms_ddkdkdketc

Claude-powerful LLM API. Completely free. Zero tokens.

## How it works

Routes your requests through **free backends** (Gemini, GitHub Models) behind a simple API key system. No billing, no rate limit tracking, no token counting.

## Deploy (truly $0)

### Option 1: HuggingFace Spaces (persistent)

1. Go to [aistudio.google.com/apikey](https://aistudio.google.com/apikey) → get a free Gemini API key
2. Go to [hf.co/new-space](https://huggingface.co/new-space) → name `free-dooms`, SDK: Docker
3. Upload `app.py` + `requirements.txt` + `Dockerfile`
4. Add a secret `GEMINI_API_KEY` in Space settings

That's it. Your API at `https://free-dooms.hf.space/v1`

### Option 2: Google Colab (GPU, temporary)

Open `colab.ipynb`, paste your Gemini key → running in 30 seconds.

## Usage

```bash
# Generate a key
curl https://your-api/v1/api-keys/generate

# Chat (Claude-level power, $0)
curl https://your-api/v1/chat/completions \
  -H "Authorization: Bearer free-dooms_a8f3b2..." \
  -d '{"messages":[{"role":"user","content":"write me a react component"}]}'
```
