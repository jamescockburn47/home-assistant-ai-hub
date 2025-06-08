#!/bin/bash
USER_INPUT="$1"
MODEL_PATH="/media/pi/data/llama.cpp/models/mistral/mistral-7b-instruct-v0.1.Q4_K_M.gguf"
LLAMA_BIN="/media/pi/data/llama.cpp/build/bin/llama-cli"

# Run llama directly with prompt and capture output
OUTPUT=$("$LLAMA_BIN" -m "$MODEL_PATH" -p "User: $USER_INPUT\n\nAssistant:" -n 128 --temp 0.8 -t 4 2>&1)

# Extract just the assistant's response
# Look for "Assistant:" and take everything after it until we hit "User" or "llama_perf"
echo "$OUTPUT" | sed -n '/^Assistant:/,/^[Ul]/p' | sed '1s/^Assistant: //; /^[Ul]/d' | sed '/^$/d'
