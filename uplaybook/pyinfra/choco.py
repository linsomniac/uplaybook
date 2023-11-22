#!/usr/bin/env python3

"""
## choco


Manage ``choco`` (Chocolatey) packages (https://chocolatey.org).
"""

from . import _run_pyinfra, PyInfraFailed, PyInfraResults
from typing import Optional, List
from ..internals import task, TemplateStr, Return


@task
def packages(packages=None, present=True, latest=False):
    """
    Add/remove/update ``choco`` packages.

    + packages: list of packages to ensure
    + present: whether the packages should be installed
    + latest: whether to upgrade packages without a specified version

    Versions:
        Package versions can be pinned like gem: ``<pkg>:<version>``.

    **Example:**

    .. code:: python

        # Note: Assumes that 'choco' is installed and
        #       user has Administrator permission.
        choco.packages(
            name="Install Notepad++",
            packages=["notepadplusplus"],
        )
    """
    operargs = {
        "packages": repr(packages),
        "present": repr(present),
        "latest": repr(latest),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import choco", "choco.packages", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def install():
    """
    Install ``choco`` (Chocolatey).
    """
    operargs = {}

    result = _run_pyinfra(
        "from pyinfra.operations import choco", "choco.install", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)
