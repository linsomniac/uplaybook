# Playbook Basics

## A Basic Playbook

A playbook is a Python source file, let's take a look at a simple playbook that sets up a
simple new project scaffold:

```python
#!/usr/bin/env python3

#  The Python docstring: The first line is used as the short description of the playbook
#  and displayed when the user types "up" to get a list of playbooks.  The full docstring
#  is displayed when the user types "up my-playbook --help".
"Create a new project"

#  load the "core" and "fs" uplaybook task libraries
from uplaybook import fs, core

project_name = "my-test-project"

#  This is a "handler" (in Ansible terms).
def initialize_project():
    with fs.cd(project_name):
        #  These are run within the "project_name" directory
        fs.mkfile("README")
        core.run("git init")
        core.run("git add .")

#  make a directory called "my-test-project" and notify the handler
fs.mkdir(project_name).notify(initialize_project)
```

This playbook creates a `my-test-project` playbook, and puts an empty `README` file in it,
then initializes git.

The `notify()` makes this playbook declarative.  A `notify()` sets up a function (known as
a "handler") to be called later, **only when a task makes a change**.  uPlaybook Tasks
will determine if they change the system (in this case, if the directory already exists,
the `mkdir()` will be a no-op).  The `initialize_project()` will be called only if the
directory is created.

This is a useful trait of a playbook because you don't want to overwrite the `README`, or
re-run the `git` commands if the project has already been created.

Output:

```bash
$ up my-test-playbook
=> mkdir(dst=my-test-project, parents=True)
>> *** Starting handler: initialize_project
=# cd(dst=my-test-project)
=> mkfile(dst=README)
=> run(command=git init, shell=True, ignore_failures=False, change=True)
Initialized empty Git repository in /home/sean/projects/uplaybook/my-test-project/.git/
=> run(command=git add ., shell=True, ignore_failures=False, change=True)
=# cd(dst=/home/sean/projects/uplaybook)
>> *** Done with handlers

*** RECAP:  total=6 changed=4 failure=0
$ #  Running it a second time:
$ up my-test-playbook
=# mkdir(dst=my-test-project, parents=True)

*** RECAP:  total=2 changed=0 failure=0
```

<!-- vim: set tw=90: -->
