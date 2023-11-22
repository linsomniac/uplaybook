#!/usr/bin/env python3

"""
## gem


Manage Ruby gem packages. (see https://rubygems.org/ )
"""

from . import _run_pyinfra, PyInfraFailed, PyInfraResults
from typing import Optional, List
from ..internals import task, TemplateStr, Return


@task
def packages(packages=None, present=True, latest=False):
    """
    Add/remove/update gem packages.

    + packages: list of packages to ensure
    + present: whether the packages should be installed
    + latest: whether to upgrade packages without a specified version

    Versions:
        Package versions can be pinned like gem: ``<pkg>:<version>``.

    **Example:**

    .. code:: python

        # Note: Assumes that 'gem' is installed.
        gem.packages(
            name="Install rspec",
            packages=["rspec"],
        )
    """
    operargs = {
        "packages": repr(packages),
        "present": repr(present),
        "latest": repr(latest),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import gem", "gem.packages", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)
