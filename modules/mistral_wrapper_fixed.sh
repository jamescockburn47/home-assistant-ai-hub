#!/bin/bash
USER_INPUT="$1"
MODEL_PATH="/media/pi/data/llama.cpp/models/mistral/mistral-7b-instruct-v0.1.Q4_K_M.gguf"
LLAMA_BIN="/media/pi/data/llama.cpp/build/bin/llama-cli"

# Run llama and capture complete output
OUTPUT=$("$LLAMA_BIN" \
    -m "$MODEL_PATH" \
    -p "User: $USER_INPUT\n\nAssistant:" \
    -n 100 \
    --temp 0.7 \
    -t 2 \
    -c 512 \
    --no-warmup \
    2>&1)

# Extract the complete assistant response (stop at User: or llama_perf)
echo "$OUTPUT" | awk '
    /^Assistant:/ {p=1; sub(/^Assistant: /, "")} 
    /^User:|llama_perf/ {if(p) exit} 
    p && NF>0 {print}
' | tr '\n' ' ' | sed 's/  */ /g; s/ *$//'

# Ensure the script exits cleanly
exit 0
