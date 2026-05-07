#!/bin/bash

if pgrep -x "kitty" > /dev/null; then
    killall -SIGUSR1 kitty
fi
