#!/usr/bin/env python3

"""
Core Tasks

Tasks that are a core part of uPlaybook.
"""

from .internals import (
    Return,
    Exit,
    TemplateStr,
    template_args,
    calling_context,
    up_context,
    Failure,
)
from typing import Optional, List, Union, Callable
import pprint
import subprocess
import sys
from types import SimpleNamespace
import argparse
import os
import pwd
import re


class Item(dict):
    """
    An (ansible-like) item for processing in a playbook (a file, directory, user...)

    A typical use case of an Item is for looping over many files and setting them
    up, or setting up many filesystem objects in a playbook.  Additionally, if used
    in a "with:" statement, it will place the attributes into the current Jinja2
    namespace.

    This can act as a dictionary (x['attr'] access), SimpleNamespace (x.attr), and also
    is a context manager.  In the context manager case, it forklifts the attributes
    up into the Jinja2 context.

    Examples:

    ```python
    for item in [
            Item(dst="foo"),
            Item(dst="bar"),
            Item(dst="baz"),
            ]:
        fs.builder(dst="{{item.dst}}")

    for item in [
            Item(dst="foo", action="directory", owner="nobody"),
            Item(dst="bar", action="exists"),
            Item(dst="/etc/apache2/sites-enabled/foo", notify=restart_apache),
            ]:
        fs.builder(**item)

    with Item(dst="foo", action="directory", owner="nobody") as item:
        #  Can access as "dst" as well as "item.dst"
        fs.exists(dst="{{dst}}")
        fs.chown(dst="{{dst}}", owner="{{owner}}")

    with Item(dst="foo", action="directory", owner="nobody"):
        fs.exists(dst="{{dst}}")
    ```
    """

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{key}'"
            )

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        if key in self:
            del self[key]
        else:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{key}'"
            )

    def __enter__(self):
        up_context.item_context.insert(0, self)
        return self

    def __exit__(self, *_):
        up_context.item_context.pop(0)


@calling_context
@template_args
def debug(msg: Optional[TemplateStr] = None, var: Optional[object] = None) -> Return:
    """
    Display informational message.

    Print a message or pretty-print a variable.

    Args:
        msg: Message to display. (optional, templateable).
        var: Object to pretty-print (optional, templateable).

    Examples:

    ```python
    core.debug(msg="Directory already exists, exiting")
    core.debug(var=ret_value)
    ```

    <!-- #taskdoc -->
    """

    output = ""
    if msg:
        output = msg + "\n"
    if var:
        output += pprint.pformat(var)
        output = "\n".join("    " + line for line in output.splitlines())
    output = output.rstrip()

    return Return(changed=False, output=output, hide_args=True)


@calling_context
@template_args
def lookup(var: str) -> object:
    """
    Looks up `var` in the "up context" and returns the value.

    This would typically be similar to Jinja2 rendering "{{var}}", but
    it does not go through "." traversing, so `var` must be a top
    level name.

    Examples:

    ```python
    print(core.lookup('name'))
    ```
    """
    return up_context.get_env()[var]


@calling_context
@template_args
def render(s: TemplateStr) -> str:
    """
    Render a string as a jinja2 template and return the value

    Args:
        s: Template to render. (templateable).

    Returns:
        Rendered template as a string.

    Examples:

    ```python
    core.render(s="Value of foo: {{foo}}")
    ```

    <!-- #taskdoc -->
    """
    return s


@calling_context
@template_args
def run(
    command: TemplateStr,
    shell: bool = True,
    ignore_failures: bool = False,
    change: bool = True,
    creates: Optional[TemplateStr] = None,
) -> object:
    """
    Run a command.  Stdout is returned as `output` in the return object.  Stderr
    and return code are stored in `extra` in return object.

    Args:
        command: Command to run (templateable).
        shell: If False, run `command` without a shell.  Safer.  Default is True:
             allows shell processing of `command` for things like output
             redirection, wildcard expansion, pipelines, etc. (optional, bool)
        ignore_failures: If True, do not treat non-0 return code as a fatal failure.
             This allows testing of return code within playbook.  (optional, bool)
        change: By default, all shell commands are assumed to have caused a change
             to the system and will trigger notifications.  If False, this `command`
             is treated as not changing the system.  (optional, bool)
        creates: If specified, if the path it specifies exists, consider the command
            to have already been run and skip future runes.

    Extra Data:

        stderr: Captured stderr output.
        returncode: The return code of the command.

    Examples:

    ```python
    core.run(command="systemctl restart sshd")
    core.run(command="rm *.foo", shell=False)   #  removes literal file "*.foo"

    r = core.run(command="date", change=False)
    print(f"Current date/time: {{r.output}}")
    print(f"Return code: {{r.extra.returncode}}")

    if core.run(command="grep -q ^user: /etc/passwd", ignore_failures=True, change=False):
        print("User exists")
    ```

    <!-- #taskdoc -->
    """
    if creates is not None and os.path.exists(creates):
        return Return(changed=False)

    sys.stdout.flush()
    sys.stderr.flush()

    p = subprocess.run(command, shell=shell, text=True, capture_output=True)

    extra = SimpleNamespace()
    extra.stderr = p.stderr
    extra.returncode = p.returncode
    failure = p.returncode != 0

    return Return(
        changed=change,
        failure=failure,
        output=p.stdout.rstrip(),
        extra=extra,
        ignore_failure=ignore_failures,
        raise_exc=Failure(f"Exit code {p.returncode}")
        if failure and not ignore_failures
        else None,
    )


