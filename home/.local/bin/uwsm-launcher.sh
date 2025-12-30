#!/bin/bash

# ┏━━━┳━━┳━┓┏━┳━━━┳┓╋╋┏━━┳━┓┏━┓
# ┗┓┏┓┣┫┣┫┃┗┛┃┃┏━━┫┃╋╋┗┫┣┻┓┗┛┏┛
# ╋┃┃┃┃┃┃┃┏┓┏┓┃┗━━┫┃╋╋╋┃┃╋┗┓┏┛
# ╋┃┃┃┃┃┃┃┃┃┃┃┃┏━━┫┃╋┏┓┃┃╋┏┛┗┓
# ┏┛┗┛┣┫┣┫┃┃┃┃┃┃╋╋┃┗━┛┣┫┣┳┛┏┓┗┓
# ┗━━━┻━━┻┛┗┛┗┻┛╋╋┗━━━┻━━┻━┛┗━┛
# Universal UWSM Launcher Script (Unified)
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

# Setup critical environment variables (enhanced version)
setup_environment() {
    # D-Bus session bus
    export DBUS_SESSION_BUS_ADDRESS="${DBUS_SESSION_BUS_ADDRESS:-unix:path=/run/user/$(id -u)/bus}"
    
    # Wayland display
    export WAYLAND_DISPLAY="${WAYLAND_DISPLAY:-wayland-1}"
    
    # Desktop environment variables
    export XDG_CURRENT_DESKTOP="${XDG_CURRENT_DESKTOP:-Hyprland}"
    export XDG_SESSION_TYPE="${XDG_SESSION_TYPE:-wayland}"
    export XDG_SESSION_DESKTOP="${XDG_SESSION_DESKTOP:-hyprland}"
    
    # Runtime directory
    export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
}

# Update D-Bus activation environment for system services
update_dbus_environment() {
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

# Show usage information
show_usage() {
    cat << EOF
Universal UWSM Launcher

Usage: $0 [OPTIONS] <command> [args...]

OPTIONS:
    -t, --type TYPE         Set uwsm service type (e.g., service, scope)
    -s, --scope SCOPE       Set uwsm scope (e.g., s, u)
    --system-mode           Enable system service mode (enhanced environment setup)
    --delay SECONDS         Add delay before launch (default: 0, system-mode: 0.1)
    -h, --help              Show this help message

EXAMPLES:
    $0 dunst                                    # Launch dunst
    $0 -t service -s s mewline                  # Launch with specific uwsm options
    $0 --system-mode mewline                    # Launch with system service environment
    $0 --system-mode --delay 0.5 blueman-tray  # System mode with custom delay
    $0 sh /path/to/script.sh --arg              # Launch script with arguments

MODES:
    Regular mode:     Standard application launcher with basic environment
    System mode:      Enhanced environment setup for system service integration
                     (Bluetooth, NetworkManager, etc.)

EOF
}

# Main launcher function
launch_with_uwsm() {
    local uwsm_opts=()
    local system_mode=false
    local delay=0
    local app_command=()
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -t|--type)
                if [[ -z "$2" ]]; then
                    echo "Error: --type requires a value"
                    exit 1
                fi
                uwsm_opts+=("-t" "$2")
                shift 2
                ;;
            -s|--scope)
                if [[ -z "$2" ]]; then
                    echo "Error: --scope requires a value"
                    exit 1
                fi
                uwsm_opts+=("-s" "$2")
                shift 2
                ;;
            --system-mode)
                system_mode=true
                delay=0.1  # Default delay for system mode
                shift
                ;;
            --delay)
                if [[ -z "$2" ]] || ! [[ "$2" =~ ^[0-9]+(\.[0-9]+)?$ ]]; then
                    echo "Error: --delay requires a numeric value"
                    exit 1
                fi
                delay="$2"
                shift 2
                ;;
            --)
                shift
                app_command=("$@")
                break
                ;;
            -*)
                uwsm_opts+=("$1")
                shift
                ;;
            *)
                app_command=("$@")
                break
                ;;
        esac
    done
    
    # Validate command
    if [[ ${#app_command[@]} -eq 0 ]]; then
        echo "Error: No command specified"
        show_usage
        exit 1
    fi
    
    # Always setup basic environment
    setup_environment
    
    # Enhanced environment setup for system mode
    if [[ "$system_mode" == true ]]; then
        echo "System mode enabled: Enhanced environment setup"
        update_dbus_environment
    fi
    
    # Apply delay if specified
    if [[ $(echo "$delay > 0" | bc -l 2>/dev/null || echo "0") -eq 1 ]]; then
        echo "Applying delay: ${delay}s"
        sleep "$delay"
    fi
    
    # Check if UWSM is installed
    if ! check_uwsm_installed; then
        echo "UWSM not installed, launching directly: ${app_command[*]}"
        "${app_command[@]}"
        return
    fi
    
    # Check if UWSM session is active
    if check_uwsm_active; then
        echo "UWSM session active, launching via uwsm: ${app_command[*]}"
        
        if [[ ${#uwsm_opts[@]} -gt 0 ]]; then
            echo "Using uwsm options: ${uwsm_opts[*]}"
            uwsm app "${uwsm_opts[@]}" -- "${app_command[@]}"
        else
            uwsm app -- "${app_command[@]}"
        fi
    else
        echo "UWSM installed but not active, launching directly: ${app_command[*]}"
        "${app_command[@]}"
    fi
}

# Run the launcher
launch_with_uwsm "$@"
