#!/bin/sh

dbus-update-activation-environment --systemd XDG_CURRENT_DESKTOP
xrdb merge $HOME/.Xresources
xsettingsd &
dunst &
picom --config $HOME/.config/bspwm/picom.conf &
sh ${XDG_BIN_HOME:-$HOME/bin}/toggle-bar.sh --start &
sh ${XDG_BIN_HOME:-$HOME/bin}/polkitkdeauth.sh & # authentication dialogue for GUI apps
sh ${XDG_BIN_HOME:-$HOME/bin}/set-wallpaper.sh --current & # set current wallpaper