#!/usr/bin/env python3

"""
## Pip tasks

This module provides tasks for interacting with pip packages.
"""

from . import _run_pyinfra, PyInfraFailed, PyInfraResults
from typing import Optional, List
from ..internals import task, TemplateStr, Return


@task
def virtualenv(
    path, python=None, venv=False, site_packages=False, always_copy=False, present=True
):
    """
    Add/remove Python virtualenvs.

    + python: python interpreter to use
    + venv: use standard venv module instead of virtualenv
    + site_packages: give access to the global site-packages
    + always_copy: always copy files rather than symlinking
    + present: whether the virtualenv should exist

    **Example:**

    .. code:: python

        pip.virtualenv(
            name="Create a virtualenv",
            path="/usr/local/bin/venv",
        )
    """
    operargs = {
        "path": repr(path),
        "python": repr(python),
        "venv": repr(venv),
        "site_packages": repr(site_packages),
        "always_copy": repr(always_copy),
        "present": repr(present),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import pip", "pip.virtualenv", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def venv(path, python=None, site_packages=False, always_copy=False, present=True):
    """
    Add/remove Python virtualenvs.

    + python: python interpreter to use
    + site_packages: give access to the global site-packages
    + always_copy: always copy files rather than symlinking
    + present: whether the virtualenv should exist

    **Example:**

    .. code:: python

        pip.venv(
            name="Create a virtualenv",
            path="/usr/local/bin/venv",
        )
    """
    operargs = {
        "path": repr(path),
        "python": repr(python),
        "site_packages": repr(site_packages),
        "always_copy": repr(always_copy),
        "present": repr(present),
    }

    result = _run_pyinfra("from pyinfra.operations import pip", "pip.venv", operargs)

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def packages(
    packages=None,
    present=True,
    latest=False,
    requirements=None,
    pip="pip3",
    virtualenv=None,
    virtualenv_kwargs=None,
    extra_install_args=None,
):
    """
    Install/remove/update pip packages.

    + packages: list of packages to ensure
    + present: whether the packages should be installed
    + latest: whether to upgrade packages without a specified version
    + requirements: location of requirements file to install/uninstall
    + pip: name or path of the pip directory to use
    + virtualenv: root directory of virtualenv to work in
    + virtualenv_kwargs: dictionary of arguments to pass to ``pip.virtualenv``
    + extra_install_args: additional arguments to the pip install command

    Virtualenv:
        This will be created if it does not exist already. ``virtualenv_kwargs``
        will be passed to ``pip.virtualenv`` which can be used to control how
        the env is created.

    Versions:
        Package versions can be pinned like pip: ``<pkg>==<version>``.

    **Example:**

    .. code:: python

        pip.packages(
            name="Install pyinfra into a virtualenv",
            packages=["pyinfra"],
            virtualenv="/usr/local/bin/venv",
        )
    """
    operargs = {
        "packages": repr(packages),
        "present": repr(present),
        "latest": repr(latest),
        "requirements": repr(requirements),
        "pip": repr(pip),
        "virtualenv": repr(virtualenv),
        "virtualenv_kwargs": repr(virtualenv_kwargs),
        "extra_install_args": repr(extra_install_args),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import pip", "pip.packages", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)
