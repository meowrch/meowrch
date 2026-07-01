#!/usr/bin/env bash
set -euo pipefail

# Директория для хранения цветов в формате pywal
PYWAL_CACHE_DIR="$HOME/.cache/wal"
mkdir -p "$PYWAL_CACHE_DIR"

# Генерируем файл colors в формате pywal
cat > "$PYWAL_CACHE_DIR/colors" <<EOF
# wallpaper
${PAWLETTE_ANSI_COLOR0}
${PAWLETTE_ANSI_COLOR1}
${PAWLETTE_ANSI_COLOR2}
${PAWLETTE_ANSI_COLOR3}
${PAWLETTE_ANSI_COLOR4}
${PAWLETTE_ANSI_COLOR5}
${PAWLETTE_ANSI_COLOR6}
${PAWLETTE_ANSI_COLOR7}
${PAWLETTE_ANSI_COLOR8}
${PAWLETTE_ANSI_COLOR9}
${PAWLETTE_ANSI_COLOR10}
${PAWLETTE_ANSI_COLOR11}
${PAWLETTE_ANSI_COLOR12}
${PAWLETTE_ANSI_COLOR13}
${PAWLETTE_ANSI_COLOR14}
${PAWLETTE_ANSI_COLOR15}
EOF

# Генерируем colors.json в формате pywal
cat > "$PYWAL_CACHE_DIR/colors.json" <<EOF
{
    "wallpaper": "",
    "alpha": "100",
    "special": {
        "background": "${PAWLETTE_COLOR_BG}",
        "foreground": "${PAWLETTE_COLOR_TEXT}",
        "cursor": "${PAWLETTE_COLOR_CURSOR}"
    },
    "colors": {
        "color0": "${PAWLETTE_ANSI_COLOR0}",
        "color1": "${PAWLETTE_ANSI_COLOR1}",
        "color2": "${PAWLETTE_ANSI_COLOR2}",
        "color3": "${PAWLETTE_ANSI_COLOR3}",
        "color4": "${PAWLETTE_ANSI_COLOR4}",
        "color5": "${PAWLETTE_ANSI_COLOR5}",
        "color6": "${PAWLETTE_ANSI_COLOR6}",
        "color7": "${PAWLETTE_ANSI_COLOR7}",
        "color8": "${PAWLETTE_ANSI_COLOR8}",
        "color9": "${PAWLETTE_ANSI_COLOR9}",
        "color10": "${PAWLETTE_ANSI_COLOR10}",
        "color11": "${PAWLETTE_ANSI_COLOR11}",
        "color12": "${PAWLETTE_ANSI_COLOR12}",
        "color13": "${PAWLETTE_ANSI_COLOR13}",
        "color14": "${PAWLETTE_ANSI_COLOR14}",
        "color15": "${PAWLETTE_ANSI_COLOR15}"
    }
}
EOF

echo "[pywal-compat] Generated: $PYWAL_CACHE_DIR/colors"
echo "[pywal-compat] Generated: $PYWAL_CACHE_DIR/colors.json"
exit 0