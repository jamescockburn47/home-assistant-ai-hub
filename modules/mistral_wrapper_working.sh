#!/usr/bin/env bash
MODEL="/media/pi/data/llama.cpp/models/mistral/mistral-7b-instruct-v0.1.Q4_K_M.gguf"
LLAMA="/media/pi/data/llama.cpp/build/bin/llama-cli"

PROMPT="${1:-"Hello"}"

pkill -9 -f llama-cli 2>/dev/null

"$LLAMA" \
  -m "$MODEL" \
  -p "$PROMPT" \
  -n 80 \
  -t 1 \
  -c 512 \
  --temp 0.8 \
  --no-warmup 2>/dev/null | \
  sed 's/^Assistant: *//' | sed 's/^User: *//' | sed '/^$/d'

