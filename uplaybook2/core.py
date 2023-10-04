#!/usr/bin/env python3

from .internals import Return, TemplateStr, template_args, calling_context, up_context
from typing import Optional
import pprint


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

    return Return(changed=True, output=output, hide_args=True)


@calling_context
@template_args
def lookup(var: str) -> object:
    return up_context.get_env()[var]
