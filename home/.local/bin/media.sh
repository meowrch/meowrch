#!/bin/bash

# Escape JSON safely
json_escape() {
	echo -n "$1" | python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))'
}

# Escape for GTK markup
html_escape() {
	echo "$1" | sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g; s/\"/\&quot;/g; s/'"'"'/\&#39;/g'
}

# Truncate safely
truncate_text() {
	local text="$1"
	local max_length="$2"
	if [ ${#text} -gt $max_length ]; then
		echo "${text:0:max_length}…"
	else
		echo "$text"
	fi
}

# Normalize for comparison
normalize() {
	echo "$1" | tr '[:upper:]' '[:lower:]' | sed 's/([^)]*)//g' | sed 's/^[[:space:]]*//; s/[[:space:]]*$//'
}

# Find which media is "Playing"
active_media=$(playerctl -l 2>/dev/null | while read -r player; do
	status=$(playerctl -p "$player" status 2>/dev/null)
	if [ "$status" = "Playing" ]; then
		echo "$player"
		break
	fi
done)

if [ -z "$active_media" ]; then
	echo '{"text": "  No media", "tooltip": ""}'
	exit 0
fi

# Get metadata from the current playing media
title=$(playerctl -p "$active_media" metadata title 2>/dev/null)
artist=$(playerctl -p "$active_media" metadata artist 2>/dev/null)

# If there is no title, escape early
if [ -z "$title" ]; then
	echo '{"text": "  No media", "tooltip": ""}'
	exit 0
fi

# Find the title containing the separation
if [[ "$title" == *"｜"* || "$title" == *"|"* || "$title" == *"-"* ]]; then
	# Separate
	if [[ "$title" == *"｜"* ]]; then
		IFS='｜' read -r part1 part2 <<< "$title"
	elif [[ "$title" == *"|"* ]]; then
		IFS='|' read -r part1 part2 <<< "$title"
	else
		IFS='-' read -r part1 part2 <<< "$title"
	fi
	part1=$(echo "$part1" | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')
	part2=$(echo "$part2" | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')
	# Normalize text to compared to metadata artist
	norm_part1=$(normalize "$part1")
	norm_part2=$(normalize "$part2")
	norm_artist=$(normalize "$artist")
	if [[ "$norm_part1" == "$norm_artist"* ]]; then
		artist="$part1"
		title="$part2"
	elif [[ "$norm_part2" == "$norm_artist"* ]]; then
		artist="$part2"
		title="$part1"
	else
		# If not clear, keep the order, Part1 is Artist
		artist="$part2"
		title="$part1"
	fi
else
	# If there is no separation mark and artist is still empty
	if [ -z "$artist" ]; then
		artist=""
	fi
fi

# If it is still a unknown artist, use fallback
if [ -z "$artist" ]; then
	if [[ "$title" == *"｜"* ]]; then
		artist=$(echo "$title" | awk -F '｜' '{print $1}' | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')
		title=$(echo "$title" | awk -F '｜' '{$1=""; sub(/^ /,""); print}' | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')
	elif [[ "$title" == *"-"* ]]; then
		artist=$(echo "$title" | awk -F '-' '{print $1}' | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')
		title=$(echo "$title" | awk -F '-' '{$1=""; sub(/^ /,""); print}' | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')
	fi
fi

# Create a display text
if [ -n "$artist" ]; then
	short_title=$(truncate_text "$title" 15)
	short_artist=$(truncate_text "$artist" 10)
	display_text="  $short_title | $short_artist"
else
	short_title=$(truncate_text "$title" 25)
	display_text="  $short_title"
fi

# Escape and export
escaped_display=$(html_escape "$display_text")
escaped_tooltip=$(json_escape "$title — $artist")
echo "{\"text\": \"$escaped_display\", \"tooltip\": $escaped_tooltip}"
