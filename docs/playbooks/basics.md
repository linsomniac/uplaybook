# Playbook Basics

## A Basic Playbook

A playbook is a Python source file, let's take a look at a simple playbook that sets up a
simple new project scaffold:

```python
#!/usr/bin/env -S python3 -m uplaybook.cli

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

## Being Declarative

The `notify()` makes this playbook declarative.  A `notify()` sets up a function (known as
a "handler") to be called later, **only when a task makes a change**.  uPlaybook Tasks
will determine if they change the system (in this case, if the directory already exists,
the `mkdir()` will be a no-op).  The `initialize_project()` will be called only if the
directory is created.

This is a useful trait of a playbook because you don't want to overwrite the `README`, or
re-run the `git` commands if the project has already been created.

Output of the above playbook, if run twice, is:

```bash
$ up my-test-playbook
=> mkdir(path=my-test-project, parents=True)
>> *** Starting handler: initialize_project
=# cd(path=my-test-project)
=> mkfile(path=README)
=> run(command=git init, shell=True, ignore_failure=False, change=True)
Initialized empty Git repository in /home/sean/projects/uplaybook/my-test-project/.git/
=> run(command=git add ., shell=True, ignore_failure=False, change=True)
=# cd(path=/home/sean/projects/uplaybook)
>> *** Done with handlers

*** RECAP:  total=6 changed=4 failure=0
$ #  Running it a second time:
$ up my-test-playbook
=# mkdir(path=my-test-project, parents=True)

*** RECAP:  total=2 changed=0 failure=0
```

Note the first run creates the directory, creates the README, and runs git.  The second
run skips the `mkdir` (that's what the "=#" denotes: no change was made), and because of
that it does not run the handler.

## Calling Tasks

The most basic component of playbooks is calling tasks, such as `fs.mkdir` or
`core.run` above.  `core` and `fs` are uPlaybook modules of "core functionality" and
"filesystem tasks" respectively.

These tasks are the heart of uPlaybook.  All uPlaybook tasks are declarative, as described
[above](#being-declarative).

## Task Return()s

Tasks return a object called `Return()`.  This has some notable features:

- It has a `notify()` method which registers a [handler](#handlers) if the task determines
  it has changed the system.
- It can be checked to see if the task failed.  This only applies to tasks that can ignore
  failures, like [core.run](../tasks/core.md#uplaybook.core.run).  For example: `if
  not core.run("false", ignore_failur=False):`
- Some tasks can be used as context managers, see [fs.cd](../tasks/fs.md#uplaybook.fs.cd)
- Capture output: the `output` attribute stores output of the task, see
  [core.run](../tasks/core.md#uplaybook.core.run) for an example.
- Extra data: The `extra` attribute stores additional information the task may return, see
  for example (fs.stat)[/tasks/fs.md#uplaybook.fs.stat] stores information about the file in
  `extra`.

## Extra Return Data

Some tasks return extra data in the `extra` attribute of the return object.  For example:

```python
stats = fs.stat("{{project_dir}}/README")
print(f"Permissions: {stats.extra.perms:o}")
if stats.S_ISDIR:
    core.fail(msg="The README is a directory, that's unexpected!")
```

## Ignoring Failures

Some tasks, such as [core.run](../tasks/core.md#uplaybook.core.run), take an `ignore_failure`
option for one-shot failure ignoring.

There is also an "IgnoreFailure" context manager to ignore failures for a block of
tasks:

```python
with core.IgnoreFailures():
    core.run("false")
    if not mkdir("/root/fail"):
        print("You are not root")
```

## Getting Help

The `up` command-line can be used to get documentation on the uPlaybook tasks with the
`--up-doc` argument.  For example:

    up --up-doc fs
    [Displays a list of tasks in the "fs" module]
    up --up-doc core
    [Displays a list of tasks in the "core" module]
    up --up-doc core.run
    [Dislays documentation for the "core.run" task]

## Handlers

An idea taken from Ansible, handlers are functions that are called only if changes are
made to the system.  They are deferred, either until the end of the playbook run, or until
[core.flush_handlers](../tasks/core.md#uplaybook.core.flush_handlers) is called.

They are deferred so that multiple tasks can all register handlers, but only run them once
rather than running multiple times.  For example, if you are installing multiple Apache
modules, and writing several configuration files, these all may "notify" the
"restart_apache" handler, but only run the handler once:

```python
def restart_apache():
    core.run("systemctl restart apache2")
