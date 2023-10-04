#!/usr/bin/env python3

import sys
import inspect
from typing import Optional


class Return:
    def __init__(self, changed: bool, extra_message: Optional[str] = None):
        self.changed = changed
        self.extra_message = extra_message
        self.print_status()

    def print_status(self):
        parent_frame_info = inspect.stack()[2]
        parent_function_name = parent_frame_info.function
        args, _, _, values = inspect.getargvalues(parent_frame_info.frame)
        call_args = ", ".join([f"{arg}={values[arg]}" for arg in args if arg != "self"])
        add_msg = f" ({self.extra_message})" if self.extra_message else ""
        prefix = "=>" if self.changed else "=#"
        print(f"{prefix} {parent_function_name}({call_args}){add_msg}")


class UpContext:
    def __init__(self):
        self.context = {}


up_context = UpContext()


def cli():
    with open(sys.argv[1], "r") as fp:
        playbook = fp.read()
        exec(playbook)
