#!/usr/bin/env python3

from .internals import (
    Return,
    TemplateStr,
    template_args,
    calling_context,
    up_context,
    Failure,
)
from typing import Optional, List
import pprint
import subprocess
import sys
from types import SimpleNamespace
import argparse


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
) -> object:
    """
    Run a command.  Stdout is returned as `output` in the return object.  Stderr
    and return code are stored in `extra` in return object.

    Arguments:

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

    Examples:

        core.run(command="systemctl restart sshd")
        core.run(command="rm *.foo", shell=False)   #  removes literal file "*.foo"

        r = core.run(command="date", change=False)
        print(f"Current date/time: {r.output}")
        print(f"Return code: {r.extra.returncode}")

        if core.run(command="grep -q ^user: /etc/passwd", ignore_failures=True, change=False):
            print("User exists")

    #taskdoc
    """
    sys.stdout.flush()
    sys.stderr.flush()

    p = subprocess.run(command, shell=shell, text=True, capture_output=True)

    extra = SimpleNamespace()
    extra.stderr = p.stderr
    extra.returncode = p.returncode
    failure = p.returncode != 0
    r = Return(
        changed=change,
        failure=failure,
        output=p.stdout.rstrip(),
        extra=extra,
        ignore_failure=ignore_failures,
        failure_exc=Failure(f"Exit code {p.returncode}"),
    )

    return r


class Argument:
    def __init__(
        self,
        name,
        label,
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
    Set up arguments for playbook
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
