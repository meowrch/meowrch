#!/bin/bash

# ┏━━━┳━━┳━┓┏━┳━━━┳┓╋╋┏━━┳━┓┏━┓
# ┗┓┏┓┣┫┣┫┃┗┛┃┃┏━━┫┃╋╋┗┫┣┻┓┗┛┏┛
# ╋┃┃┃┃┃┃┃┏┓┏┓┃┗━━┫┃╋╋╋┃┃╋┗┓┏┛
# ╋┃┃┃┃┃┃┃┃┃┃┃┃┏━━┫┃╋┏┓┃┃╋┏┛┗┓
# ┏┛┗┛┣┫┣┫┃┃┃┃┃┃╋╋┃┗━┛┣┫┣┳┛┏┓┗┓
# ┗━━━┻━━┻┛┗┛┗┻┛╋╋┗━━━┻━━┻━┛┗━┛
# The program was created by DIMFLIX
# Github: https://github.com/DIMFLIX-OFFICIAL


SESSION_TYPE="$XDG_SESSION_TYPE"
ENABLED_COLOR="#A3BE8C"
DISABLED_COLOR="#D35F5E"
SIGNAL_ICONS=("󰤟 " "󰤢 " "󰤥 " "󰤨 ")
SECURED_SIGNAL_ICONS=("󰤡 " "󰤤 " "󰤧 " "󰤪 ")
WIFI_CONNECTED_ICON=" "
ETHERNET_CONNECTED_ICON=" "

get_status() {
    if nmcli -t -f TYPE,STATE device status | grep 'ethernet:connected' > /dev/null; then
        local status_icon="󰈀"
        local status_color=$ENABLED_COLOR
    elif nmcli -t -f TYPE,STATE device status | grep 'wifi:connected' > /dev/null; then
        local wifi_info=$(nmcli --terse --fields "IN-USE,SIGNAL,SECURITY,SSID" device wifi list --rescan no | grep '\*')
        if [ -n "$wifi_info" ]; then
            IFS=: read -r in_use signal security ssid <<< "$wifi_info"
            local signal_icon="${SIGNAL_ICONS[3]}"
            local signal_level=$((signal / 25))
            if [[ "$signal_level" -lt "${#SIGNAL_ICONS[@]}" ]]; then
                signal_icon="${SIGNAL_ICONS[$signal_level]}"
            fi
            if [[ "$security" =~ WPA || "$security" =~ WEP ]]; then
                signal_icon="${SECURED_SIGNAL_ICONS[$signal_level]}"
            fi
            status_icon="$signal_icon"
            local status_color=$ENABLED_COLOR
        else
            status_icon=" "
            local status_color=$DISABLED_COLOR
        fi
    else
        local status_icon=" "
        local status_color=$DISABLED_COLOR
    fi

    if [[ "$SESSION_TYPE" == "wayland" ]]; then
        echo "<span color=\"$status_color\">$status_icon</span>"
    elif [[ "$SESSION_TYPE" == "x11" ]]; then
        echo "%{F$status_color}$status_icon%{F-}"
    fi
}

manage_wifi() {
    nmcli --terse --fields "IN-USE,SIGNAL,SECURITY,SSID" device wifi list > /tmp/wifi_list.txt

    local ssids=()
    local formatted_ssids=()
    local active_ssid=""

    while IFS=: read -r in_use signal security ssid; do
        if [ -z "$ssid" ]; then continue; fi # Пропускаем сети без SSID

        local signal_icon="${SIGNAL_ICONS[3]}"
        local signal_level=$((signal / 25))
        if [[ "$signal_level" -lt "${#SIGNAL_ICONS[@]}" ]]; then
            signal_icon="${SIGNAL_ICONS[$signal_level]}"
        fi

        if [[ "$security" =~ WPA || "$security" =~ WEP ]]; then
            signal_icon="${SECURED_SIGNAL_ICONS[$signal_level]}"
        fi

        # Добавляем иконку подключения, если сеть активна
        local formatted="$signal_icon $ssid"
        if [[ "$in_use" =~ \* ]]; then
            active_ssid="$ssid"
            formatted="$WIFI_CONNECTED_ICON $formatted"
        fi
        ssids+=("$ssid")
        formatted_ssids+=("$formatted")
    done < /tmp/wifi_list.txt

    local formatted_list=""
    for formatted_ssid in "${formatted_ssids[@]}"; do
        formatted_list+="$formatted_ssid\n"
    done

    formatted_list=$(printf "%s" "$formatted_list")

    local chosen_network=$(echo -e "$formatted_list" | rofi -dmenu -i -selected-row 1 -p "Wi-Fi SSID: ")
    local ssid_index=-1
    for i in "${!formatted_ssids[@]}"; do
        if [[ "${formatted_ssids[$i]}" == "$chosen_network" ]]; then
            ssid_index=$i
            break
        fi
    done

    local chosen_id="${ssids[$ssid_index]}"

    if [ -z "$chosen_network" ]; then
        rm /tmp/wifi_list.txt
        return
    else
        # Проверяем состояние выбранной сети
        local device_status=$(nmcli -t -f STATE device show wlan0 | grep STATE | cut -d: -f2)

        # Определяем действие в зависимости от состояния сети
        local action
        if [[ "$chosen_id" == "$active_ssid" ]]; then
            action="  Disconnect"
        else
            action="󰸋  Connect"
        fi

        action=$(echo -e "$action\n  Forget" | rofi -dmenu -p "Action: ")
        case $action in
            "󰸋  Connect")
                local success_message="You are now connected to the Wi-Fi network \"$chosen_id\"."
                local saved_connections=$(nmcli -g NAME connection show)
                if [[ $(echo "$saved_connections" | grep -Fx "$chosen_id") ]]; then
                    nmcli connection up id "$chosen_id" | grep "successfully" && notify-send "Connection Established" "$success_message"
                else
                    local wifi_password=$(rofi -dmenu -p "Password: " -password)
                    nmcli device wifi connect "$chosen_id" password "$wifi_password" | grep "successfully" && notify-send "Connection Established" "$success_message"
                fi
                ;;
            "  Disconnect")
                nmcli device disconnect wlan0 && notify-send "Disconnected" "You have been disconnected from $chosen_id."
                ;;
            "  Forget")
                nmcli connection delete id "$chosen_id" && notify-send "Forgotten" "The network $chosen_id has been forgotten."
                ;;
        esac
    fi

    rm /tmp/wifi_list.txt
}

