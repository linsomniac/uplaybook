#!/usr/bin/env python3

"""
## npm


Manage npm (aka node aka Node.js) packages.
"""

from . import _run_pyinfra, PyInfraFailed, PyInfraResults
from typing import Optional, List
from ..internals import task, TemplateStr, Return


@task
def packages(packages=None, present=True, latest=False, directory=None):
    """
    Install/remove/update npm packages.

    + packages: list of packages to ensure
    + present: whether the packages should be present
    + latest: whether to upgrade packages without a specified version
    + directory: directory to manage packages for, defaults to global

    Versions:
        Package versions can be pinned like npm: ``<pkg>@<version>``.
    """
    operargs = {
        "packages": repr(packages),
        "present": repr(present),
        "latest": repr(latest),
        "directory": repr(directory),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import npm", "npm.packages", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)
