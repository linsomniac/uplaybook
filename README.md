# uPlaybook

Unleash the Power of Automation with uPlaybook

In a world where time is precious, uPlaybook emerges as your go-to solution for project
templating and automation.  uPlaybook allows you to streamline your workflows, automate
repetitive tasks, and configure projects with unparalleled ease.

The desired state of the system is specified via a "playbook" (optionally including
data and templates).  Playbooks are then run, with command-line arguments providing
runtime customization of the run.  For example, a provided playbook creates
a skeleton playbook with "up new-uplaybook my-example-playbook".

uPlaybook takes ideas from Ansible and Cookiecutter, trading their YAML syntax for
Python. Playbooks are like shell scripts, oriented specifically towards setting up
systems or environments.  Playbooks include CLI argument handling, which traditionally
has been tricky to do well in shell scripts.

Despite its simplicity, uPlaybook doesn't compromise on functionality.  The core
tasks can be augmented by arbitrary Python code for ultimate power.

## Use cases:

- Shell scripts, but declarative rather than command-based.  Built in arg parsing,
  templating, and "handlers" called when changes are made (as in Ansible).
- Project templating.  Think "cookiecutter", but with a declarative scripting.
  For example: It could conditionally create files based on argument values, can
  do "git init" if a directory is created, etc...
- IT Automation.  Current task support for system administration tasks are rudimentary,
  but longer term I plan to add tasks for package installation, service management, etc...

## High-level Ideas

Some core ideas of it:

    - Python syntax
    - First-class CLI argument handling.
    - Declare the state you want to end up at.
    - Tasks communicate whether they have changed something.
    - Changed tasks can trigger a handler (if this file changes, restart a service).
    - Jinja2 templating of arguments and files delivered via fs.copy()
    - Status output.

## Installation

Installation can be done with:

    pip install uplaybook

Or to run from the repository:

    git clone git@github.com:linsomniac/uplaybook.git
    pip install poetry
    poetry shell

The above starts a shell with uPlaybook available to run.

## Getting Started

You can create a skeleton playbook, in the uplaybook git checkout, with:

    up new-uplaybook my-test-playbook

Which creates a "my-test-playbook" directory with the skeleton playbook file
"playbook".  The playbook used to create this skeleton is in
".uplaybooks/new-uplaybook/playbook"

## State

This is Beta software: The core is done but as it gets real world use things
may change in incompatible ways before final release.

Currently (Nov 2023) I'm working on:

- Documentation.
- Test driving uPlaybook to find rough edges.
- Adding more Tasks.

If you look at it, your feedback would be appreciated.

## Examples

## Documentation

