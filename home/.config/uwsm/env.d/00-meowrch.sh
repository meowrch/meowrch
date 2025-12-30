#!/usr/bin/env sh

# Basic PATH prepending (user local bin)
PATH="$HOME/.local/bin:$PATH"

# Less history file location
LESSHISTFILE="${LESSHISTFILE:-/tmp/less-hist}"

# Export all variables
export PATH LESSHISTFILE
