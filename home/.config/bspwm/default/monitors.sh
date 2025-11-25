#!/bin/sh

# Define workspaces on the primary monitor
bspc monitor -d 1 2 3 4 5 6 7 8 9 10

# Uncomment to define workspaces on YOUR_MONITOR (for multiple monitors setup)
#bspc monitor YOUR_MONITOR -d 6 7 8 9

# Enable window focus follow mouse pointer
bspc config focus_follows_pointer true

# Auto set monitor
monitor=$(xrandr --query | grep " connected" | awk '{ print $1 }' | head -n 1)
resolution=$(xrandr --query | grep -A1 "^$monitor" | grep -Eo '[0-9]+x[0-9]+' | sort -V | tail -n 1)
refresh_rate=$(xrandr --query | grep -A1 "^$monitor" | grep -Eo '[0-9]+\.[0-9]+' | sort -V | tail -n 1)

if [[ -n $monitor && -n $resolution && -n $refresh_rate ]]; then
    xrandr --output "$monitor" --mode "$resolution" --rate "$refresh_rate"
fi
