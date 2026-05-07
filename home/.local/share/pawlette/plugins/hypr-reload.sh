#!/bin/bash

if pgrep -x "Hyprland" > /dev/null; then
    if command -v hyprctl &> /dev/null; then
        hyprctl reload
    fi
fi
