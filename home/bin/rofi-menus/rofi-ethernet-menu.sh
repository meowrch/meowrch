#!/usr/bin/env bash

# ┏━━━┳━━┳━┓┏━┳━━━┳┓╋╋┏━━┳━┓┏━┓
# ┗┓┏┓┣┫┣┫┃┗┛┃┃┏━━┫┃╋╋┗┫┣┻┓┗┛┏┛
# ╋┃┃┃┃┃┃┃┏┓┏┓┃┗━━┫┃╋╋╋┃┃╋┗┓┏┛
# ╋┃┃┃┃┃┃┃┃┃┃┃┃┏━━┫┃╋┏┓┃┃╋┏┛┗┓
# ┏┛┗┛┣┫┣┫┃┃┃┃┃┃╋╋┃┗━┛┣┫┣┳┛┏┓┗┓
# ┗━━━┻━━┻┛┗┛┗┻┛╋╋┗━━━┻━━┻━┛┗━┛
# The program was created by DIMFLIX
# https://github.com/DIMFLIX-OFFICIAL/rofi-sys-tools


# Если запущено с аргументом status, проверяем подключение Ethernet и выводим иконку
# P.S - это сделано для удобной конфигурации polybar
if [[ $1 == "status" ]]; then
  if nmcli -t -f TYPE,STATE device status | grep 'ethernet:connected' > /dev/null; then
    echo "%{F#A3BE8C}󰈁%{F-}" # зеленый для подключенного состояния
  else
    echo "%{F#D35F5E}󰈂%{F-}" # красный для отключенного состояния
  fi
else

	# Проверяем статус NetworkManager
	network_status=$(ps aux | grep NetworkManager | grep -v grep)

	# Если служба не запущена
	if [ -z "$network_status" ]; then
	  # Скрываем ввод пароля
	  echo -n "Root Password: "
	  read -s password
	  echo $password | sudo -S systemctl start NetworkManager
	fi

	# Получаем список Ethernet устройств
	eth_devices=$(nmcli device status | grep ethernet | awk '{print $1}')
	if [ -z "$eth_devices" ]; then
	  notify-send "Error" "Ethernet device not found."
	  exit 1
	fi

	# Подготавливаем список для выбора
	eth_list=""
	for dev in $eth_devices; do
	  dev_status=$(nmcli device status | grep "$dev" | awk '{print $3}')
	  if [ "$dev_status" = "connected" ]; then
	    eth_list+="  $dev\n"
	  else
	    eth_list+="  $dev\n"
	  fi
	done

	# Позволяем пользователю выбрать устройство
	chosen_device=$(echo -e "$eth_list" | rofi -dmenu -i -p "Select Ethernet device: " | awk '{print $2}')
	if [ -z "$chosen_device" ]; then
	  exit
	fi

	# Получаем статус выбранного устройства
	device_status=$(nmcli device status | grep "$chosen_device" | awk '{print $3}')

	# Выполняем действие в зависимости от статуса
	if [ "$device_status" = "connected" ]; then
	  nmcli device disconnect "$chosen_device" && notify-send "Disconnected" "You have been disconnected from $chosen_device."
	elif [ "$device_status" = "disconnected" ]; then
	  nmcli device connect "$chosen_device" && notify-send "Connected" "You are now connected to $chosen_device."
	else
	  notify-send "Error" "Unable to determine the action for $chosen_device."
	fi
fi
