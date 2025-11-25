#!/bin/sh

if command -v clipnotify >/dev/null 2>&1 && command -v xclip >/dev/null 2>&1 && command -v cliphist >/dev/null 2>&1; then
    (
        while clipnotify; do 
            xclip -o -selection c | cliphist store
        done
    ) &
fi
