#!/bin/bash

# ┏━━━┳━━┳━┓┏━┳━━━┳┓╋╋┏━━┳━┓┏━┓
# ┗┓┏┓┣┫┣┫┃┗┛┃┃┏━━┫┃╋╋┗┫┣┻┓┗┛┏┛
# ╋┃┃┃┃┃┃┃┏┓┏┓┃┗━━┫┃╋╋╋┃┃╋┗┓┏┛
# ╋┃┃┃┃┃┃┃┃┃┃┃┃┏━━┫┃╋┏┓┃┃╋┏┛┗┓
# ┏┛┗┛┣┫┣┫┃┃┃┃┃┃╋╋┃┗━┛┣┫┣┳┛┏┓┗┓
# ┗━━━┻━━┻┛┗┛┗┻┛╋╋┗━━━┻━━┻━┛┗━┛
# The program was created by DIMFLIX
# Github: https://github.com/DIMFLIX-OFFICIAL

SESSION_TYPE=$XDG_SESSION_TYPE

if [ "$SESSION_TYPE" == "wayland" ]; then
    killall waybar || waybar

elif [ "$SESSION_TYPE" == "x11" ]; then
    pgrep -x polybar
    status=$?
    if [ $status -eq 0 ]; then
        killall polybar && bspc config -m focused top_padding 0
    else 
        $HOME/.config/polybar/launch.sh && bspc config -m focused top_padding 31
    fi
else
    echo "Тип сеанса не определен или не является Wayland/X11."
fi
