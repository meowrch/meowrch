#!/bin/bash

## Script To Manage Speaker Volume For Axyl OS.

# Get Volume
get_volume() {
	volume=$(echo $(pamixer --get-volume))
	echo "$volume"
}

# Get icons
get_icon() {
	vol="$(get_volume)"
	current="${vol%%%}"
	if [[ "$current" -eq "0" ]]; then
		icon='/usr/share/icons/Papirus-Dark/symbolic/status/audio-volume-muted-symbolic.svg'
	elif [[ ("$current" -ge "0") && ("$current" -le "30") ]]; then
		icon='/usr/share/icons/Papirus-Dark/symbolic/status/audio-volume-low-symbolic.svg'
	elif [[ ("$current" -ge "30") && ("$current" -le "60") ]]; then
		icon='/usr/share/icons/Papirus-Dark/symbolic/status/audio-volume-medium-symbolic.svg'
	elif [[ ("$current" -ge "60") && ("$current" -le "90") ]]; then
		icon='/usr/share/icons/Papirus-Dark/symbolic/status/audio-volume-high-symbolic.svg'
	elif [[ ("$current" -ge "90") && ("$current" -le "100") ]]; then
		icon='/usr/share/icons/Papirus-Dark/symbolic/status/audio-volume-overamplified-symbolic.svg'
	fi
}

# Increase Volume
up_volume() {
	pamixer -i 2 --unmute && get_icon && dunstify -u low --replace=69 -i "$icon" "Volume : $(get_volume)%"
}

# Decrease Volume
down_volume() {
	pamixer -d 2 --unmute && get_icon && dunstify -u low --replace=69 -i "$icon" "Volume : $(get_volume)%"
}

# Toggle Mute
toggle_mute() {
    status=$(pamixer --get-mute)

	if [[ "$status" == "true" ]]; then
		pamixer --unmute && get_icon && dunstify -u low --replace=69 -i "$icon" "Unmute"
	else
		pamixer --mute && dunstify -u low --replace=69 -i '/usr/share/icons/Papirus-Dark/symbolic/status/audio-volume-muted-symbolic.svg' "Mute"
	fi
}

# Execute accordingly
if [[ "$1" == "--get" ]]; then
	get_volume
elif [[ "$1" == "--up" ]]; then
	up_volume
elif [[ "$1" == "--down" ]]; then
        down_volume
elif [[ "$1" == "--toggle" ]]; then
	toggle_mute
else
	get_volume
fi
