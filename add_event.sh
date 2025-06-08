#!/bin/bash
TOKEN="Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhZjAwN2ZhMWJiMjI0NGQwYTYxZDE1MTUwN2FlZTU0YyIsImlhdCI6MTc0ODg4ODI1NCwiZXhwIjoyMDY0MjQ4MjU0fQ.Yaz5G0PSNW868ehaXZkzRSXJGGzYPvlK2lNWL4ERqM4"
HA_IP="192.168.1.211"
ENTITY="calendar.james_a_cockburn_gmail_com"

START="$1"
END="$2"
SUMMARY="$3"

DATA=$(cat <<EOF
{
  "entity_id": "$ENTITY",
  "start": "$START",
  "end": "$END",
  "summary": "$SUMMARY"
}
EOF
)

curl -s -X POST "http://$HA_IP:8123/api/services/calendar/create_event" \
     -H "Authorization: $TOKEN" \
     -H "Content-Type: application/json" \
     -d "$DATA"
