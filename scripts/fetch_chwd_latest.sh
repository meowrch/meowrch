#!/usr/bin/env bash
set -e

BASE_URL="https://mirror.cachyos.org/repo/x86_64/cachyos"
PACKAGE="chwd"

# fetch directory listing
listing=$(wget -qO- "$BASE_URL/")

# find latest file via regex and sort
latest=$(echo "$listing" \
    | grep -oE "${PACKAGE}-[0-9]+\\.[0-9]+\\.[0-9]+-[0-9]+-x86_64\\.pkg\\.tar\\.zst" \
    | sort -V \
    | tail -n1)

if [ -z "$latest" ]; then
    echo "ERROR: could not find chwd package in mirror"
    exit 1
fi

url="$BASE_URL/$latest"
echo "Downloading $url ..."
wget -O "$latest" "$url"
echo "Installing $latest via pacman -U ..."
sudo pacman -U --noconfirm "$latest"
sudo chwd -a

