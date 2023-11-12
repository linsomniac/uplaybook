# uPlaybook

Unleash the Power of Automation with uPlaybook

In a world where time is precious, uPlaybook emerges as your go-to solution for project
templating and automation.  uPlaybook allows you to streamline your workflows, automate
repetitive tasks, and configure projects with unparalleled ease.

The desired state of the system is specified via a "playbook" (an idea taken from
Ansible).  Running a playbook sets up, updates, or repairs projects or systems.
Command-line argument processing enables playbook specialization at run-time.
In "examples/new-uplaybook" is a sample which creates a skeleton playbook by
running the command: `up new-uplaybook my-example-playbook`.

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

uPlaybook delivers the following ideas:

    - Python syntax
    - First-class CLI argument handling.
    - Declare the state you want to end up at.
    - Tasks communicate whether they have changed something.
    - Changed tasks can trigger a handler (if this config file changes, restart a service).
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
`.uplaybooks/new-uplaybook/playbook`

## State

This is Beta software: The core is done but as it gets real world use things
may change in incompatible ways before final release.

Currently (Nov 2023) I'm working on:

- Documentation.
- Test driving uPlaybook to find rough edges.
- Adding more Tasks.

If you look at it, your feedback would be appreciated.

## Example Playbooks

- [New uPlaybook](examples/new-uplaybook/playbook)

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

### Taks can trigger handlers if they change something

```python
def restart_apache()
    core.service(name="apache2", state="restarted")

fs.template(path="/etc/apache2/sites-enabled/test.conf", src="test.conf.j2").notify(restart_apache)
fs.template(path="/etc/apache2/sites-enabled/other_site.conf", src="other_site.conf.j2").notify(restart_apache)
```

The above will retart apache if either of the config files get created or updated.
It will only restart apache once even if both files get updated.

### Running a playbook displays status of tasks

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
=> run(command=rm -rf testdir, shell=True, ignore_failure=False, change=True)
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

## License

Creative Commons Zero v1.0 Universal
