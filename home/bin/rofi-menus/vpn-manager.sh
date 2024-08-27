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
VPN_DIR="$HOME/.cache/rofivpnmenu/vpns"
PID_DIR="$HOME/.cache/rofivpnmenu/pids"
VPN_CONNECTED_ICON=" "
DISABLED_COLOR="#D35F5E"
ENABLED_COLOR="#A3BE8C"
mkdir -p "$VPN_DIR" "$PID_DIR"


print_error() {
    echo "Usage: $0 [--status] [--enabled-color] [--disabled-color]"
    exit 1
}

upload_config() {
    CONFIGS=$(zenity --file-selection --multiple --separator="|" \
        --title="Select VPN configurations" \
        --file-filter="OpenVPN configuration files | *.ovpn")
    if [ $? -eq 0 ]; then
        IFS='|' read -ra ADDR <<< "$CONFIGS"
        for i in "${ADDR[@]}"; do
            if [[ $i == *.ovpn ]]; then
                cp "$i" "$VPN_DIR"
                notify-send "OpenVPN" "Configuration files have been successfully added!"
            else
                zenity --error --text="Only files with the extension .ovpns are allowed to download."
            fi
        done
    fi
}

delete_vpn_config() {
    local SELECTED_VPN="$1"
    PID_FILE="$PID_DIR/$SELECTED_VPN.pid"
    # Если файл с PID существует, читаем PID и принудительно завершаем процесс
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if [ -n "$PID" ]; then
            # Отправляем сигнал SIGTERM для завершения процесса
            kill "$PID"
            # Ждем немного и проверяем, завершился ли процесс, если нет - принудительно завершаем
            sleep 1
            if kill -0 "$PID" 2>/dev/null; then
                kill -9 "$PID"
            fi
        fi
        # Удаляем файл с PID
        rm -f "$PID_FILE"
    fi
    # Удаляем файл конфигурации VPN
    VPN_CONFIG_FILE="$VPN_DIR/$SELECTED_VPN"
    if [ -f "$VPN_CONFIG_FILE" ]; then
        rm -f "$VPN_CONFIG_FILE"
    fi
    notify-send "OpenVPN" "The $SELECTED_VPN configuration has been successfully deleted!"
}

