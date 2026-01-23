#!/bin/bash

setfont cyr-sun16
clear

echo """
                          ▄▀▄     ▄▀▄           ▄▄▄▄▄
                         ▄█░░▀▀▀▀▀░░█▄         █░▄▄░░█
                     ▄▄  █░░░░░░░░░░░█  ▄▄    █░█  █▄█
                    █▄▄█ █░░▀░░┬░░▀░░█ █▄▄█  █░█   
███╗░░░███╗███████╗░█████╗░░██╗░░░░░░░██╗██████╗░░█████╗░██╗░░██╗
████╗░████║██╔════╝██╔══██╗░██║░░██╗░░██║██╔══██╗██╔══██╗██║░░██║
██╔████╔██║█████╗░░██║░░██║░╚██╗████╗██╔╝██████╔╝██║░░╚═╝███████║
██║╚██╔╝██║██╔══╝░░██║░░██║░░████╔═████║░██╔══██╗██║░░██╗██╔══██║
██║░╚═╝░██║███████╗╚█████╔╝░░╚██╔╝░╚██╔╝░██║░░██║╚█████╔╝██║░░██║
╚═╝░░░░░╚═╝╚══════╝░╚════╝░░░░╚═╝░░░╚═╝░░╚═╝░░╚═╝░╚════╝░╚═╝░░╚═╝
"""
echo
echo "Starting pre-install..." && sleep 2


##==> Detecting system architecture
#######################################################
ARCH=$(uname -m)
echo ""
echo "========================================="
echo "  ARCHITECTURE DETECTION"
echo "========================================="
echo "Detected architecture: $ARCH"

case "$ARCH" in
    x86_64)
        echo "Platform: x86_64 Desktop/Laptop"
        echo "Full feature support available"
        ;;
    aarch64)
        echo "Platform: ARM 64-bit (aarch64)"
        echo "Note: Some features limited on ARM"
        echo "  - Gaming packages will be skipped"
        echo "  - Some proprietary apps unavailable"
        ;;
    armv7l)
        echo "Platform: ARM 32-bit (armv7l)"
        echo "Note: Limited feature support"
        echo "  - Hyprland not recommended"
        echo "  - Some packages may not be available"
        ;;
    *)
        echo "ERROR: Unsupported architecture: $ARCH"
        echo "Meowrch supports: x86_64, aarch64, armv7l"
        exit 1
        ;;
esac

# Export architecture for Python installer
export MEOWRCH_ARCH=$ARCH
echo "========================================="
echo ""
sleep 2


##==> Initializing git submodules
#######################################################
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "Initializing git submodules..."
    git submodule update --init --recursive
else
    echo "Error: This directory is not a git repository. Please clone the project using git clone."
    exit 1
fi
#######################################################


##==> Installing basic dependencies for pacman
#######################################################
dependencies=(python python-pip)
for package in "${dependencies[@]}"; do
    if ! pacman -Q $package &> /dev/null; then
        sudo pacman -S --needed $package
    fi
done
#######################################################


##==> Installing python and dependencies for it
#######################################################
declare -a packages=(
	"inquirer"
	"loguru"
	"psutil"
	"gputil"
	"pyamdgpuinfo"
	"colorama"
)

for package in "${packages[@]}"; do
    if ! pip show $package &> /dev/null; then
        pip install $package --break-system-packages
    fi
done
#######################################################


##==> Building the system
#######################################################
python Builder/install.py
