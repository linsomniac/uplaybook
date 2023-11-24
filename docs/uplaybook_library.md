# Playbook Library

## Playbook Search Path

uPlaybook searches for playbooks by using the $UP_PLAYBOOK_PATH environment variable, with
the default being:
`.:.uplaybooks:~/.config/uplaybook:~/.config/uplaybook/library:/etc/uplaybook`

This means `up` will look for playbooks in:

- The current directory.
- A `.uplaybooks` directory in the current directory.  This is a great place to put
  project-specific playbooks.
- The directory `.config/uplaybook` in your home directory.  This is where you would want
  to put playbooks that you might use anywhere, for example a playbook that creates a new
  project scaffolding.  The recommended location for playbooks you develop, which you
  want to be available system-wide (as opposed to project-specific playbooks).
- The directory `.config/uplaybook/library` in your home directory.  The recommended
  location for playbooks you download.
- The directory `/etc/uplaybook` is a location for system-wide playbooks.

For example, if you want to install the example "new-uplaybook" playbook from the
uPlaybook github repository, you could do:

    mkdir -p ~/.config/uplaybook/library
    cp -av examples/new-uplaybook ~/.config/uplaybook/library/

## Sharing Playbooks with Git

To share playbooks among hosts, you may wish to put your `~/.config/uplaybook` directory
under git version control.  Exclude the `library` subdirectory if you are using it for
playbooks you have downloaded:

    cd ~/.config/uplaybook
    git init .
    echo /library/ >.gitignore
    git add .
    git commit

<!-- vim: set tw=90: -->
