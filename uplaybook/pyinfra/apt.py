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
    packages: Optional[List[TemplateStr]] = None,
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
    apt.packages(packages=["neovim"])
    apt.packages(packages=["neovim"], latest=True)
    ```
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
        "cache_time": cache_time,
    }

    result = _run_pyinfra(
        "from pyinfra.operations import apt", "apt.packages", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def key(src=None, keyserver=None, keyid=None):
    """
    Add apt gpg keys with ``apt-key``.

    + src: filename or URL
    + keyserver: URL of keyserver to fetch key from
    + keyid: key ID or list of key IDs when using keyserver

    keyserver/id:
        These must be provided together.

    **Examples:**

    ```python
    # Note: If using URL, wget is assumed to be installed.
    apt.key(
        name="Add the Docker apt gpg key",
        src="https://download.docker.com/linux/ubuntu/gpg",
    )

    apt.key(
        name="Install VirtualBox key",
        src="https://www.virtualbox.org/download/oracle_vbox_2016.asc",
    )
    ```
    """
    operargs = {
        "src": repr(src),
        "keyserver": repr(keyserver),
        "keyid": repr(keyid),
    }

    result = _run_pyinfra("from pyinfra.operations import apt", "apt.key", operargs)

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def repo(src, present=True, filename=None):
    """
    Add/remove apt repositories.

    + src: apt source string eg ``deb http://X hardy main``
    + present: whether the repo should exist on the system
    + filename: optional filename to use ``/etc/apt/sources.list.d/<filename>.list``. By
      default uses ``/etc/apt/sources.list``.

    **Example:**

    ```python
    apt.repo(
        name="Install VirtualBox repo",
        src="deb https://download.virtualbox.org/virtualbox/debian bionic contrib",
    )
    ```
    """
    operargs = {
        "src": repr(src),
        "present": repr(present),
        "filename": repr(filename),
    }

    result = _run_pyinfra("from pyinfra.operations import apt", "apt.repo", operargs)

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def ppa(src, present=True):
    """
    Add/remove Ubuntu ppa repositories.

    + src: the PPA name (full ppa:user/repo format)
    + present: whether it should exist

    Note:
        requires ``apt-add-repository`` on the remote host

    **Example:**

    ```python
    # Note: Assumes software-properties-common is installed.
    apt.ppa(
        name="Add the Bitcoin ppa",
        src="ppa:bitcoin/bitcoin",
    )
    ```
    """
    operargs = {
        "src": repr(src),
        "present": repr(present),
    }

    result = _run_pyinfra("from pyinfra.operations import apt", "apt.ppa", operargs)

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def deb(src, present=True, force=False):
    """
    Add/remove ``.deb`` file packages.

    + src: filename or URL of the ``.deb`` file
    + present: whether or not the package should exist on the system
    + force: whether to force the package install by passing `--force-yes` to apt

    Note:
        When installing, ``apt-get install -f`` will be run to install any unmet
        dependencies.

    URL sources with ``present=False``:
        If the ``.deb`` file isn't downloaded, pyinfra can't remove any existing
        package as the file won't exist until mid-deploy.

    **Example:**

    ```python
    # Note: Assumes wget is installed.
    apt.deb(
        name="Install Chrome via deb",
        src="https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb",
    )
    ```
    """
    operargs = {
        "src": repr(src),
        "present": repr(present),
        "force": repr(force),
    }

    result = _run_pyinfra("from pyinfra.operations import apt", "apt.deb", operargs)

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def update(cache_time=None):
    """
    Updates apt repositories.

    + cache_time: cache updates for this many seconds

    **Example:**

    ```python
    apt.update(
        name="Update apt repositories",
        cache_time=3600,
    )
    ```
    """
    operargs = {
        "cache_time": repr(cache_time),
    }

    result = _run_pyinfra("from pyinfra.operations import apt", "apt.update", operargs)

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def upgrade(auto_remove=False):
    """
    Upgrades all apt packages.

    + autoremove: removes transitive dependencies that are no longer needed.

    **Example:**

    ```python
    # Upgrade all packages
    apt.upgrade(
        name="Upgrade apt packages",
    )

    # Upgrade all packages and remove unneeded transitive dependencies
    apt.upgrade(
        name="Upgrade apt packages and remove unneeded dependencies"
        auto_remove=True
    )
    ```
    """
    operargs = {
        "auto_remove": repr(auto_remove),
    }

    result = _run_pyinfra("from pyinfra.operations import apt", "apt.upgrade", operargs)

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def dist_upgrade():
    """
    Updates all apt packages, employing dist-upgrade.

    **Example:**

    ```python
    apt.dist_upgrade(
        name="Upgrade apt packages using dist-upgrade",
    )
    ```
    """
    operargs = {}

    result = _run_pyinfra(
        "from pyinfra.operations import apt", "apt.dist_upgrade", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)
