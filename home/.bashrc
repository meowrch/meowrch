#
# ~/.bashrc
#

# Export shared environment variables
#########################################
function shenv() { export "$1=$2"; }

# Load environment variables from .env file
source ~/.env
#########################################

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

# Aliases
alias ls='ls --color=auto'
alias grep='grep --color=auto'

# Prompt settings
set PS1='[\u@\h \W]\$ '