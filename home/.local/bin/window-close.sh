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


if [ "$SESSION_TYPE" = "wayland" ]; then
    hyprctl dispatch killactive ""
elif [ "$SESSION_TYPE" = "x11" ]; then
    win_id=$(bspc query -N -n focused)
    is_sticky=$(bspc query -N -n "$win_id.sticky")
    is_locked=$(bspc query -N -n "$win_id.locked")
    
    if [[ -n "$is_sticky" && -n "$is_locked" ]]; then
        bspc node "$win_id" -g sticky=off
        bspc node "$win_id" -g locked=off
        sleep 0.1
    fi

    bspc node "$win_id" -c
else
    echo "Unsupported session type: $SESSION_TYPE"
    exit 1
fi
