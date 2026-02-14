#!/bin/sh
# media-active.sh - Detect active media playback for idle inhibition
# Used by hypridle listeners to skip lock/suspend when media is playing.
#
# Exit 0 = media is playing (do NOT lock/suspend)
# Exit 1 = no media active (proceed with lock/suspend)
#
# Toggle: export MEOWRCH_IDLE_MEDIA_GUARD=0 to disable this check.

# If guard is explicitly disabled, always report no media
if [ "${MEOWRCH_IDLE_MEDIA_GUARD:-1}" = "0" ]; then
    exit 1
fi

# Check MPRIS playback via playerctl (covers browsers, Spotify, mpv, etc.)
if command -v playerctl >/dev/null 2>&1; then
    if playerctl -a status 2>/dev/null | grep -q "Playing"; then
        exit 0
    fi
fi

# Check PipeWire/WirePlumber streams via wpctl (catches audio the above misses)
if command -v wpctl >/dev/null 2>&1; then
    if wpctl status 2>/dev/null | grep -q '\[active\]'; then
        exit 0
    fi
fi

# No active media found (or both tools missing)
exit 1
