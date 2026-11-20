[[ -f ~/.bashrc ]] && . ~/.bashrc
# straight into the desktop on tty1, like an O2 coming out of standby
if [[ -z $DISPLAY && $(tty) = /dev/tty1 && ! -e ~/.no-autostart ]]; then
    exec startx /etc/porygon/session -- -keeptty >~/.xorg.log 2>&1
fi
