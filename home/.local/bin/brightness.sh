#!/bin/bash

# ┏━━━┳━━┳━┓┏━┳━━━┳┓╋╋┏━━┳━┓┏━┓
# ┗┓┏┓┣┫┣┫┃┗┛┃┃┏━━┫┃╋╋┗┫┣┻┓┗┛┏┛
# ╋┃┃┃┃┃┃┃┏┓┏┓┃┗━━┫┃╋╋╋┃┃╋┗┓┏┛
# ╋┃┃┃┃┃┃┃┃┃┃┃┃┏━━┫┃╋┏┓┃┃╋┏┛┗┓
# ┏┛┗┛┣┫┣┫┃┃┃┃┃┃╋╋┃┗━┛┣┫┣┳┛┏┓┗┓
# ┗━━━┻━━┻┛┗┛┗┻┛╋╋┗━━━┻━━┻━┛┗━┛
# The program was created by DIMFLIX (Modified by K1rsN7)
# Github: https://github.com/DIMFLIX-OFFICIAL

SESSION_TYPE="$XDG_SESSION_TYPE"
DEFAULT_COLOR="#61afef"

get_backlight_device() {
    local devices=$(ls /sys/class/backlight/)
    if [ -z "$devices" ]; then
        echo "none"
    else
        local name_device=$(echo $devices | awk '{print $1}') 
        local status=$(cat /sys/class/backlight/$name_device/device/enabled)

        if [[ "$status" == "disabled" ]]; then
            echo "none"
        else
            echo $name_device
        fi
    fi
}

get_brightness() {
    brightnessctl -d "$1" | grep -o "(.*" | tr -d "()"
}

brightness_icon() {
    local value=$1
    local color="$2"
    
    case $value in
        9[0-9]%) icon="" ;;
        8[0-9]%) icon="" ;;
        7[0-9]%) icon="" ;;
        6[0-9]%) icon="" ;;
        5[1-9]%) icon="" ;;
        4[0-9]%) icon="" ;;
        3[0-9]%) icon="" ;;
        2[0-9]%) icon="" ;;
        1[0-9]%) icon="" ;;
        [1-9]%) icon="" ;;
        100%) icon="";;
        50%) icon="";;
        0%) icon="" ;;  
        *) icon="" ;;
    esac 

    if [[ "$SESSION_TYPE" == "wayland" ]]; then
        echo "<span color=\"$color\">$icon $value</span>"
    elif [[ "$SESSION_TYPE" == "x11" ]]; then
        echo "%{F$color}$icon $value%{F-}"
    fi
}

BRIGHTNESS_DEVICE=$(get_backlight_device)

if [ "$BRIGHTNESS_DEVICE" = "none" ]; then
    exit 1
fi

BRIGHTNESS_VALUE=$(get_brightness "$BRIGHTNESS_DEVICE")
status_mode=false
while [[ "$#" -gt 0 ]]; do
    case "$1" in
        --status)
        	status_mode=true
            shift
            ;;
        --color)
            DEFAULT_COLOR="$2"
            shift 2
            ;;
        --up)
            brightnessctl -d "$BRIGHTNESS_DEVICE" set +5%
            exit 0
            ;;
        --down)
            brightnessctl -d "$BRIGHTNESS_DEVICE" set 5%-
            exit 0
            ;;
        --max)
            brightnessctl -d "$BRIGHTNESS_DEVICE" set 100%
            exit 0
            ;;
        --min)
            brightnessctl -d "$BRIGHTNESS_DEVICE" set 0%
            exit 0
            ;;
        *)
            echo "Invalid argument. Use '--status [color]', '--color [color]', 'up', 'down', 'max', or 'min'."
            exit 1
            ;;
    esac
done

if [[ $status_mode == true ]]; then
    echo "$(brightness_icon $BRIGHTNESS_VALUE $DEFAULT_COLOR)"
    exit 0
fi
