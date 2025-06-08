#!/bin/bash
# Test wrapper with correct responses for each type
INPUT="$1"

if echo "$INPUT" | grep -q -i "fact\|Wikipedia"; then
    echo "The human brain uses 20% of the body's energy despite being only 2% of body weight."
elif echo "$INPUT" | grep -q -i "word\|Wiktionary"; then
    echo "Serendipity: Finding something good without looking for it."
elif echo "$INPUT" | grep -q -i "quote\|Wikiquote"; then
    echo "The only way to do great work is to love what you do. - Steve Jobs"
elif echo "$INPUT" | grep -q -i "history"; then
    echo "On this day in 1969, the first ARPANET link was established."
elif echo "$INPUT" | grep -q -i "joke"; then
    echo "Why don't scientists trust atoms? Because they make up everything!"
elif echo "$INPUT" | grep -q -i "riddle"; then
    echo "What has keys but no locks? A keyboard."
else
    echo "Test response"
fi
