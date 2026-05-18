#!/bin/sh

bspc config border_width 3
bspc config borderless_monocle true

# Set the border colors for focused and normal windows
PALETTE="$HOME/.local/state/pawlette/active_palette.json"
if [[ -f "$PALETTE" ]]; then
    COLOR_PRIMARY=$(jq -r '.color_primary' "$PALETTE")
    bspc config focused_border_color "$COLOR_PRIMARY"
else
    bspc config focused_border_color "#b4befe"
fi

# Set mouse cursor to left pointer
xsetroot -cursor_name left_ptr

# Configure gaps and window gap size
bspc config gapless_monocle false
bspc config window_gap 10

# Configure actions for moving and resizing floating windows with the mouse
bspc config pointer_modifier mod4
bspc config pointer_action1 move
bspc config pointer_action2 resize_side
bspc config pointer_action3 resize_corner
