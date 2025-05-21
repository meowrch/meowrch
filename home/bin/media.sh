#!/bin/bash

# Escape JSON (use Python for safety)
json_escape() {
  echo -n "$1" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))'
}

# Escape HTML for GTK markup
html_escape() {
  echo "$1" | sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g; s/\"/\&quot;/g; s/'"'"'/\&#39;/g'
}

# Get information
title=$(playerctl metadata title 2>/dev/null)
artist=$(playerctl metadata artist 2>/dev/null)

# If there is no media playing, display "No media"
if [ -z "$title" ]; then
  echo '{"text": "  No media", "tooltip": ""}'
  exit 0
fi

# Truncate
truncate_text() {
  local text="$1"
  local max_length="$2"
  if [ ${#text} -gt $max_length ]; then
    echo "${text:0:max_length}…"
  else
    echo "$text"
  fi
}

short_title=$(truncate_text "$title" 10)
short_artist=$(truncate_text "$artist" 10)

# Escape text for GTK Markup (must use HTML_escape)
escaped_display=$(html_escape "  $short_title | $short_artist")
escaped_tooltip=$(json_escape "$title — $artist")  # Tooltip is still JSON should use json_escape

# JSON export
echo "{\"text\": \"$escaped_display\", \"tooltip\": $escaped_tooltip}"