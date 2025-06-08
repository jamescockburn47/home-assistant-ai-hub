#!/bin/bash
USER_INPUT="$1"
MODEL_PATH="/media/pi/data/llama.cpp/models/mistral/mistral-7b-instruct-v0.1.Q4_K_M.gguf"
LLAMA_BIN="/media/pi/data/llama.cpp/build/bin/llama-cli"

# Run with minimal memory usage
"$LLAMA_BIN" \
    -m "$MODEL_PATH" \
    -p "User: $USER_INPUT\n\nAssistant:" \
    -n 50 \
    --temp 0.7 \
    -t 2 \
    -c 512 \
    --batch-size 256 \
    --no-mmap \
    2>&1 | sed -n '/^Assistant:/,/^$/p' | head -n1 | sed 's/^Assistant: //'
