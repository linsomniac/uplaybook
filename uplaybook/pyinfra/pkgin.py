#!/usr/bin/env python3

"""
## pkgin


Manage pkgin packages.
"""

from . import _run_pyinfra, PyInfraFailed, PyInfraResults
from typing import Optional, List
from ..internals import task, TemplateStr, Return


@task
def upgrade():
    """
    Upgrades all pkgin packages.
    """
    operargs = {}

    result = _run_pyinfra(
        "from pyinfra.operations import pkgin", "pkgin.upgrade", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def update():
    """
    Updates pkgin repositories.
    """
    operargs = {}

    result = _run_pyinfra(
        "from pyinfra.operations import pkgin", "pkgin.update", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def packages(packages=None, present=True, latest=False, update=False, upgrade=False):
    """
    Add/remove/update pkgin packages.

    + packages: list of packages to ensure
    + present: whether the packages should be installed
    + latest: whether to upgrade packages without a specified version
    + update: run ``pkgin update`` before installing packages
    + upgrade: run ``pkgin upgrade`` before installing packages

    **Examples:**

    .. code:: python

        # Update package list and install packages
        pkgin.packages(
            name="Install tmux and Vim",
            packages=["tmux", "vim"],
            update=True,
        )

        # Install the latest versions of packages (always check)
        pkgin.packages(
            name="Install latest Vim",
            packages=["vim"],
            latest=True,
        )
    """
    operargs = {
        "packages": repr(packages),
        "present": repr(present),
        "latest": repr(latest),
        "update": repr(update),
        "upgrade": repr(upgrade),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import pkgin", "pkgin.packages", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)
