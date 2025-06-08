#!/bin/bash
USER_INPUT="$1"
MODEL_PATH="/media/pi/data/llama.cpp/models/mistral/mistral-7b-instruct-v0.1.Q4_K_M.gguf"
LLAMA_BIN="/media/pi/data/llama.cpp/build/bin/llama-cli"

# Kill any existing llama processes first
pkill -9 -f llama-cli 2>/dev/null

# Run llama with timeout to ensure it dies
timeout --kill-after=95s 90s "$LLAMA_BIN" \
    -m "$MODEL_PATH" \
    -p "Respond with ONLY the requested content. No introductions or conclusions. User: $USER_INPUT\n\nAssistant:" \
    -n 100 \
    --temp 0.7 \
    -t 2 \
    -c 512 \
    --no-warmup \
    2>&1 | awk '
    /^Assistant:/ {p=1; sub(/^Assistant: /, "")} 
    /^User:|llama_perf/ {if(p) exit} 
    p && NF>0 {print}
' | tr '\n' ' ' | sed 's/  */ /g; s/ *$//; s/ *\[end of text\] *$//'

# Ensure cleanup
exit 0
