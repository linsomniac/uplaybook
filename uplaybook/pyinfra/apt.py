#!/usr/bin/env python3

"""
## Apt package tasks

This module provides tasks for interacting with the apt package manager.
"""

from . import _run_pyinfra, PyInfraFailed, PyInfraResults
from typing import Optional, List
from ..internals import task, TemplateStr, Return


@task
def packages(
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
