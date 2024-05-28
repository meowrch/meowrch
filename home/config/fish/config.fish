#####################################
##==> General Environment Settings
#####################################
set -gx LANG en_US.UTF-8
set -gx MICRO_TRUECOLOR 1
set -gx _JAVA_AWT_WM_NONREPARTENTING 1
set -gx _JAVA_OPTIONS '-Dawt.useSystemAAFontSettings=on -Dswing.aatext=true'

#####################################
##==> Aliases
#####################################
alias cls="clear"
alias g="git"
alias n="nvim"
alias m="micro"
alias syslog_emerg="sudo dmesg --level=emerg,alert,crit"
alias syslog="sudo dmesg --level=err,warn"
alias xlog='grep "(EE)\|(WW)\|error\|failed" ~/.local/share/xorg/Xorg.0.log'
alias vacuum="journalctl --vacuum-size=100M"
alias vacuum_time="journalctl --vacuum-time=2weeks"

#####################################
##==> Custom Functions
#####################################
function yy
    set tmp (mktemp -t "yazi-cwd.XXXXXX")
    yazi $argv --cwd-file="$tmp"
    if set cwd (cat -- "$tmp"); and [ -n "$cwd" ]; and [ "$cwd" != "$PWD" ]
        cd -- "$cwd"
    end
    rm -f -- "$tmp"
end

function run_in_alacritty
    # Проверяем, используется ли терминал Alacritty
    if test "$TERM" = "alacritty"
        # Выполняем команды, переданные в качестве аргументов к этой функции
        eval $argv
    end
end

#####################################
##==> Universal Variables
#####################################
set -U fish_greeting ''
set -gx EDITOR micro
set -gx VISUAL micro
set -gx BROWSER /usr/bin/firefox

#####################################
##==> Interactive Session Settings
#####################################
if status is-interactive
   # Commands to run in interactive sessions can go here
end

#####################################
##==> Shell Customization
#####################################
starship init fish | source

#####################################
##==> Development Tools
#####################################
##==> Pyenv
pyenv init - | source

#####################################
##==> Fun Stuff
#####################################
run_in_alacritty pokemon-colorscripts --no-title -s -r

#####################################
##==> End
#####################################
functions -e run_in_alacritty
