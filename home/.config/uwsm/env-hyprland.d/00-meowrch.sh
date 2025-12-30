#!/usr/bin/env sh

HYPRLAND_NO_SD_NOTIFY=1 # If systemd, disables the sd_notify calls
HYPRLAND_NO_SD_VARS=1 # Disables management of variables in systemd and dbus activation environments.

# Export all variables
export HYPRLAND_NO_SD_NOTIFY HYPRLAND_NO_SD_VARS