# Функция для управления Ethernet
manage_ethernet() {
    # Получаем список Ethernet устройств
    local eth_devices=$(nmcli device status | grep ethernet | awk '{print $1}')
    if [ -z "$eth_devices" ]; then
        notify-send "Error" "Ethernet device not found."
        return
    fi

    # Подготавливаем список для выбора
    local eth_list=""
    for dev in $eth_devices; do
        local dev_status=$(nmcli device status | grep "$dev" | awk '{print $3}')
        if [ "$dev_status" = "connected" ]; then
            eth_list+="$ETHERNET_CONNECTED_ICON$dev\n"
        else
            eth_list+="$dev\n"
        fi
    done

    # Позволяем пользователю выбрать устройство
    local chosen_device=$(echo -e "$eth_list" | rofi -dmenu -i -p "Select Ethernet device: ")

    if [ -z "$chosen_device" ]; then
        return
    fi

    # Получаем статус выбранного устройства
    chosen_device=$(echo $chosen_device | sed "s/$ETHERNET_CONNECTED_ICON//")
    local device_status=$(nmcli device status | grep "$chosen_device" | awk '{print $3}')

    # Выполняем действие в зависимости от статуса
    if [ "$device_status" = "connected" ]; then
        nmcli device disconnect "$chosen_device" && notify-send "Disconnected" "You have been disconnected from $chosen_device."
    elif [ "$device_status" = "disconnected" ]; then
        nmcli device connect "$chosen_device" && notify-send "Connected" "You are now connected to $chosen_device."
    else
        notify-send "Error" "Unable to determine the action for $chosen_device."
    fi
}

# Главное меню
main_menu() {
    ##==> Получаем необходимые аргументы
    ###############################################
    while [[ $# -gt 0 ]]; do
        case $1 in
            --status)
                status_mode=true
                shift
                ;;
            --enabled-color)
                ENABLED_COLOR="$2"
                shift 2
                ;;
            --disabled-color)
                DISABLED_COLOR="$2"
                shift 2
                ;;
            *)
                shift
                ;;
        esac
    done
	        
    if [[ $status_mode == true ]]; then
        get_status
        exit 1
    fi

    ##==> Если служба не запущена
    ###############################################
    if ! pgrep -x "NetworkManager" > /dev/null; then
        echo -n "Root Password: "
        read -s password
        echo "$password" | sudo -S systemctl start NetworkManager
    fi

    ##==> Получаем кнопки действий и функцианал для них
    #######################################################
    local wifi_status=$(nmcli -fields WIFI g)
    local wifi_toggle
    if [[ "$wifi_status" =~ "enabled" ]]; then
        wifi_toggle="󱛅  Disable Wi-Fi"
        wifi_toggle_command="off"
        manage_wifi_btn="\n󱓥 Manage Wi-Fi"
    else
        wifi_toggle="󱚽  Enable Wi-Fi"
        wifi_toggle_command="on"
        manage_wifi_btn=""
    fi

    ##==> Выводим Rofi меню
    #######################################################
    local chosen_option=$(echo -e "$wifi_toggle$manage_wifi_btn\n󱓥 Manage Ethernet" | rofi -dmenu -p " Network Management: ")
    case $chosen_option in
        "$wifi_toggle")
            nmcli radio wifi $wifi_toggle_command
            ;;
        "󱓥 Manage Wi-Fi")
            manage_wifi
            ;;
        "󱓥 Manage Ethernet")
            manage_ethernet
            ;;
    esac
}

main_menu "$@"