class Argument:
    """
    An argument for a playbook.

    List arguments if a playbook needs additional information from the user.
    This is used in combination with the `core.playbook_args()` task.

    Args:
        name: The name of the argument, this will determine the "--name" of the command-line
            flag and the variable the value is stored in (str).
            label: A label used when prompting the user for input (For future use, optional)
        description: Detailed information on the argument for use in "--help" output.
            (str, optional)
        type: The type of the argument: str, bool, int, password (default=str)
        default: A default value for the argument.  Arguments without a default
            must be specified in the command-line, if a default is given an option with
            "--name" will be available.

    Examples:

    ```python
    core.playbook_args(
            core.Argument(name="user"),
            core.Argument(name="hostname", default=None)
            )
    core.debug(msg="Arguments: user={{ARGS.user}}  hostname={{ARGS.hostname}}")

    #  Run with "up2 playbookname --hostname=localhost username
    ```
    """

    def __init__(
        self,
        name: str,
        label: Optional[str] = None,
        description: Optional[str] = None,
        type: str = "str",
        default: Optional[object] = None,
    ):
        self.name = name
        self.label = label
        self.description = description
        self.type = type
        self.default = default


@calling_context
@template_args
def playbook_args(
    *options: List[Argument],
) -> None:
    """
    Specify arguments for a playbook.

    Optionally, a playbook may specify that it needs arguments.  If defined,
    this will create an argument parser and command-line arguemnts and
    options.

    Examples:

    ```python
    core.playbook_args(
            core.Argument(name="is_owner", default=False, type="bool"),
            core.Argument(name="user"),
            core.Argument(name="hostname", default="localhost")
            )
    core.debug(msg="Arguments: user={{playbook_args.user}}  hostname={{playbook_args.hostname}}")
    core.debug(msg="Arguments: is_owner={{playbook_args.is_owner}}")
    #  run examples:
    #    up playbook.pb my_username
    #    up playbook.pb --is-owner my_username
    #    up playbook.pb --no-is-owner my_username my_hostname
    ```

    <!-- #taskdoc -->
    """
    parser = argparse.ArgumentParser(
        prog=f"up:{up_context.playbook_name}", description=up_context.playbook_docstring
    )

    for arg in options:
        arg_type = {
            "bool": bool,
            "str": str,
            "int": int,
            "password": str,
        }[arg.type]

        kw_args: dict[str, object] = {}
        if arg.description is not None:
            kw_args["help"] = arg.description
        if arg.type == "bool":
            kw_args["action"] = argparse.BooleanOptionalAction

        #  name is "--<NAME>" if default is specified, else make it a positional arg
        argument = arg.name if arg.default is None else "--" + arg.name
        if argument.startswith("--"):
            kw_args["dest"] = argument[2:].replace("-", "_")
        else:
            argument = argument.replace("-", "_")

        parser.add_argument(argument, type=arg_type, default=arg.default, **kw_args)

    args, remaining = parser.parse_known_args(up_context.remaining_args)
    up_context.remaining_args = remaining

    #  update up_context.ARGS
    for k, v in vars(args).items():
        setattr(up_context.context["ARGS"], k, v)


