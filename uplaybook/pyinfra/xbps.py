#!/usr/bin/env python3

"""
## xbps


Manage XBPS packages and repositories. Note that XBPS package names are case-sensitive.
"""

from . import _run_pyinfra, PyInfraFailed, PyInfraResults
from typing import Optional, List
from ..internals import task, TemplateStr, Return


@task
def upgrade():
    """
    Upgrades all XBPS packages.
    """
    operargs = {}

    result = _run_pyinfra(
        "from pyinfra.operations import xbps", "xbps.upgrade", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def update():
    """
    Update XBPS repositories.
    """
    operargs = {}

    result = _run_pyinfra(
        "from pyinfra.operations import xbps", "xbps.update", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def packages(packages=None, present=True, update=False, upgrade=False):
    """
    Install/remove/update XBPS packages.

    + packages: list of packages to ensure
    + present: whether the packages should be installed
    + update: run ``xbps-install -S`` before installing packages
    + upgrade: run ``xbps-install -y -u`` before installing packages

    **Example:**

    .. code:: python

        xbps.packages(
            name="Install Vim and Vim Pager",
            packages=["vimpager", "vim"],
        )
    """
    operargs = {
        "packages": repr(packages),
        "present": repr(present),
        "update": repr(update),
        "upgrade": repr(upgrade),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import xbps", "xbps.packages", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)
