#!/usr/bin/env bash

# ┏━━━┳━━┳━┓┏━┳━━━┳┓╋╋┏━━┳━┓┏━┓
# ┗┓┏┓┣┫┣┫┃┗┛┃┃┏━━┫┃╋╋┗┫┣┻┓┗┛┏┛
# ╋┃┃┃┃┃┃┃┏┓┏┓┃┗━━┫┃╋╋╋┃┃╋┗┓┏┛
# ╋┃┃┃┃┃┃┃┃┃┃┃┃┏━━┫┃╋┏┓┃┃╋┏┛┗┓
# ┏┛┗┛┣┫┣┫┃┃┃┃┃┃╋╋┃┗━┛┣┫┣┳┛┏┓┗┓
# ┗━━━┻━━┻┛┗┛┗┻┛╋╋┗━━━┻━━┻━┛┗━┛
# The program was created by DIMFLIX
# Github: https://github.com/DIMFLIX

# --- Configuration ---
SELECTING_THEME="$HOME/.config/rofi/selecting.rasi"

RANDOM_ICON="${XDG_DATA_HOME:-$HOME/.local/share}/meowrch/assets/random.png"
DEFAULT_LOGO="$HOME/.local/share/meowrch/assets/default-theme-logo.png"

DYNAMIC_ON_ICON="${XDG_DATA_HOME:-$HOME/.local/share}/meowrch/assets/dynamic-theme-on-logo.png"
DYNAMIC_OFF_ICON="${XDG_DATA_HOME:-$HOME/.local/share}/meowrch/assets/dynamic-theme-off-logo.png"
DYNAMIC_STATE_FILE="$HOME/.local/state/meowrch/dynamic_theme"

CURRENT_WALL="$HOME/.local/share/wallpapers/.current.wall"
THEMES_DIR="$HOME/.local/share/pawlette/themes"

# Placeholder if no color is found
MISSING_CHAR=""

# --- Functions ---
get_variant_color() {
    local theme="$1"
    local variant="$2"
    local toml_file="$THEMES_DIR/$theme/colors.toml"

    [[ ! -f "$toml_file" ]] && echo "" && return

    local section
    if [[ "$variant" == "default" ]]; then
        section="\[colors\]"
    else
        section="\[variants\.$variant\]"
    fi

    # Parse ONLY the specified section. If there is no color, return an empty string.
    local color=$(sed -n "/$section/,/^\[/p" "$toml_file" | \
        grep -E "color_primary|color_secondary|color_border_active|color_cursor" | \
        head -n 1 | \
        grep -oP '#[0-9a-fA-F]{6}' | head -n 1)

    echo "$color"
}

get_logo() {
    local theme_name="$1"
    local logo_path="$THEMES_DIR/$theme_name/logo.png"
    [[ -f "$logo_path" ]] && echo "$logo_path" || echo "$DEFAULT_LOGO"
}

execute_apply() {
    local theme="$1"
    local variant="$2"
    mkdir -p "$(dirname "$DYNAMIC_STATE_FILE")"
    echo "0" > "$DYNAMIC_STATE_FILE"
    if [[ -z "$variant" || "$variant" == "default" ]]; then
        pawlette apply theme "$theme"
    else
        pawlette apply theme "$theme" --variant "$variant"
    fi
}

toggle_dynamic_theme() {
    mkdir -p "$(dirname "$DYNAMIC_STATE_FILE")"
    [[ ! -f "$DYNAMIC_STATE_FILE" ]] && echo "0" > "$DYNAMIC_STATE_FILE"
    local current_state=$(cat "$DYNAMIC_STATE_FILE")
    if [[ "$current_state" == "1" ]]; then
        echo "0" > "$DYNAMIC_STATE_FILE"
    else
        echo "1" > "$DYNAMIC_STATE_FILE"
        [[ -f "$CURRENT_WALL" ]] && pawlette apply image "$CURRENT_WALL"
    fi
}

generate_main_list() {
    local dyn_status="disabled"
    local dyn_icon="$DYNAMIC_OFF_ICON"
    if [[ -f "$DYNAMIC_STATE_FILE" ]]; then
        [[ $(cat "$DYNAMIC_STATE_FILE") == "1" ]] && dyn_status="enabled" && dyn_icon="$DYNAMIC_ON_ICON"
    fi
    echo -en "Dynamic Theme ($dyn_status)\x00icon\x1f$dyn_icon\n"
    echo -en "Random Theme\x00icon\x1f$RANDOM_ICON\n"
    pawlette list | while read -r line; do
        theme=$(echo "$line" | awk '{print $1}')
        [[ -z "$theme" ]] && continue
        echo -en "$theme\x00icon\x1f$(get_logo "$theme")\n"
    done
}

apply_random() {
    local random_line=$(pawlette list | shuf -n 1)
    local theme=$(echo "$random_line" | awk '{print $1}')
    if [[ "$random_line" == *"("* ]]; then
        local variants=$(echo "$random_line" | grep -oP '\(\K[^\)]+' | tr -d ',')
        local variants_array=("default" $variants)
        execute_apply "$theme" "${variants_array[$RANDOM % ${#variants_array[@]}]}"
    else
        execute_apply "$theme" "default"
    fi
}

main() {
    command -v rofi >/dev/null || { echo "Rofi не найден!"; exit 1; }

    selected_theme=$(generate_main_list | rofi -dmenu -i -p "Theme" -theme "$SELECTING_THEME")
    [[ -z "$selected_theme" ]] && exit 0

    if [[ "$selected_theme" == "Dynamic Theme"* ]]; then
        toggle_dynamic_theme; exit 0
    elif [[ "$selected_theme" == "Random Theme" ]]; then
        apply_random; exit 0
    fi

    theme_info=$(pawlette list | grep "^$selected_theme")
    if [[ "$theme_info" == *"("* ]]; then
        variants_raw=$(echo "$theme_info" | grep -oP '\(\K[^\)]+' | tr -d ',')
        list_with_colors=""
        
        for v in "default" $variants_raw; do
            hex=$(get_variant_color "$selected_theme" "$v")
            
            if [[ "$hex" =~ ^#[0-9a-fA-F]{6}$ ]]; then
                list_with_colors+="<span foreground='$hex'>●</span> $v\n"
            else
                list_with_colors+="$MISSING_CHAR $v\n"
            fi
        done

        selected_row=$(echo -ne "${list_with_colors%\\n}" | rofi -dmenu -i -p "$selected_theme" -markup-rows)
        
        [[ -z "$selected_row" ]] && exit 0
        
        # Remove the tags and the circle from the string, leaving only the variant name
        selected_variant=$(echo "$selected_row" | sed 's/<[^>]*>//g' | sed 's/^[● ]*//' | xargs)
        
        execute_apply "$selected_theme" "$selected_variant"
    else
        execute_apply "$selected_theme" "default"
    fi
}

main "$@"
