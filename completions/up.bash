#  Place in ~/.bashrc or in /etc/bash_completion.d/
#  or "source up.bash" in your for a temporary completion setup

# up-completion.bash
_up_completion() {
    #echo "Completion started $COMP_CWORD" >&2
    if [ ${COMP_CWORD} -eq 1 ]; then
        local playbooks=$(up --up-list-playbooks)
        #echo "Playbooks: $playbooks" >&2
        COMPREPLY=($(compgen -W "$playbooks" -- "${COMP_WORDS[COMP_CWORD]}"))
        #echo "COMPREPLY: ${COMPREPLY[@]}" >&2
    fi
}

complete -F _up_completion up
