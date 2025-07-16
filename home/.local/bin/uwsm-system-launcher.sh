#!/bin/bash

# ┏━━━┳━━┳━┓┏━┳━━━┳┓╋╋┏━━┳━┓┏━┓
# ┗┓┏┓┣┫┣┫┃┗┛┃┃┏━━┫┃╋╋┗┫┣┻┓┗┛┏┛
# ╋┃┃┃┃┃┃┃┏┓┏┓┃┗━━┫┃╋╋╋┃┃╋┗┓┏┛
# ╋┃┃┃┃┃┃┃┃┃┃┃┃┏━━┫┃╋┏┓┃┃╋┏┛┗┓
# ┏┛┗┛┣┫┣┫┃┃┃┃┃┃╋╋┃┗━┛┣┫┣┳┛┏┓┗┓
# ┗━━━┻━━┻┛┗┛┗┻┛╋╋┗━━━┻━━┻━┛┗━┛
# UWSM System Service Launcher
# Created by DIMFLIX
# Github: https://github.com/DIMFLIX

# This wrapper is specifically for applications that interact with system services
# like Bluetooth, NetworkManager, etc.

# Check if UWSM is installed
check_uwsm_installed() {
    command -v uwsm >/dev/null 2>&1
}

# Check if UWSM session is active
check_uwsm_active() {
    uwsm check is-active >/dev/null 2>&1
}

# Setup critical environment variables
setup_environment() {
    # D-Bus session bus
    export DBUS_SESSION_BUS_ADDRESS="${DBUS_SESSION_BUS_ADDRESS:-unix:path=/run/user/$(id -u)/bus}"
    
    # Wayland display
    export WAYLAND_DISPLAY="${WAYLAND_DISPLAY:-wayland-1}"
    
    # Desktop environment
    export XDG_CURRENT_DESKTOP="${XDG_CURRENT_DESKTOP:-Hyprland}"
    export XDG_SESSION_TYPE="${XDG_SESSION_TYPE:-wayland}"
    export XDG_SESSION_DESKTOP="${XDG_SESSION_DESKTOP:-hyprland}"
    
    # Runtime directory
    export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
    
    # Ensure D-Bus activation environment is updated
    if command -v dbus-update-activation-environment >/dev/null 2>&1; then
        dbus-update-activation-environment --systemd \
            DBUS_SESSION_BUS_ADDRESS \
            WAYLAND_DISPLAY \
            XDG_CURRENT_DESKTOP \
            XDG_SESSION_TYPE \
            XDG_SESSION_DESKTOP \
            XDG_RUNTIME_DIR >/dev/null 2>&1 || true
    fi
}

# Main launcher function
launch_system_app() {
    if [[ $# -eq 0 ]]; then
        echo "Usage: $0 <command> [args...]"
        echo "Example: $0 mewline"
        echo "This launcher is for apps that interact with system services"
        exit 1
    fi
    
    # Always setup environment first
    setup_environment
    
    # Check if UWSM is installed and active
    if check_uwsm_installed && check_uwsm_active; then
        echo "UWSM session active, launching system app via uwsm: $*"
        
        # Small delay to ensure environment is propagated
        sleep 0.1
        
        # Use uwsm but with environment setup
        uwsm app -- "$@"
    else
        echo "UWSM not active, launching system app directly: $*"
        "$@"
    fi
}

# Run the launcher
launch_system_app "$@"
