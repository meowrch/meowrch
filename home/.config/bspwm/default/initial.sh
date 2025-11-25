#!/bin/sh

# Start sxhkd
pkill -x sxhkd 2>/dev/null
sxhkd -c ~/.config/bspwm/sxhkdrc &

# Set window manager name to LG3D to fix some Java applications display issues
wmname LG3D
