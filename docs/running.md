# Running

## Listing playbooks

Running "up" will list available playbooks and their descriptions:

    $ up
    usage: up [--help] [--up-full-traceback] [--up-list-playbooks] [--up-debug] [--up-docs [DOCS_ARG]] [playbook]

    Available playbooks:
      - install-apache-module (.uplaybooks/install-apache-module)
          Install and enable an Apache module
      - new-uplaybook (.uplaybooks/new-uplaybook)
          Create a new uplaybook.

## Getting Playbook Help

Run with a playbook and `--help` to get more information about a playbook and any
arguments it takes:

    $ up new-uplaybook --help
    usage: up:new-uplaybook [-h] [--git | --no-git] [--single-file | --no-single-file] [--force | --no-force] playbook_name

    Create a new uplaybook. This playbook creates a new, example, uplaybook. This can be
    used as a skeleton to create new uplaybooks.

    positional arguments:
      playbook_name         Name of playbook to create, creates directory of this name.

    options:
      -h, --help            show this help message and exit
      --git, --no-git       Initialize git (only for directory-basd playbooks). (default: False)
      --single-file, --no-single-file
                            Create a single-file uplaybook rather than a directory. (default: False)
      --force, --no-force   Reset the playbook back to the default if it already exists
                            (default is to abort if playbook already exists). (default: False)

## Getting Task Help

Run `up --up-docs module.task` to get help about a task:

    $ up --up-docs fs.cp
    # fs.cp

    Copy the `src` file to `dst`, optionally templating the contents in `src`.
    [...]

Or to get a list of tasks in a module, specify `up --up-docs module`

    $ up --up-docs fs
    Filesystem Related Tasks

    This module contains uPlaybook tasks that are related to file system operations.

    ## Available Tasks:

    - fs.builder - All-in-one filesystem builder.
    - fs.cd - Change working directory to `dst`.
    - fs.chmod - Chan.cpge permissions of `dst`.

## "Command" (she-bang) Playbooks

uPlaybook can be run as a "script" on Unix-like OSes by adding a "she-bang" line
`#!/usr/bin/env -S python3 -m uplaybook.cli`.

    #!/usr/bin/env -S python3 -m uplaybook.cli
    [rest of playbook here]

If you `chmod 755` the playbook file, you can then directly run the playbook file as a
command.  For example if your playbook is in a file called "myplaybook", you can now run
`myplaybook` instead of `up myplaybook`.  This would primarily be used for file-based
playbooks, not directory-based, as for directory playbooks you'd need to do
`path/to/directory/playbook`; that will work it just isn't conventional.

<!-- vim: set tw=90: -->
