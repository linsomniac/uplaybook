#!/usr/bin/env python3

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

        for item in [
                Item(path="foo"),
                Item(path="bar"),
                Item(path="baz"),
                ]:
            fs.builder(path="{{item.path}}")

        for item in [
                Item(path="foo", action="directory", owner="nobody"),
                Item(path="bar", action="exists"),
                Item(path="/etc/apache2/sites-enabled/foo", notify=restart_apache),
                ]:
            fs.builder(**item)

        with Item(path="foo", action="directory", owner="nobody") as item:
            #  Can access as "path" as well as "item.path"
            fs.exists(path="{{path}}")
            fs.chown(path="{{path}}", owner="{{owner}}")

        with Item(path="foo", action="directory", owner="nobody"):
            fs.exists(path="{{path}}")

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

    Arguments:

    - **msg**: Message to display. (optional, templateable).
    - **var**: Object to pretty-print (optional, templateable).

    Examples:

        core.debug(msg="Directory already exists, exiting")
        core.debug(var=ret_value)

    #taskdoc
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

    Example:
        print(core.lookup('name'))
    """
    return up_context.get_env()[var]


@calling_context
@template_args
def render(s: TemplateStr) -> str:
    """
    Render a string as a jinja2 template and return the value

    Arguments:

    - **s**: Template to render. (templateable).

    Returns:

    - Rendered template as a string.

    Examples:

        core.render(s="Value of foo: {{foo}}")

    #taskdoc
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

    Arguments:

    - **command**: Command to run (templateable).
    - **shell**: If False, run `command` without a shell.  Safer.  Default is True:
             allows shell processing of `command` for things like output
             redirection, wildcard expansion, pipelines, etc. (optional, bool)
    - **ignore_failures**: If True, do not treat non-0 return code as a fatal failure.
             This allows testing of return code within playbook.  (optional, bool)
    - **change**: By default, all shell commands are assumed to have caused a change
             to the system and will trigger notifications.  If False, this `command`
             is treated as not changing the system.  (optional, bool)
    - **creates**: If specified, if the path it specifies exists, consider the command
            to have already been run and skip future runes.

    Extra:

    - **stderr**: Captured stderr output.
    - **returncode**: The return code of the command.

    Examples:

        core.run(command="systemctl restart sshd")
        core.run(command="rm *.foo", shell=False)   #  removes literal file "*.foo"

        r = core.run(command="date", change=False)
        print(f"Current date/time: {{r.output}}")
        print(f"Return code: {{r.extra.returncode}}")

        if core.run(command="grep -q ^user: /etc/passwd", ignore_failures=True, change=False):
            print("User exists")

    #taskdoc
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
        raise_exc=Failure(f"Exit code {p.returncode}"),
    )


class Argument:
    """
    An argument for a playbook.

    List arguments if a playbook needs additional information from the user.
    This is used in combination with the `core.playbook_args()` task.

    Arguments:

    - **name**: The name of the argument, this will determine the "--name" of the command-line
        flag and the variable the value is stored in (str).
    - **label**: A label used when prompting the user for input (For future use, optional)
    - **description**: Detailed information on the argument for use in "--help" output.
        (str, optional)
    - **type**: The type of the argument: str, bool, int, password (default=str)
    - **default**: A default value for the argument.  Arguments without a default
        must be specified in the command-line, if a default is given an option with
        "--name" will be available.

    Example:
        core.playbook_args(
                core.Argument(name="user"),
                core.Argument(name="hostname", default=None)
                )
        core.debug(msg="Arguments: user={{playbook_args.user}}  hostname={{playbook_args.hostname}}")

        #  Run with "up2 playbookname --hostname=localhost username
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

    Example:
        core.playbook_args(
                core.Argument(name="user"),
                core.Argument(name="hostname")
                )
        core.debug(msg="Arguments: user={{playbook_args.user}}  hostname={{playbook_args.hostname}}")

    #taskdoc
    """
    parser = argparse.ArgumentParser(prog=f"up:{up_context.playbook_name}")

    name_mapping: dict[str, str] = {}
    for arg in options:
        kw_args: dict[str, object] = {
            "type": arg.type,
        }
        # orig_arg_name = arg.name
        arg_name = arg.name.replace("_", "-")
        name_mapping[arg.name] = arg.name
        if arg.default is not None:
            kw_args["dest"] = arg.name
            arg_name = "--" + arg_name
            kw_args["default"] = arg.default
        else:
            name_mapping[arg.name] = arg_name
        if arg.description is not None:
            kw_args["help"] = arg.description
        kw_args["type"] = {
            "bool": bool,
            "str": str,
            "int": int,
            "password": str,
        }[arg.type]
        if kw_args["type"] is bool:
            kw_args["action"] = argparse.BooleanOptionalAction

        parser.add_argument(arg_name, **kw_args)
    args, remaining = parser.parse_known_args(up_context.remaining_args)
    up_context.remaining_args = remaining

    args_vars = vars(args)
    for arg in options:
        setattr(
            up_context.context["playbook_args"],
            arg.name,
            args_vars[name_mapping[arg.name]],
        )
        up_context.context[arg.name] = args_vars[name_mapping[arg.name]]