core.run("apt -y install apache2", creates="/etc/apache2").notify(restart_apache)
fs.cp(src="site1.conf.j2", path="/etc/apache2/sites-enabled/site1.conf").notify(restart_apache)
fs.cp(src="site2.conf.j2", path="/etc/apache2/sites-enabled/site2.conf").notify(restart_apache)
fs.cp(src="site3.conf.j2", path="/etc/apache2/sites-enabled/site3.conf").notify(restart_apache)
core.flush_handlers()
#  ensure apache is running
run("wget -O /dev/null http://localhost/")
```

Handlers that are `.notify()`ed on a task only get registered if the task changes the
system.  In this way, handlers are conditional on the task having performed some action.
You can also notify a handler directly:

```python
core.notify(handler)
```

Handlers can be either a single handler function or a list of handlers:

```python
fs.cp(src="site.conf.j2", path="/etc/apache2/sites-available/site.conf").notify([
    a2ensite,
    restart_apache
    ])
```

## Arguments

Playbooks can include arguments and options for customizing the playbook run.  For
example:

    core.playbook_args(
            core.Argument(name="playbook_name",
                          description="Name of playbook to create, creates directory of this name."),
            core.Argument(name="git", default=False, type="bool",
                          description="Initialize git (only for directory-basd playbooks)."),
            core.Argument(name="single-file", default=False, type="bool",
                          description="Create a single-file uplaybook rather than a directory."),
            core.Argument(name="force", default=False, type="bool",
                          description="Reset the playbook back to the default if it "
                          "already exists (default is to abort if playbook already exists)."),
            )

This set up an argument of "playbook_name" and options of "--git", "--single-file", and
"--force".

These can be accessed as `ARGS.playbook_name`, `ARGS.git`, `ARGS.single_file`, etc...
Also note that `ARGS` can be imported from uplaybook to keep Language Server from
complaining: `from uplaybook import ARGS`.

!!! Note "Note on dash in name"

    A dash in the argument name is converted to an underscore in the `ARGS` list.

See [core.Argument](../tasks/core.md#uplaybook.core.Argument) for full documentation.

## Item Lists

Another idea taken from Ansible is looping over items.  See
[core.Item](../tasks/core.md#uplaybook.core.Item) and
[fs.builder](../tasks/fs.md#uplaybook.fs.builder) for some examples on how to effectively use
item lists.

Example:

    for item in [
            core.Item(path="foo", action="directory", owner="nobody"),
            core.Item(path="bar", action="exists"),
            core.Item(path="/etc/apache2/sites-enabled/foo", notify=restart_apache),
            ]:
        fs.builder(**item)

fs.builder is an incredibly powerful paradigm for managing the state on files and
directories on a system.

## Keeping Playbooks Declarative

You have the flexibility to determine whether to make your playbooks declarative or not.

The benefits of declarative playbooks are that they can be updated and re-run to update
the system configuration, for "configuration as code" usage.  For example: you could have
a playbook that sets up your user environment, or configures a web server.  Rather than
updating the configurations directly, if your configuration is a playbook you can update
the playbook and then run it on system reinstallation, or across a cluster of systems.

However, as you have the full power of Python at your command, you need to be aware of
whether you are trying to make a declarative playbook or not.

For example, a playbook that creates scaffolding for a new project may not be something
you can re-run.  Since scaffolding is a starting point for user customization, it may not
be possible or reasonable to re-run the playbook at a later time.  In this case, you may
wish to detect a re-run, say by checking if the project directory already exists, and
abort the run.

To make a declarative playbook, you need to ensure that all steps of the playbook,
including Python code, is repeatable when re-run.

<!-- vim: set tw=90: -->
