#!/usr/bin/env python3

"""
pyinfra shim

This module allows uPlaybook to call pyinfra tasks on the local machine
"""

from .internals import (
    Return,
    Failure,
    TemplateStr,
    RawStr,
    up_context,
    task,
)
from . import internals
from typing import Union, Optional, Callable, List, Dict
import tempfile
import subprocess
import os
import re
from collections import namedtuple

PyInfraResults = namedtuple("PyInfraResults", ["changed", "no_change", "errors"])


class PyInfraFailed(Exception):
    def __init__(self, message, stdout, stderr):
        message = f"pyinfra execution failed: {message}\n   stdout: {stdout}\n   stderr: {stderr}"
        super().__init__(message, stdout, stderr)


def _run_pyinfra(
    imports: str, operator: str, operargs: Dict[str, object]
) -> PyInfraResults:
    """
    Run a pyinfra operation.

    Args:
        imports: The imports that the operator will need.
        operator: The name of the operator to run.
        operargs: kwargs-style arguments to the operator, the value needs to be a
                valid python value of the type appropraite for the argument.
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp_file:
        tmp_file.write(imports)
        tmp_file.write("\n")
        tmp_file.write(operator)
        tmp_file.write("(")
        for k, v in operargs.items():
            tmp_file.write(f"{k}={v}, ")
        tmp_file.write(")")

        tmp_file.close()

        s = subprocess.run(
            ["pyinfra", "@local", tmp_file.name], text=True, capture_output=True
        )

        os.remove(tmp_file.name)

        if s.returncode != 0:
            raise PyInfraFailed(
                f"Exit code {s.returncode}, expecting 0.", s.stdout, s.stderr
            )

        # [@local]   Changed: 0   No change: 1   Errors: 0
        match = re.search(
            r"\[@local\]\s+Changed:\s*(?P<changed>\d+)\s+No change:\s*(?P<no_change>\d+)\s+Errors:\s*(?P<errors>\d+)",
            s.stderr,
        )
        if not match:
            raise PyInfraFailed(
                f"Unable to parse pyinfra output for 'Changed' message",
                s.stdout,
                s.stderr,
            )

        groups = match.groupdict()
        return PyInfraResults(
            int(groups["changed"]),
            int(groups["no_change"]),
            int(groups["errors"]),
        )


@task
def apt_packages(
    packages: List[TemplateStr],
    present: bool = True,
    latest: bool = False,
    update: bool = False,
    cache_time: Optional[int] = None,
    upgrade: bool = False,
    force: bool = False,
    no_recommends: bool = False,
    allow_downgrades: bool = False,
    #  need to figure out what these are, they aren't documented as to type
    # extra_install_args=None,
    # extra_uninstall_args=None,
) -> Return:
    """
    Manage packages with apt (install, uninstall, update)

    Package versions can be given, as with apt, "<package>=<version>".

    Args:
        packages: List of packages (templatable)
        present: Should packages be installed
        latest: Upgrade packages (if no specific version is given)
        update: Run apt update before installing packages
        cache_time: When used with update, cache for this many seconds
        upgrade: Run apt upgrade before installing packages
        force: Force package installs by passing –force-yes to apt
        no_recommends: Don’t install recommended packages
        allow_downgrades: Allow downgrading packages with version (–allow-downgrades)

    Not yet implemented:
        extra_install_args: Additional arguments to the apt install command
        extra_uninstall_args: additional arguments to the apt uninstall command

    Examples:

    ```python
    pyinfra.apt_packages(packages=["neovim"])
    pyinfra.apt_packages(packages=["neovim"], latest=True)
    ```

    <!-- #taskdoc -->
    """
    operargs = {
        "packages": repr(packages),
        "present": present,
        "latest": latest,
        "update": update,
        "upgrade": upgrade,
        "force": force,
        "no_recommends": no_recommends,
        "allow_downgrades": allow_downgrades,
    }
    if cache_time is not None:
        operargs["cache_time"] = (cache_time,)

    result = _run_pyinfra(
        "from pyinfra.operations import apt", "apt.packages", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)
