#!/usr/bin/env bash

# ┏━━━┳━━┳━┓┏━┳━━━┳┓╋╋┏━━┳━┓┏━┓
# ┗┓┏┓┣┫┣┫┃┗┛┃┃┏━━┫┃╋╋┗┫┣┻┓┗┛┏┛
# ╋┃┃┃┃┃┃┃┏┓┏┓┃┗━━┫┃╋╋╋┃┃╋┗┓┏┛
# ╋┃┃┃┃┃┃┃┃┃┃┃┃┏━━┫┃╋┏┓┃┃╋┏┛┗┓
# ┏┛┗┛┣┫┣┫┃┃┃┃┃┃╋╋┃┗━┛┣┫┣┳┛┏┓┗┓
# ┗━━━┻━━┻┛┗┛┗┻┛╋╋┗━━━┻━━┻━┛┗━┛
# The program was created by DIMFLIX
# Github: https://github.com/DIMFLIX-OFFICIAL

SESSION_TYPE=$XDG_SESSION_TYPE

pin_hyprland() {
    # Get the data of the active window
    win_data=$(hyprctl -j activewindow)
    win_float=$(jq -r '.floating' <<< "$win_data")
    win_pinned=$(jq -r '.pinned' <<< "$win_data")

    # The logic of entrenchment
    if [[ "$win_float" == "false" && "$win_pinned" == "false" ]]; then
        hyprctl dispatch togglefloating active
        hyprctl dispatch pin active
    elif [[ "$win_pinned" == "false" ]]; then
        hyprctl dispatch pin active
    else
        hyprctl dispatch pin active  # Unfasten if already fastened
    fi
}

pin_bspwm() {
    # Get active window ID
    win_id=$(bspc query -N -n focused)
    
    # Check if window is pinned (sticky + locked)
    is_sticky=$(bspc query -N -n "$win_id.sticky")
    is_locked=$(bspc query -N -n "$win_id.locked")
    
    if [[ -n "$is_sticky" && -n "$is_locked" ]]; then
        # Unpin window
        bspc node "$win_id" -g sticky=off
        bspc node "$win_id" -g locked=off
    else
        # Ensure window is floating
        if [[ -z $(bspc query -N -n "$win_id.floating") ]]; then
            bspc node "$win_id" -t floating
        fi
        
        # Pin window
        bspc node "$win_id" -g sticky=on
        bspc node "$win_id" -g locked=on
        
        # Optional: bring to front and center
        bspc node "$win_id" -f
        bspc node "$win_id" -c
    fi
}

# Main logic
if [ "$SESSION_TYPE" = "wayland" ]; then
    pin_hyprland
elif [ "$SESSION_TYPE" = "x11" ]; then
    pin_bspwm
else
    echo "Unsupported session type: $SESSION_TYPE"
    exit 1
fi
