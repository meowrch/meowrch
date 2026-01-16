#!/bin/sh

xrdb merge $HOME/.Xresources
xsettingsd &
dunst &

##==> Picom 
##########################################################
GPU_PROFILE="${XDG_BIN_HOME:-$HOME/.local/bin}/gpu-detect-profile.sh"
[ -x "$GPU_PROFILE" ] && GPU_SETUP="$("$GPU_PROFILE")" || GPU_SETUP="unknown"

case "$GPU_SETUP" in
  nvidia-only|hybrid-intel-nvidia)
    # NVIDIA: full optimization with sync-fence
    picom -b --backend glx --vsync \
      --use-damage \
      --xrender-sync-fence \
      --glx-no-stencil \
      --glx-no-rebind-pixmap\
      --config $HOME/.config/bspwm/picom.conf &
    ;;
  amd-only|hybrid-amd-intel)
    # AMD/Mesa: no sync-fence, no rebind-pixmap (glitches on AMDGPU)
    picom -b --backend glx --vsync \
      --use-damage \
      --glx-no-stencil \
      --glx-use-copysubbuffer-mesa \
      --config $HOME/.config/bspwm/picom.conf &
    ;;
  intel-only)
    # Intel iGPU: aggressive flags for modern GPUs (Gen 9+)
    # WARNING: If you see artifacts/transparency bugs on older Intel:
    #   - Remove --glx-no-stencil
    #   - Remove --glx-no-rebind-pixmap
    #   - Or switch to: --backend xrender
    picom -b --backend glx --vsync \
      --use-damage \
      --glx-no-stencil \
      --glx-no-rebind-pixmap \
      --config $HOME/.config/bspwm/picom.conf &
    ;;
  nouveau-only|hybrid-intel-nouveau)
    # Nouveau: glx + damage, no extras
    picom -b --backend glx --vsync \
      --use-damage \
      --config $HOME/.config/bspwm/picom.conf &
    ;;
  *)
    # Fallback: safe xrender backend
    picom -b --backend xrender --vsync \
    	--config $HOME/.config/bspwm/picom.conf &
    ;;
esac
##########################################################

sh ${XDG_BIN_HOME:-$HOME/bin}/toggle-bar.sh --start &
sh ${XDG_BIN_HOME:-$HOME/bin}/polkitkdeauth.sh & # authentication dialogue for GUI apps
sh ${XDG_BIN_HOME:-$HOME/bin}/set-wallpaper.sh --current & # set current wallpaper