@calling_context
@template_args
def become(user: Union[int, TemplateStr]) -> Return:
    """
    Switch to running as another user in a playbook.

    If used as a context manager, you are switched back to the original user after the context.

    Arguments:

    - **user**: User name or UID of user to switch to.

    Example:
        core.become(user="nobody")

        with core.become(user="backup"):
            #  to tasks as backup user
            fs.mkfile(path="/tmp/backupfile")
        #  now you are back to the previous user

    #taskdoc
    """
    new_user = user
    if type(new_user) == str:
        new_user = pwd.getpwnam(new_user).pw_uid

    assert type(new_user) == int
    old_uid = os.getuid()
    os.seteuid(new_user)

    return Return(changed=False, context_manager=lambda: os.seteuid(old_uid))


@calling_context
@template_args
def require(user: Union[int, TemplateStr]) -> Return:
    """
    Verify we are running as the specified user.

    Arguments:

    - **user**: User name or UID of user to verify.  (int or str, templateable)

    Example:
        core.require(user="nobody")

    #taskdoc
    """
    new_user = user
    if type(new_user) == str:
        new_user = pwd.getpwnam(new_user).pw_uid

    assert type(new_user) == int
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

    Arguments:

    - **msg**: Message to display with failure (str, templateable).

    Example:
        core.fail(msg="Unable to download file")

    #taskdoc
    """
    return Return(changed=False, failure=True, raise_exc=Failure(msg))


@calling_context
@template_args
def exit(returncode: int = 0, msg: Union[TemplateStr, str] = "") -> Return:
    """
    End a playbook run.

    Arguments:

    - **returncode**: Exit code for process, 0 is success, 1-255 are failure (int, default=0).
    - **msg**: Message to display (str, templatable, default "").

    Example:
        core.exit()
        core.exit(returncode=1)
        core.exit(msg="Unable to download file", returncode=1)

    #taskdoc
    """
    return Return(
        changed=False, failure=returncode != 0, raise_exc=Exit(msg, returncode)
    )


@calling_context
@template_args
def notify(function: Callable) -> Return:
    """
    Add a notify handler to be called later.

    Arguments:

    - **function**: A function that takes no arguments, which is called at a later time.

    Example:
        core.notify(lambda: core.run(command="systemctl restart apache2"))
        core.notify(lambda: fs.remove("tmpdir", recursive=True))

    #taskdoc
    """
    up_context.add_handler(function)

    return Return(changed=False)


@calling_context
@template_args
def flush_handlers() -> Return:
    """
    Run any registred handlers.

    Example:
        core.flush_handlers()

    #taskdoc
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

    Arguments:

    - **path**: File location to look for a match in. (templateable)
    - **search**: The string (or regex) to look for. (templateable)
    - **regex**: Do a regex search, if False do a simple string search. (bool, default=True)
    - **ignore_failures**: If True, do not treat file absence as a fatal failure.
             (optional, bool, default=True)

    Examples:

        if core.grep(path="/tmp/foo", search="secret=xyzzy"):
            #  code for when the string is found.

    #taskdoc
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
