# Getting Started

## Installing

Typically you are able to install uPlaybook by running: `python3 -m pip install uplaybook`

For more detailed installation instructions, see [Installing uPlaybook](installing.md)

## Running

You probably don't have any playbooks available if you are a new user.  So to get
started you probably want to clone the git repo to get an example playbook:

    cd /tmp
    git clone git@github.com:linsomniac/uplaybook.git
    cd uplaybook
    up

This should produce a list of available playbooks, similar to:

    usage: up [--help] [--up-full-traceback] [--up-list-playbooks] [--up-debug]
           [--up-docs [DOCS_ARG]] [playbook]

    Available playbooks:
      - new-uplaybook (.uplaybooks/new-uplaybook)
          Create a new uplaybook.

You can see what command-line arguments are available by running `up new-uplaybook
--help`:

    usage: up:new-uplaybook [-h] [--git | --no-git] [--single-file | --no-single-file]
           [--force | --no-force] playbook_name

    Create a new uplaybook. This playbook creates a new, example, uplaybook. This can be
    used as a skeleton to create new uplaybooks.

    positional arguments:
      playbook_name         Name of playbook to create, creates directory of this name.

    options:
      -h, --help            show this help message and exit
      --git, --no-git       Initialize git (only for directory-basd playbooks). (default: False)
      --single-file, --no-single-file
                            Create a single-file uplaybook rather than a directory. (default: False)
      --force, --no-force   Reset the playbook back to the default if it already exists (default is to abort if playbook
                            already exists). (default: False)

You can create a test "skeleton" playbook called "my-test-playbook" by running `up
new-uplaybook my-test-playbook`:

    $ up new-uplaybook my-test-playbook
    =! exists(path=my-test-playbook, ignore_failure=True) (failure ignored)
    => mkdir(path=my-test-playbook, parents=True)
    =# cd(path=my-test-playbook)
    => cp(path=playbook, src=playbook.j2, template=True, template_filenames=True, recursive=True) (Contents)
    =# cd(path=/home/sean/projects/uplaybook)
    >> *** Starting handler: git_init
    =# cd(path=my-test-playbook)
    => run(command=git init, shell=True, ignore_failure=False, change=True)
    Initialized empty Git repository in /home/sean/projects/uplaybook/my-test-playbook/.git/
    => run(command=git add ., shell=True, ignore_failure=False, change=True)
    =# cd(path=/home/sean/projects/uplaybook)
    >> *** Done with handlers

    *** RECAP:  total=9 changed=4 failure=0

Look in the `my-new-playbook` directory to see the sample playbook, edit the
`my-new-playbook/playbook` file to work on your new playbook:

    $ ls -l my-test-playbook/
    .rwxrwxr-x sean sean 561 B Sun Nov 12 06:38:06 2023 playbook

You can modify the playbook and run it with `up my-new-playbook`

<!-- vim: set tw=90: -->
