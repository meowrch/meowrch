#!/usr/bin/env bash

# ┏━━━┳━━┳━┓┏━┳━━━┳┓╋╋┏━━┳━┓┏━┓
# ┗┓┏┓┣┫┣┫┃┗┛┃┃┏━━┫┃╋╋┗┫┣┻┓┗┛┏┛
# ╋┃┃┃┃┃┃┃┏┓┏┓┃┗━━┫┃╋╋╋┃┃╋┗┓┏┛
# ╋┃┃┃┃┃┃┃┃┃┃┃┃┏━━┫┃╋┏┓┃┃╋┏┛┗┓
# ┏┛┗┛┣┫┣┫┃┃┃┃┃┃╋╋┃┗━┛┣┫┣┳┛┏┓┗┓
# ┗━━━┻━━┻┛┗┛┗┻┛╋╋┗━━━┻━━┻━┛┗━┛
# The program was created by DIMFLIX
# https://github.com/DIMFLIX-OFFICIAL/rofi-sys-tools


# Проверяем, запущен ли NetworkManager
if ! pgrep -x "NetworkManager" > /dev/null; then
  echo -n "Root Password: "
  read -s password
  echo $password | sudo -S systemctl start NetworkManager
fi

notify-send "Getting list of available Wi-Fi networks..."

# Сохраняем вывод nmcli во временный файл
nmcli --terse --fields "IN-USE,SIGNAL,SECURITY,SSID" device wifi list > /tmp/wifi_list.txt

ssids=()
formatted_ssids=()

while IFS=: read -r in_use signal security ssid; do
  if [ -z "$ssid" ]; then continue; fi # Пропускаем сети без SSID

  # Определение иконки силы сигнала и защиты
  signal_icon="󰤟󰤢󰤥󰤨" # По умолчанию
  if [ "$signal" -lt 25 ]; then signal_icon="󰤟 "
  elif [ "$signal" -lt 50 ]; then signal_icon="󰤢 "
  elif [ "$signal" -lt 75 ]; then signal_icon="󰤥 "
  else signal_icon="󰤨 "; fi

  if [[ "$security" =~ WPA || "$security" =~ WEP ]]; then
    if [ "$signal" -lt 25 ]; then signal_icon="󰤡 "
    elif [ "$signal" -lt 50 ]; then signal_icon="󰤤 "
    elif [ "$signal" -lt 75 ]; then signal_icon="󰤧 "
    else signal_icon="󰤪 "; fi
  fi

  # Формирование строки для вывода
  formatted="$signal_icon $ssid"
  if [[ "$in_use" =~ \* ]]; then
    formatted="  $formatted"
    # Добавляем в начало массивов
    ssids=( "$ssid" "${ssids[@]}" )
    formatted_ssids=( "$formatted" "${formatted_ssids[@]}" )
  else
    # Добавляем в конец массивов
    ssids+=("$ssid")
    formatted_ssids+=("$formatted")
  fi
done < /tmp/wifi_list.txt

# Получение списка для rofi
formatted_list=""
for formatted_ssid in "${formatted_ssids[@]}"; do
  formatted_list+="$formatted_ssid\n"
done

# Удаление последнего перевода строки
formatted_list=$(printf "%s" "$formatted_list")

connected=$(nmcli -fields WIFI g)
if [[ "$connected" =~ "enabled" ]]; then
  toggle="󱛅  Disable Wi-Fi"
elif [[ "$connected" =~ "disabled" ]]; then
  toggle="󱚽  Enable Wi-Fi"
fi

chosen_network=$(echo -e "$toggle\n$formatted_list" | rofi -dmenu -i -selected-row 1 -p "Wi-Fi SSID: ")
ssid_index=-1
for i in "${!formatted_ssids[@]}"; do
  if [[ "${formatted_ssids[$i]}" == "$chosen_network" ]]; then
    ssid_index=$i
    break
  fi
done

chosen_id="${ssids[$ssid_index]}"

if [ -z "$chosen_network" ]; then
  # Удаление временного файла перед выходом
  rm /tmp/wifi_list.txt
  exit
elif [ "$chosen_network" = "󱚽  Enable Wi-Fi" ]; then
  nmcli radio wifi on
elif [ "$chosen_network" = "󱛅  Disable Wi-Fi" ]; then
  nmcli radio wifi off
else
  action=$(echo -e "󰸋  Connect\n  Disconnect\n  Forget" | rofi -dmenu -p "Action: ")
  case $action in
    "󰸋  Connect")
      success_message="You are now connected to the Wi-Fi network \"$chosen_id\"."
      saved_connections=$(nmcli -g NAME connection show)
      if [[ $(echo "$saved_connections" | grep -Fx "$chosen_id") ]]; then
        nmcli connection up id "$chosen_id" | grep "successfully" && notify-send "Connection Established" "$success_message"
      else
        wifi_password=$(rofi -dmenu -p "Password: " -password)
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

# Удаление временного файла после работы скрипта
rm /tmp/wifi_list.txt
