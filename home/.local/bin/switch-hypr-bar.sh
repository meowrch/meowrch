#!/bin/bash

# ┏━━━┳━━┳━┓┏━┳━━━┳┓╋╋┏━━┳━┓┏━┓
# ┗┓┏┓┣┫┣┫┃┗┛┃┃┏━━┫┃╋╋┗┫┣┻┓┗┛┏┛
# ╋┃┃┃┃┃┃┃┏┓┏┓┃┗━━┫┃╋╋╋┃┃╋┗┓┏┛
# ╋┃┃┃┃┃┃┃┃┃┃┃┃┏━━┫┃╋┏┓┃┃╋┏┛┗┓
# ┏┛┗┛┣┫┣┫┃┃┃┃┃┃╋╋┃┗━┛┣┫┣┳┛┏┓┗┓
# ┗━━━┻━━┻┛┗┛┗┻┛╋╋┗━━━┻━━┻━┛┗━┛
# The program was created by DIMFLIX
# Github: https://github.com/DIMFLIX

CONFIG_FILE="$HOME/.config/hypr/hyprland.conf"

current_bar=$(grep -E '^exec-once = (waybar|mewline)\b' "$CONFIG_FILE" | grep -oE 'waybar|mewline')
new_bar=$([ "$current_bar" == "waybar" ] && echo "mewline" || echo "waybar")

sed -i "s/^exec-once = $current_bar/exec-once = $new_bar/" "$CONFIG_FILE"


pkill -x "$current_bar"
nohup "$new_bar" >/dev/null 2>&1 &
disown

exit 0
