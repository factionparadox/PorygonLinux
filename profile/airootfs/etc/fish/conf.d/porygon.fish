# Porygon's fish setup (winterm runs fish; logins on the text consoles keep bash)
status is-interactive; or exit

set -g fish_greeting ""
# Porygon's colours
set -g fish_color_command 5496ce
set -g fish_color_param f0f2f8
set -g fish_color_quote f7b2c2
set -g fish_color_error ec809a --bold
set -g fish_color_comment 8f8798
set -g fish_color_operator 96c4ea
set -g fish_color_autosuggestion 6e6878
set -g fish_pager_color_prefix ec809a --bold

function fish_prompt
    set -l last $status
    set_color ec809a; printf '%s' $USER
    set_color 8f8798; printf '@'
    set_color 5496ce; printf '%s ' (prompt_hostname)
    set_color f0f2f8; printf '%s' (prompt_pwd)
    if test $last -ne 0
        set_color ec809a; printf ' [%s]' $last
    end
    set_color f7b2c2; printf ' > '
    set_color normal
end

# short forms for Porygon's own commands
abbr -a up upgrade
abbr -a in 'upgrade install'
abbr -a undo 'upgrade undo'
abbr -a ff fastfetch