# Функция для отключения всех активных VPN подключений
disconnect_all_vpns() {
    for PID_PATH in "$PID_DIR"/*.pid; do
        # Если путь не существует, пропускаем итерацию
        [[ ! -e $PID_PATH ]] && continue
        VPN_PID=$(basename "$PID_PATH" .pid) # Получаем только имя файла VPN без расширения .pid
        PID=$(cat "$PID_PATH")
        if [ -n "$PID" ]; then
            # Отправляем сигнал SIGTERM для завершения процесса
            kill "$PID"
            # Ждем немного и проверяем, завершился ли процесс, если нет - принудительно завершаем
            sleep 1
            if kill -0 "$PID" 2>/dev/null; then
                kill -9 "$PID"
            fi
            notify-send "OpenVPN" "Disconnected from $VPN_PID"
        fi
        rm -f "$PID_PATH"
    done
}

toggle_vpn() {
    local VPN="$1"
    PID_FILE="$PID_DIR/$VPN.pid"
    if [ -f "$PID_FILE" ]; then
        # Если уже подключены к этому VPN, отключаемся
        PID=$(cat "$PID_FILE")
        if [ -n "$PID" ]; then
            # Отправляем сигнал SIGTERM для завершения процесса
            kill "$PID"
            # Ждем немного и проверяем, завершился ли процесс, если нет - принудительно завершаем
            sleep 1
            if kill -0 "$PID" 2>/dev/null; then
                kill -9 "$PID"
            fi
        fi
        rm -f "$PID_FILE"
        notify-send "OpenVPN" "Disconnected from $VPN"
    else
        PASSWORD=$(rofi -dmenu -password -p "Enter the sudo password:")

        if [ $? -ne 0 ]; then
            notify-send "OpenVPN" "Connection canceled"
            return
        fi
        
        disconnect_all_vpns # Отключаем все активные VPN перед подключением к новому

        echo $PASSWORD | sudo -S nohup openvpn --config "$VPN_DIR/$VPN" >/dev/null 2>&1 &
        PID=$!
        echo $PID > "$PID_FILE"
        notify-send "OpenVPN" "Connecting to $VPN initiated"
    fi
}

vpn_action_menu() {
    local VPN="$1"
    PID_FILE="$PID_DIR/$VPN.pid"
    ACTIONS="  Connect\n  Delete the config file"
    if [ -f "$PID_FILE" ]; then
        ACTIONS="  Disconnect\n  Delete the config file"
    fi
    ACTION=$(echo -e "$ACTIONS" | rofi -dmenu -p "Action with $VPN:")
    if [ $? -eq 0 ]; then
        case "$ACTION" in
            "  Connect"|"  Disconnect")
                toggle_vpn "$VPN"
                ;;
            "  Delete the config file")
                delete_vpn_config "$VPN"
                ;;
        esac
    fi
}

show_rofi_menu() {
    local VPN_LIST=("$VPN_DIR"/*.ovpn) # Читаем список .ovpn файлов в массив
    local MENU_ITEMS=("󰩍  Upload configuration files") # Массив элементов меню

    # Проверяем, существуют ли конфигурационные файлы .ovpn
    if compgen -G "$VPN_DIR"/*.ovpn > /dev/null; then
        for VPN_PATH in "${VPN_LIST[@]}"; do
            # Если путь не существует, пропускаем итерацию
            [[ ! -e $VPN_PATH ]] && continue
            VPN=$(basename "$VPN_PATH")
            VPN_STATUS=""
            PID_FILE="$PID_DIR/$VPN.pid"
            if [ -f "$PID_FILE" ]; then
                PID=$(cat "$PID_FILE")
                # Проверяем, активен ли процесс с таким PID
                if [ -n "$PID" ] && ps -p $PID > /dev/null; then
                    # Получаем полную команду запуска процесса
                    COMMAND=$(ps -p $PID -o args=)
                    # Проверяем, содержит ли она упоминание openvpn
                    if [[ "$COMMAND" == *"openvpn"* ]]; then
                        VPN_STATUS="$VPN_CONNECTED_ICON "
                    fi
                else
                    # Если процесса нет, удаляем файл PID
                    rm -f "$PID_FILE"
                fi
            fi
            MENU_ITEMS+=("$VPN_STATUS$VPN")
        done
    fi
    IFS=$'\n' # Устанавливаем внутренний разделитель полей в новую строку
    SELECTED_VPN=$(printf "%s\n" "${MENU_ITEMS[@]}" | rofi -dmenu -p "Select VPN:" -matching fuzzy)
    if [ $? -ne 0 ]; then
        return
    fi
    if [[ "$SELECTED_VPN" == "󰩍  Upload configuration files" ]]; then
        upload_config
        return
    fi

    SELECTED_VPN="${SELECTED_VPN#$VPN_CONNECTED_ICON }"
    vpn_action_menu "$SELECTED_VPN"
}

print_status() {
    local connected=false
    # Проверяем, есть ли активные VPN подключения
    for PID_PATH in "$PID_DIR"/*.pid; do
        [[ ! -e $PID_PATH ]] && continue
        PID=$(cat "$PID_PATH")
        if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then
            connected=true
            break
        fi
    done

    if $connected; then
        local icon="󰯄 "
        local color=$ENABLED_COLOR
    else
        local icon="󰯄 "
        local color=$DISABLED_COLOR
    fi

    if [[ "$SESSION_TYPE" == "wayland" ]]; then
        echo "<span color=\"$color\">$icon</span>"
    elif [[ "$SESSION_TYPE" == "x11" ]]; then
        echo "%{F$color}$icon%{F-}"
    fi
}

# Обработка аргументов командной строки
while [[ "$#" -gt 0 ]]; do
    case $1 in
		--enabled-color)
			ENABLED_COLOR="$2"
			shift
			;;
		--disabled-color)
			DISABLED_COLOR="$2"
			shift
			;;
        --status) status=true ;;
        *) print_error ;;
    esac
    shift
done

if [[ "$status" == true ]]; then
    print_status
    exit 0
fi

show_rofi_menu
