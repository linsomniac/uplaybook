#!/usr/bin/env python3

"""
## dnf


Manage dnf packages and repositories. Note that dnf package names are case-sensitive.
"""

from . import _run_pyinfra, PyInfraFailed, PyInfraResults
from typing import Optional, List
from ..internals import task, TemplateStr, Return


@task
def key(src):
    """
    Add dnf gpg keys with ``rpm``.

    + key: filename or URL

    Note:
        always returns one command, not idempotent

    **Example:**

    .. code:: python

        linux_id = host.get_fact(LinuxDistribution)["release_meta"].get("ID")
        dnf.key(
            name="Add the Docker CentOS gpg key",
            src=f"https://download.docker.com/linux/{linux_id}/gpg",
        )
    """
    operargs = {
        "src": repr(src),
    }

    result = _run_pyinfra("from pyinfra.operations import dnf", "dnf.key", operargs)

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def repo(
    src,
    present=True,
    baseurl=None,
    description=None,
    enabled=True,
    gpgcheck=True,
    gpgkey=None,
):
    """
    Add/remove/update dnf repositories.

    + name: URL or name for the ``.repo``   file
    + present: whether the ``.repo`` file should be present
    + baseurl: the baseurl of the repo (if ``name`` is not a URL)
    + description: optional verbose description
    + enabled: whether this repo is enabled
    + gpgcheck: whether set ``gpgcheck=1``
    + gpgkey: the URL to the gpg key for this repo

    ``Baseurl``/``description``/``gpgcheck``/``gpgkey``:
        These are only valid when ``name`` is a filename (ie not a URL). This is
        for manual construction of repository files. Use a URL to download and
        install remote repository files.

    **Examples:**

    .. code:: python

        # Download a repository file
        dnf.rpm(
            name="Install Docker-CE repo via URL",
            src="https://download.docker.com/linux/centos/docker-ce.repo",
        )

        # Create the repository file from baseurl/etc
        dnf.repo(
            name="Add the Docker CentOS repo",
            src="DockerCE",
            baseurl="https://download.docker.com/linux/centos/7/$basearch/stable",
        )
    """
    operargs = {
        "src": repr(src),
        "present": repr(present),
        "baseurl": repr(baseurl),
        "description": repr(description),
        "enabled": repr(enabled),
        "gpgcheck": repr(gpgcheck),
        "gpgkey": repr(gpgkey),
    }

    result = _run_pyinfra("from pyinfra.operations import dnf", "dnf.repo", operargs)

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

        major_centos_version = host.get_fact(LinuxDistribution)["major"]
        dnf.rpm(
           name="Install EPEL rpm to enable EPEL repo",
           src=f"https://dl.fedoraproject.org/pub/epel/epel-release-latest-{major_centos_version}.noarch.rpm",
        )
    """
    operargs = {
        "src": repr(src),
        "present": repr(present),
    }

    result = _run_pyinfra("from pyinfra.operations import dnf", "dnf.rpm", operargs)

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def update():
    """
    Updates all dnf packages.
    """
    operargs = {}

    result = _run_pyinfra("from pyinfra.operations import dnf", "dnf.update", operargs)

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
    nobest=False,
    extra_install_args=None,
    extra_uninstall_args=None,
):
    """
    Install/remove/update dnf packages & updates.

    + packages: list of packages to ensure
    + present: whether the packages should be installed
    + latest: whether to upgrade packages without a specified version
    + update: run ``dnf update`` before installing packages
    + clean: run ``dnf clean`` before installing packages
    + nobest: add the no best option to install
    + extra_install_args: additional arguments to the dnf install command
    + extra_uninstall_args: additional arguments to the dnf uninstall command

    Versions:
        Package versions can be pinned as follows: ``<pkg>=<version>``

    **Examples:**

    .. code:: python

        # Update package list and install packages
        dnf.packages(
            name='Install Vim and Vim enhanced',
            packages=["vim-enhanced", "vim"],
            update=True,
        )

        # Install the latest versions of packages (always check)
        dnf.packages(
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
        "nobest": repr(nobest),
        "extra_install_args": repr(extra_install_args),
        "extra_uninstall_args": repr(extra_uninstall_args),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import dnf", "dnf.packages", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)
