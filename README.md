# uPlaybook2

An experiment into a python-centric ansible/cookiecutter-like system.  Currently not usable except
by the author.

Some core ideas of it:

    - Python-like syntax
    - Declare the state you want to end up at.
    - Tasks communicate whether they have changed something.
    - Changed tasks can trigger a handler (if this file changes, restart a service).
    - Jinja2 templating of arguments and files delivered via fs.template()
    - Status output.

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

### core.debug:

Display informational message.

Print a message or pretty-print a variable.

#### Arguments:

- **msg**: Message to display. (optional, templateable).
- **var**: Object to pretty-print (optional, templateable).

#### Examples:

    core.debug(msg="Directory already exists, exiting")
    core.debug(var=ret_value)

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

### fs.cd:

Change working directory to `path`.

#### Arguments:

- **path**: Directory to change into (templateable).

#### Examples:

    fs.cd(path="/tmp")

### fs.mkdir:

Create a directory.

#### Arguments:

- **path**: Name of file to create (templateable).
- **mode**: Permissions of directory (optional, templatable string or int).
- **parents**: Make parent directories if needed.

#### Examples:

    fs.mkdir(path="/tmp/foo")
    fs.mkdir(path="/tmp/bar", mode="a=rX,u+w")
    fs.mkdir(path="/tmp/baz/qux", mode=0o755, parents=True)

### fs.mkfile:

Create an empty file if it does not already exist.

#### Arguments:

- **path**: Name of file to create (templateable).
- **mode**: Permissions of file (optional, templatable string or int).

#### Examples:

    fs.mkfile(path="/tmp/foo")
    fs.mkfile(path="/tmp/bar", mode="a=rX,u+w")
    fs.mkfile(path="/tmp/baz", mode=0o755)

### fs.template:

Jinja2 templating is used to fill in `src` file to write to `dst`.

#### Arguments:

- **dst**: Name of destination file. (templateable).
- **src**: Name of template to use as source (optional, templateable).
       Defaults to the basename of `dst` + ".j2".
- **mode**: Permissions of file (optional, templatable string or int).

#### Examples:

    fs.template("/tmp/foo")
    fs.mkfile("/tmp/bar", 0o755)
