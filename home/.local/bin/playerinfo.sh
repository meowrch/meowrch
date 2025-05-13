#!/bin/env bash

THUMB=/tmp/meowrch-mpris
STATUS=$(playerctl status 2>/dev/null)

SKELETON_MODE=0
while [[ $# -gt 0 ]]; do
    case "$1" in
        --enable-skeleton)
            SKELETON_MODE=1
            shift
            ;;
        --*)
            # Основной аргумент (--title, --artist и т.д.)
            MAIN_ARG="$1"
            shift
            break  # Выходим из цикла после нахождения основного аргумента
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

if [ -z "$MAIN_ARG" ]; then
    echo "Usage: $0 [--enable-skeleton] <argument>"
    echo "Valid arguments: --title, --artist, --position, --length, --album, --source, --arturl, --art-path"
    exit 1
fi

get_metadata() {
    key=$1
    playerctl metadata --format "{{ $key }}" 2>/dev/null
}

get_source_info() {
    trackid=$(get_metadata "mpris:trackid")
    if [[ "$trackid" == *"firefox"* ]]; then
        echo -e "Firefox 󰈹"
    elif [[ "$trackid" == *"spotify"* ]]; then
        echo -e "Spotify "
    elif [[ "$trackid" == *"chromium"* ]]; then
        echo -e "Chrome "
    elif [[ "$trackid" == *"YoutubeMusic"* ]]; then
        echo -e "YouTubeMusic "
    else
        echo ""
    fi
}

get_position() {
    playerctl position 2>/dev/null
}

convert_length() {
    local length=$1
    local seconds=$((length / 1000000))
    local minutes=$((seconds / 60))
    local remaining_seconds=$((seconds % 60))
    printf "%d:%02d m" $minutes $remaining_seconds
}

convert_position() {
    local position=$1
    local seconds=${position%.*}
    local minutes=$((seconds / 60))
    local remaining_seconds=$((seconds % 60))
    printf "%d:%02d" $minutes $remaining_seconds
}

fetch_thumb() {
    artUrl=$(playerctl metadata --format '{{mpris:artUrl}}' 2>/dev/null)
    [[ -z "$artUrl" ]] && return 1

    [[ "${artUrl}" = "$(cat "${THUMB}.inf" 2>/dev/null)" ]] && return 0

    printf "%s\n" "$artUrl" > "${THUMB}.inf"

    if curl -so "${THUMB}.png" "$artUrl"; then
        magick "${THUMB}.png" -quality 50 "${THUMB}.png" 2>/dev/null
    else
        rm -f "${THUMB}"*
        return 1
    fi
}

if [[ -n "$STATUS" ]]; then
    { fetch_thumb ;} &
fi

case "$MAIN_ARG" in
--title)
    if [[ -z "$STATUS" ]]; then
        [[ $SKELETON_MODE -eq 1 ]] && echo "<span color='#444444' background='#444444'>▆▆▆▆▆▆▆▆▆▆▆▆▆▆▆▆▆▆</span>"
    else
        title=$(get_metadata "xesam:title")
        echo "${title:0:50}"
    fi
    ;;
--artist)
    if [[ -z "$STATUS" ]]; then
        [[ $SKELETON_MODE -eq 1 ]] && echo "<span color='#444444' background='#444444'>▆▆▆▆▆▆▆▆▆▆▆▆</span>"
    else
        artist=$(get_metadata "xesam:artist")
        echo "${artist:0:50}"
    fi
    ;;
--position)
    if [[ -z "$STATUS" ]]; then
        [[ $SKELETON_MODE -eq 1 ]] && echo "<span color='#444444' background='#444444'>▆▆:▆▆/▆▆:▆▆</span>"
    else
        position=$(get_position)
        length=$(get_metadata "mpris:length")
        if [ -n "$position" ] && [ -n "$length" ]; then
            position_formatted=$(convert_position "$position")
            length_formatted=$(convert_length "$length")
            echo "$position_formatted/$length_formatted"
        else
            echo ""
        fi
    fi
    ;;
--length)
    if [[ -z "$STATUS" ]]; then
        echo ""
    else
        length=$(get_metadata "mpris:length")
        [ -n "$length" ] && convert_length "$length"
    fi
    ;;
--status)
    if [[ $STATUS == "Playing" ]]; then
        echo "󰎆"
    elif [[ $STATUS == "Paused" ]]; then
        echo ""
    else
        [[ $SKELETON_MODE -eq 1 ]] && echo "<span color='#444444' background='#444444'>▆▆</span>" || echo ""
    fi
    ;;
--album)
    if [[ -z "$STATUS" ]]; then
        [[ $SKELETON_MODE -eq 1 ]] && echo "<span color='#444444' background='#444444'>▆▆▆▆▆▆▆▆</span>" || echo ""
    else
        album=$(get_metadata "xesam:album")
        if [ -n "$album" ]; then
            echo "$album"
        else
            echo "No album"
        fi
    fi
    ;;
--source)
    if [[ -z "$STATUS" ]]; then
        [[ $SKELETON_MODE -eq 1 ]] && echo "<span color='#444444' background='#444444'>▆▆▆▆▆▆▆▆</span>" || echo ""
    else
        get_source_info
    fi
    ;;
--arturl)
    [[ -z "$STATUS" ]] && exit
    get_metadata "mpris:artUrl"
    ;;
--art-path)
    if [[ -n "$STATUS" ]]; then
        echo "${THUMB}.png"
    fi
    ;;
*)
    echo "Invalid option: $1"
    exit 1
    ;;
esac