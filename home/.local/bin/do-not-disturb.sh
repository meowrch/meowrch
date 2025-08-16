#!/usr/bin/env bash

# ┏━━━┳━━┳━┓┏━┳━━━┳┓╋╋┏━━┳━┓┏━┓
# ┗┓┏┓┣┫┣┫┃┗┛┃┃┏━━┫┃╋╋┗┫┣┻┓┗┛┏┛
# ╋┃┃┃┃┃┃┃┏┓┏┓┃┗━━┫┃╋╋╋┃┃╋┗┓┏┛
# ╋┃┃┃┃┃┃┃┃┃┃┃┃┏━━┫┃╋┏┓┃┃╋┏┛┗┓
# ┏┛┗┛┣┫┣┫┃┃┃┃┃┃╋╋┃┗━┛┣┫┣┳┛┏┓┗┓
# ┗━━━┻━━┻┛┗┛┗┻┛╋╋┗━━━┻━━┻━┛┗━┛
# The program was created by DIMFLIX
# Github: https://github.com/DIMFLIX

notify="notify-send"
tmp_disturb="/tmp/xmonad/donotdisturb"
log_file="/tmp/toggle_dnd.log"
SESSION_TYPE=$XDG_SESSION_TYPE
ENABLED_COLOR="#A3BE8C"
DISABLED_COLOR="#d35f5e"

[ ! -d "$tmp_disturb" ] && mkdir -p "$tmp_disturb"

# --------------------------------------------------------
#  Определяем клиентов
# --------------------------------------------------------
DUNST_CMD="dunstctl"

SWAYNC_CMD=""
SWAYNC_MODE=""
if command -v swayncctl &>/dev/null; then
    SWAYNC_CMD="swayncctl"
    SWAYNC_MODE="ctl"
elif command -v swaync-client &>/dev/null; then
    SWAYNC_CMD="swaync-client"
    SWAYNC_MODE="client"
fi

# --------------------------------------------------------
#  ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# --------------------------------------------------------
is_dunst_running() {
    pgrep -x dunst &>/dev/null
}

is_swaync_running() {
    pgrep -x swaync &>/dev/null
}

# --------------------------------------------------------
#  ЛОГИКА
# --------------------------------------------------------
toggle_notifications() {
    local final_state=""

    # --- DUNST ---
    if command -v "$DUNST_CMD" &>/dev/null && is_dunst_running; then
        if [ "$($DUNST_CMD is-paused)" == "true" ]; then
            $DUNST_CMD set-paused false
            final_state="false"
        else
            $DUNST_CMD set-paused true
            final_state="true"
        fi
    fi

    # --- SWAYNC ---
    if [ -n "$SWAYNC_CMD" ] && is_swaync_running; then
        if [ "$SWAYNC_MODE" == "ctl" ]; then
            # Старый swayncctl
            if [ "$($SWAYNC_CMD get-dnd)" == "true" ]; then
                $SWAYNC_CMD set-dnd false
                final_state="false"
            else
                $SWAYNC_CMD set-dnd true
                final_state="true"
            fi
        elif [ "$SWAYNC_MODE" == "client" ]; then
            # Новый swaync-client
            if [ "$($SWAYNC_CMD --get-dnd)" == "true" ]; then
                $SWAYNC_CMD --dnd-off >/dev/null
                final_state="false"
            else
                $SWAYNC_CMD --dnd-on >/dev/null
                final_state="true"
            fi
        fi
    fi

    # --- RESULT ---
    if [ "$final_state" == "true" ]; then
        $notify "Do Not Disturb: ON"
    elif [ "$final_state" == "false" ]; then
        $notify "Do Not Disturb: OFF"
    else
        $notify "⚠ No active notifiers"
    fi
}

get_status() {
    local dunst_status="false"
    local swaync_status="false"

    if command -v "$DUNST_CMD" &>/dev/null && is_dunst_running; then
        dunst_status=$($DUNST_CMD is-paused)
    fi
    if [ -n "$SWAYNC_CMD" ] && is_swaync_running; then
        if [ "$SWAYNC_MODE" == "ctl" ]; then
            swaync_status=$($SWAYNC_CMD get-dnd)
        else
            swaync_status=$($SWAYNC_CMD --get-dnd)
        fi
    fi

    if [[ "$dunst_status" == "true" || "$swaync_status" == "true" ]]; then
        local icon="󱏧 "
        local color=$DISABLED_COLOR
    else
        local icon="󱅫 "
        local color=$ENABLED_COLOR
    fi

    if [[ "$SESSION_TYPE" == "wayland" ]]; then
        echo "<span color=\"$color\">$icon</span>"
    elif [[ "$SESSION_TYPE" == "x11" ]]; then
        echo "%{F$color}$icon%{F-}"
    else
        echo "$icon"
    fi
}

# --------------------------------------------------------
#  АРГУМЕНТЫ
# --------------------------------------------------------
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --status) status=true ;;
        --enabled-color) ENABLED_COLOR="$2"; shift ;;
        --disabled-color) DISABLED_COLOR="$2"; shift ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
    shift
done

# --------------------------------------------------------
#  MAIN
# --------------------------------------------------------
if [[ "$status" == true ]]; then
    get_status | tee -a "$log_file"
else
    toggle_notifications
fi
