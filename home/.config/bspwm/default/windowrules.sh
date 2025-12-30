#!/bin/sh

# Obtaining screen dimensions
SW=$(xdpyinfo | awk '/dimensions:/ {print $2}' | cut -d'x' -f1)
SH=$(xdpyinfo | awk '/dimensions:/ {print $2}' | cut -d'x' -f2)

# Function that calculates window dimensions based on percentages
rect() {
    w_pct=$1
    h_pct=$2
    
    w=$((SW * w_pct / 100))
    h=$((SH * h_pct / 100))
    x=$(( (SW - w) / 2 ))
    y=$(( (SH - h) / 2 ))
    
    echo "${w}x${h}+${x}+${y}"
}

bspc rule -a feh state=floating
bspc rule -a '*:sun-awt-X11-XWindowPeer' manage=off
bspc rule -a 'vlc' state=floating center=true
bspc rule -a 'Blueman-manager' state=floating center=true
bspc rule -a 'qt5ct' state=floating center=true
bspc rule -a 'qt6ct' state=floating center=true
bspc rule -a 'ark' state=floating center=true
bspc rule -a 'Xarchiver' state=floating center=true
bspc rule -a 'Yad' state=floating center=true
bspc rule -a 'Blueman-manager' state=floating center=true
bspc rule -a 'org.gnome.FileRoller' state=floating rectangle=$(rect 63 74) center=true
bspc rule -a 'Gnome-calculator' state=floating rectangle=$(rect 19 47) center=true
bspc rule -a 'loupe' state=floating rectangle=$(rect 63 74) center=true
bspc rule -a 'hotkeyhub' state=floating rectangle=$(rect 63 74) center=true
bspc rule -a 'qalculate-gtk' state=floating rectangle=$(rect 45 55) center=true
bspc rule -a 'pavucontrol' state=floating rectangle=$(rect 48 42) center=true