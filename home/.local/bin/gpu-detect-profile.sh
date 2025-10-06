#!/usr/bin/env sh
# gpu-detect-profile — unified GPU profile detection for Meowrch
# Behavior:
# - Executed: prints profile to stdout.
# - Sourced: sets/export GPU_SETUP (quiet; no stdout).
# Profiles:
#   nvidia-only | amd-only | intel-only | nouveau-only |
#   hybrid-intel-nvidia | hybrid-amd-intel | hybrid-intel-nouveau

cmd_exists() { command -v "$1" >/dev/null 2>&1; }

# Detectors (POSIX)
_detect_nvidia() {
  if cmd_exists nvidia-smi && nvidia-smi >/dev/null 2>&1; then
    echo 1
  elif lsmod | grep -q '^nvidia'; then
    echo 1
  else
    echo 0
  fi
}

_detect_amd() {
  if cmd_exists lspci && lspci -nn | grep -E "(VGA|3D)" | grep -iq "1002"; then
    echo 1
  else
    echo 0
  fi
}

_detect_intel() {
  if cmd_exists lspci && lspci -nn | grep -E "(VGA|3D)" | grep -iq "8086"; then
    echo 1
  else
    echo 0
  fi
}

_detect_nouveau() {
  if lsmod | grep -q '^nouveau'; then
    echo 1
  else
    echo 0
  fi
}

NVIDIA=$(_detect_nvidia)
AMD=$(_detect_amd)
INTEL=$(_detect_intel)
NOUVEAU=$(_detect_nouveau)

key="${AMD}${INTEL}${NOUVEAU}${NVIDIA}"

GPU_SETUP="unknown"
case "$key" in
  0101) GPU_SETUP=hybrid-intel-nvidia ;;
  1100) GPU_SETUP=hybrid-amd-intel ;;
  0110) GPU_SETUP=hybrid-intel-nouveau ;;
  0001) GPU_SETUP=nvidia-only ;;
  1000) GPU_SETUP=amd-only ;;
  0010) GPU_SETUP=nouveau-only ;;
  0100) GPU_SETUP=intel-only ;;
  *)
    # Heuristic fallback if exact combo didn't match
    if [ "$NVIDIA" = "1" ] && [ "$INTEL" = "1" ]; then
      GPU_SETUP=hybrid-intel-nvidia
    elif [ "$AMD" = "1" ] && [ "$INTEL" = "1" ]; then
      GPU_SETUP=hybrid-amd-intel
    elif [ "$INTEL" = "1" ] && [ "$NOUVEAU" = "1" ]; then
      GPU_SETUP=hybrid-intel-nouveau
    elif [ "$NVIDIA" = "1" ]; then
      GPU_SETUP=nvidia-only
    elif [ "$AMD" = "1" ]; then
      GPU_SETUP=amd-only
    elif [ "$INTEL" = "1" ]; then
      GPU_SETUP=intel-only
    elif [ "$NOUVEAU" = "1" ]; then
      GPU_SETUP=nouveau-only
    else
      GPU_SETUP=unknown
    fi
    ;;
 esac

# Export for callers that source this file
export GPU_SETUP

# If not sourced, print the profile
if ! ( return 0 2>/dev/null ); then
  printf '%s\n' "$GPU_SETUP"
fi

