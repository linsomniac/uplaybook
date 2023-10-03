#!/usr/bin/env python3

import sys
import inspect
from typing import Optional


def make_task(cls):
    stack = inspect.stack()
    caller_frame = stack[1].frame
    caller_namespace = caller_frame.f_globals
    caller_namespace[cls.name] = cls()


class BaseTask:
    @property
    def name(self):
        return self.__class__.__name__


class Return:
    def __init__(self, changed: bool, extra_message: Optional[str] = None):
        self.changed = changed
        self.extra_message = extra_message
        self.print_status()

    def print_status(self):
        for frame_info in inspect.stack():
            frame_self = frame_info.frame.f_locals.get('self', None)
            if frame_self and isinstance(frame_self, BaseTask):
                args, _, _, values = inspect.getargvalues(frame_info.frame)
                call_args = ", ".join([f"{arg}={values[arg]}" for arg in args if arg != "self"])

                parent_function_name = values["self"].name
                add_msg = f" ({self.extra_message})" if self.extra_message else ""
                prefix = "=>" if self.changed else "=#"
                print(f"{prefix} {parent_function_name}({call_args}){add_msg}")
                break


class UpContext:
    def __init__(self):
        self.context = {}

up_context = UpContext()


def cli():
    with open(sys.argv[1], "r") as fp:
        playbook = fp.read()
        exec(playbook)
