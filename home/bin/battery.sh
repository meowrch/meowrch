#!/bin/bash

# ┏━━━┳━━┳━┓┏━┳━━━┳┓╋╋┏━━┳━┓┏━┓
# ┗┓┏┓┣┫┣┫┃┗┛┃┃┏━━┫┃╋╋┗┫┣┻┓┗┛┏┛
# ╋┃┃┃┃┃┃┃┏┓┏┓┃┗━━┫┃╋╋╋┃┃╋┗┓┏┛
# ╋┃┃┃┃┃┃┃┃┃┃┃┃┏━━┫┃╋┏┓┃┃╋┏┛┗┓
# ┏┛┗┛┣┫┣┫┃┃┃┃┃┃╋╋┃┗━┛┣┫┣┳┛┏┓┗┓
# ┗━━━┻━━┻┛┗┛┗┻┛╋╋┗━━━┻━━┻━┛┗━┛
# The program was created by DIMFLIX


# Путь к файлу-флагу
FLAG_FILE="/tmp/battery_low.flag"

# Функция для проверки существования аккумулятора
has_battery() {
    local battery_path=$(upower -e | grep 'BAT')
    if [ -z "$battery_path" ]; then
        return 1
    else
        return 0
    fi
}

# Функция для получения процента заряда батареи
get_battery_charge() {
    upower -i $(upower -e | grep 'BAT') | grep percentage | awk '{print $2}' | sed s/%//
}

# Функция для проверки, идет ли зарядка
is_charging() {
    upower -i $(upower -e | grep 'BAT') | grep state | awk '{print $2}'
}

# Функция для вывода уведомления с оставшимся временем работы аккумулятора
notify_battery_time() {
    local remaining_time=$(upower -i $(upower -e | grep 'BAT') | grep --color=never -E "time to empty|time to full" | awk '{print $4, $5}')
    if [ -z "$remaining_time" ] || [[ "$remaining_time" == *"0"* ]]; then
        notify-send "Battery Status" "Remaining time: data is being calculated or unavailable."
    else
        notify-send "Battery Status" "Remaining time: $remaining_time"
    fi
}

# Проверяем, существует ли батарея
if ! has_battery; then
    exit 0
fi

# Уведомление с информацией о времени работы
if [ "$1" == "notify" ]; then
    notify_battery_time
    exit 0
fi

# Массив иконок зарядки
CHARGING_ICONS=("󰢟 " "󰢜 " "󰂆 " "󰂇 " "󰂈 " "󰢝 " "󰂉 " "󰢞 " "󰂊 " "󰂋 " "󰂅 ")

# Функция для вывода иконки в зависимости от уровня заряда
battery_icon() {
    local charge=$1
    local color="%{F#A0E8A2}"

    # Изменяем цвет на красный для уровней ниже 15%
    if [ "$charge" -lt 15 ]; then
        color="%{F#D35F5D}"
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

    echo -n "${color}${icon}%{F-}"
}

# Функция для вывода анимированной иконки зарядки
charging_icon() {
    local charge=$1
    local index=$(($charge / 10))
    local color="%{F#A0E8A2}"

    if [ "$index" -eq 10 ]; then
        icon="${CHARGING_ICONS[9]}" # Иконка для 100%
    else
        icon="${CHARGING_ICONS[$index]}"
    fi

    echo -n "${color}${icon}%{F-}"
}

# Получаем текущий заряд батареи и статус зарядки
BATTERY_CHARGE=$(get_battery_charge)
CHARGING_STATUS=$(is_charging)

# Если началась зарядка, удаляем флаг, чтобы сбросить предупреждение
if [ "$CHARGING_STATUS" == "charging" ] && [ -f "$FLAG_FILE" ]; then
    rm "$FLAG_FILE"
fi

# Выводим информацию о батарее
if [ "$CHARGING_STATUS" == "charging" ]; then
    echo "$(charging_icon $BATTERY_CHARGE)$BATTERY_CHARGE%"
elif [ "$CHARGING_STATUS" == "fully-charged" ]; then
    echo "%{F#A0E8A2}󰁹%{F-} 100%"
else
    echo "$(battery_icon $BATTERY_CHARGE)$BATTERY_CHARGE%"
fi

# Отправка уведомления при низком уровне заряда
LOW_BATTERY_THRESHOLD=15
if [ "$BATTERY_CHARGE" -le "$LOW_BATTERY_THRESHOLD" ]; then
    if [ ! -f "$FLAG_FILE" ] && [ "$CHARGING_STATUS" != "charging" ]; then
        notify-send "Low battery charge" "The battery charge level is $BATTERY_CHARGE%, connect the charger." -u critical
        touch "$FLAG_FILE"
    fi
elif [ "$BATTERY_CHARGE" -gt "$LOW_BATTERY_THRESHOLD" ]; then
    if [ -f "$FLAG_FILE" ]; then
        rm "$FLAG_FILE"
    fi
fi
