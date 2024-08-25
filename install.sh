#!/bin/bash

clear

echo "┏━┓┏━┳━━━┳━━━┳┓┏┓┏┳━━━┳━━━┳┓╋┏┓╋╋┏━━┓┏┓╋┏┳━━┳┓╋╋┏━━━┳━━━┳━━━┓"
echo "┃┃┗┛┃┃┏━━┫┏━┓┃┃┃┃┃┃┏━┓┃┏━┓┃┃╋┃┃╋╋┃┏┓┃┃┃╋┃┣┫┣┫┃╋╋┗┓┏┓┃┏━━┫┏━┓┃"
echo "┃┏┓┏┓┃┗━━┫┃╋┃┃┃┃┃┃┃┗━┛┃┃╋┗┫┗━┛┃╋╋┃┗┛┗┫┃╋┃┃┃┃┃┃╋╋╋┃┃┃┃┗━━┫┗━┛┃"
echo "┃┃┃┃┃┃┏━━┫┃╋┃┃┗┛┗┛┃┏┓┏┫┃╋┏┫┏━┓┃╋╋┃┏━┓┃┃╋┃┃┃┃┃┃╋┏┓┃┃┃┃┏━━┫┏┓┏┛"
echo "┃┃┃┃┃┃┗━━┫┗━┛┣┓┏┓┏┫┃┃┗┫┗━┛┃┃╋┃┃╋╋┃┗━┛┃┗━┛┣┫┣┫┗━┛┣┛┗┛┃┗━━┫┃┃┗┓"
echo "┗┛┗┛┗┻━━━┻━━━┛┗┛┗┛┗┛┗━┻━━━┻┛╋┗┛╋╋┗━━━┻━━━┻━━┻━━━┻━━━┻━━━┻┛┗━┛"
echo
echo "≽ܫ≼ Starting pre-install..." && sleep 2

##==> Installing basic dependencies for pacman
#######################################################
dependencies=(python)
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
	"pyyaml"
	"pillow"
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
