<p align="center"><img src="docs/assets/logo.png" width="25%" height="25%" /><br />uPlaybook</p>

# Unleash the Power of Automation with uPlaybook

uPlaybook (pronounced "Micro Playbook") fits in between templaters like Cookiecutter and
full "fleet level" Configuration Management/Infrastructure as Code ecosystem like Ansible.
If Ansible was a shell script: you'd have uPlaybook.

uPlaybook only targets running on a
single system, so the complexities of managing your "fleet inventory" are gone.  On top of
that is

uPlaybook consists of "playbooks" of declarative "tasks" with the full power of Python,
providing for a richer scripting experience than YAML (as done in Ansible).  The
declarative nature allows you to specify the desired state of a system or service, and the
playbook will make the required changes.  Modify the playbook and re-run it to gain new
state, and keep the playbook in git to version and reuse it.

# Benefits

- Targets running on the local system: Does away with the complexities of managing a
  "fleet infrastructure".
- Playbook discoverability: Run "up" and a list of available playbooks is displayed.
  System, user, and project level playbooks are found via a search path.
- Argument handling: Easy CLI argument handling, playbooks can create project scaffolding,
  deploy and configure Apache modules, etc...
- Shell scripts, but declarative rather than command-based.  Built in arg parsing,
  templating, and "handlers" called when changes are made (as in Ansible).

# Use-cases

- Streamline your workflows
- Automate repetitive tasks
- Configure projects
- Install and deploy software or services
- Manage workstation or server installation and configuration
- Project templating.
- IT Automation.

Command-line argument processing enables playbook specialization at run-time.
In "examples/new-uplaybook" is a sample which creates a skeleton playbook by
running the command: `up new-uplaybook my-example-playbook`.

uPlaybook takes ideas from Ansible and Cookiecutter, trading their YAML syntax for
Python. Playbooks are like shell scripts, oriented specifically towards setting up
systems or environments.  Playbooks include CLI argument handling, which traditionally
has been tricky to do well in shell scripts.

Despite its simplicity, uPlaybook doesn't compromise on functionality.  The core
tasks can be augmented by arbitrary Python code for ultimate power.

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

    pipx install uplaybook

or:

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

## Documentation

[Full uPlaybook Documentation](https://linsomniac.github.com/uplaybook)

## Simple Examples

Deploy an Apache site:

```python
from uplaybook import fs, core, pyinfra

#  Restart apache, but only if the site config or symlink to sites-enabled notify
#  that it has changed
def restart_apache():
    pyinfra.systemd.service(service="apache2", restarted=True)

pyinfra.apt.packages(packages=["apache2"])
fs.write(src="my-site.conf.j2", path="/etc/apache2/sites-available/my-site.conf").notify(restart_apache)
fs.ln(src="/etc/apache2/sites-available/my-site.conf", path="/etc/apache2/sites-enabled/", symbolic=True).notify(restart_apache)
```

Enable an Apache module:

```python
from uplaybook import fs, core, pyinfra

core.playbook_args(
        core.Argument(name="module_name", description="Name of module"),
        core.Argument(name="remove", type="bool", default=False,
                      description="Remove the module rather than install it"),
        )

def restart_and_enable_apache():
    pyinfra.systemd.service(service="apache2", restarted=True, enabled=True)

if not ARGS.remove:
    pyinfra.apt.packages(packages=["apache2", f"libapache2-mod-{ARGS.module_name}"]
          ).notify(restart_and_enable_apache)
    fs.ln(src="/etc/apache2/mods-available/{{ ARGS.module_name }}.load",
          path="/etc/apache2/mods-enabled/{{ ARGS.module_name }}.load",
          symbolic=True).notify(restart_and_enable_apache)
else:
    fs.rm(path="/etc/apache2/mods-enabled/{{ ARGS.module_name }}.load",
          ).notify(restart_and_enable_apache)
    pyinfra.apt.packages(packages=[f"libapache2-mod-{ARGS.module_name}"], present=False,
          ).notify(restart_and_enable_apache)
```

## Example Playbooks

- [New uPlaybook](examples/new-uplaybook/playbook)

## State

This is Beta software: The core is done but as it gets real world use things
may change in incompatible ways before final release.

Currently (Late Nov 2023) I'm working on:

- Documentation.
- Test driving uPlaybook to find rough edges.
- Adding more Tasks.

If you look at it, your feedback would be appreciated.

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
