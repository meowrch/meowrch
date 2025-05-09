#!/usr/bin/env bash

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

print_error() {
    echo "Usage: $0 --device <input|output> --action <increase|decrease|toggle> [--status] [--enabled-color] [--disabled-color]"
    exit 1
}

notify_vol() {
    vol=$(get_volume)
    notify-send -u low "Volume" "${vol}%"
}

get_volume() {
    if [[ "${srce}" == "--default-source" ]]; then
        pamixer "${srce}" --get-volume
    else
        pamixer --get-volume
    fi
}

print_status() {
    local vol=$(get_volume)
    
    if [[ "${device}" == "output" ]]; then
        if [[ $(pamixer --get-mute) == "true" ]]; then
            local icon="  $vol%"
			local color=$DISABLED_COLOR
        elif [[ "$vol" -le 30 ]]; then
            local icon=" $vol%"
			local color=$ENABLED_COLOR
        elif [[ "$vol" -le 60 ]]; then
            local icon=" $vol%"
			local color=$ENABLED_COLOR
        elif [[ "$vol" -le 80 ]]; then
            local icon="  $vol%"
			local color=$ENABLED_COLOR
        else
            local icon="  $vol%" 
			local color=$ENABLED_COLOR
        fi
    elif [[ "${device}" == "input" ]]; then
        if [[ $(pamixer "${srce}" --get-mute) == "true" ]]; then
            local icon="  $vol%"
			local color=$DISABLED_COLOR
        else
            local icon=" $vol%"
			local color=$ENABLED_COLOR
        fi
    fi

	if [[ "$SESSION_TYPE" == "wayland" ]]; then
        echo "<span color=\"$color\">$icon</span>"
    elif [[ "$SESSION_TYPE" == "x11" ]]; then
        echo "%{F$color}$icon%{F-}"
    fi
}

action_volume() {
    case "${action}" in
        increase) 
            pamixer "${srce}" -i 2 
            ;;
        decrease) 
            pamixer "${srce}" -d 2 
            ;;
        toggle) 
            pamixer "${srce}" -t 
            notify_mute 
            exit 0 
            ;;
        *) 
            print_error 
            ;;
    esac
}

notify_mute() {
    if [[ $(pamixer "${srce}" --get-mute) == "true" ]]; then
        notify-send -u low "Muted"
    else
        notify-send -u low "Unmuted"
    fi
}

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --device) device="$2"; shift ;;
        --action) action="$2"; shift ;;
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

case "${device}" in
    input) srce="--default-source" ;;
    output) srce="" ;;
    *) print_error ;;
esac

if [[ -z "${device}" ]]; then
    print_error
fi

if [[ "$status" == true ]]; then
    print_status
    exit 0
fi

if [[ -z "${action}" ]]; then
    print_error
fi

# Execute action
action_volume
