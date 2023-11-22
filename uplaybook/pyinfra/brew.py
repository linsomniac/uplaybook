#!/usr/bin/env python3

"""
## brew


Manage brew packages on mac/OSX. See https://brew.sh/
"""

from . import _run_pyinfra, PyInfraFailed, PyInfraResults
from typing import Optional, List
from ..internals import task, TemplateStr, Return


@task
def update():
    """
    Updates brew repositories.
    """
    operargs = {}

    result = _run_pyinfra(
        "from pyinfra.operations import brew", "brew.update", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def upgrade():
    """
    Upgrades all brew packages.
    """
    operargs = {}

    result = _run_pyinfra(
        "from pyinfra.operations import brew", "brew.upgrade", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def packages(packages=None, present=True, latest=False, update=False, upgrade=False):
    """
    Add/remove/update brew packages.

    + packages: list of packages to ensure
    + present: whether the packages should be installed
    + latest: whether to upgrade packages without a specified version
    + update: run ``brew update`` before installing packages
    + upgrade: run ``brew upgrade`` before installing packages

    Versions:
        Package versions can be pinned like brew: ``<pkg>@<version>``.

    **Examples:**

    .. code:: python

        # Update package list and install packages
        brew.packages(
            name='Install Vim and vimpager',
            packages=["vimpager", "vim"],
            update=True,
        )

        # Install the latest versions of packages (always check)
        brew.packages(
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
        "from pyinfra.operations import brew", "brew.packages", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def cask_args(host):
    operargs = {
        "host": repr(host),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import brew", "brew.cask_args", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def cask_upgrade():
    """
    Upgrades all brew casks.
    """
    operargs = {}

    result = _run_pyinfra(
        "from pyinfra.operations import brew", "brew.cask_upgrade", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def casks(casks=None, present=True, latest=False, upgrade=False):
    """
    Add/remove/update brew casks.

    + casks: list of casks to ensure
    + present: whether the casks should be installed
    + latest: whether to upgrade casks without a specified version
    + upgrade: run brew cask upgrade before installing casks

    Versions:
        Cask versions can be pinned like brew: ``<pkg>@<version>``.

    **Example:**

    .. code:: python

        brew.casks(
            name='Upgrade and install the latest cask',
            casks=["godot"],
            upgrade=True,
            latest=True,
        )
    """
    operargs = {
        "casks": repr(casks),
        "present": repr(present),
        "latest": repr(latest),
        "upgrade": repr(upgrade),
    }

    result = _run_pyinfra("from pyinfra.operations import brew", "brew.casks", operargs)

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def tap(src, present=True):
    """
    Add/remove brew taps.

    + src: the name of the tap
    + present: whether this tap should be present or not

    **Examples:**

    .. code:: python

        brew.tap(
            name="Add a brew tap",
            src="includeos/includeos",
        )

        # Multiple taps
        for tap in ["includeos/includeos", "ktr0731/evans"]:
            brew.tap(
                name={f"Add brew tap {tap}"},
                src=tap,
            )
    """
    operargs = {
        "src": repr(src),
        "present": repr(present),
    }

    result = _run_pyinfra("from pyinfra.operations import brew", "brew.tap", operargs)

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)