@calling_context
@template_args
def become(user: Union[int, TemplateStr]) -> Return:
    """
    Switch to running as another user in a playbook.

    If used as a context manager, you are switched back to the original user after the context.

    Args:
        user: User name or UID of user to switch to.

    Examples:

    ```python
    core.become(user="nobody")

    with core.become(user="backup"):
        #  to tasks as backup user
        fs.mkfile(dst="/tmp/backupfile")
    #  now you are back to the previous user
    ```
    <!-- #taskdoc -->
    """
    new_user = user
    if isinstance(new_user, str):
        new_user = pwd.getpwnam(new_user).pw_uid

    assert isinstance(new_user, int)
    old_uid = os.getuid()
    os.seteuid(new_user)

    return Return(changed=False, context_manager=lambda: os.seteuid(old_uid))


@calling_context
@template_args
def require(user: Union[int, TemplateStr]) -> Return:
    """
    Verify we are running as the specified user.

    Args:
        user: User name or UID of user to verify.  (int or str, templateable)

    Examples:

    ```python
    core.require(user="nobody")
    ```
    <!-- #taskdoc -->
    """
    new_user = user
    if isinstance(new_user, str):
        new_user = pwd.getpwnam(new_user).pw_uid

    assert isinstance(new_user, int)
    current_uid = os.getuid()

    if current_uid != new_user:
        Return(
            changed=False,
            failure=True,
            raise_exc=Failure(f"Expected to run as user {user}, got uid={current_uid}"),
        )

    return Return(changed=False)


@calling_context
@template_args
def fail(msg: TemplateStr) -> Return:
    """
    Abort a playbook run.

    Args:
        msg: Message to display with failure (str, templateable).

    Examples:

    ```python
    core.fail(msg="Unable to download file")
    ```

    <!-- #taskdoc -->
    """
    return Return(changed=False, failure=True, raise_exc=Failure(msg))


@calling_context
@template_args
def exit(returncode: int = 0, msg: Union[TemplateStr, str] = "") -> Return:
    """
    End a playbook run.

    Args:
        returncode: Exit code for process, 0 is success, 1-255 are failure (int, default=0).
        msg: Message to display (str, templatable, default "").

    Examples:

    ```python
    core.exit()
    core.exit(returncode=1)
    core.exit(msg="Unable to download file", returncode=1)
    ```

    <!-- #taskdoc -->
    """
    return Return(
        changed=False, failure=returncode != 0, raise_exc=Exit(msg, returncode)
    )


@calling_context
@template_args
def notify(function: Callable) -> Return:
    """
    Add a notify handler to be called later.

    Args:
        function: A function that takes no arguments, which is called at a later time.

    Examples:

    ```python
    core.notify(lambda: core.run(command="systemctl restart apache2"))
    core.notify(lambda: fs.remove("tmpdir", recursive=True))
    ```

    <!-- #taskdoc -->
    """
    up_context.add_handler(function)

    return Return(changed=False)


@calling_context
@template_args
def flush_handlers() -> Return:
    """
    Run any registred handlers.

    Examples:

    ```python
    core.flush_handlers()
    ```

    <!-- #taskdoc -->
    """
    up_context.flush_handlers()

    return Return(changed=False)


@calling_context
@template_args
def grep(
    path: TemplateStr,
    search: TemplateStr,
    regex: bool = True,
    ignore_failures: bool = True,
) -> object:
    """
    Look for `search` in the file `path`

    Args:
        path: File location to look for a match in. (templateable)
        search: The string (or regex) to look for. (templateable)
        regex: Do a regex search, if False do a simple string search. (bool, default=True)
        ignore_failures: If True, do not treat file absence as a fatal failure.
             (optional, bool, default=True)

    Examples:

    ```python
    if core.grep(path="/tmp/foo", search="secret=xyzzy"):
        #  code for when the string is found.
    ```

    <!-- #taskdoc -->
    """
    with open(path, "r") as fp:
        if regex:
            rx = re.compile(search)
            for line in fp.readlines():
                if rx.search(line):
                    return Return(changed=False, failure=False)
        else:
            for line in fp.readlines():
                if search in line:
                    return Return(changed=False, failure=False)

    return Return(
        changed=False,
        failure=True,
        ignore_failure=ignore_failures,
        raise_exc=Failure("No match found") if not ignore_failures else None,
    )


@calling_context
@template_args
def print(
    msg: TemplateStr,
) -> None:
    """
    uPlaybook print helper, like python print() but does jinja templating.

    Args:
        msg: Message to print. (templateable)

    Examples:

    ```python
    core.print("Arguments: {{playbook_arguments}}")
    ```

    <!-- #taskdoc -->
    """
    sys.stdout.write(msg + "\n")
