#!/usr/bin/env python3

"""
## Apk package tasks

This module provides tasks for interacting with the apk package manager.
"""

from . import _run_pyinfra, PyInfraFailed, PyInfraResults
from typing import Optional, List
from ..internals import task, TemplateStr, Return


@task
def upgrade(available=False):
    """
    Upgrades all apk packages.

    + available: force all packages to be upgraded (recommended on whole Alpine version upgrades)
    """
    raise NotImplementedError()
    operargs = {
        "available": repr(available),
    }

    result = _run_pyinfra("from pyinfra.operations import apk", "apk.upgrade", operargs)

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def update():
    """
    Updates apk repositories.
    """
    raise NotImplementedError()
    operargs = {}

    result = _run_pyinfra("from pyinfra.operations import apk", "apk.update", operargs)

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def packages(packages=None, present=True, latest=False, update=False, upgrade=False):
    """
    Add/remove/update apk packages.

    + packages: list of packages to ensure
    + present: whether the packages should be installed
    + latest: whether to upgrade packages without a specified version
    + update: run ``apk update`` before installing packages
    + upgrade: run ``apk upgrade`` before installing packages

    Versions:
        Package versions can be pinned like apk: ``<pkg>=<version>``.

    **Examples:**

    .. code:: python

        # Update package list and install packages
        apk.packages(
            name="Install Asterisk and Vim",
            packages=["asterisk", "vim"],
            update=True,
        )

        # Install the latest versions of packages (always check)
        apk.packages(
            name="Install latest Vim",
            packages=["vim"],
            latest=True,
        )
    """
    raise NotImplementedError()
    operargs = {
        "packages": repr(packages),
        "present": repr(present),
        "latest": repr(latest),
        "update": repr(update),
        "upgrade": repr(upgrade),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import apk", "apk.packages", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)
