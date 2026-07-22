#!/usr/bin/env python3

"""
A rich set of OS tasks

##  pyinfra Introduction

uPlaybook wrappers of pyinfra https://docs.pyinfra.com/en/3.x/ operators.

This set of tasks provides a rich set of system management routines.
This wraps the pyinfra application.
"""

__is_task_module__ = True

#  Full docs are in `docs/tasks/pyinfra/intro.md`

from collections import namedtuple
from typing import Dict
import json
import tempfile
import subprocess
import os

PyInfraResults = namedtuple("PyInfraResults", ["changed", "no_change", "errors"])


class PyInfraGlobalArgContext(dict):
    def __init__(self):
        super().__init__(self)


pyinfra_global_args = PyInfraGlobalArgContext()


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
    operargs = operargs.copy()
    operargs.update(pyinfra_global_args)

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
            ["pyinfra", "--json", "-y", "@local", tmp_file.name],
            text=True,
            capture_output=True,
        )

        os.remove(tmp_file.name)

        if s.returncode != 0:
            raise PyInfraFailed(
                f"Exit code {s.returncode}, expecting 0.", s.stdout, s.stderr
            )

        try:
            totals = json.loads(s.stdout)["results"]["totals"]
            return PyInfraResults(
                int(totals["success"]),
                int(totals["no_change"]),
                int(totals["error"]),
            )
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            raise PyInfraFailed(
                "Unable to parse pyinfra JSON results.",
                s.stdout,
                s.stderr,
            ) from exc


from . import apk
from . import apt
from . import brew
from . import bsdinit
from . import choco
from . import dnf
from . import files
from . import gem
from . import git
from . import iptables
from . import launchd
from . import lxd
from . import mysql
from . import npm
from . import openrc
from . import pacman
from . import pip
from . import pkg
from . import pkgin
from . import postgresql
from . import puppet
from . import server
from . import ssh
from . import systemd
from . import sysvinit
from . import upstart
from . import vzctl
from . import windows
from . import windows_files
from . import xbps
from . import yum
from . import zypper
