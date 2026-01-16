#!/usr/bin/env bash

# ┏━━━┳━━┳━┓┏━┳━━━┳┓╋╋┏━━┳━┓┏━┓
# ┗┓┏┓┣┫┣┫┃┗┛┃┃┏━━┫┃╋╋┗┫┣┻┓┗┛┏┛
# ╋┃┃┃┃┃┃┃┏┓┏┓┃┗━━┫┃╋╋╋┃┃╋┗┓┏┛
# ╋┃┃┃┃┃┃┃┃┃┃┃┃┏━━┫┃╋┏┓┃┃╋┏┛┗┓
# ┏┛┗┛┣┫┣┫┃┃┃┃┃┃╋╋┃┗━┛┣┫┣┳┛┏┓┗┓
# ┗━━━┻━━┻┛┗┛┗┻┛╋╋┗━━━┻━━┻━┛┗━┛
# Arch Linux Update Checker with Cache
# Enhanced version for bspwm status bar

SESSION_TYPE=$XDG_SESSION_TYPE
DEFAULT_UPDATED_COLOR="#a6e3a1"
DEFAULT_UNUPDATED_COLOR="#fab387"
DEFAULT_TERMINAL="kitty"

# Cache settings
CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/system-update"
CACHE_FILE="$CACHE_DIR/updates.cache"
CACHE_DURATION=300  # 5 minutes in seconds

show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --status              Show the update status."
    echo "  --updated-color COLOR Set the color for zero updates (default: $DEFAULT_UPDATED_COLOR)."
    echo "  --unupdated-color COLOR Set the color for non-zero updates (default: $DEFAULT_UNUPDATED_COLOR)."
    echo "  --terminal TERMINAL   Specify the terminal to run (default: $DEFAULT_TERMINAL)."
    echo "  --force               Force update check, ignore cache."
    echo "  --help                Show this message."
    echo ""
    echo "Example:"
    echo "  $0 --status"
    echo "  $0 --status --force"
    echo "  $0 --terminal kitty"
}

# Create cache directory if not exists
ensure_cache_dir() {
    mkdir -p "$CACHE_DIR"
}

# Check if cache is valid
is_cache_valid() {
    if [ ! -f "$CACHE_FILE" ]; then
        return 1
    fi
    
    local current_time=$(date +%s)
    local cache_time=$(stat -c %Y "$CACHE_FILE" 2>/dev/null || stat -f %m "$CACHE_FILE" 2>/dev/null)
    
    if [ -z "$cache_time" ]; then
        return 1
    fi
    
    local age=$((current_time - cache_time))
    
    if [ "$age" -lt "$CACHE_DURATION" ]; then
        return 0
    fi
    return 1
}

# Read cached value
read_cache() {
    cat "$CACHE_FILE" 2>/dev/null || echo "0"
}

# Write to cache
write_cache() {
    echo "$1" > "$CACHE_FILE"
}

# Invalidate cache
invalidate_cache() {
    rm -f "$CACHE_FILE"
}

# Check for Arch Linux
check_release() {
    if [ ! -f /etc/arch-release ]; then
        return 1
    fi
    return 0
}

# Get AUR helper
get_aurhlpr() {
    if command -v yay &>/dev/null; then
        echo "yay"
    elif command -v paru &>/dev/null; then
        echo "paru"
    else
        echo ""
    fi
}

# Check official updates
check_official_updates() {
    local count=0
    if command -v checkupdates &>/dev/null; then
        count=$(checkupdates 2>/dev/null | wc -l)
    fi
    echo "$count"
}

# Check AUR updates
check_aur_updates() {
    local aur_helper
    aur_helper=$(get_aurhlpr)
    
    if [ -z "$aur_helper" ]; then
        echo 0
        return
    fi
    
    local count=0
    if command -v "$aur_helper" &>/dev/null; then
        count=$($aur_helper -Qum 2>/dev/null | wc -l)
    fi
    echo "$count"
}

# Check Flatpak updates
check_flatpak_updates() {
    local count=0
    if command -v flatpak &>/dev/null; then
        count=$(flatpak remote-ls --updates 2>/dev/null | wc -l)
    fi
    echo "$count"
}

# Calculate total updates
calculate_updates() {
    local force_check=${1:-0}
    
    ensure_cache_dir
    
    # Use cache if valid and not forced
    if [ "$force_check" -eq 0 ] && is_cache_valid; then
        read_cache
        return
    fi
    
    # Perform actual check
    local ofc aur fpk total
    ofc=$(check_official_updates)
    aur=$(check_aur_updates)
    fpk=$(check_flatpak_updates)
    total=$((ofc + aur + fpk))
    
    # Write to cache
    write_cache "$total"
    
    echo "$total"
}

# Print status for statusbar
print_status() {
    local updates color force_check
    force_check=${3:-0}
    
    updates=$(calculate_updates "$force_check")
    color=${2:-$DEFAULT_UNUPDATED_COLOR}
    
    if [ "$updates" -eq 0 ]; then
        updates=""
        color=${1:-$DEFAULT_UPDATED_COLOR}
    fi
    
    if [ "$SESSION_TYPE" == "wayland" ]; then
        echo "<span color=\"$color\">󰮯 $updates </span>"
    elif [ "$SESSION_TYPE" == "x11" ]; then
        echo "%{F$color}󰮯 $updates %{F-}"
    fi
}

# Trigger upgrade in terminal
trigger_upgrade() {
    local aurhlpr
    aurhlpr=$(get_aurhlpr)
    
    if [ -z "$aurhlpr" ]; then
        aurhlpr="pacman"
    fi
    
    local terminal=${1:-$DEFAULT_TERMINAL}
    
    local command='sudo '"$aurhlpr"' -Syu && flatpak update -y; read -n 1 -p "Press any key to continue..."'
    
    case $terminal in
        alacritty)
            alacritty -e bash -c "$command"
            ;;
        kitty)
            kitty -e bash -c "$command"
            ;;
        gnome-terminal)
            gnome-terminal -- bash -c "$command; exec bash"
            ;;
        xterm)
            xterm -e bash -c "$command"
            ;;
        wezterm)
            wezterm start -- bash -c "$command"
            ;;
        *)
            echo "Unsupported terminal: $terminal. Please run the command manually."
            exit 1
            ;;
    esac
    
    # Invalidate cache after update
    invalidate_cache
}

main() {
    check_release || exit 0
    
    local updated_color="$DEFAULT_UPDATED_COLOR"
    local unupdated_color="$DEFAULT_UNUPDATED_COLOR"
    local terminal="$DEFAULT_TERMINAL"
    local status=0
    local force_check=0
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --status)
                status=1
                ;;
            --updated-color)
                shift
                updated_color="$1"
                ;;
            --unupdated-color)
                shift
                unupdated_color="$1"
                ;;
            --terminal)
                shift
                terminal="$1"
                ;;
            --force)
                force_check=1
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                echo "Unknown argument: $1"
                show_help
                exit 1
                ;;
        esac
        shift
    done
    
    if [ "$status" -eq 1 ]; then
        print_status "$updated_color" "$unupdated_color" "$force_check"
    else
        trigger_upgrade "$terminal"
    fi
}

main "$@"
