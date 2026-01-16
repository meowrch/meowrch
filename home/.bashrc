#####################################
##==> Environment
#####################################
set -a
eval "$(/usr/lib/systemd/user-environment-generators/30-systemd-environment-d-generator)"
set +a

#####################################
##==> Aliases
#####################################
alias cls="clear"
alias g="git"
alias n="nvim"
alias m="micro"
alias ls="lsd"
alias tree="lsd --tree"
alias ...='cd ../..'
alias ....='cd ../../..'
alias .....='cd ../../../..'
shopt -s autocd

#####################################
##==> binds
#####################################
bind '"\e[1;5C": forward-word'   # Ctrl+→
bind '"\e[1;5D": backward-word'  # Ctrl+←

#####################################
##==> Custom Functions
#####################################
wget() {
    command wget --hsts-file="${XDG_DATA_HOME}/wget-hsts" "$@"
}

nvidia-settings() {
    mkdir -p "${XDG_CONFIG_HOME}/nvidia/"
    command nvidia-settings --config="${XDG_CONFIG_HOME}/nvidia/settings" "$@"
}

cd() {
    case $1 in
        ...*) builtin cd "${1//../..}" ;;
        *) builtin cd "$@" ;;
    esac
}

function y() {
	local tmp="$(mktemp -t "yazi-cwd.XXXXXX")" cwd
	yazi "$@" --cwd-file="$tmp"
	IFS= read -r -d '' cwd < "$tmp"
	[ -n "$cwd" ] && [ "$cwd" != "$PWD" ] && builtin cd -- "$cwd"
	rm -f -- "$tmp"
}

#####################################
##==> Shell Customization
#####################################
eval "$(starship init bash)"
pokemon-colorscripts --no-title -s -r 1,3,6

#####################################
##==> Plugins
#####################################
if [ -f /usr/share/bash-completion/bash_completion ]; then
    source /usr/share/bash-completion/bash_completion
fi
