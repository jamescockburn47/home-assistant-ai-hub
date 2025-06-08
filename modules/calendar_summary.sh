#!/bin/bash

# Summary script: fetch calendar, summarise with Mistral, speak with Piper

ENTITY_ID="calendar.james_a_cockburn_gmail_com"
HA_URL="http://localhost:8123"
TOKEN_FILE="/media/data/assistant/secrets/ha_token.txt"
WRAPPER="/media/pi/data/assistant/modules/mistral_wrapper.sh"
PIPER="/media/pi/data/piper/build/piper"
VOICE_MODEL="/media/pi/data/piper/voices/en_GB-alba-medium.onnx"
VOICE_CFG="/media/pi/data/piper/voices/en_GB-alba-medium.onnx.json"
TEMP_JSON="/tmp/calendar_summary_events.json"
OUTPUT_WAV="/tmp/calendar_summary.wav"

# Load token
HA_TOKEN=$(cat "$TOKEN_FILE")

# Define time range
START=$(date -I)
END=$(date -I -d "7 days")

# Fetch calendar events
curl -s -H "Authorization: Bearer $HA_TOKEN" \
     "$HA_URL/api/calendars/$ENTITY_ID?start=$START&end=$END" > "$TEMP_JSON"

# Format events into prompt
EVENTS=$(jq -r '.[] | "\(.summary) at \(.start)"' "$TEMP_JSON" | paste -sd ', ' -)
[[ -z "$EVENTS" ]] && EVENTS="There are no events scheduled this week."

# Query Mistral for summary
SUMMARY=$("$WRAPPER" "Summarise these events for the week: $EVENTS")

# Speak the summary
echo "$SUMMARY" | "$PIPER" \
    --model "$VOICE_MODEL" \
    --config "$VOICE_CFG" \
    --output_file "$OUTPUT_WAV"

aplay "$OUTPUT_WAV"