[Full uPlaybook Documentation](https://linsomniac.github.com/uplaybook)

## Compared to...

### Ansible

The primary benefits uPlaybook has is using a Python syntax and ease of running against
the local system.  Ansible has a much richer task ecosystem, and the ability to run
plays on many remote systems at once.

### Cookiecutter

uPlaybook has a richer configuration syntax and more flexibility since it is based on the
Python language.  Cookiecutter has more available cookiecutters, and the limited syntax
does provide more safety against what third-party cookiecutters can do when you run them.

### Shell

uPlaybook has first class CLI argument handling, is declarative and the ability (not yet
implemented) to ask what changes the playbook will make, and tries to bring some shell
first class actions into Python.  Shell is better at blindly running commands and
pipelines.

## What Is uPlaybook

Ansible and uPlaybook1 both describe the desired state of the system via a YAML
structure.  This is easy to build tooling around, but is kind of cumbersome, especially
when you try to apply programming paradigms to it like loops, conditionals, and includes.

For example, an Ansible block might look like:

```yaml
- name: haproxy syslog config
  template:
    src: 49-haproxy.conf.j2
    dest: /etc/rsyslog.d/49-haproxy.conf
    owner: root
    group: root
    mode: a=r,u+w
  notify: Restart rsyslog
```

uPlaybook is, currently an experiment, into making a Python-based environment for expressing
similar ideas:

```python
with core.Item(path="/etc/rsyslog.d/49-haproxy.conf"):
    core.template(src="49-haproxy.conf.j2", path="{{path}}", mode="a=r,u+w").notify(restart_syslog)
    core.chown(path="{{path}}", owner="root", group="root")
```

## Installation

Currently, install "up2" by cloning this repo and running: `pip install -e up2`

## Documentation

Documentation, including task documentation, can now be accessed by running
`up2 --up-doc <task-name>` (for example: `up2 --up-doc fs.mkfile`) and the
module documentation including a list of tasks can be gotten from
`up2 --up-doc <module>` (for example: `up2 --up-doc fs`)

## Features

### Uplifting of variables into templating

```python
version = "3.2"
fs.mkdir(path="myprogram-{{version}}")  # Makes directory "myprogram-3.2"
fs.template(path="foo", src="foo.j2")   # "foo.j2" can access "{{version}}"
```

### Jinja2 templating of most arguments

```python
path="/etc/rsyslog.d/49-haproxy.conf"
fs.template(src="{{ path | basename }}.j2")  # src becomes "49-haproxy.conf.j2"
```

### Tasks only take effect if they change the system

```python
fs.mkfile(path="foo")   #  Only takes action if "foo" does not exist
fs.mkfile(path="foo")   #  Never takes action because "foo" would be created above
```

## Taks can trigger handlers if they change something

```python
def restart_apache()
    core.service(name="apache2", state="restarted")

fs.template(path="/etc/apache2/sites-enabled/test.conf", src="test.conf.j2").notify(restart_apache)
fs.template(path="/etc/apache2/sites-enabled/other_site.conf", src="other_site.conf.j2").notify(restart_apache)
```

The above will retart apache if either of the config files get created or updated.
It will only restart apache once even if both files get updated.

## Running a playbook displays status of tasks

```python
core.run("rm -rf testdir")
fs.builder(state="directory", path="testdir", mode="a=rX,u+w")
fs.cd("testdir")
fs.builder(state="exists", path="testfile", mode="a=rX")
fs.chown(path="testfile", group="docker")
fs.builder(state="exists", path="testfile", mode="a=rX", group="sean")
```

Produces the following status output:

```
=> run(command=rm -rf testdir, shell=True, ignore_failures=False, change=True)
==> mkdir(path=testdir, mode=a=rX,u+w, parents=True)
==# chmod(path=testdir, mode=493)
=> builder(path=testdir, mode=a=rX,u+w, state=directory)
=# cd(path=testdir)
==> mkfile(path=testfile, mode=a=rX)
==# chmod(path=testfile, mode=292)
=> builder(path=testfile, mode=a=rX, state=exists)
=> chown(path=testfile, group=docker) (group)
===# chmod(path=testfile, mode=292)
==# mkfile(path=testfile, mode=a=rX)
==# chmod(path=testfile, mode=292)
==> chown(path=testfile, group=sean) (group)
=# builder(path=testfile, mode=a=rX, group=sean, state=exists)

*** RECAP:  total=14 changed=7 failure=0
```

Where ">" in the status means a change occurred, "#" means no change happened, and additional "="
indentations indicate a task triggered by a parent task.  The parent task is the dedented task after
the extra indents (the "builder") tasks above.

## Example:

Example showing what a playbook might look like, and the output of running it
including detecting when no changes are made and updating permissions:

    #!/usr/bin/env python3

    from uplaybook import fs, core

    def test_handler2():
        fs.mkfile('qux')
        fs.mkfile('xyzzy')

    def test_handler():
        fs.mkfile('bar').notify(test_handler2)
        fs.mkfile('baz').notify(test_handler2)

    fs.mkdir("testdir", mode="a=rX,u+w")
    fs.cd('testdir')

    foo = "test"
    fs.mkfile("foo{{foo}}").notify(test_handler)

    fs.makedirs("foodir/bar/baz", mode="a=rX,u+w")
    core.run('date')
    if core.run('true'):
        print('Successfully ran true')
    if not core.run('false', ignore_failures=True):
        print('Successfully ran false')

Which produces the following output:

    [N] sean@seans-laptop ~/p/u/up2 (main)> up2 testpb
    => mkdir(path=testdir, mode=a=rX,u+w)
    =# cd(path=testdir)
    => mkfile(path=foo, mode=None)
    => makedirs(path=foodir/bar/baz, mode=a=rX,u+w)
    => run(command=date, shell=True, ignore_failures=False, change=True)
    Sat Oct  7 06:09:34 AM MDT 2023

    => run(command=true, shell=True, ignore_failures=False, change=True)
    Successfully ran true
    =! run(command=false, shell=True, ignore_failures=True, change=True) (failure ignored)
    Successfully ran false
    >> *** Starting handler: test_handler
    => mkfile(path=bar, mode=None)
    => mkfile(path=baz, mode=None)
    >> *** Starting handler: test_handler2
    => mkfile(path=qux, mode=None)
    => mkfile(path=xyzzy, mode=None)
    >> *** Done with handlers

    *** RECAP:  total=11 changed=10 failure=0
    [N] sean@seans-laptop ~/p/u/up2 (main)> up2 testpb
    =# mkdir(path=testdir, mode=a=rX,u+w)
    =# cd(path=testdir)
    =# mkfile(path=foo, mode=None)
    =# makedirs(path=foodir/bar/baz, mode=a=rX,u+w)
    => run(command=date, shell=True, ignore_failures=False, change=True)
    Sat Oct  7 06:09:55 AM MDT 2023

    => run(command=true, shell=True, ignore_failures=False, change=True)
    Successfully ran true
    =! run(command=false, shell=True, ignore_failures=True, change=True) (failure ignored)
    Successfully ran false

    *** RECAP:  total=7 changed=3 failure=0
