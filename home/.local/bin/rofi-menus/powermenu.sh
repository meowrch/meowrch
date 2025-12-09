#!/bin/env bash

choice=$(printf "  Lock\n󰍃  Logout\n󰒲  Suspend\n  Reboot\n  Shutdown" | rofi -dmenu)

case "$choice" in
  "  Lock") sh ${XDG_BIN_HOME:-$HOME/bin}/screen-lock.sh ;;
  "󰍃  Logout") 
    if [[ "$XDG_CURRENT_DESKTOP" == "bspwm" ]]; then
      bspc quit
    else
      pkill -KILL -u "$USER"
    fi
    ;;
  "󰒲  Suspend") sh ${XDG_BIN_HOME:-$HOME/bin}/screen-lock.sh --suspend ;;
  "  Reboot") systemctl reboot ;;
  "  Shutdown") systemctl poweroff ;;
esac
