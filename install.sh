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
