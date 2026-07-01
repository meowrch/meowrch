#!/bin/bash

if pgrep -x "waybar" > /dev/null; then
    killall -SIGUSR2 waybar
fi
