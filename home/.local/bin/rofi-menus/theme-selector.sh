#!/usr/bin/env bash

# ┏━━━┳━━┳━┓┏━┳━━━┳┓╋╋┏━━┳━┓┏━┓
# ┗┓┏┓┣┫┣┫┃┗┛┃┃┏━━┫┃╋╋┗┫┣┻┓┗┛┏┛
# ╋┃┃┃┃┃┃┃┏┓┏┓┃┗━━┫┃╋╋╋┃┃╋┗┓┏┛
# ╋┃┃┃┃┃┃┃┃┃┃┃┃┏━━┫┃╋┏┓┃┃╋┏┛┗┓
# ┏┛┗┛┣┫┣┫┃┃┃┃┃┃╋╋┃┗━┛┣┫┣┳┛┏┓┗┓
# ┗━━━┻━━┻┛┗┛┗┻┛╋╋┗━━━┻━━┻━┛┗━┛
# The program was created by DIMFLIX
# Github: https://github.com/DIMFLIX

# Configuration
RANDOM_ICON="${XDG_DATA_HOME:-$HOME/.local/share}/meowrch/assets/random.png"
ROFI_THEME="$HOME/.config/rofi/selecting.rasi"

# Get themes info
THEMES_JSON=$(pawlette get-themes-info)

# JSON parsing function
get_theme_logo() {
    echo "$THEMES_JSON" | jq -r --arg theme "$1" '.[$theme].logo'
}

# Generate rofi list
generate_rofi_list() {
    echo -en "Random Theme\x00icon\x1f$RANDOM_ICON\n"
    echo "$THEMES_JSON" | jq -r 'keys[]' | while read -r theme; do
        logo=$(get_theme_logo "$theme")
        [[ -f "$logo" ]] && echo -en "$theme\x00icon\x1f$logo\n" || echo -en "$theme\n"
    done
}

# Main logic
main() {
    command -v jq >/dev/null || { echo "Install jq"; exit 1; }
    command -v rofi >/dev/null || { echo "Install rofi"; exit 1; }
    command -v pawlette >/dev/null || { echo "Install pawlette"; exit 1; }

    selected=$(generate_rofi_list | rofi -dmenu -i -p "Theme" -theme "$ROFI_THEME")
    [[ -z "$selected" ]] && exit 0

    if [[ "$selected" == "Random Theme" ]]; then
        themes=($(echo "$THEMES_JSON" | jq -r 'keys[]'))
        random_theme="${themes[RANDOM % ${#themes[@]}]}"
        pawlette set-theme "$random_theme"
    else
        pawlette set-theme "$selected"
    fi
}

main "$@"
