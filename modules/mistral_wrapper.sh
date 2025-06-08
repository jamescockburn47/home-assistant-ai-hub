#!/bin/bash

# Mistral prompt wrapper with persistent memory
# Usage: ./mistral_wrapper.sh "Your prompt here"

USER_INPUT="$1"
MODEL_PATH="/media/pi/data/llama.cpp/models/mistral/mistral-7b-instruct-v0.1.Q4_K_M.gguf"
LLAMA_BIN="/media/pi/data/llama.cpp/build/bin/llama-cli"
MEMORY_FILE="/media/pi/data/assistant/memory/mistral_context.txt"
TEMP_PROMPT="/tmp/mistral_prompt.txt"

mkdir -p "$(dirname "$MEMORY_FILE")"

# Append user input to persistent memory
echo -e "\nUser: $USER_INPUT" >> "$MEMORY_FILE"

# Build full conversation prompt
echo -e "The following is a helpful assistant responding to user queries.\n" > "$TEMP_PROMPT"
cat "$MEMORY_FILE" >> "$TEMP_PROMPT"

# Run Mistral with full context
RESPONSE=$("$LLAMA_BIN" -m "$MODEL_PATH" -f "$TEMP_PROMPT" -n 256 --temp 0.8)

# Extract and store assistant reply
ASSISTANT_REPLY=$(echo "$RESPONSE" | sed -n '/Assistant:/,$p' | sed 's/^Assistant: //')
echo "Assistant: $ASSISTANT_REPLY" >> "$MEMORY_FILE"

# Output to screen or pipeline
echo "$ASSISTANT_REPLY"
