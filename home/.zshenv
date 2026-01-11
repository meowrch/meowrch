#####################################
##==> Environment
#####################################
export ZDOTDIR="${XDG_CONFIG_HOME:-$HOME/.config}/zsh"

setopt allexport
eval "$(/usr/lib/systemd/user-environment-generators/30-systemd-environment-d-generator)"
unsetopt allexport
