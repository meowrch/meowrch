#####################################
##==> Environment
#####################################
for line in (/usr/lib/systemd/user-environment-generators/30-systemd-environment-d-generator)
    set -l parts (string split -m 1 '=' -- $line)
    if test (count $parts) -eq 2
        set -l value (string trim -c '"' -- $parts[2])
        set -gx $parts[1] $value
    end
end

#####################################
##==> Aliases
#####################################
alias cls="clear"
alias g="git"
alias n="nvim"
alias m="micro"
alias ls="lsd"
alias tree="lsd --tree"
alias ssh="kitty +kitten ssh"

#####################################
##==> Custom Functions
#####################################
function wget
    command wget --hsts-file="$XDG_DATA_HOME/wget-hsts" $argv
end

function nvidia-settings
    mkdir -p $XDG_CONFIG_HOME/nvidia/
    command nvidia-settings --config="$XDG_CONFIG_HOME/nvidia/settings" $argv
end

function y
	set tmp (mktemp -t "yazi-cwd.XXXXXX")
	yazi $argv --cwd-file="$tmp"
	if read -z cwd < "$tmp"; and [ -n "$cwd" ]; and [ "$cwd" != "$PWD" ]
		builtin cd -- "$cwd"
	end
	rm -f -- "$tmp"
end

#####################################
##==> Shell Customization
#####################################
starship init fish | source
set fish_greeting

#####################################
##==> Fun Stuff
#####################################
pokemon-colorscripts --no-title -s -r 1,3,6
