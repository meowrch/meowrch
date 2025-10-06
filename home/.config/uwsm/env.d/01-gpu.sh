# 00-gpu.sh - GPU detection
# This env script will detect the presence of various GPUs on the system
# and set environment variables accordingly.
# This is OVERRIDABLE by the user, so it can be customized as needed.
# create you own file that is alphabetically after this one

# Usage:
#
# The 'key' variable is a 4-digit string representing GPU presence:
#   1st digit: AMD GPU present (1) or not (0)
#   2nd digit: Intel GPU present (1) or not (0)
#   3rd digit: Nouveau GPU present (1) or not (0)
#   4th digit: NVIDIA GPU present (1) or not (0)
#
# Example:
#   key="0101" means AMD=0, Intel=1, Nouveau=0, NVIDIA=1 (hybrid Intel-NVIDIA setup)
#   key="1000" means AMD=1, Intel=0, Nouveau=0, NVIDIA=0 (AMD only)
#   key="0010" means AMD=0, Intel=0, Nouveau=1, NVIDIA=0 (Nouveau only)
#

# Detection logic moved to $HOME/.local/bin/gpu-detect-profile unified script

detect_nvidia_vaapi() {
  # Check if libva-nvidia-driver is installed by looking for the VA-API driver
  if [ -f "/usr/lib/dri/nvidia_drv_video.so" ] || [ -f "/usr/lib64/dri/nvidia_drv_video.so" ]; then
    echo 1
  else
    echo 0
  fi
}

# Use unified detector script (sets/export GPU_SETUP when sourced)
GPU_SETUP=""
if [ -r "$HOME/.local/bin/gpu-detect-profile.sh" ]; then
  . "$HOME/.local/bin/gpu-detect-profile.sh"
fi


# Apply environment variables based on resolved GPU_SETUP
case "$GPU_SETUP" in
  hybrid-intel-nvidia)
    export __GLX_VENDOR_LIBRARY_NAME=nvidia
    export VK_LAYER_NV_optimus=1

    # Detect optional VA-API driver for NVIDIA once
    NVIDIA_VAAPI=$(detect_nvidia_vaapi)

    if [ "$NVIDIA_VAAPI" = "1" ]; then
      export NVD_BACKEND=direct # Requires 'libva-nvidia-driver' package
    fi
    ;;

  hybrid-amd-intel)
    # Allow defaults; uncomment to force Mesa VAAPI
    # export LIBVA_DRIVER_NAME=radeonsi
    # export VDPAU_DRIVER=radeonsi
    ;;

  hybrid-intel-nouveau)
    # Allow defaults
    ;;

  nvidia-only)
    # NVIDIA requires these for proper Wayland/Hyprland support
    export LIBVA_DRIVER_NAME=nvidia
    export __GLX_VENDOR_LIBRARY_NAME=nvidia
    export __GL_VRR_ALLOWED=1
    if [ "$NVIDIA_VAAPI" = "1" ]; then
      export NVD_BACKEND=direct # Requires 'libva-nvidia-driver' package
    fi
    ;;

  amd-only)
    # Allow defaults; uncomment to force Mesa VAAPI
    # export LIBVA_DRIVER_NAME=radeonsi
    # export VDPAU_DRIVER=radeonsi
    ;;

  nouveau-only)
    # Allow defaults
    ;;

  intel-only)
    # Allow defaults (iHD vs i965 auto)
    ;;

  *)
    ;;
esac

export GPU_SETUP
echo "GPU setup detected: $GPU_SETUP"
