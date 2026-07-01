#!/bin/bash

# Configuration
BASE_THEME="adw-gtk3"
CUSTOM_CSS_GTK3="$HOME/.config/gtk-3.0/gtk.css"
CUSTOM_CSS_GTK4="$HOME/.config/gtk-4.0/gtk.css"
CACHE_FILE="${XDG_STATE_HOME:-$HOME/.local/state}/pawlette/gtk-theme-cache"

# Generate a unique theme name based on a color hash
generate_theme_name() {
    local hash=$(echo "$PAWLETTE_COLOR_PRIMARY$PAWLETTE_COLOR_BG$PAWLETTE_COLOR_SURFACE" | md5sum | cut -c1-8)
    echo "pawlette-$hash"
}

# Removing an old theme from the cache
cleanup_old_theme() {
    if [ -f "$CACHE_FILE" ]; then
        local old_theme=$(cat "$CACHE_FILE")
        if [ -n "$old_theme" ] && [ -d "$HOME/.themes/$old_theme" ]; then
            echo "Removing old theme: $old_theme"
            rm -rf "$HOME/.themes/$old_theme"
        fi
    fi
}

# Looking for a base theme
base_theme_path=""
for dir in "$HOME/.themes" "$HOME/.local/share/themes" "/usr/share/themes"; do
    if [ -d "$dir/$BASE_THEME" ]; then
        base_theme_path="$dir/$BASE_THEME"
        echo "Found base theme at: $base_theme_path"
        break
    fi
done

if [ -z "$base_theme_path" ]; then
    echo "Error: Base theme '$BASE_THEME' not found"
    exit 1
fi

# Generate a name for a new theme
CUSTOM_THEME=$(generate_theme_name)
echo "Generated theme name: $CUSTOM_THEME"

# Deleting the old theme
cleanup_old_theme

# Let's create a directory for a custom theme
custom_theme_dir="$HOME/.themes/$CUSTOM_THEME"
echo "Creating custom theme at: $custom_theme_dir"
mkdir -p "$custom_theme_dir"

# Copy index.theme if it exists
if [ -f "$base_theme_path/index.theme" ]; then
    cp "$base_theme_path/index.theme" "$custom_theme_dir/"
    sed -i "s/Name=.*/Name=$CUSTOM_THEME/" "$custom_theme_dir/index.theme"
fi

# Function for generating CSS
generate_css() {
    local version=$1
    cat << EOF
/* Import base theme */
@import url("file://$base_theme_path/gtk-$version/gtk.css");

/* Pawlette custom styles */
@define-color accent_color         ${PAWLETTE_COLOR_PRIMARY};
@define-color accent_bg_color      ${PAWLETTE_COLOR_PRIMARY};
@define-color accent_fg_color      ${PAWLETTE_COLOR_TEXT};

@define-color window_bg_color      ${PAWLETTE_COLOR_BG};
@define-color window_fg_color      ${PAWLETTE_COLOR_TEXT};

@define-color view_bg_color        ${PAWLETTE_COLOR_BG};
@define-color view_fg_color        ${PAWLETTE_COLOR_TEXT};

@define-color headerbar_bg_color   ${PAWLETTE_COLOR_BG};
@define-color headerbar_fg_color   ${PAWLETTE_COLOR_TEXT};

@define-color card_bg_color        ${PAWLETTE_COLOR_SURFACE};
@define-color card_fg_color        ${PAWLETTE_COLOR_TEXT};

@define-color popover_bg_color     ${PAWLETTE_COLOR_BG};
@define-color popover_fg_color     ${PAWLETTE_COLOR_TEXT};

@define-color sidebar_bg_color     ${PAWLETTE_COLOR_BG};
@define-color sidebar_fg_color     ${PAWLETTE_COLOR_TEXT};

@define-color dialog_bg_color      ${PAWLETTE_COLOR_SURFACE};
@define-color dialog_fg_color      ${PAWLETTE_COLOR_TEXT};

@define-color error_color          ${PAWLETTE_COLOR_RED};
@define-color success_color        ${PAWLETTE_COLOR_GREEN};
@define-color warning_color        ${PAWLETTE_COLOR_YELLOW};
EOF
}

# === GTK-3.0 ===
echo "Setting up GTK-3.0..."
mkdir -p "$custom_theme_dir/gtk-3.0"
generate_css "3.0" > "$custom_theme_dir/gtk-3.0/gtk.css"

if [ -d "$base_theme_path/gtk-3.0/assets" ]; then
    ln -sf "$base_theme_path/gtk-3.0/assets" "$custom_theme_dir/gtk-3.0/assets"
fi

# === GTK-4.0 ===
echo "Setting up GTK-4.0..."
mkdir -p "$custom_theme_dir/gtk-4.0"
generate_css "4.0" > "$custom_theme_dir/gtk-4.0/gtk.css"

if [ -d "$base_theme_path/gtk-4.0/assets" ]; then
    ln -sf "$base_theme_path/gtk-4.0/assets" "$custom_theme_dir/gtk-4.0/assets"
fi

# Let's create symlinks for the remaining theme components
for component in gtk-2.0 metacity-1 xfwm4 openbox-3 cinnamon gnome-shell plank unity; do
    if [ -d "$base_theme_path/$component" ]; then
        ln -sf "$base_theme_path/$component" "$custom_theme_dir/$component"
    fi
done

# Updating settings.ini in GTK configurations
echo "Updating GTK settings..."
for gtk_dir in "$HOME/.config/gtk-3.0" "$HOME/.config/gtk-4.0"; do
    settings_file="$gtk_dir/settings.ini"
    if [ -f "$settings_file" ]; then
        sed -i "s/^gtk-theme-name=.*/gtk-theme-name=$CUSTOM_THEME/" "$settings_file"
    fi
done

# Updating gtkrc for GTK 2.0
for gtkrc_path in "$HOME/.gtkrc-2.0" "$HOME/.gtkrc" "$HOME/.config/gtk-2.0/gtkrc"; do
    if [ -f "$gtkrc_path" ]; then
        sed -i "s/^gtk-theme-name=.*/gtk-theme-name=\"$CUSTOM_THEME\"/" "$gtkrc_path"
    fi
done

# Let's apply the theme
if command -v gsettings &> /dev/null; then
    echo "Applying theme: $CUSTOM_THEME"
    gsettings set org.gnome.desktop.interface gtk-theme "$CUSTOM_THEME"
fi

# Use via xsettingsd if installed
if command -v xsettingsd &> /dev/null; then
    echo "Reloading xsettingsd..."
    killall -HUP xsettingsd 2>/dev/null || true
fi

# We store the theme name in the cache
mkdir -p "$(dirname "$CACHE_FILE")"
echo "$CUSTOM_THEME" > "$CACHE_FILE"

echo "Theme applied: $CUSTOM_THEME"