#!/usr/bin/env python3

import sys
import inspect
from typing import Optional, Union
from typing import Callable, Any
from functools import wraps
import jinja2
import os
import platform
import types
import multiprocessing
import socket
from types import SimpleNamespace
import traceback
import ast


def platform_info() -> types.SimpleNamespace:
    """
    Linux:
         'arch': 'x86_64',
         'release_codename': 'jammy',
         'release_id': 'ubuntu',
         'os_family': 'debian',
         'release_name': 'Ubuntu',
         'release_version': '22.04',
         'system': 'Linux'

    MacOS:
        'arch': 'arm64',
        'release_version': '13.0.1',
        'system': 'Darwin'

    Windows:
        'arch': 'AMD64',
        'release_edition': 'ServerStandard',
        'release_name': '10',
        'release_version': '10.0.17763',
        'system': 'Windows'
    """
    env = types.SimpleNamespace()
    uname = platform.uname()
    env.system = platform.system()
    if env.system == "Linux":
        release = platform.freedesktop_os_release()
        env.release_name = release["NAME"]
        env.release_id = release["ID"]
        env.release_version = release["VERSION_ID"]
        env.release_like = release["ID_LIKE"]
        env.release_codename = release["VERSION_CODENAME"]
    if env.system == "Darwin":
        macver = platform.mac_ver()
        env.release_version = macver[0]
    if env.system == "Windows":
        env.release_version = uname.version
        env.release_name = uname.release
        env.release_edition = platform.win32_edition()
    env.arch = uname.machine
    env.cpu_count = multiprocessing.cpu_count()
    env.fqdn = socket.getfqdn()

    try:
        import psutil

        vm = psutil.virtual_memory()
        env.memory_total = vm.total
        env.memory_available = vm.available
        env.memory_used = vm.used
        env.memory_percent_used = vm.percent
    except ImportError:
        pass

    return env


class UpContext:
    """
    A singleton object for storing and managing context data.
    """

    def __init__(self):
        self.globals = {"environ": os.environ, "platform": platform_info()}
        self.context = {}
        self.calling_context = {}
        self.changed_count = 0
        self.failure_count = 0
        self.total_count = 0
        self.ignore_failure_count = 0

        self.jinja_env = jinja2.Environment()
        self.jinja_env.filters["basename"] = os.path.basename
        self.jinja_env.filters["dirname"] = os.path.dirname
        self.jinja_env.filters["abspath"] = os.path.abspath

    def get_env(self, env_in: Optional[dict] = None) -> dict:
        """Returns the jinja template environment"""
        env = self.globals.copy()
        env.update(self.context)
        env.update(self.calling_context)
        if env_in:
            env.update(env_in)
        return env

    def ignore_failures(self):
        """Is ignore_failures mode active?"""
        return self.ignore_failure_count > 0


up_context = UpContext()


class TemplateStr(str):
    """
    A subclass of str to mark what arguments of a task are templated.
    """

    pass


