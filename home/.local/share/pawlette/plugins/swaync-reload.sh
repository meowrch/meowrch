#!/usr/bin/env bash

if pgrep -x "swaync" > /dev/null; then
    swaync-client -rs
fi