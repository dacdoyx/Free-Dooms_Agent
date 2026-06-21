#!/bin/bash
set -e

echo "=== Free-dooms_ddkdkdketc API ==="
echo ""

# Deploy to HuggingFace Spaces (free) — 1 click
cat << 'EOF'
  DEPLOY TO HUGGINGFACE SPACES (TRULY $0):

  1. Go to https://huggingface.co/new-space
  2. Name: free-dooms-ddkdkdketc
  3. License: MIT
  4. Space SDK: Docker
  5. Upload these files:
     - app.py
     - requirements.txt
     - Dockerfile (below)
  
  That's it. Your API lives at:
  https://free-dooms-ddkdkdketc.hf.space/v1/chat/completions

  NO API KEY NEEDED. NO TOKEN COST. FOREVER FREE.
EOF
