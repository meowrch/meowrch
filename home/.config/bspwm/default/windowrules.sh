#!/bin/sh

bspc rule -a feh state=floating
bspc rule -a '*:sun-awt-X11-XWindowPeer' manage=off
bspc rule -a 'vlc' state=floating center=true
bspc rule -a 'Blueman-manager' state=floating center=true
bspc rule -a 'qt5ct' state=floating rectangle=900x600+0+0 center=true
bspc rule -a 'qt6ct' state=floating rectangle=900x600+0+0 center=true
bspc rule -a 'ark' state=floating rectangle=1200x800+0+0 center=true
bspc rule -a 'Xarchiver' state=floating rectangle=1200x800+0+0 center=true
bspc rule -a 'pavucontrol' state=floating center=true
bspc rule -a 'Yad' state=floating center=true
bspc rule -a 'Blueman-manager' state=floating center=true
bspc rule -a 'org.gnome.FileRoller' state=floating rectangle=1200x800+0+0 center=true
bspc rule -a 'Gnome-calculator' state=floating rectangle=360x500+0+0 center=true
bspc rule -a 'loupe' state=floating rectangle=1200x800+0+0 center=true
bspc rule -a 'hotkeyhub' state=floating rectangle=1200x800+0+0 center=true
bspc rule -a 'qalculate-gtk' state=floating rectangle=850x560+0+0 center=true
bspc rule -a 'pavucontrol' state=floating rectangle=920x450+0+0 center=true