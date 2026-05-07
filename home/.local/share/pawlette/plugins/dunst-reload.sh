#!/bin/bash

if pgrep -x "dunst" > /dev/null; then
    killall -HUP dunst
fi
