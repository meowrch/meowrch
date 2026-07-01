#!/bin/bash

# Path to the Pawlette palette and temporary file
PALETTE_FILE="$HOME/.local/state/pawlette/active_palette.json"
TEMP_SCREEN="/tmp/screenshot_$(date +%s).png"

# Select the accent color HEX from Pawlette; otherwise, the default lavender will be used
if [ -f "$PALETTE_FILE" ]; then
    HEX_COLOR=$(jq -r '.color_primary' "$PALETTE_FILE" | tr -d '#[:space:]')
else
    HEX_COLOR="b4befe" 
fi

# Checking command-line arguments
MODE="select"
if [[ "$1" == "--full" || "$1" == "-f" ]]; then
    MODE="full"
fi

# ==========================================
# WAYLAND (Hyprland): Проверяем через WAYLAND_DISPLAY
# ==========================================
if [ -n "$WAYLAND_DISPLAY" ]; then
    if [ "$MODE" = "full" ]; then
        grim -t png - | wl-copy -t image/png
        notify-send "Screenshot" "A screenshot of the entire screen has been taken" -i screenshot
    else
        COLOR_BACKGROUND="${HEX_COLOR}1a"
        COLOR_BORDER="${HEX_COLOR}ff"
        
        grim -g "$(slurp -b "$COLOR_BACKGROUND" -c "$COLOR_BORDER" -w 3)" - | satty --filename - --output-filename "$TEMP_SCREEN"
    fi

# ==========================================
# X11 (bspwm)
# ==========================================
else
    if [ "$MODE" = "full" ]; then
        maim | xclip -selection clipboard -t image/png
        notify-send "Screenshot" "A screenshot of the entire screen has been taken" -i screenshot
    else
        # Parse HEX to 0-1 format for slop
        HEX_R=${HEX_COLOR:0:2}
        HEX_G=${HEX_COLOR:2:2}
        HEX_B=${HEX_COLOR:4:2}
        
        R=$(echo "scale=2; $((16#$HEX_R)) / 255" | bc)
        G=$(echo "scale=2; $((16#$HEX_G)) / 255" | bc)
        B=$(echo "scale=2; $((16#$HEX_B)) / 255" | bc)
        A="0.7" 
        
        SLOP_COLOR="$R,$G,$B,$A"
        
        maim -s -c "$SLOP_COLOR" -l -b 3 | satty --filename - --output-filename "$TEMP_SCREEN"
    fi
fi

