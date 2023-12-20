#!/usr/bin/env python3

import sys
from typing import Union, List, Iterator
import os
import traceback
import ast
import argparse
import importlib
import pydoc
import re
from pathlib import Path
import itertools
from .internals import (
    up_context,
    uplaybook_version,
    PlaybookInfo,
    Failure,
    Exit,
    import_script_as_module,
)


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
        "--up-version",
        action="store_true",
        help="Display the version and exit?",
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

    if "--up-version" in sys.argv:
        print(f"uPlaybook version: {uplaybook_version}")
        sys.exit(0)

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


def show_playbook_traceback(e: Exception) -> None:
    """
    Display the current traceback, but only the parts that reference the playbook(s).
    Traceback is printed to stdout.
    """
    up_context.console.print(
        "[bold red]uPlaybook Traceback (most recent call last):[/]"
    )
    exc_type, exc_value, exc_tb = sys.exc_info()
    for entry in traceback.extract_tb(exc_tb):
        if entry.filename not in up_context.playbook_files_seen:
            continue
        up_context.console.print(
            f'  File: "{entry.filename}", line {entry.lineno}, in {entry.name}',
            highlight=True,
        )
        up_context.console.print(f"    {entry.line}", highlight=True)
        #', '_line', 'filename', 'line', 'lineno', 'locals', 'name']

    if isinstance(e, Failure):
        up_context.console.print(
            f"[bold red]Task Failure, Cause:[/]\n   {str(e)}", highlight=True
        )
    else:
        up_context.console.print(
            "".join(traceback.format_exception_only(exc_value)).rstrip(), highlight=True
        )


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
    except Exception as e:
        if args.up_full_traceback or not full_playbook_path:
            print(traceback.format_exc())
        else:
            show_playbook_traceback(e)
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


if __name__ == "__main__":
    cli()
