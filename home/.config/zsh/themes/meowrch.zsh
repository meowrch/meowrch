ZSH_HIGHLIGHT_HIGHLIGHTERS=(main cursor)
typeset -gA ZSH_HIGHLIGHT_STYLES

# Main styles
ZSH_HIGHLIGHT_STYLES[default]='fg=#cdd6f4'
ZSH_HIGHLIGHT_STYLES[unknown-token]='fg=#f38ba8'

# Commands and functions
ZSH_HIGHLIGHT_STYLES[command]='fg=#89b4fa'
ZSH_HIGHLIGHT_STYLES[alias]='fg=#89b4fa'
ZSH_HIGHLIGHT_STYLES[builtin]='fg=#89b4fa'
ZSH_HIGHLIGHT_STYLES[function]='fg=#89b4fa'

# Parameters and arguments
ZSH_HIGHLIGHT_STYLES[single-hyphen-option]='fg=#f2cdcd'
ZSH_HIGHLIGHT_STYLES[double-hyphen-option]='fg=#f2cdcd'
ZSH_HIGHLIGHT_STYLES[path]='fg=#cdd6f4,underline'
ZSH_HIGHLIGHT_STYLES[path_pathseparator]='fg=#f38ba8'

# Keywords and operators
ZSH_HIGHLIGHT_STYLES[reserved-word]='fg=#f38ba8'
ZSH_HIGHLIGHT_STYLES[redirection]='fg=#f5c2e7'
ZSH_HIGHLIGHT_STYLES[commandseparator]='fg=#f38ba8'

# Strings and quotes
ZSH_HIGHLIGHT_STYLES[single-quoted-argument]='fg=#a6e3a1'
ZSH_HIGHLIGHT_STYLES[double-quoted-argument]='fg=#a6e3a1'
ZSH_HIGHLIGHT_STYLES[back-quoted-argument]='fg=#cba6f7'

# Comments
ZSH_HIGHLIGHT_STYLES[comment]='fg=#7f849c'

# Errors and warnings
ZSH_HIGHLIGHT_STYLES[unknown-token]='fg=#f38ba8'
ZSH_HIGHLIGHT_STYLES[arg0]='fg=#cdd6f4'

# Autocomplete
ZSH_HIGHLIGHT_STYLES[autodirectory]='fg=#fab387,italic'
ZSH_HIGHLIGHT_STYLES[history-expansion]='fg=#cba6f7'

# Special styles
ZSH_HIGHLIGHT_STYLES[globbing]='fg=#cdd6f4'
ZSH_HIGHLIGHT_STYLES[assign]='fg=#cdd6f4'
ZSH_HIGHLIGHT_STYLES[precommand]='fg=#89b4fa,italic'

# Cursor
ZSH_HIGHLIGHT_STYLES[cursor]='fg=#cdd6f4'

# Additional settings for full compliance
ZSH_HIGHLIGHT_STYLES[suffix-alias]='fg=#89b4fa'
ZSH_HIGHLIGHT_STYLES[global-alias]='fg=#89b4fa'
ZSH_HIGHLIGHT_STYLES[command-substitution-delimiter]='fg=#cdd6f4'
ZSH_HIGHLIGHT_STYLES[back-quoted-argument-delimiter]='fg=#f38ba8'
