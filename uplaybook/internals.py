#!/usr/bin/env python3

"""
Internal uPlaybook objects and methods.

These objects and methods typically are used by task developers, though some may be usful
for reference by users.  These are typically not used directly by end-users, though other
parts of the documentation may refer to these classes.
"""

import sys
import inspect
from typing import Optional, Union, List, Callable, Any, Iterator
from types import ModuleType
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
import argparse
import importlib
import pydoc
import re
from pathlib import Path
from collections import namedtuple
import itertools
from rich.console import Console


PlaybookInfo = namedtuple("PlaybookInfo", ["name", "directory", "playbook_file"])


class Failure(Exception):
    """
    The default exception raised if a task fails.
    """

    pass


class Exit(Exception):
    """
    The exception raised to exit a playbook early.
    """

    def __init__(self, msg: str, return_code: int) -> None:
        super().__init__(msg)
        self.return_code = return_code


def PlatformInfo() -> types.SimpleNamespace:
    """
    See "docs/templating.md#platform_info" for more information.
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
        self.globals = {"environ": os.environ, "platform": PlatformInfo()}
        self.context = {"ARGS": SimpleNamespace()}
        self.calling_context = {}
        self.item_context = []
        self.changed_count = 0
        self.failure_count = 0
        self.total_count = 0
        self.ignore_failure_count = 0
        self.handler_list = []
        self.call_depth = 0
        self.remaining_args = []
        self.parsed_args = argparse.Namespace()
        self.playbook_namespace = {}  #  Namespace of the playbook module
        self.playbook_name = ""  #  Name of the playbook being run
        self.playbook_docstring = ""
        self.playbook_directory = "."  #  Directory playbook is in
        self.playbook_files_seen = set()
        self.console = Console()

        self.jinja_env = jinja2.Environment(undefined=jinja2.StrictUndefined)
        self.jinja_env.filters["basename"] = os.path.basename
        self.jinja_env.filters["dirname"] = os.path.dirname
        self.jinja_env.filters["abspath"] = os.path.abspath

    def get_env(self, env_in: Optional[dict] = None) -> dict:
        """Returns the jinja template environment"""
        env = self.globals.copy()
        env.update(self.context)
        env.update(self.playbook_namespace)
        env.update(self.calling_context)
        for ctx in self.item_context[::-1]:
            env.update(ctx)
        if env_in:
            env.update(env_in)
        return env

    def ignore_failures(self):
        """Is ignore_failures mode active?"""
        return self.ignore_failure_count > 0

    def add_handler(self, fn: Callable) -> None:
        """Add a notify function."""
        if fn in self.handler_list:
            return

        self.handler_list.append(fn)

    def flush_handlers(self) -> None:
        """Run all the handler functions."""
        did_handler = False
        while self.handler_list:
            did_handler = True
            fn = self.handler_list.pop(0)
            print(f">> *** Starting handler: {fn.__name__}")
            fn()
        if did_handler:
            print(f">> *** Done with handlers")


up_context = UpContext()


class CallDepth:
    """
    A context manager to increment the call depth when one task calls another task.
    """

    def __enter__(self):
        up_context.call_depth += 1

    def __exit__(self, *args):
        up_context.call_depth -= 1


class TemplateStr(str):
    """
    A subclass of str to mark what arguments of a task are templated.
    """

    pass


class RawStr(str):
    """
    A subclass of str which is not to have Jinja2 template expansion.
    """

    pass


def template_args(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to pre-processes arguments to the function of type TemplateStr through Jinja.

    If an argument has a type annotation of TemplateStr this decorator will treat the string
    value of that argument as a Jinja2 template and render it. The resulting value (after
    rendering) is then passed to the wrapped function.

    Args:
        func (Callable): The function to be wrapped.

    Returns:
        Callable: The wrapped function with potentially modified arguments.

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
        if type(s) == RawStr:
            return s
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
            if value not in args and name not in kwargs:
                continue
            if not (
                isinstance(value, list) and isinstance(value[0], str)
            ) and not isinstance(value, str):
                continue

            annotation = sig.parameters[name].annotation

            if (
                annotation == Optional[List[TemplateStr]]
                or annotation == List[TemplateStr]
            ) and isinstance(value, list):
                if name in kwargs:
                    kwargs[name] = list([_render_jinja_arg(x) for x in value])
                else:
                    args[bound_args.args.index(value)] = list(
                        [_render_jinja_arg(x) for x in value]
                    )

            # Check for TemplateStr directly or as part of a Union
            elif isinstance(value, str) and (
                annotation is TemplateStr
                or (
                    hasattr(annotation, "__origin__")
                    and issubclass(TemplateStr, annotation.__args__)
                )
            ):
                if name in kwargs:
                    kwargs[name] = _render_jinja_arg(value)
                else:
                    args[bound_args.args.index(value)] = _render_jinja_arg(value)

        return func(*args, **kwargs)

    return wrapper


TaskCallInfo = namedtuple(
    "TaskCallInfo",
    [
        "function_name",
        "function_qualname",
        "module_name",
        "annotations",
        "args",
        "kwargs",
    ],
)


def calling_context(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to save off the calling function namespace into up_context.calling_context.

    This decorator saves off the namespace of the function that calls the wrapped function
    for later use by templating.

    Args:
        func (Callable): The function to be wrapped.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        current_frame = inspect.currentframe()
        env = current_frame.f_back.f_locals.copy()
        up_context.calling_context = env
        up_context.task_call_info = TaskCallInfo(
            func.__name__,
            func.__qualname__,
            func.__module__,
            func.__annotations__,
            args,
            kwargs.copy(),
        )

        ret = func(*args, **kwargs)

        up_context.task_call_info = None
        up_context.calling_context = {}

        return ret

    return wrapper


def task(func: Callable[..., Any]) -> Callable[..., Any]:
    """A decorator for tasks, combines @calling_context and @template_args"""
    func.__is_uplaybook_task__ = True
    return calling_context(template_args(func))


class Return:
    """
    A return type from tasks to track success/failure, display status, etc...

    This can be used as a context manager if a `context_manager` function is provided.
    See `fs.cd()` for an example.

    It can also be used as a boolean, to check success/failure (needs `ignore_failure`, or failure
    will raise exception).  See `core.run()` for an exaple.

    Args:
        changed: If True, mark the task as having changed system state. (bool)
        failure: If True, mark the task as having failed. (optional, bool)
        ignore_failure: If True, failure is not considered fatal, execution can continue on.
                (bool, default False)
        extra_message: An extra message to display in the status line in parens (optional, str)
        output: Output of the task to display, for example stdout of a run command.  (optional, str)
        hide_args: If true, do not display any arguments names/values.  Useful for `debug()`
                which doesn't need to show the message in the status line as well as the output.
                (bool, default=False)
        secret_args: Arguments that have secrets in them, so obscure the value.  (optional, set)
        extra: Extra data to be returned to the caller, as a `types.SimpleNamespace()`, for
                example `run()` will return exit code and stderr as extra.  (optional, types.SimpleNamespace())
        raise_exc: Raise this exception after handling the return.  If failure=True, this exception will be
                raised, if not specified a Failure() exception will be raised. (optional, Exception())
        context_manager: This type can optionally behave as a Context Manager, and if so this function
                will be called with no parameters at the end of the context.  Use a closure if you want to
                associate data with the function call ("lambda: function(args)").  (optional, Callable).

    Examples:

        Return(changed=True)
        Return(changed=False)
        Return(changed=True, extra_message="Permissions")
        Return(changed=True, extra=SimpleNamespace(stderr=s))
        Return(changed=True, context_manager=lambda: f(arg))
    """

    def __init__(
        self,
        changed: bool,
        failure: bool = False,
        ignore_failure: bool = False,
        extra_message: Optional[str] = None,
        output: Optional[str] = None,
        hide_args: bool = False,
        secret_args: set = set(),
        extra: Optional[SimpleNamespace] = None,
        raise_exc: Optional[Exception] = None,
        context_manager: Optional[Callable] = None,
    ) -> None:
        self.changed = changed
        self.extra_message = extra_message
        self.output = output
        self.hide_args = hide_args
        self.extra = extra
        self.failure = failure
        self.secret_args = secret_args
        self.raise_exc = raise_exc
        self.context_manager = context_manager

        self.print_status()

        failure_ok = ignore_failure or up_context.ignore_failures is True

        up_context.total_count += 1
        if changed:
            up_context.changed_count += 1
        if failure and not failure_ok:
            up_context.failure_count += 1
            raise self.raise_exc if self.raise_exc is not None else Failure(
                "Unspecified failure in task"
            )
        if self.raise_exc:
            raise self.raise_exc

    def __enter__(self) -> "Return":
        """
        Begin a context if used as a context manager.

        Raises:
            AttributeError: if no `context_manager` was specified.

        Returns:
            The Return() object, so it can be used as "with fn() as return_obj:"
        """
        if not self.context_manager:
            raise AttributeError("This instance is not a valid context manager.")
        return self

    def __exit__(self, *_) -> None:
        """
        End the context if used as a context manager.

        This will call the `context_manager` function if it is given.
        """
        assert self.context_manager is not None
        self.context_manager()

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

            #  overwrite the original arguments (if any had been modified in function call)
            #  NOTE: This only works for the inner-most of nested calls, this will need to
            #  be converted to a stack to handle nesting.
            if up_context.task_call_info:
                values.update(up_context.task_call_info.kwargs)

            call_args = ", ".join(
                [
                    f"{arg}=" + ("***" if arg in self.secret_args else f"{values[arg]}")
                    for arg in args
                    if arg != "self" and values[arg] is not None
                ]
            )

        add_msg = f" ({self.extra_message})" if self.extra_message else ""

        prefix = "=#"
        suffix = ""
        style = ""
        if self.changed:
            prefix = "=>"
            style = "green"
        if self.failure:
            prefix = "=!"
            suffix = " (failure ignored)"
            style = "red"
        call_depth = "=" * up_context.call_depth

        up_context.console.print(
            f"{call_depth}{prefix} {parent_function_name}({call_args}){add_msg}{suffix}",
            style=style,
            highlight=False,
            markup=False,
        )
        if self.output:
            up_context.console.print(self.output, markup=False, highlight=True)

    def __repr__(self) -> str:
        """
        Format this object for display.
        """
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

    def __bool__(self) -> bool:
        """
        If checked for truthfulness, return True if not `failure`.
        """
        return not self.failure

    def notify(self, handler: Union[Callable, List]) -> None:
        """
        Register a handler function to call if changed.

        Args:
            handler:  A function or a list of functions to register for calling later,
                    if the task has changed the system.  (callable or list)
        """
        if self.changed:
            if callable(handler):
                up_context.add_handler(handler)
            else:
                for x in handler:
                    up_context.add_handler(x)


def extract_docstring_from_file(filename: str) -> Union[str, None]:
    """Open the specified file and retrieve the docstring from it.

    Returns None if no docstring is found"""
    if os.path.isdir(filename):
        filename = os.path.join(filename, "playbook")
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


def import_script_as_module(module_name: str, paths_to_try: List[str]) -> ModuleType:
    """
    Imports a Python script as a module, whether it ends in ".py" or not.
    Given the name of a module to import, and a list of absolute or relative path names
    (including the filename), import the module.  The module is set up so that it can
    later be imported, but a reference to the module is also returned.

    Args:
        module_name (str): The name of the module to import.
                This doesn't have to match the filename.
        paths_to_try (List[str]): A list of file paths to look for the file to load.
                This can be absolute or relative paths to the file, the first file that
                exists is used.

    Returns:
        Module: A reference to the imported module.

    Raises:
        FileNotFoundError: If the module file is not found in any of the specified directory paths.
        ImportError: If there are issues importing the module, such as invalid Python syntax in the module file.

    Example:
        my_module = import_script_as_module("my_module", ["my_module", "../my_module"])

        # Now you can either directly use "my_module"
        my_module.function()

        # Or you can later import it:
        import my_module
    """
    from pathlib import Path
    import os

    for try_filename in paths_to_try:
        if os.path.exists(try_filename):
            module_filename = Path(try_filename).resolve()
            break
    else:
        raise FileNotFoundError(f"Unable to find '{module_name}' module to import")

    from importlib.util import spec_from_loader, module_from_spec
    from importlib.machinery import SourceFileLoader
    import sys

    spec = spec_from_loader(
        module_name, SourceFileLoader(module_name, str(module_filename))
    )
    if spec is None:
        raise ImportError("Unable to spec_from_loader() the module, no error returned.")
    module = module_from_spec(spec)
    module.__dict__.update(up_context.get_env())
    up_context.playbook_namespace = module.__dict__
    spec.loader.exec_module(module)

    return module


def find_updocs(name: str) -> str:
    """
    Given a module/task name, return the docstring for it.

    This iterates over the various options for how a "--up-docs" may be requested and returns
    the first appropriate docstring found.

    Args:
        name: The "--up-docs" document to find.

    Returns:
        The associated updoc.
    """
    if name == "__main__":
        from . import __doc__

        return __doc__

    #  if a module is specified
    try:
        module = importlib.import_module(f".{name}", package=__package__)
        docs = (module.__doc__ if module.__doc__ is not None else "").rstrip()

        task_functions = []
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                callable(attr)
                and getattr(attr, "__doc__", None)
                and getattr(attr, "__is_uplaybook_task__", False)
            ):
                first_line = getattr(attr, "__doc__", "").lstrip().split("\n")[0]
                task_functions.append(f"{attr_name} - {first_line}")

        docs = (docs + "\n\n## Available Tasks:\n\n").lstrip("\n")
        for task_name in task_functions:
            docs += f"- {name}.{task_name}\n"

        return docs
    except ModuleNotFoundError:
        pass

    #  module.task docs
    module_name, function_name = name.rsplit(".", 1)
    module = importlib.import_module(f".{module_name}", package=__package__)
    function = getattr(module, function_name)
    return f"# {name}\n\n" + function.__doc__.lstrip("\n")


def display_docs(name: str) -> None:
    """
    Display the documentation for the component specified by `name`.

    This displays the docstring from the module or task referred to by `name`,
    formatting it for nicer representation.

    Args:
        name: Module name or module.task name.  If special value "__main__" it displays
                the up2 documentation.
    """
    docs = find_updocs(name)
    pydoc.pager(re.sub(r"#\w+", "", docs).rstrip())


class UpArgumentParser(argparse.ArgumentParser):
    """Wrapper so that "up", when run with no arguments, lists available playbooks."""

    def print_usage(self, file=None):
        super().print_usage(file)
        self.help_list_playbooks()

    def print_help(self, file=None):
        super().print_help(file)
        self.help_list_playbooks()

    def help_list_playbooks(self):
        print()
        print("Available playbooks:")
        playbooks_seen = set()
        for playbook in list_playbooks():
            duplicate = (
                " *HIDDEN BY PREVIOUS PLAYBOOK*"
                if playbook.name in playbooks_seen
                else ""
            )
            playbooks_seen.add(playbook.name)
            print(f"  - {playbook.name} ({playbook.directory}{duplicate})")
            docs = extract_docstring_from_file(playbook.playbook_file)
            desc = (docs if docs else "").lstrip().split("\n", 1)[0]

            if desc:
                print(f"      {desc}")
        print()


def parse_args() -> argparse.Namespace:
    """
    The main CLI argument parser.

    Returns:
        The parsed arguments.
    """
    parser = UpArgumentParser(
        prog="up",
        description="Run playbooks of actions, typically to set up some sort of environment.",
        add_help=False,
    )

    parser.add_argument(
        "--help",
        action="store_true",
        help="Display help about usage.",
    )
    parser.add_argument(
        "--up-full-traceback",
        action="store_true",
        help="Display a full traceback rather than the default abbreviated version.",
    )
    parser.add_argument(
        "--up-list-playbooks",
        action="store_true",
        help="Display a list of playbook names and exit.",
    )
    parser.add_argument(
        "--up-debug",
        action="store_true",
        help="Display additional debugging information during playbook run.",
    )
    parser.add_argument(
        "--up-docs",
        type=str,
        nargs="?",
        const="__main__",
        default=None,
        dest="docs_arg",
        help="Display documentation, if an optional value is given the help for that component will be displayed.",
    )
    parser.add_argument(
        "playbook", type=str, nargs="?", default=None, help="Name of the playbook."
    )

    args, remaining_args = parser.parse_known_args()

    if args.up_list_playbooks:
        for playbook in list_playbooks():
            print(f"{playbook.name}")
        sys.exit(0)
    if args.help:
        if args.playbook is None:
            parser.print_help()
            sys.exit(0)
        remaining_args.insert(0, "--help")
    if args.docs_arg:
        display_docs(args.docs_arg)
        if args.docs_arg == "__main__":
            print()
            parser.print_help()
        sys.exit(0)

    if not args.playbook:
        parser.print_usage()
        sys.exit(1)

    up_context.remaining_args = remaining_args
    up_context.parsed_args = args

    return args


def get_playbook_search_paths() -> List[Path]:
    """
    Get the playbook search path (either the default or from the environment)
    and return an iterable of the path objects.

    Returns:
        List[Paths] for the list of locations to look for playbooks."""

    search_path = os.environ.get(
        "UP_PLAYBOOK_PATH",
        ".:.uplaybooks:~/.config/uplaybook:~/.config/uplaybook/library:/etc/uplaybook",
    )
    return [Path(x).expanduser().joinpath(".") for x in search_path.split(":")]


def list_playbooks() -> Iterator[PlaybookInfo]:
    """
    Walk the playbook path and return a list of available playbooks.
    Playbook files take precedence over "playbook/playbook".  Sorted by
    playbook name within each component of the search path.

    Returns:

    """
    for playbook_path in get_playbook_search_paths():
        possible_playbooks = sorted(
            itertools.chain(
                playbook_path.glob("*.pb"), playbook_path.glob("*/playbook")
            ),
            key=lambda x: x.name,
        )
        for playbook_file in possible_playbooks:
            if playbook_file.exists():
                directory = playbook_file.parent
                if playbook_file.name == "playbook" and directory.as_posix() != ".":
                    name = directory.name
                else:
                    name = playbook_file.name
                yield PlaybookInfo(name, directory, playbook_file)


def find_playbook(playbookname: str) -> PlaybookInfo:
    """
    Finds and returns the path of a specified playbook file.

    Search for the playbook in the UP_PLAYBOOK_PATH environment variable,
    or a default if not specified.

    Args:
        playbookname (str): The name of the playbook file to search for.

    Returns:
        Path: The path of the found playbook file.

    Raises:
        FileNotFoundError: If the playbook file is not found in the search paths."""

    #  absolute path name given, just use it
    if os.path.sep in playbookname or (
        os.path.altsep and os.path.altsep in playbookname
    ):
        playbook = Path(playbookname)
        if playbook.is_dir() and (playbook / "playbook").exists():
            playbook = playbook / "playbook"
        return PlaybookInfo(
            playbook.name, playbook.absolute().parent, playbook.absolute()
        )

    for playbook in list_playbooks():
        if playbook.name == playbookname or (
            playbook.name.endswith(".pb")
            and not playbookname.endswith(".pb")
            and playbook.name == (playbookname + ".pb")
        ):
            return playbook

    searchpath = get_playbook_search_paths()
    raise FileNotFoundError(
        f"Unable to locate a playbook by the name of {playbookname},"
        f" searched in path {searchpath}."
    )


def find_file(filename: str) -> Path:
    """
    Finds and returns the path of a template/file.

    This function uses a colon-separated search path, either gotten from the
    UP_FILES_PATH environment variable or the default.  "..." specified in
    the search path is relative to the directory the playbook is found in.

    Returns:
    Path: The path of the found template file.

    Raises:
    FileNotFoundError: If the template file is not found in the search paths.
    """
    search_path = os.environ.get("UP_FILES_PATH", "...:.../files:.")

    if Path(filename).is_absolute():
        return Path(filename)

    playbook_directory = Path(up_context.playbook_directory)

    for directory in search_path.split(":"):
        if directory == "...":
            p = playbook_directory.joinpath(filename)
            if p.exists():
                return p
            continue
        if directory.startswith(".../"):
            p = playbook_directory.joinpath(directory[4:]).joinpath(filename)
            if p.exists():
                return p
            continue

        p = Path(directory).joinpath(filename)
        if p.exists():
            return p

    raise FileNotFoundError(
        f"Could not find file {filename}, searched in {search_path}"
    )


def show_playbook_traceback() -> None:
    """
    Display the current traceback, but only the parts that reference the playbook(s).
    Traceback is printed to stdout.
    """
    tb_lines = traceback.format_exc().splitlines()
    print(tb_lines[0])
    print_next_line = False
    for line in tb_lines[1:-1]:
        if print_next_line:
            print(line)
            print_next_line = False
            continue
        if line.startswith("  File "):
            filename = line.split()[1].strip('",')
            if filename in up_context.playbook_files_seen:
                print(line)
                print_next_line = True
    print(tb_lines[-1])


def cli() -> None:
    """
    The main entry point for the CLI.
    """
    args = parse_args()

    full_playbook_path = None
    return_code = 0
    try:
        pb_name = args.playbook
        up_context.playbook_name = pb_name
        playbook = find_playbook(pb_name)
        up_context.playbook_directory = playbook.directory.absolute()
        full_playbook_path = Path(playbook.playbook_file).absolute()

        docs = extract_docstring_from_file(full_playbook_path)
        up_context.playbook_docstring = docs if docs else ""

        up_context.playbook_files_seen.add(full_playbook_path.as_posix())
        import_script_as_module(
            pb_name, [playbook.playbook_file, playbook.playbook_file]
        )
    except Exit as e:
        return_code = e.return_code
        pass
    except Exception:
        if args.up_full_traceback or not full_playbook_path:
            print(traceback.format_exc())
        else:
            show_playbook_traceback()
        return_code = 1

    up_context.flush_handlers()

    recap_msg = "*** RECAP"
    failure_count_msg = f"failure={up_context.failure_count}"
    if up_context.failure_count > 0:
        failure_count_msg = f"[bold red]{failure_count_msg}[/]"
        recap_msg = f"[bold red]{recap_msg}[/]"
    else:
        recap_msg = f"[green]{recap_msg}[/]"

    up_context.console.print(
        f"\n{recap_msg}:  total={up_context.total_count} changed={up_context.changed_count} {failure_count_msg}",
        markup=True,
        highlight=True,
    )

    sys.exit(return_code)
