#!/bin/bash
# Script to diagnose sensor mapping issues

echo "=== Daily Brain Boost Sensor Mapping Check ==="
echo "Date: $(date)"
echo ""

echo "1. Checking file contents:"
echo "========================="
echo ""

# Check each file and show full content
for file in fact.txt on_this_day.txt quote.txt poem.txt history.txt word.txt riddle.txt joke.txt; do
    filepath="/srv/homeassistant/ai/$file"
    if [ -f "$filepath" ]; then
        echo "FILE: $file"
        echo "Size: $(stat -c '%s' "$filepath") bytes"
        echo "Modified: $(stat -c '%y' "$filepath")"
        echo "--- FULL CONTENT ---"
        cat "$filepath"
        echo ""
        echo "--- FIRST LINE ---"
        head -1 "$filepath"
        echo ""
        echo "--- LAST LINE ---"
        tail -1 "$filepath"
        echo ""
        echo "===================="
        echo ""
    else
        echo "ERROR: $filepath not found!"
        echo ""
    fi
done

echo ""
echo "2. Expected Sensor Mapping:"
echo "==========================="
echo "sensor.ai_fact         → fact.txt"
echo "sensor.verified_fact   → on_this_day.txt"
echo "sensor.ai_quote        → quote.txt"
echo "sensor.verified_quote  → poem.txt"
echo "sensor.ai_history      → history.txt"
echo "sensor.verified_word   → word.txt"
echo "sensor.ai_riddle       → riddle.txt"
echo "sensor.ai_joke         → joke.txt"
echo ""

echo "3. Checking Home Assistant Configuration:"
echo "========================================="
# Look for file sensor configurations
for config_path in "/home/homeassistant/.homeassistant/configuration.yaml" "/config/configuration.yaml" "/home/pi/.homeassistant/configuration.yaml"; do
    if [ -f "$config_path" ]; then
        echo "Found config at: $config_path"
        echo ""
        echo "File sensor definitions:"
        grep -A10 "platform: file" "$config_path" | grep -B2 -A8 "name:"
        break
    fi
done

echo ""
echo "4. Checking for value_template issues:"
echo "======================================"
echo "If sensors show only last lines, check for value_template in config."
echo "File sensors might have templates that extract specific parts."
echo ""

echo "5. Quick Fix Commands:"
echo "====================="
echo ""
echo "To reload file sensors:"
echo "  Developer Tools → YAML → Reload FILE"
echo ""
echo "To check a specific sensor's config:"
echo "  Developer Tools → States → Search for sensor name"
echo ""
echo "To manually test a file sensor:"
echo "  cat /srv/homeassistant/ai/fact.txt"
echo ""

echo "6. Creating test file to verify sensors work:"
echo "============================================="
echo "TEST CONTENT - Generated at $(date)" > /srv/homeassistant/ai/test.txt
echo "If you create a test sensor pointing to this file,"
echo "it should show: 'TEST CONTENT - Generated at $(date)'"
echo ""

echo "=== Check Complete ==="
