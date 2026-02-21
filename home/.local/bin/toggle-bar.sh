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
declare -A BAR_CMD
declare -A BAR_PROCESS

# hyprland
BAR_CMD["mewline"]="${XDG_BIN_HOME:-$HOME/bin}/uwsm-launcher.sh -t service -s s mewline"
BAR_PROCESS["mewline"]="mewline"

BAR_CMD["waybar"]="${XDG_BIN_HOME:-$HOME/bin}/uwsm-launcher.sh -t service -s s waybar"
BAR_PROCESS["waybar"]="waybar"

# bspwm
BAR_CMD["polybar"]="$HOME/.config/polybar/launch.sh"
BAR_PROCESS["polybar"]="polybar"

# Add new bars in the same way:
# BAR_CMD["mybar"]="$HOME/.config/mybar/start.sh"
# BAR_PROCESS["mybar"]="mybar"

# Список доступных баров для каждого оконного менеджера
declare -A WM_BARS
WM_BARS["hyprland"]="mewline waybar"
WM_BARS["bspwm"]="polybar"

# ---------- Initial setup ----------
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

# ---------- Argument parsing ----------
ACTION="toggle"
case "$1" in
    "--start")  ACTION="start"  ;;
    "--stop")   ACTION="stop"   ;;
    "--toggle") ACTION="toggle" ;;
    "--next")   ACTION="next"   ;;
    "")
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
    local bar_name="$1"
    local cmd="${BAR_CMD[$bar_name]}"
    [[ -z "$cmd" ]] && return 1

    # Extract the first token (executable file)
    local exe
    exe=$(echo "$cmd" | awk '{print $1}')

    if [[ "$exe" == /* ]]; then
        # Absolute path — check that the file exists and execute
        [[ -x "$exe" ]]
    else
        # Relative name — search in PATH
        command -v "$exe" >/dev/null 2>&1
    fi
}

launch_bar() {
    local bar_name="$1"
    local cmd="${BAR_CMD[$bar_name]}"
    if [[ -z "$cmd" ]]; then
        echo "Error: no command defined for bar '$bar_name'" >&2
        exit 1
    fi

    # Run the command in the background, detach from the terminal
    nohup sh -c "$cmd" >/dev/null 2>&1 &
    disown
}

# Please wait up to 2 seconds for the bar process to appear.
ensure_bar_running() {
    local bar_name="$1"
    local process_name="${BAR_PROCESS[$bar_name]:-$bar_name}"

    if pgrep -x "$process_name" >/dev/null; then
        return 0
    fi

    launch_bar "$bar_name"
    sleep 2
    pgrep -x "$process_name" >/dev/null
}

stop_bar() {
    local bar_name="$1"
    local process_name="${BAR_PROCESS[$bar_name]:-$bar_name}"

    if pgrep -x "$process_name" >/dev/null; then
        pkill -x "$process_name"

        # Specific cleanup for bspwm (polybar)
        if [[ "$WM" == "bspwm" && "$bar_name" == "polybar" ]]; then
            bspc config -m focused top_padding 0 2>/dev/null
        fi
    fi
}

# Get the next bar in the cyclic list for the current WM
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

# Read the current bar from the status file; if it's not there, pick the first one available.
get_current_bar() {
    if [[ -f "$FLAG_FILE" ]]; then
        cat "$FLAG_FILE"
    else
        local first_bar
        first_bar=$(echo "${WM_BARS[$WM]}" | awk '{print $1}')
        echo "$first_bar" > "$FLAG_FILE"
        echo "$first_bar"
    fi
}

# ---------- Core actions ----------
case "$ACTION" in
    "start")
        current_bar=$(get_current_bar)

        if ! is_bar_installed "$current_bar"; then
            echo "Error: bar '$current_bar' is not installed or command not found." >&2
            exit 1
        fi

        launch_bar "$current_bar"

        if [[ "$WM" == "bspwm" && "$current_bar" == "polybar" ]]; then
            bspc config -m focused top_padding 31 2>/dev/null
        fi
        ;;

    "stop")
        current_bar=$(get_current_bar)
        stop_bar "$current_bar"
        ;;

    "toggle")
        current_bar=$(get_current_bar)
        process_name="${BAR_PROCESS[$current_bar]:-$current_bar}"

        if pgrep -x "$process_name" >/dev/null; then
            stop_bar "$current_bar"
        else
            if ! is_bar_installed "$current_bar"; then
                echo "Error: bar '$current_bar' is not installed or command not found." >&2
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
        current_bar=$(get_current_bar)
        next_bar=$(get_next_bar "$current_bar")
        echo "Switching from $current_bar to $next_bar"

        stop_bar "$current_bar"
        echo "$next_bar" > "$FLAG_FILE"

        if ! is_bar_installed "$next_bar"; then
            echo "Error: next bar '$next_bar' is not installed or command not found." >&2
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