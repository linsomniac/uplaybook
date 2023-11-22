#!/usr/bin/env python3

"""
## zypper


"""

from . import _run_pyinfra, PyInfraFailed, PyInfraResults
from typing import Optional, List
from ..internals import task, TemplateStr, Return


@task
def repo(
    src,
    baseurl=None,
    present=True,
    description=None,
    enabled=True,
    gpgcheck=True,
    gpgkey=None,
    type="rpm-md",
):
    """
    Add/remove/update zypper repositories.

    + src: URL or name for the ``.repo``   file
    + baseurl: the baseurl of the repo (if ``name`` is not a URL)
    + present: whether the ``.repo`` file should be present
    + description: optional verbose description
    + enabled: whether this repo is enabled
    + gpgcheck: whether set ``gpgcheck=1``
    + gpgkey: the URL to the gpg key for this repo
    + type: the type field this repo (defaults to ``rpm-md``)

    ``Baseurl``/``description``/``gpgcheck``/``gpgkey``:
        These are only valid when ``name`` is a filename (ie not a URL). This is
        for manual construction of repository files. Use a URL to download and
        install remote repository files.

    **Examples:**

    .. code:: python

        # Download a repository file
        zypper.repo(
            name="Install container virtualization repo via URL",
            src="https://download.opensuse.org/repositories/Virtualization:containers/openSUSE_Tumbleweed/Virtualization:containers.repo",
        )

        # Create the repository file from baseurl/etc
        zypper.repo(
            name="Install container virtualization repo",
            src=="Virtualization:containers (openSUSE_Tumbleweed)",
            baseurl="https://download.opensuse.org/repositories/Virtualization:/containers/openSUSE_Tumbleweed/",
        )
    """
    operargs = {
        "src": repr(src),
        "baseurl": repr(baseurl),
        "present": repr(present),
        "description": repr(description),
        "enabled": repr(enabled),
        "gpgcheck": repr(gpgcheck),
        "gpgkey": repr(gpgkey),
        "type": repr(type),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import zypper", "zypper.repo", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def rpm(src, present=True):
    """
    Add/remove ``.rpm`` file packages.

    + src: filename or URL of the ``.rpm`` package
    + present: whether ore not the package should exist on the system

    URL sources with ``present=False``:
        If the ``.rpm`` file isn't downloaded, pyinfra can't remove any existing
        package as the file won't exist until mid-deploy.

    **Example:**

    .. code:: python

        zypper.rpm(
           name="Install task from rpm",
           src="https://github.com/go-task/task/releases/download/v2.8.1/task_linux_amd64.rpm",
        )
    """
    operargs = {
        "src": repr(src),
        "present": repr(present),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import zypper", "zypper.rpm", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def update():
    """
    Updates all zypper packages.
    """
    operargs = {}

    result = _run_pyinfra(
        "from pyinfra.operations import zypper", "zypper.update", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def packages(
    packages=None,
    present=True,
    latest=False,
    update=False,
    clean=False,
    extra_global_install_args=None,
    extra_install_args=None,
    extra_global_uninstall_args=None,
    extra_uninstall_args=None,
):
    """
    Install/remove/update zypper packages & updates.

    + packages: list of packages to ensure
    + present: whether the packages should be installed
    + latest: whether to upgrade packages without a specified version
    + update: run ``zypper update`` before installing packages
    + clean: run ``zypper clean --all`` before installing packages
    + extra_global_install_args: additional global arguments to the zypper install command
    + extra_install_args: additional arguments to the zypper install command
    + extra_global_uninstall_args: additional global arguments to the zypper uninstall command
    + extra_uninstall_args: additional arguments to the zypper uninstall command

    Versions:
        Package versions can be pinned like zypper: ``<pkg>=<version>``

    **Examples:**

    .. code:: python

        # Update package list and install packages
        zypper.packages(
            name="Install Vim and Vim enhanced",
            packages=["vim-enhanced", "vim"],
            update=True,
        )

        # Install the latest versions of packages (always check)
        zypper.packages(
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
        "clean": repr(clean),
        "extra_global_install_args": repr(extra_global_install_args),
        "extra_install_args": repr(extra_install_args),
        "extra_global_uninstall_args": repr(extra_global_uninstall_args),
        "extra_uninstall_args": repr(extra_uninstall_args),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import zypper", "zypper.packages", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)
