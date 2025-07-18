#!/usr/bin/env sh
# This script is designed to improve the performance and reduce audio latency
# for sound cards by setting the PCI latency timer to an optimal value of 80
# cycles. It also resets the default value of the latency timer for other PCI
# devices, which can help prevent devices with high default latency timers from
# causing gaps in sound.

# Check if the script is run with root privileges
if [ "$(id -u)" -ne 0 ]; then
  echo "Error: This script must be run with root privileges." >&2
  exit 1
fi

# Reset the latency timer for all PCI devices
setpci -v -s '*:*' latency_timer=20
setpci -v -s '0:0' latency_timer=0

# Set latency timer for all sound cards
setpci -v -d "*:*:04xx" latency_timer=80
