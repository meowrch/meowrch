#!/bin/bash

# ┏━━━┳━━┳━┓┏━┳━━━┳┓╋╋┏━━┳━┓┏━┓
# ┗┓┏┓┣┫┣┫┃┗┛┃┃┏━━┫┃╋╋┗┫┣┻┓┗┛┏┛
# ╋┃┃┃┃┃┃┃┏┓┏┓┃┗━━┫┃╋╋╋┃┃╋┗┓┏┛
# ╋┃┃┃┃┃┃┃┃┃┃┃┃┏━━┫┃╋┏┓┃┃╋┏┛┗┓
# ┏┛┗┛┣┫┣┫┃┃┃┃┃┃╋╋┃┗━┛┣┫┣┳┛┏┓┗┓
# ┗━━━┻━━┻┛┗┛┗┻┛╋╋┗━━━┻━━┻━┛┗━┛
# Universal UWSM Launcher Script
# Created by DIMFLIX
# Github: https://github.com/DIMFLIX

# Check if UWSM is installed
check_uwsm_installed() {
    command -v uwsm >/dev/null 2>&1
}

# Check if UWSM session is active
check_uwsm_active() {
    uwsm check is-active >/dev/null 2>&1
}

# Main launcher function
launch_with_uwsm() {
    if [[ $# -eq 0 ]]; then
        echo "Usage: $0 <command> [args...]"
        echo "Example: $0 dunst"
        echo "Example: $0 sh /path/to/script.sh --arg"
        exit 1
    fi

    # Check if UWSM is installed
    if ! check_uwsm_installed; then
        echo "UWSM not installed, launching directly: $*"
        "$@"
        return
    fi

    # Check if UWSM session is active
    if check_uwsm_active; then
        echo "UWSM session active, launching via uwsm: $*"
        
        # Ensure critical environment variables are set
        export DBUS_SESSION_BUS_ADDRESS="${DBUS_SESSION_BUS_ADDRESS:-unix:path=/run/user/$(id -u)/bus}"
        export WAYLAND_DISPLAY="${WAYLAND_DISPLAY:-wayland-1}"
        export XDG_CURRENT_DESKTOP="${XDG_CURRENT_DESKTOP:-Hyprland}"
        
        uwsm app -- "$@"
    else
        echo "UWSM installed but not active, launching directly: $*"
        "$@"
    fi
}

# Run the launcher
launch_with_uwsm "$@"
