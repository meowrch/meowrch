#!/bin/sh
# media-active.sh - Detect active media playback for idle inhibition
# Used by hypridle listeners to skip lock/suspend when media is playing.
#
# Exit 0 = media is playing (do NOT lock/suspend)
# Exit 1 = no media active (proceed with lock/suspend)
#
# Toggle: export MEOWRCH_IDLE_MEDIA_GUARD=0 to disable this check.
# Debug:  export MEOWRCH_MEDIA_GUARD_DEBUG=1 to log detector to stderr.

_debug() { [ "${MEOWRCH_MEDIA_GUARD_DEBUG:-0}" = "1" ] && printf '%s\n' "$1" >&2; }

# If guard is explicitly disabled, always report no media
if [ "${MEOWRCH_IDLE_MEDIA_GUARD:-1}" = "0" ]; then
    exit 1
fi

# A) MPRIS playback via playerctl (covers browsers, Spotify, mpv, etc.)
if command -v playerctl >/dev/null 2>&1; then
    if playerctl -a status 2>/dev/null | grep -q "Playing"; then
        _debug "active: playerctl"
        exit 0
    fi
fi

# B) PulseAudio sink-inputs via pactl (accurate: only matches truly playing streams)
if command -v pactl >/dev/null 2>&1; then
    if pactl list sink-inputs 2>/dev/null | grep -q "State: RUNNING"; then
        _debug "active: pactl"
        exit 0
    fi
    # pactl exists but nothing RUNNING — skip wpctl fallback
    _debug "inactive"
    exit 1
fi

# C) Fallback: wpctl (conservative — only if pactl is missing)
if command -v wpctl >/dev/null 2>&1; then
    if wpctl status 2>/dev/null | grep -q '\[active\]'; then
        _debug "active: wpctl"
        exit 0
    fi
fi

# No active media found (or no detectors available)
_debug "inactive"
exit 1
