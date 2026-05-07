#!/bin/bash

if pgrep -x "cava" > /dev/null; then
    killall -USR1 cava
fi