def template_args(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to pre-processes arguments to the function of type TemplateStr through Jinja.

    If an argument has a type annotation of TemplateStr this decorator will treat the string
    value of that argument as a Jinja2 template and render it. The resulting value (after
    rendering) is then passed to the wrapped function.

    Args:
    - func (Callable): The function to be wrapped.

    Returns:
    - Callable: The wrapped function with potentially modified arguments.

    Usage:
    @template_args
    def example_function(a: Union[TemplateStr, str]):
        print(a)

    example_function("Hello {{ 'World' }}")  # Outputs: "Hello World"
    """
    sig = inspect.signature(func)

    def _render_jinja_arg(s: str) -> str:
        """Render the arguments as Jinja2, use the up_context and the calling environment.
        NOTE: This is hardcoded to be run from inside this decorator
        Is likely to be fragile.
        """
        return up_context.jinja_env.from_string(s).render(up_context.get_env())

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Convert args to mutable list
        args = list(args)

        # Get bound arguments
        bound_args = sig.bind(*args, **kwargs)
        bound_args.apply_defaults()

        # Process bound arguments and replace if type is TemplateStr
        for name, value in bound_args.arguments.items():
            if not isinstance(value, str) or (value not in args and name not in kwargs):
                continue

            annotation = sig.parameters[name].annotation

            # Check for TemplateStr directly or as part of a Union
            if annotation is TemplateStr or (
                hasattr(annotation, "__origin__")
                and issubclass(TemplateStr, annotation.__args__)
            ):
                if name in kwargs:
                    kwargs[name] = _render_jinja_arg(value)
                else:
                    args[bound_args.args.index(value)] = _render_jinja_arg(value)

        return func(*args, **kwargs)

    return wrapper


def calling_context(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to save off the calling function namespace into up_context.calling_context.

    This decorator saves off the namespace of the function that calls the wrapped function
    for later use by templating.

    Args:
    - func (Callable): The function to be wrapped.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        current_frame = inspect.currentframe()
        env = current_frame.f_back.f_back.f_locals.copy()
        up_context.calling_context = env

        ret = func(*args, **kwargs)

        up_context.calling_context = {}

        return ret

    return wrapper


class Return:
    """
    A return type from tasks to track success/failure, display status, etc...
    """

    def __init__(
        self,
        changed: bool,
        failure: bool = False,
        extra_message: Optional[str] = None,
        output: Optional[str] = None,
        hide_args: bool = False,
        extra: Optional[SimpleNamespace] = None,
    ) -> None:
        self.changed = changed
        self.extra_message = extra_message
        self.output = output
        self.hide_args = hide_args
        self.print_status()
        self.extra = extra
        self.failure = failure

        up_context.total_count += 1
        if changed:
            up_context.changed_count += 1
        if failure:
            up_context.failure_count += 1

    def print_status(self) -> None:
        """
        Display the output and status of the task.
        """
        parent_function_name = "<Unknown>"
        for parent_frame_info in inspect.stack()[2:]:
            parent_function_name = parent_frame_info.function
            if not parent_function_name.startswith("_"):
                break

        if self.hide_args:
            call_args = "..."
        else:
            args, _, _, values = inspect.getargvalues(parent_frame_info.frame)
            call_args = ", ".join(
                [f"{arg}={values[arg]}" for arg in args if arg != "self"]
            )

        add_msg = f" ({self.extra_message})" if self.extra_message else ""
        prefix = "=>" if self.changed else "=#"
        print(f"{prefix} {parent_function_name}({call_args}){add_msg}")
        if self.output:
            print(self.output)

    def __repr__(self) -> str:
        values = [f"changed={self.changed}"]
        if self.extra_message is not None:
            values.append(f"extra_message={repr(self.extra_message)}")
        if self.extra is not None:
            for k, v in vars(self.extra).items():
                values.append(f"extra.{k}={repr(v)}")

        formatted_output = ""
        if self.output is not None:
            if len(self.output) < 60 or self.output.count("\n") < 4:
                values.append(f"output={repr(self.output)}")
            else:
                formatted_output = ',\noutput="""\n' + self.output + '"""'
        return f"Return({', '.join(values)}{formatted_output})"


class Failure(Exception):
    pass


def extract_docstring_from_file(filename: str) -> Union[str, None]:
    """Open the specified file and retrieve the docstring from it.

    Returns None if no docstring is found"""
    with open(filename, "r") as f:
        try:
            node = ast.parse(f.read())
        except Exception:
            return None

        if (
            node.body
            and isinstance(node.body[0], ast.Expr)
            and isinstance(node.body[0].value, ast.Str)
        ):
            return ast.get_docstring(node)

    return None


# Test the function
import sys

docstring = extract_docstring_from_file(sys.argv[1])
if docstring:
    print(docstring)
else:
    print("No docstring found!")


def cli() -> None:
    """
    The main entry point for the CLI.
    """
    with open(sys.argv[1], "r") as fp:
        playbook = fp.read()
        try:
            exec(playbook)
        except Exception:
            print(traceback.format_exc())

        print()
        print(
            f"*** RECAP:  total={up_context.total_count} changed={up_context.changed_count} failure={up_context.failure_count}"
        )
