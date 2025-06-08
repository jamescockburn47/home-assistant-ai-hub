#!/bin/bash
# Wrapper to run DeepSeek model for fast summary or short queries

LLAMA_CLI="/media/pi/data/llama.cpp/build/bin/llama-cli"
MODEL_PATH="/media/pi/data/llama.cpp/models/deepseek/deepseek-coder.Q4_K_M.gguf"

# Accept prompt as first argument
PROMPT="$1"

# Optional: max tokens, default 50
MAX_TOKENS="${2:-50}"

# Optional: temperature, default 0.7
TEMP="${3:-0.7}"

# Run llama-cli with DeepSeek model and arguments
"$LLAMA_CLI" -m "$MODEL_PATH" -p "$PROMPT" -n "$MAX_TOKENS" --temp "$TEMP"
