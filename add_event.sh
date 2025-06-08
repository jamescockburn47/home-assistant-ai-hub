#!/bin/bash
# Add a calendar event via the Home Assistant API.
# Usage: ./add_event.sh "2024-06-01T13:00:00" "2024-06-01T14:00:00" "Meeting"
#
# The script expects HA_TOKEN to contain your long-lived access token.
# It will source a local .env if present.
# The Authorization header is constructed as "Bearer $HA_TOKEN".
if [ -f ".env" ]; then
    set -a
    source ".env"
    set +a
fi

if [ -z "$HA_TOKEN" ]; then
    echo "HA_TOKEN not set. Export it or place it in .env" >&2
    exit 1
fi

TOKEN="$HA_TOKEN"
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
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d "$DATA"
