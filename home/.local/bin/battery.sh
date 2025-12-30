#!/bin/bash

# ┏━━━┳━━┳━┓┏━┳━━━┳┓╋╋┏━━┳━┓┏━┓
# ┗┓┏┓┣┫┣┫┃┗┛┃┃┏━━┫┃╋╋┗┫┣┻┓┗┛┏┛
# ╋┃┃┃┃┃┃┃┏┓┏┓┃┗━━┫┃╋╋╋┃┃╋┗┓┏┛
# ╋┃┃┃┃┃┃┃┃┃┃┃┃┏━━┫┃╋┏┓┃┃╋┏┛┗┓
# ┏┛┗┛┣┫┣┫┃┃┃┃┃┃╋╋┃┗━┛┣┫┣┳┛┏┓┗┓
# ┗━━━┻━━┻┛┗┛┗┻┛╋╋┗━━━┻━━┻━┛┗━┛
# The program was created by DIMFLIX
# Github: https://github.com/DIMFLIX

FLAG_DIR="/tmp/battery_flags"
BATTERY_THRESHOLDS=(15 10 5 3)
CHARGING_ICONS=("󰢟 " "󰢜 " "󰂆 " "󰂇 " "󰂈 " "󰢝 " "󰂉 " "󰢞 " "󰂊 " "󰂋 " "󰂅 ")
SESSION_TYPE="$XDG_SESSION_TYPE"
DISCHARGED_COLOR=""
CHARGED_COLOR=""

# Создаем директорию для флагов, если её нет
mkdir -p "$FLAG_DIR"

has_battery() {
    local battery_path=$(upower -e | grep 'BAT')
    [ -z "$battery_path" ] && return 1 || return 0
}

get_battery_charge() {
    upower -i $(upower -e | grep 'BAT') | grep percentage | awk '{print $2}' | sed s/%//
}

is_charging() {
    upower -i $(upower -e | grep 'BAT') | grep state | awk '{print $2}'
}

notify_battery_time() {
    local remaining_time=$(upower -i $(upower -e | grep 'BAT') | grep --color=never -E "time to empty|time to full" | awk '{print $4, $5}')
    if [ -z "$remaining_time" ] || [[ "$remaining_time" == *"0"* ]]; then
        notify-send "Battery Status" "Remaining time: data is being calculated or unavailable."
    else
        notify-send "Battery Status" "Remaining time: $remaining_time"
    fi
}

print_status() {
    local charge=$(get_battery_charge)
    local charging_status=$(is_charging)
    local icon=""
    local color=""
    local icon_only=false

    for arg in "$@"; do
        if [[ "$arg" == "--icon-only" ]]; then
            icon_only=true
        fi
    done

    if [ "$charging_status" == "charging" ]; then
        icon="${CHARGING_ICONS[9]}"
        color=$CHARGED_COLOR
    elif [ "$charging_status" == "fully-charged" ]; then
        icon="󰁹 "
        color=$CHARGED_COLOR
    else
        if [ "$charge" -le "15" ]; then
            color=$DISCHARGED_COLOR
        else
            color=$CHARGED_COLOR
        fi
        case $charge in
            100|9[0-9]) icon="󰁹 " ;;
            8[0-9]) icon="󰂂 " ;;
            7[0-9]) icon="󰂁 " ;;
            6[0-9]) icon="󰂀 " ;;
            5[0-9]) icon="󰁿 " ;;
            4[0-9]) icon="󰁾 " ;;
            3[0-9]) icon="󰁽 " ;;
            2[0-9]) icon="󰁼 " ;;
            1[5-9]) icon="󰁺 " ;;
            *) icon="󰂎 " ;;
        esac
    fi

    local output=""
    if $icon_only; then
        output="$icon"
    else
        output="${icon}${charge}%"
    fi

    if [[ -n "$color" ]]; then
        if [[ "$SESSION_TYPE" == "wayland" ]]; then
            echo "<span color=\"$color\">$output</span>"
        elif [[ "$SESSION_TYPE" == "x11" ]]; then
            echo "%{F$color}$output%{F-}"
        fi
    else
        echo "$output"
    fi
}

check_battery_notifications() {
    local battery_charge=$(get_battery_charge)
    local charging_status=$(is_charging)
    local lock_file="$FLAG_DIR/.battery.lock"
    
    # Если началась зарядка, удаляем все флаги
    if [ "$charging_status" == "charging" ]; then
        rm -f "$FLAG_DIR"/*.flag 2>/dev/null
        return
    fi
    
    # Проверяем каждый порог
    for threshold in "${BATTERY_THRESHOLDS[@]}"; do
        local flag_file="$FLAG_DIR/battery_${threshold}.flag"
        
        if [ "$battery_charge" -le "$threshold" ]; then
            # Используем flock для атомарной проверки и создания флага
            (
                flock -n 200 || exit 1
                
                # Повторная проверка внутри lock
                if [ ! -f "$flag_file" ]; then
                    local urgency="critical"
                    local timeout=10000
                    
                    # Для 5% делаем чтобы уведомление не закрывалось
                    if [ "$threshold" -eq 5 ]; then
                        timeout=0 
                    fi

                    touch "$flag_file"

                    # Для 3% делаем чтобы ноутбук уходил в сон
                    if [ "$threshold" -eq 3 ]; then
                        sh ${XDG_BIN_HOME:-$HOME/bin}/screen-lock.sh --suspend
                        exit 0
                    fi 
                    
                    notify-send "Low battery charge" \
                        "The battery charge level is $battery_charge%, connect the charger." \
                        -u "$urgency" \
                        -t "$timeout"
                fi
            ) 200>"$lock_file"
        else
            # Если заряд выше порога, удаляем соответствующий флаг
            rm -f "$flag_file" 2>/dev/null
        fi
    done
}

main() {
    local status_mode=false
    local notify_mode=false
    local icon_only=false
    
    while [[ "$#" -gt 0 ]]; do
        case "$1" in
            --status)
                status_mode=true
                shift
                ;;
            --notify)
                notify_mode=true
                shift
                ;;
            --charged-color)
                CHARGED_COLOR="$2"
                shift 2
                ;;
            --discharged-color)
                DISCHARGED_COLOR="$2"
                shift 2
                ;;
            --icon-only)
                icon_only=true
                shift
                ;;
            *)
                echo "Invalid option: $1"
                exit 1
                ;;
        esac
    done

    if [[ $status_mode == true ]]; then
        if $icon_only; then
            print_status --icon-only
        else
            print_status
        fi
    fi

    if [[ $notify_mode == true ]]; then
        notify_battery_time
    fi

    # Проверяем уведомления о низком заряде
    check_battery_notifications
}

if has_battery; then
    main "$@"
else
    status_mode=false
    icon_only=false

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --status)
                status_mode=true
                shift
                ;;
            --icon-only)
                icon_only=true
                shift
                ;;
            --charged-color)
                CHARGED_COLOR="$2"
                shift 2
                ;;
            --discharged-color)
                DISCHARGED_COLOR="$2"
                shift 2
                ;;
            *)
                shift
                ;;
        esac
    done

    if [[ $status_mode == true ]]; then
        output="󱟩"
        color="$DISCHARGED_COLOR"
        
        if ! $icon_only; then
            if [[ -n "$color" ]]; then
                case "$SESSION_TYPE" in
                    "wayland") echo "<span color='$color'>$output</span>" ;;
                    "x11")     echo "%{F$color}$output%{F-}" ;;
                    *)         echo "$output" ;;
                esac
            else
                echo "$output"
            fi
        else
            echo "$output"
        fi
    fi
fi
