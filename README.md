# uPlaybook2

A Python-like declarative IT automation tool.

**Note**: This is an early work in progress.  See "State" below.

uPlaybook2 takes ideas from Ansible and Cookiecutter and gives it a Python syntax
rather than YAML.  The desired state of the system is specified via this "playbook"
and associated templates and data.  You can then run this playbook, providing
additional arguments for this run.

Use cases:

- Shell scripts, but declarative rather than command-based.  Built in arg parsing,
  templating, "handlers" called when changes are made, and encryption of secrets.
- Project templating.  Think "cookiecutter", but with a declarative scripting.
  For example: It could conditionally create files based on argument values, can
  do "git init" if a directory is created, etc...
- IT Automation.  Eventually I hope for it to add components for system state
  manipulation like: service/user/group management, package installation, etc.

## High-level Ideas

Some core ideas of it:

    - Python-like syntax
    - Declare the state you want to end up at.
    - Tasks communicate whether they have changed something.
    - Changed tasks can trigger a handler (if this file changes, restart a service).
    - Jinja2 templating of arguments and files delivered via fs.template()
    - Status output.

## State

Currently (Oct 2023) this is experimental: the core functionality is implemented
and it is usable with a limited number of tasks(), to start trying it in real use.
As real use is made of it, things may evolve, so playbooks created may need to adapt
as new things are tried.

If you look at it, your feedback would be appreciated.

## What Is uPlaybook2

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

uPlaybook2 is, currently an experiment, into making a Python-based environment for expressing
similar ideas:

```python
template(src="49-haproxy.conf.j2", path="/etc/rsyslog.d/49-haproxy.conf", mode="a=r,u+w").notify(restart_syslog)
chown(owner="root", group="root")  #  picks up `path` because of above line
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

    from uplaybook2 import fs, core, up_context

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

## Task Documentation

<!-- (@@@ Put documentation here) -->

### core.debug:

Display informational message.

Print a message or pretty-print a variable.

#### Arguments:

- **msg**: Message to display. (optional, templateable).
- **var**: Object to pretty-print (optional, templateable).

#### Examples:

    core.debug(msg="Directory already exists, exiting")
    core.debug(var=ret_value)

### core.playbook_args:

Specify arguments for a playbook.

Optionally, a playbook may specify that it needs arguments.  If defined,
this will create an argument parser and command-line arguemnts and
options.

Example:
    core.playbook_args(
            core.Argument(name="user"),
            core.Argument(name="hostname")
            )
    core.debug(msg="Arguments: user={{playbook_args.user}}  hostname={{playbook_args.hostname}}")

### core.render:

Render a string as a jinja2 template and return the value

#### Arguments:

- **s**: Template to render. (templateable).

#### Returns:

- Rendered template as a string.

#### Examples:

    core.render(s="Value of foo: {{foo}}")

### core.run:

Run a command.  Stdout is returned as `output` in the return object.  Stderr
and return code are stored in `extra` in return object.

#### Arguments:

- **command**: Command to run (templateable).
- **shell**: If False, run `command` without a shell.  Safer.  Default is True:
         allows shell processing of `command` for things like output
         redirection, wildcard expansion, pipelines, etc. (optional, bool)
- **ignore_failures**: If true, do not treat non-0 return code as a fatal failure.
         This allows testing of return code within playbook.  (optional, bool)
- **change**: By default, all shell commands are assumed to have caused a change
         to the system and will trigger notifications.  If False, this `command`
         is treated as not changing the system.  (optional, bool)

Extra:

- **stderr**: Captured stderr output.
- **returncode**: The return code of the command.

#### Examples:

    core.run(command="systemctl restart sshd")
    core.run(command="rm *.foo", shell=False)   #  removes literal file "*.foo"

    r = core.run(command="date", change=False)
    print(f"Current date/time: {r.output}")
    print(f"Return code: {r.extra.returncode}")

    if core.run(command="grep -q ^user: /etc/passwd", ignore_failures=True, change=False):
        print("User exists")

### fs.builder:

All-in-one filesystem builder.

This is targeted for use with Items() loops, for easily populating or
modifying many filesystem objects in compact declarations.

#### Arguments:

- **path**: Name of destination filesystem object. (templateable).
- **src**: Name of template to use as source (optional, templateable).
        Defaults to the basename of `path` + ".j2".
- **mode**: Permissions of file (optional, templatable string or int).
- **owner**: Ownership to set on `path`. (optional, templatable).
- **group**: Group to set on `path`. (optional, templatable).
- **action**: Type of `path` to build, can be: "directory", "template", "exists", "copy".
        (optional, templatable, default="template")
- **notify**:  Handler to notify of changes.
        (optional, Callable)

#### Examples:

    fs.builder("/tmp/foo")
    fs.builder("/tmp/bar", action="directory")
    for _ in Items(
            Item(path="/tmp/{{ modname }}", action="directory"),
            Item(path="/tmp/{{ modname }}/__init__.py"),
            defaults=Item(mode="a=rX,u+w")
            ):
        builder()

### fs.cd:

Change working directory to `path`.

#### Arguments:

- **path**: Directory to change into (templateable).

#### Examples:

    fs.cd(path="/tmp")

### fs.chmod:

Change permissions of path.

#### Arguments:

- **path**: Path to change (templateable).
- **mode**: Permissions of path (optional, templatable string or int).
- **is_directory**: Treat path as a directory, impacts "X".  If not specified
        `path` is examined to determine if it is a directory.
        (optional, bool).

#### Examples:

    fs.chmod(path="/tmp/foo", mode="a=rX,u+w")
    fs.chmod(path="/tmp/foo", mode=0o755)

### fs.chown:

Change ownership/group of path.

#### Arguments:

- **path**: Path to change (templateable).
- **owner**: Ownership to set on `path`. (optional, templatable).
- **group**: Group to set on `path`. (optional, templatable).

#### Examples:

    fs.chown(path="/tmp", owner="root")
    fs.chown(path="/tmp", group="wheel")
    fs.chown(path="/tmp", owner="nobody", group="nobody")

### fs.copy:

Copy the `src` file to `path`, optionally templating the contents in `src`.

#### Arguments:

- **path**: Name of destination file. (templateable).
- **src**: Name of template to use as source (optional, templateable).
        Defaults to the basename of `path` + ".j2".
- **mode**: Permissions of directory (optional, templatable string or int).
        Sets mode on creation.
- **template**: If True, apply Jinja2 templating to the contents of `src`,
       otherwise copy verbatim.  (default: True)

#### Examples:

    fs.copy(path="/tmp/foo")
    fs.copy(src="bar-{{ fqdn }}.j2", path="/tmp/bar", template=False)

### fs.mkdir:

Create a directory.  Defaults to creating necessary parent directories.

#### Arguments:

- **path**: Name of file to create (templateable).
- **mode**: Permissions of directory (optional, templatable string or int).
            Sets mode on creation.
- **parents**: Make parent directories if needed.  (optional, default=True)

#### Examples:

    fs.mkdir(path="/tmp/foo")
    fs.mkdir(path="/tmp/bar", mode="a=rX,u+w")
    fs.mkdir(path="/tmp/baz/qux", mode=0o755, parents=True)

### fs.mkfile:

Create an empty file if it does not already exist.

#### Arguments:

- **path**: Name of file to create (templateable).
- **mode**: Permissions of file (optional, templatable string or int).
   Atomically sets mode on creation.

#### Examples:

    fs.mkfile(path="/tmp/foo")
    fs.mkfile(path="/tmp/bar", mode="a=rX,u+w")
    fs.mkfile(path="/tmp/baz", mode=0o755)
