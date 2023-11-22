#!/usr/bin/env python3

"""
## pacman


Manage pacman packages. (Arch Linux package manager)
"""

from . import _run_pyinfra, PyInfraFailed, PyInfraResults
from typing import Optional, List
from ..internals import task, TemplateStr, Return


@task
def upgrade():
    """
    Upgrades all pacman packages.
    """
    operargs = {}

    result = _run_pyinfra(
        "from pyinfra.operations import pacman", "pacman.upgrade", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def update():
    """
    Updates pacman repositories.
    """
    operargs = {}

    result = _run_pyinfra(
        "from pyinfra.operations import pacman", "pacman.update", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def packages(packages=None, present=True, update=False, upgrade=False):
    """
    Add/remove pacman packages.

    + packages: list of packages to ensure
    + present: whether the packages should be installed
    + update: run ``pacman -Sy`` before installing packages
    + upgrade: run ``pacman -Su`` before installing packages

    Versions:
        Package versions can be pinned like pacman: ``<pkg>=<version>``.

    **Example:**

    .. code:: python

        pacman.packages(
            name="Install Vim and a plugin",
            packages=["vim-fugitive", "vim"],
            update=True,
        )
    """
    operargs = {
        "packages": repr(packages),
        "present": repr(present),
        "update": repr(update),
        "upgrade": repr(upgrade),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import pacman", "pacman.packages", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)
