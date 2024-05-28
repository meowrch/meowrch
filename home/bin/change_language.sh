#!/bin/bash

CURRENT_LAYOUT=$(xset -q|grep LED| awk '{ print $10 }')

setxkbmap -layout us,ru -option "grp:alt_shift_toggle"
if [ "$CURRENT_LAYOUT" = "00000000" ]; then
	notify-send "Lang: US" -t 700
fi

if [ "$CURRENT_LAYOUT" = "00001000" ]; then
    notify-send "Lang: RU" -t 700
fi
