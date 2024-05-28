#!/usr/bin/env bash

notify="notify-send"
tmp_disturb="/tmp/xmonad/donotdisturb"

if [ ! -d $tmp_disturb ]; then
        mkdir -p $tmp_disturb
fi

log_file="/tmp/toggle_dnd.log"

# Функция для переключения статуса уведомлений
toggle_notifications() {
    if [ "$(dunstctl is-paused)" == "true" ]; then
        dunstctl set-paused false
        $notify "Dunst: Active"
    else
    	dunstctl set-paused true
    fi
}

# Функция для получения текущего статуса уведомлений
get_status() {
    if [ "$(dunstctl is-paused)" == "true" ]; then
        echo "%{F#d35f5e}󱏧" # Иконка для выключенного состояния
    else
        echo "%{F#A3BE8C}󱅫" # Иконка для включенного состояния
    fi
}

# Проверка аргументов
case "$1" in
    status)
        get_status | tee -a $log_file
        ;;
    *)
        toggle_notifications
        ;;
esac
