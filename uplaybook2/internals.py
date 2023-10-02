#!/usr/bin/env python3

import sys
import inspect
from typing import Optional


class Return:
    def __init__(self, changed: bool, msg: Optional[str] = None):
        self.changed = changed

        parent_frame = inspect.currentframe().f_back
        # parent_locals = parent_frame.f_locals
        args, _, _, values = inspect.getargvalues(parent_frame)
        parent_function_name = values["self"].name
        call_args = ", ".join([f"{arg}={values[arg]}" for arg in args if arg != "self"])
        add_msg = f" ({msg})" if msg else ""
        prefix = "=>" if changed else "=="
        print(f"{prefix} {parent_function_name}({call_args}){add_msg}")



class UpContext:
    def __init__(self):
        self.context = {}

up_context = UpContext()

def cli():
    with open(sys.argv[1], "r") as fp:
        playbook = fp.read()
        exec(playbook)
