#!/bin/bash
# Script to check what's actually in the files and find the issue

echo "=== Checking Current File Contents ==="
echo "Time: $(date)"
echo ""

# Function to show file details
check_file() {
    local file=$1
    local filepath="/srv/homeassistant/ai/$file"
    
    echo "----------------------------------------"
    echo "FILE: $file"
    if [ -f "$filepath" ]; then
        echo "Modified: $(stat -c '%y' "$filepath")"
        echo "Size: $(stat -c '%s' "$filepath") bytes"
        echo "MD5: $(md5sum "$filepath" | cut -d' ' -f1)"
        echo "Content:"
        cat "$filepath"
    else
        echo "ERROR: File not found!"
    fi
    echo ""
}

# Check each file
for file in fact.txt on_this_day.txt quote.txt poem.txt history.txt word.txt riddle.txt joke.txt; do
    check_file "$file"
done

echo ""
echo "=== Looking for other scripts or cron jobs ==="
echo ""

# Check for cron jobs
echo "Checking crontab for pi user:"
crontab -l 2>/dev/null | grep -E "(brain|boost|ai)" || echo "No related cron jobs found"

echo ""
echo "Checking system cron:"
sudo grep -r "brain\|boost" /etc/cron* 2>/dev/null || echo "No system cron jobs found"

echo ""
echo "=== Looking for other versions of the script ==="
find /media/pi/data/assistant -name "*brain*.py" -o -name "*boost*.py" | while read script; do
    echo "Found: $script"
    echo "Modified: $(stat -c '%y' "$script")"
    echo "First few lines:"
    head -5 "$script" | sed 's/^/  /'
    echo ""
done

echo ""
echo "=== Checking for backup or cache directories ==="
find /srv/homeassistant -name "*.txt.bak" -o -name "*.txt.old" 2>/dev/null | head -10

echo ""
echo "=== Checking running processes ==="
ps aux | grep -E "(python.*brain|python.*boost)" | grep -v grep

echo ""
echo "=== Recent file modifications in output directory ==="
echo "Files modified in last 10 minutes:"
find /srv/homeassistant/ai -name "*.txt" -mmin -10 -exec ls -la {} \;

echo ""
echo "Files modified in last hour:"
find /srv/homeassistant/ai -name "*.txt" -mmin -60 -exec ls -la {} \;

echo ""
echo "=== Checking for file watchers or sync services ==="
systemctl list-units --type=service --state=running | grep -E "(sync|watch|backup)" | head -10

echo ""
echo "=== IMPORTANT: Comparing with your log output ==="
echo ""
echo "Your log showed these previews:"
echo "fact.txt: 'Did you know that honey never spoils? Archaeologis...'"
echo "quote.txt: '\"Believe you can and you're halfway there.\" - Theo...'"
echo "riddle.txt: 'I speak without a mouth and hear without ears. I h...'"
echo ""
echo "Are these EXACTLY the same as what's in the files above?"
echo "If yes, then GPT is giving cached/similar responses."
echo "If no, then something is overwriting your files after generation."
