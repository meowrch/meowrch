#!/bin/bash

# ┏━━━┳━━┳━┓┏━┳━━━┳┓╋╋┏━━┳━┓┏━┓
# ┗┓┏┓┣┫┣┫┃┗┛┃┃┏━━┫┃╋╋┗┫┣┻┓┗┛┏┛
# ╋┃┃┃┃┃┃┃┏┓┏┓┃┗━━┫┃╋╋╋┃┃╋┗┓┏┛
# ╋┃┃┃┃┃┃┃┃┃┃┃┃┏━━┫┃╋┏┓┃┃╋┏┛┗┓
# ┏┛┗┛┣┫┣┫┃┃┃┃┃┃╋╋┃┗━┛┣┫┣┳┛┏┓┗┓
# ┗━━━┻━━┻┛┗┛┗┻┛╋╋┗━━━┻━━┻━┛┗━┛
# The program was created by DIMFLIX
# Github: https://github.com/DIMFLIX

FLAG_FILE="$HOME/.config/hypr/current_bar"

# Initialize the flag file if necessary
[ ! -f "$FLAG_FILE" ] && echo "mewline" > "$FLAG_FILE"

# Define current and new status bars
current_bar=$(cat "$FLAG_FILE")
new_bar=$([ "$current_bar" == "waybar" ] && echo "mewline" || echo "waybar")

# Update the flag file
echo "$new_bar" > "$FLAG_FILE"

# Stop the current bar
pkill -x "$current_bar"

# Run the new bar through a single script
nohup "${XDG_BIN_HOME:-$HOME/bin}/toggle-bar.sh" --start >/dev/null 2>&1 &
disown

exit 0