#!/bin/bash
USER_INPUT="$1"
LOG_FILE="/tmp/mistral_calls.log"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# Log the call
echo "[$TIMESTAMP] Called with: $USER_INPUT" >> "$LOG_FILE"

# Check if another instance is running
if pgrep -f "llama-cli" > /dev/null; then
    echo "[$TIMESTAMP] ERROR: Another instance already running!" >> "$LOG_FILE"
    echo "Another Mistral instance is already running"
    exit 1
fi

# For now, just return a test response
echo "[$TIMESTAMP] Returning test response" >> "$LOG_FILE"
echo "Test response for: ${USER_INPUT:0:50}..."
