#!/bin/bash

# ┏━━━┳━━┳━┓┏━┳━━━┳┓╋╋┏━━┳━┓┏━┓
# ┗┓┏┓┣┫┣┫┃┗┛┃┃┏━━┫┃╋╋┗┫┣┻┓┗┛┏┛
# ╋┃┃┃┃┃┃┃┏┓┏┓┃┗━━┫┃╋╋╋┃┃╋┗┓┏┛
# ╋┃┃┃┃┃┃┃┃┃┃┃┃┏━━┫┃╋┏┓┃┃╋┏┛┗┓
# ┏┛┗┛┣┫┣┫┃┃┃┃┃┃╋╋┃┗━┛┣┫┣┳┛┏┓┗┓
# ┗━━━┻━━┻┛┗┛┗┻┛╋╋┗━━━┻━━┻━┛┗━┛
# The program was created by DIMFLIX
# Github: https://github.com/DIMFLIX

# ---------- Configuration ----------
declare -A WM_BARS
WM_BARS["hyprland"]="mewline waybar"
WM_BARS["bspwm"]="polybar"

STATE_DIR="$HOME/.cache/meowrch"
mkdir -p "$STATE_DIR"

# Detect window manager from XDG_SESSION_DESKTOP
XDG_DESKTOP="${XDG_SESSION_DESKTOP,,}"
case "$XDG_DESKTOP" in
    hyprland|hyprland*) WM="hyprland" ;;
    bspwm|bspwm*)       WM="bspwm" ;;
    *)
        echo "Unsupported window manager: $XDG_DESKTOP"
        exit 1
        ;;
esac

FLAG_FILE="$STATE_DIR/current_bar_${WM}"

# Default action if no arguments
ACTION="toggle"
case "$1" in
    "--start")  ACTION="start"  ;;
    "--stop")   ACTION="stop"   ;;
    "--toggle") ACTION="toggle" ;;
    "--next")   ACTION="next"   ;;
    "")
        # no argument = toggle (old behaviour)
        ACTION="toggle"
        ;;
    *)
        echo "Unknown argument: $1"
        echo "Usage: $0 [--start|--stop|--toggle|--next]"
        exit 1
        ;;
esac

# ---------- Helper functions ----------
is_bar_installed() {
    command -v "$1" >/dev/null 2>&1
}

launch_bar() {
    local bar_name="$1"
    if [[ "$WM" == "hyprland" ]]; then
        # Use uwsm-launcher.sh for both mewline and waybar
        nohup "${XDG_BIN_HOME:-$HOME/bin}/uwsm-launcher.sh" -t service -s s "$bar_name" >/dev/null 2>&1 &
        disown
    elif [[ "$WM" == "bspwm" && "$bar_name" == "polybar" ]]; then
        "$HOME/.config/polybar/launch.sh" &
    fi
}

# Wait up to 2 seconds for the bar process to appear
ensure_bar_running() {
    local bar_name="$1"
    if pgrep -x "$bar_name" >/dev/null; then
        return 0
    fi
    launch_bar "$bar_name"
    sleep 2
    pgrep -x "$bar_name" >/dev/null
}

stop_bar() {
    local bar_name="$1"
    if pgrep -x "$bar_name" >/dev/null; then
        pkill -x "$bar_name"
        # bspwm specific cleanup
        if [[ "$WM" == "bspwm" && "$bar_name" == "polybar" ]]; then
            bspc config -m focused top_padding 0 2>/dev/null
        fi
    fi
}

# Get the next bar in the circular list for the current WM
get_next_bar() {
    local current="$1"
    local -a bars=(${WM_BARS[$WM]})
    local len=${#bars[@]}
    if [[ $len -eq 0 ]]; then
        echo ""
        return 1
    fi
    local idx=-1
    for i in "${!bars[@]}"; do
        if [[ "${bars[$i]}" == "$current" ]]; then
            idx=$i
            break
        fi
    done
    if [[ $idx -eq -1 ]]; then
        echo "${bars[0]}"
    else
        echo "${bars[$(( (idx + 1) % len ))]}"
    fi
}

# Read current bar from flag file, or set to first available if missing
get_current_bar() {
    if [[ -f "$FLAG_FILE" ]]; then
        cat "$FLAG_FILE"
    else
        local first_bar=$(echo ${WM_BARS[$WM]} | awk '{print $1}')
        echo "$first_bar" > "$FLAG_FILE"
        echo "$first_bar"
    fi
}

# ---------- Core actions ----------
case "$ACTION" in
    "start")
        # Startup: try to run the current bar; if it fails, try others in order.
        current_bar=$(get_current_bar)
        attempted=()
        bar="$current_bar"
        success=false
        while true; do
            if is_bar_installed "$bar"; then
                if ensure_bar_running "$bar"; then
                    # Update flag if we changed bar
                    if [[ "$bar" != "$current_bar" ]]; then
                        echo "$bar" > "$FLAG_FILE"
                    fi
                    # bspwm padding
                    if [[ "$WM" == "bspwm" && "$bar" == "polybar" ]]; then
                        bspc config -m focused top_padding 31 2>/dev/null
                    fi
                    success=true
                    break
                fi
            fi
            attempted+=("$bar")
            bar=$(get_next_bar "$bar")
            # Stop if we cycled through all bars
            if [[ "$bar" == "$current_bar" ]] || [[ ${#attempted[@]} -ge ${#WM_BARS[$WM]} ]]; then
                break
            fi
        done
        if [[ "$success" == false ]]; then
            echo "Error: no working bar found." >&2
            exit 1
        fi
        ;;

    "stop")
        # Stop only the current bar (if running)
        current_bar=$(get_current_bar)
        stop_bar "$current_bar"
        ;;

    "toggle")
        # If current bar is running, stop it; otherwise start it (no fallback)
        current_bar=$(get_current_bar)
        if pgrep -x "$current_bar" >/dev/null; then
            stop_bar "$current_bar"
        else
            if ! is_bar_installed "$current_bar"; then
                echo "Error: bar '$current_bar' is not installed." >&2
                exit 1
            fi
            if ! ensure_bar_running "$current_bar"; then
                echo "Error: failed to start '$current_bar'." >&2
                exit 1
            fi
            if [[ "$WM" == "bspwm" && "$current_bar" == "polybar" ]]; then
                bspc config -m focused top_padding 31 2>/dev/null
            fi
        fi
        ;;

    "next")
        # Switch to the next bar in the list, stop current, start next (no fallback)
        current_bar=$(get_current_bar)
        next_bar=$(get_next_bar "$current_bar")
        echo "Switching from $current_bar to $next_bar"
        stop_bar "$current_bar"
        # Update flag immediately
        echo "$next_bar" > "$FLAG_FILE"
        if ! is_bar_installed "$next_bar"; then
            echo "Error: next bar '$next_bar' is not installed." >&2
            exit 1
        fi
        if ! ensure_bar_running "$next_bar"; then
            echo "Error: failed to start '$next_bar'." >&2
            exit 1
        fi
        if [[ "$WM" == "bspwm" && "$next_bar" == "polybar" ]]; then
            bspc config -m focused top_padding 31 2>/dev/null
        fi
        ;;
esac

exit 0
