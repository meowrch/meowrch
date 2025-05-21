#!/bin/bash

# Get media's metadata
title=$(playerctl metadata title 2>/dev/null)
artist=$(playerctl metadata artist 2>/dev/null)

# If there is no media playing, display "No media"
if [ -z "$title" ]; then
  echo '{"text": "  No media", "tooltip": ""}'
  exit 0
fi

# Shorten title if longer than 20 characters
short_title=$title
if [ ${#title} -gt 20 ]; then
  short_title="${title:0:20}..."
fi

# Returns JSON
echo "{\"text\": \"  $short_title\", \"tooltip\": \"$artist - $title\"}"