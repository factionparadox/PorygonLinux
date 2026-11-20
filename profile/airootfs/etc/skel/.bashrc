[[ $- != *i* ]] && return
alias ls='ls --color=auto'
PS1='\[\e[38;2;120;160;210m\]\u@\h\[\e[0m\]:\w\$ '
