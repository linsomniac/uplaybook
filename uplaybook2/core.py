#!/usr/bin/env python3

from .internals import (
    Return,
    TemplateStr,
    template_args,
    calling_context,
    up_context,
    Failure,
)
from typing import Optional
import pprint
import subprocess
import sys
from types import SimpleNamespace


@calling_context
@template_args
def debug(msg: Optional[TemplateStr] = None, var: Optional[object] = None) -> Return:
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
    """Render a string as a jinja2 template and return the value"""
    return s


@calling_context
@template_args
def run(
    command: TemplateStr, shell: bool = True, ignore_failures: bool = False
) -> object:
    sys.stdout.flush()
    sys.stderr.flush()

    p = subprocess.run(command, shell=shell, text=True, capture_output=True)

    extra = SimpleNamespace()
    extra.stderr = p.stderr
    extra.returncode = p.returncode
    failure = p.returncode != 0
    r = Return(
        changed=True,
        failure=failure,
        output=p.stdout,
        extra=extra,
        ignore_failure=ignore_failures,
        failure_exc=Failure(f"Exit code {p.returncode}"),
    )

    return r
