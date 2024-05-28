#!/bin/bash

# ┏━━━┳━━┳━┓┏━┳━━━┳┓╋╋┏━━┳━┓┏━┓
# ┗┓┏┓┣┫┣┫┃┗┛┃┃┏━━┫┃╋╋┗┫┣┻┓┗┛┏┛
# ╋┃┃┃┃┃┃┃┏┓┏┓┃┗━━┫┃╋╋╋┃┃╋┗┓┏┛
# ╋┃┃┃┃┃┃┃┃┃┃┃┃┏━━┫┃╋┏┓┃┃╋┏┛┗┓
# ┏┛┗┛┣┫┣┫┃┃┃┃┃┃╋╋┃┗━┛┣┫┣┳┛┏┓┗┓
# ┗━━━┻━━┻┛┗┛┗┻┛╋╋┗━━━┻━━┻━┛┗━┛
# The program was created by DIMFLIX


# Функция для определения доступного устройства управления яркостью
get_backlight_device() {
    local devices=$(ls /sys/class/backlight/)
    if [ -z "$devices" ]; then
        echo "none"
    else
        local name_device=$(echo $devices | awk '{print $1}') # Выбирем первй монитор с регулировкой яркости
        local status=$(cat /sys/class/backlight/$name_device/device/enabled) # Получим статус экрана с регулировкой яркости

        # Проверка на включение экрана с регулировкой яркости
        if [[ "$status" == "disabled" ]]; then
            echo "none"
        else
            echo $name_device
        fi
    fi 
}


# Функция для получения текущей яркости
get_brightness() {
    brightnessctl -d "$1" | grep -o "(.*" | tr -d "()"
}

BRIGHTNESS_DEVICE=$(get_backlight_device)
BRIGHTNESS_ICON='%{F#61afef} %{F-}'

if [ "$BRIGHTNESS_DEVICE" = "none" ]; then
    exit 1
fi

BRIGHTNESS_VALUE=$(get_brightness "$BRIGHTNESS_DEVICE")

case "$1" in
    up)
        brightnessctl -d "$BRIGHTNESS_DEVICE" set +5%
        ;;
    down)
        brightnessctl -d "$BRIGHTNESS_DEVICE" set 5%-
        ;;
    max)
        brightnessctl -d "$BRIGHTNESS_DEVICE" set 100%
        ;;
    min)
        brightnessctl -d "$BRIGHTNESS_DEVICE" set 1%
        ;;
    status)
        echo "$BRIGHTNESS_ICON $BRIGHTNESS_VALUE"
        ;;
    *)
        echo "Invalid argument. Use 'up', 'down', 'max', 'min', or 'status'."
        ;;
esac
