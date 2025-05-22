#####################################
##==> Variables
#####################################
function shenv() { export $1=$2 }
source ~/.env

#####################################
##==> Aliases
#####################################
alias cls="clear"
alias g="git"
alias n="nvim"
alias m="micro"
alias ls="lsd"
alias tree="lsd --tree"
alias -g ...='../..'
alias -g ....='../../..'
alias -g .....='../../../..'
setopt autocd

#####################################
##==> binds
#####################################
bindkey '^[[1;5C' forward-word
bindkey '^[[1;5D' backward-word

#####################################
##==> Custom Functions
#####################################
function wget() {
    command wget --hsts-file="${XDG_DATA_HOME}/wget-hsts" "$@"
}

function nvidia-settings() {
    mkdir -p "${XDG_CONFIG_HOME}/nvidia/"
    command nvidia-settings --config="${XDG_CONFIG_HOME}/nvidia/settings" "$@"
}

function cd() {
    if [[ $@ == "...*" ]]; then
        builtin cd "${@//../..}"
    else
        builtin cd "$@"
    fi
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
eval "$(starship init zsh)"
pokemon-colorscripts --no-title -s -r 1,3,6

#####################################
##==> Plugins
#####################################
[[ -f /usr/share/zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh ]] && \
    source /usr/share/zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh

[[ -f /usr/share/zsh/plugins/zsh-history-substring-search/zsh-history-substring-search.zsh ]] && \
    source /usr/share/zsh/plugins/zsh-history-substring-search/zsh-history-substring-search.zsh

[[ -f /usr/share/zsh/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh ]] && \
    source /usr/share/zsh/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh

[[ -f "$HOME/.config/zsh/themes/meowrch.zsh" ]] && \
    source "$HOME/.config/zsh/themes/meowrch.zsh"
