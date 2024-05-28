#!/bin/env bash

choice=$(printf "Lock\nLogout\nSuspend\nReboot\nShutdown" | rofi -dmenu)
case "$choice" in
  Lock) sh $HOME/bin/screen-lock ;;
  Logout) pkill -KILL -u "$USER" ;;
  Suspend) systemctl suspend && sh $HOME/bin/screen-lock ;;
  Reboot) systemctl reboot ;;
  Shutdown) systemctl poweroff ;;
esac
