#
# ~/.bashrc
#

# Export shared environment variables
#########################################
function shenv() { export "$1=$2"; }

# Load environment variables from .env file
source ~/.env
#########################################

# Aliases
#########################################
alias ls='ls --color=auto'
alias grep='grep --color=auto'
#########################################

# Pyenv
#########################################
if command -v pyenv 1>/dev/null 2>&1; then
   eval "$(pyenv init -)" 
fi
#########################################

# Prompt settings
set PS1='[\u@\h \W]\$ '

# If not running interactively, don't do anything
[[ $- != *i* ]] && return