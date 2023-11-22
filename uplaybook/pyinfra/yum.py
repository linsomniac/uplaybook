#!/usr/bin/env python3

"""
## Yum package tasks

This module provides tasks for interacting with the yum package manager.
"""

from . import _run_pyinfra, PyInfraFailed, PyInfraResults
from typing import Optional, List
from ..internals import task, TemplateStr, Return


@task
def key(src):
    """
    Add yum gpg keys with ``rpm``.

    + src: filename or URL

    Note:
        always returns one command, not state checking

    **Example:**

    .. code:: python

        linux_id = host.get_fact(LinuxDistribution)["release_meta"].get("ID")
        yum.key(
            name="Add the Docker CentOS gpg key",
            src=f"https://download.docker.com/linux/{linux_id}/gpg",
        )
    """
    raise NotImplementedError()
    operargs = {
        "src": repr(src),
    }

    result = _run_pyinfra("from pyinfra.operations import yum", "yum.key", operargs)

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
    Add/remove/update yum repositories.

    + src: URL or name for the ``.repo``   file
    + present: whether the ``.repo`` file should be present
    + baseurl: the baseurl of the repo (if ``name`` is not a URL)
    + description: optional verbose description
    + enabled: whether this repo is enabled
    + gpgcheck: whether set ``gpgcheck=1``
    + gpgkey: the URL to the gpg key for this repo

    ``Baseurl``/``description``/``gpgcheck``/``gpgkey``:
        These are only valid when ``src`` is a filename (ie not a URL). This is
        for manual construction of repository files. Use a URL to download and
        install remote repository files.

    **Examples:**

    .. code:: python

        # Download a repository file
        yum.repo(
            name="Install Docker-CE repo via URL",
            src="https://download.docker.com/linux/centos/docker-ce.repo",
        )

        # Create the repository file from baseurl/etc
        yum.repo(
            name="Add the Docker CentOS repo",
            src="DockerCE",
            baseurl="https://download.docker.com/linux/centos/7/$basearch/stable",
        )
    """
    raise NotImplementedError()
    operargs = {
        "src": repr(src),
        "present": repr(present),
        "baseurl": repr(baseurl),
        "description": repr(description),
        "enabled": repr(enabled),
        "gpgcheck": repr(gpgcheck),
        "gpgkey": repr(gpgkey),
    }

    result = _run_pyinfra("from pyinfra.operations import yum", "yum.repo", operargs)

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

        major_version = host.get_fact(LinuxDistribution)["major"]
        dnf.rpm(
           name="Install EPEL rpm to enable EPEL repo",
           src=f"https://dl.fedoraproject.org/pub/epel/epel-release-latest-{major_version}.noarch.rpm",
        )
    """
    raise NotImplementedError()
    operargs = {
        "src": repr(src),
        "present": repr(present),
    }

    result = _run_pyinfra("from pyinfra.operations import yum", "yum.rpm", operargs)

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def update():
    """
    Updates all yum packages.
    """
    raise NotImplementedError()
    operargs = {}

    result = _run_pyinfra("from pyinfra.operations import yum", "yum.update", operargs)

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
    Install/remove/update yum packages & updates.

    + packages: list of packages to ensure
    + present: whether the packages should be installed
    + latest: whether to upgrade packages without a specified version
    + update: run ``yum update`` before installing packages
    + clean: run ``yum clean all`` before installing packages
    + nobest: add the no best option to install
    + extra_install_args: additional arguments to the yum install command
    + extra_uninstall_args: additional arguments to the yum uninstall command

    Versions:
        Package versions can be pinned as follows: ``<pkg>=<version>``

    **Examples:**

    .. code:: python

        # Update package list and install packages
        yum.packages(
            name="Install Vim and Vim enhanced",
            packages=["vim-enhanced", "vim"],
            update=True,
        )

        # Install the latest versions of packages (always check)
        yum.packages(
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
        "clean": repr(clean),
        "nobest": repr(nobest),
        "extra_install_args": repr(extra_install_args),
        "extra_uninstall_args": repr(extra_uninstall_args),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import yum", "yum.packages", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def key(src):
    """
    Add yum gpg keys with ``rpm``.

    + src: filename or URL

    Note:
        always returns one command, not state checking

    **Example:**

    .. code:: python

        linux_id = host.get_fact(LinuxDistribution)["release_meta"].get("ID")
        yum.key(
            name="Add the Docker CentOS gpg key",
            src=f"https://download.docker.com/linux/{linux_id}/gpg",
        )
    """
    raise NotImplementedError()
    operargs = {
        "src": repr(src),
    }

    result = _run_pyinfra("from pyinfra.operations import yum", "yum.key", operargs)

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
    Add/remove/update yum repositories.

    + src: URL or name for the ``.repo``   file
    + present: whether the ``.repo`` file should be present
    + baseurl: the baseurl of the repo (if ``name`` is not a URL)
    + description: optional verbose description
    + enabled: whether this repo is enabled
    + gpgcheck: whether set ``gpgcheck=1``
    + gpgkey: the URL to the gpg key for this repo

    ``Baseurl``/``description``/``gpgcheck``/``gpgkey``:
        These are only valid when ``src`` is a filename (ie not a URL). This is
        for manual construction of repository files. Use a URL to download and
        install remote repository files.

    **Examples:**

    .. code:: python

        # Download a repository file
        yum.repo(
            name="Install Docker-CE repo via URL",
            src="https://download.docker.com/linux/centos/docker-ce.repo",
        )

        # Create the repository file from baseurl/etc
        yum.repo(
            name="Add the Docker CentOS repo",
            src="DockerCE",
            baseurl="https://download.docker.com/linux/centos/7/$basearch/stable",
        )
    """
    raise NotImplementedError()
    operargs = {
        "src": repr(src),
        "present": repr(present),
        "baseurl": repr(baseurl),
        "description": repr(description),
        "enabled": repr(enabled),
        "gpgcheck": repr(gpgcheck),
        "gpgkey": repr(gpgkey),
    }

    result = _run_pyinfra("from pyinfra.operations import yum", "yum.repo", operargs)

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

        major_version = host.get_fact(LinuxDistribution)["major"]
        dnf.rpm(
           name="Install EPEL rpm to enable EPEL repo",
           src=f"https://dl.fedoraproject.org/pub/epel/epel-release-latest-{major_version}.noarch.rpm",
        )
    """
    raise NotImplementedError()
    operargs = {
        "src": repr(src),
        "present": repr(present),
    }

    result = _run_pyinfra("from pyinfra.operations import yum", "yum.rpm", operargs)

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def update():
    """
    Updates all yum packages.
    """
    raise NotImplementedError()
    operargs = {}

    result = _run_pyinfra("from pyinfra.operations import yum", "yum.update", operargs)

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
    Install/remove/update yum packages & updates.

    + packages: list of packages to ensure
    + present: whether the packages should be installed
    + latest: whether to upgrade packages without a specified version
    + update: run ``yum update`` before installing packages
    + clean: run ``yum clean all`` before installing packages
    + nobest: add the no best option to install
    + extra_install_args: additional arguments to the yum install command
    + extra_uninstall_args: additional arguments to the yum uninstall command

    Versions:
        Package versions can be pinned as follows: ``<pkg>=<version>``

    **Examples:**

    .. code:: python

        # Update package list and install packages
        yum.packages(
            name="Install Vim and Vim enhanced",
            packages=["vim-enhanced", "vim"],
            update=True,
        )

        # Install the latest versions of packages (always check)
        yum.packages(
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
        "clean": repr(clean),
        "nobest": repr(nobest),
        "extra_install_args": repr(extra_install_args),
        "extra_uninstall_args": repr(extra_uninstall_args),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import yum", "yum.packages", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)
