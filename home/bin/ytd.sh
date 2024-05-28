#!/bin/env bash
set -e

if [[ $1 == "-h" || $1 == "--help" ]]; then

	echo "Description: A shortcut to download youtube videos and converts to either mp3 ot mp4."

	printf "\n"
	echo "Usage: ytd [OPTION] [youtube video link]"
	echo "  -h, --help      This help screen."
	echo "  --mp3           Converts youtube video to mp3 format."
	echo "  --mp4           Downloads youtube video with the highest video and audio quality."
    echo "  -s, --search    Searches for the video you're looking for."

elif [[ $1 == "--mp3" ]]; then
	youtube-dl -x --audio-format mp3 --prefer-ffmpeg "$2"
elif [[ "$1" == "--mp4" ]]; then
	youtube-dl -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio" --merge-output-format mp4 "$2"
elif [[ "$1" == "-s" || "$1" == "--search" ]]; then
    youtube-dl "ytsearch1: $2"
fi

