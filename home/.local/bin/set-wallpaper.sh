#!/usr/bin/env bash

# ┏━━━┳━━┳━┓┏━┳━━━┳┓╋╋┏━━┳━┓┏━┓
# ┗┓┏┓┣┫┣┫┃┗┛┃┃┏━━┫┃╋╋┗┫┣┻┓┗┛┏┛
# ╋┃┃┃┃┃┃┃┏┓┏┓┃┗━━┫┃╋╋╋┃┃╋┗┓┏┛
# ╋┃┃┃┃┃┃┃┃┃┃┃┃┏━━┫┃╋┏┓┃┃╋┏┛┗┓
# ┏┛┗┛┣┫┣┫┃┃┃┃┃┃╋╋┃┗━┛┣┫┣┳┛┏┓┗┓
# ┗━━━┻━━┻┛┗┛┗┻┛╋╋┗━━━┻━━┻━┛┗━┛
# The program was created by DIMFLIX
# Github: https://github.com/DIMFLIX

DATA_HOME="${XDG_DATA_HOME:-$HOME/.local/share}"
WALLPAPERS_DIR="${DATA_HOME}/wallpapers"
CURRENT_WALL_LINK="$WALLPAPERS_DIR/.current.wall"
SESSION_TYPE=${XDG_SESSION_TYPE:-unknown}
# Path to the dynamic theme state file
DYNAMIC_STATE_FILE="$HOME/.local/state/meowrch/dynamic_theme"

mkdir -p "$WALLPAPERS_DIR" || {
    echo "Failed to create wallpapers directory: $WALLPAPERS_DIR"
    exit 1
}

update_wallpaper_link() {
    local target_wallpaper
    target_wallpaper=$(realpath "$1") || return 1
    
    [[ -L "$CURRENT_WALL_LINK" ]] && rm "$CURRENT_WALL_LINK"

    ln -sfn "$target_wallpaper" "$CURRENT_WALL_LINK" || {
        echo "Failed to create symlink"
        return 1
    }
}

pawlette_dynamic_theme_hook() {
    local wallpaper="$1"

    if [[ -f "$DYNAMIC_STATE_FILE" ]]; then
        state=$(cat "$DYNAMIC_STATE_FILE")
        if [[ "$state" == "1" ]]; then
            # If dynamic themes are enabled, -
            # force Pawlette to rebuild itself to match the new wallpaper
            pawlette apply image "$wallpaper"
        fi
    fi
}

get_refresh_rate() {
    local default_fps=60
    [[ "$SESSION_TYPE" != "wayland" ]] && echo $default_fps && return
    
    if command -v wlr-randr >/dev/null; then
        wlr-randr --json 2>/dev/null | jq -r '.[].modes[] | select(.current == true) | .refresh | round' | sort -nr | head -1
    else
        echo $default_fps
    fi
}

get_cursor_pos() {
    [[ "$SESSION_TYPE" != "wayland" ]] && echo "0,0" && return
    
    if command -v hyprctl >/dev/null; then
        hyprctl cursorpos 2>/dev/null | tr -d ' ' | tr '\n' ',' | sed 's/,$//'
    else
        echo "0,0"
    fi
}

apply_awww() {
    command -v awww >/dev/null || { echo "Install awww for Wayland" >&2; exit 1; }

    # Waiting for the daemon to be ready (up to 6 seconds)
    local max_attempts=20
    local attempt=0

    while [[ $attempt -lt $max_attempts ]]; do
        if awww query >/dev/null 2>&1; then
            break
        fi
        
        # If the daemon isn't running, let's try starting it manually
        if ! pgrep -f "awww-daemon" >/dev/null; then
            echo "awww-daemon not running, starting it..." >&2
            sh ${XDG_BIN_HOME:-$HOME/bin}/uwsm-launcher.sh -t service -s s awww-daemon
        fi

        sleep 0.3
        attempt=$((attempt+1))
    done

    if [[ $attempt -eq $max_attempts ]]; then
        echo "ERROR: awww daemon not available after $max_attempts attempts" >&2
        exit 1
    fi

    local refresh_rate=$(get_refresh_rate)
    local cursor_pos=$(get_cursor_pos)
    
    if awww img "$1" \
        --transition-bezier .43,1.19,1,.4 \
        --transition-type grow \
        --transition-duration 0.4 \
        --transition-fps "$refresh_rate" \
        --invert-y \
        --transition-pos "$cursor_pos"
    then
        update_wallpaper_link "$1"
        pawlette_dynamic_theme_hook "$1"
    fi
}

apply_feh() {
    command -v feh >/dev/null || { echo "Install feh for X11"; exit 1; }
    
    if feh --no-fehbg --bg-fill "$1"; then
        update_wallpaper_link "$1"
        pawlette_dynamic_theme_hook "$1"
    fi
}

apply_current_wallpaper() {
    local target_wall=""

    if [[ -L "$CURRENT_WALL_LINK" ]]; then
        target_wall=$(readlink -f "$CURRENT_WALL_LINK")
        
        if [[ ! -f "$target_wall" ]]; then
            target_wall=""
        fi
    fi

    if [[ -z "$target_wall" ]]; then
        echo "Current wallpaper link missing or broken. Selecting random..."
        
        target_wall=$(find "$WALLPAPERS_DIR" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" \) 2>/dev/null | shuf -n 1)
        
        if [[ -z "$target_wall" ]]; then
            echo "No wallpapers found in $WALLPAPERS_DIR"
            exit 1
        fi
    fi
    
    case "$SESSION_TYPE" in
        "wayland") apply_awww "$target_wall" ;;
        "x11")     apply_feh "$target_wall" ;;
        *)
            command -v awww >/dev/null && apply_awww "$target_wall"
            command -v feh >/dev/null && apply_feh "$target_wall"
            ;;
    esac
}

if [[ "$1" == "--current" ]]; then
    apply_current_wallpaper
    exit $?
else
    [[ -z "$1" ]] && { echo "No wallpaper specified"; exit 1; }
    [[ ! -f "$1" ]] && { echo "File not found: $1"; exit 1; }
fi

case "$SESSION_TYPE" in
    "wayland") apply_awww "$1" ;;
    "x11")     apply_feh "$1" ;;
    *)
        echo "Unknown session type: $SESSION_TYPE"
        echo "Trying fallback methods..."
        command -v awww >/dev/null && apply_awww "$1"
        command -v feh >/dev/null && apply_feh "$1"
        exit 1
        ;;
esac
