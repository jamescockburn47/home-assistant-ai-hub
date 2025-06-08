#!/usr/bin/env bash
# 1-at-a-time Mistral wrapper – 75 s hard limit
set -euo pipefail
PROMPT="$1"
MODEL="/media/pi/data/llama.cpp/models/mistral/mistral-7b-instruct-v0.1.Q4_K_M.gguf"
LLAMA="/media/pi/data/llama.cpp/build/bin/llama-cli"
LOCK="/tmp/mistral.lock"

(
  flock -n 200 || { echo "busy" ; exit 1 ; }
  pkill -9 -f "$LLAMA" 2>/dev/null || true     # stale jobs

  timeout --kill-after=5s 75s \
    "$LLAMA" -m "$MODEL" \
    -p "Respond concisely. User: $PROMPT\n\nAssistant:" \
    -n 80 -t 1 -c 256 --no-warmup -b 8 2>&1 |
  sed -n '/^Assistant:/,/^User:/p' |
  sed '1s/^Assistant:[[:space:]]*//' |
  grep -vE '^(llama_|sampler|generate|main:|system_info:|load|eval)' |
  tr '\n' ' ' |
  sed -E 's/[[:space:]]*\[end of text\][[:space:]]*$//' |
  fold -s -w 999
) 200>"$LOCK"
