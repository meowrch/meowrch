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
dependencies=(pyenv)
for package in "${dependencies[@]}"; do
    if ! pacman -Q $package &> /dev/null; then
        sudo pacman -S --needed $package
    fi
done
#######################################################


##==> Installing python and dependencies for it
#######################################################
installed_python_version=$(pyenv versions --bare | grep -E '^[0-9]+\.[0-9]+\.[0-9]+$' | sort -V | tail -n 1)
declare -a packages=(
	"inquirer"
	"loguru"
	"psutil"
	"gputil"
	"pyamdgpuinfo"
	"pyyaml"
	"pillow"
)

if [[ -z "$installed_python_version" || "$installed_python_version" < "3.11.0" ]]; then
    pyenv install 3.11.8
    pyenv global 3.11.8
else
    pyenv global "$installed_python_version"
fi

for package in "${packages[@]}"; do
    if ! pyenv exec pip show $package &> /dev/null; then
        pyenv exec pip install $package
    fi
done
#######################################################


##==> Building the system
#######################################################
python Builder/install.py
