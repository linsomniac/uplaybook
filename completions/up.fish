function __fish_up_get_playbooks
    up --up-list-playbooks
end

function __fish_up_completions
    for playbook in (__fish_up_get_playbooks)
        echo $playbook
    end
end

complete -c up -n '__fish_use_subcommand' -a '(__fish_up_completions)' --description 'List of playbooks'
