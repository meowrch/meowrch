#!/usr/bin/env bash

# ┏━━━┳━━┳━┓┏━┳━━━┳┓╋╋┏━━┳━┓┏━┓
# ┗┓┏┓┣┫┣┫┃┗┛┃┃┏━━┫┃╋╋┗┫┣┻┓┗┛┏┛
# ╋┃┃┃┃┃┃┃┏┓┏┓┃┗━━┫┃╋╋╋┃┃╋┗┓┏┛
# ╋┃┃┃┃┃┃┃┃┃┃┃┃┏━━┫┃╋┏┓┃┃╋┏┛┗┓
# ┏┛┗┛┣┫┣┫┃┃┃┃┃┃╋╋┃┗━┛┣┫┣┳┛┏┓┗┓
# ┗━━━┻━━┻┛┗┛┗┻┛╋╋┗━━━┻━━┻━┛┗━┛
# The program was created by DIMFLIX
# Github: https://github.com/DIMFLIX-OFFICIAL


SESSION_TYPE=$XDG_SESSION_TYPE
DEFAULT_UPDATED_COLOR="#a6e3a1"
DEFAULT_UNUPDATED_COLOR="#fab387"
DEFAULT_TERMINAL="kitty"


show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --status              Show the update status."
    echo "  --updated-color COLOR Set the color for zero updates (default: $DEFAULT_UPDATED_COLOR)."
    echo "  --unupdated-color COLOR Set the color for non-zero updates (default: $DEFAULT_UNUPDATED_COLOR)."
    echo "  --terminal TERMINAL   Specify the terminal to run (default: $DEFAULT_TERMINAL)."
    echo "  --help                Show this message."
    echo ""
    echo "Example:"
    echo "  $0 --status"
    echo "  $0 --terminal kitty"
}

check_release() {
    if [ ! -f /etc/arch-release ]; then
        return 1
    fi
    return 0
}

pkg_installed() {
    pacman -Qq "$1" &>/dev/null
}

get_aurhlpr() {
    if command -v yay &>/dev/null; then
        echo "yay"
    elif command -v paru &>/dev/null; then
        echo "paru"
    else
        echo "No AUR helper found"
        exit 1
    fi
}

check_aur_updates() {
    local aurhlpr
    aurhlpr=$(get_aurhlpr)
    echo $(${aurhlpr} -Qua | wc -l)
}

check_official_updates() {
    (while pgrep -x checkupdates > /dev/null; do sleep 1; done)
    echo $(checkupdates | wc -l)
}

check_flatpak_updates() {
    if ! pkg_installed flatpak; then
        echo 0
        return
    fi
    echo $(flatpak remote-ls --updates | wc -l)
}

calculate_updates() {
    local ofc aur fpk
    ofc=$(check_official_updates)
    aur=$(check_aur_updates)
    fpk=$(check_flatpak_updates)
    echo $((ofc + aur + fpk))
}

print_status() {
    local updates color
    updates=$(calculate_updates)
    color=${2:-$DEFAULT_UNUPDATED_COLOR}

    if [ "$updates" -eq 0 ]; then
        updates=""
        color=${1:-$DEFAULT_UPDATED_COLOR}
    fi

    if [ "$SESSION_TYPE" == "wayland" ]; then
        echo "<span color=\"$color\">󰮯 $updates </span>"
    elif [ "$SESSION_TYPE" == "x11" ]; then
        echo "%{F$color}󰮯 $updates %{F-}"
    fi
}

trigger_upgrade() {
    local aurhlpr=$(get_aurhlpr)    
	local terminal=${1:-$DEFAULT_TERMINAL}
    local command="echo 'Official packages to update: \$(checkupdates | wc -l)'; \
                   echo 'AUR packages to update: \$(${aurhlpr} -Qua | wc -l)'; \
                   echo 'Flatpak packages to update: \$(flatpak remote-ls --updates | wc -l)'; \
                   echo; \
                   sudo ${aurhlpr} -Syu && sudo flatpak update"

    case $terminal in
        alacritty)
            alacritty -e bash -c "bash -c \"$command\""
            ;;
        kitty)
            kitty -e bash -c "bash -c \"$command\""
            ;;
        gnome-terminal)
            gnome-terminal -- bash -c "$command; exec bash"
            ;;
        xterm)
            xterm -e bash -c "bash -c \"$command\""
            ;;
        *)
            echo "Unsupported terminal: $terminal. Please run the command manually."
            exit 1
            ;;
    esac
}

main() {
    check_release || exit 0

    local updated_color="$DEFAULT_UPDATED_COLOR"
    local unupdated_color="$DEFAULT_UNUPDATED_COLOR"
    local terminal="$DEFAULT_TERMINAL"
    local status=0

    while [[ $# -gt 0 ]]; do
        case $1 in
            --status)
                status=1
                ;;
            --updated-color)
                shift
                updated_color="$1"
                ;;
            --unupdated-color)
                shift
                unupdated_color="$1"
                ;;
            --terminal)
                shift
                terminal="$1"
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                echo "Unknown argument: $1"
                show_help
                exit 1
                ;;
        esac
        shift
    done

    if [ "$status" -eq 1 ]; then
        print_status "$updated_color" "$unupdated_color"
    else
        trigger_upgrade "$terminal"
    fi
}

main "$@"
