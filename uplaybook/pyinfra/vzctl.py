#!/usr/bin/env python3

"""
## vzctl


Manage OpenVZ containers with ``vzctl``.
"""

from . import _run_pyinfra, PyInfraFailed, PyInfraResults
from typing import Optional, List
from ..internals import task, TemplateStr, Return


@task
def start(ctid, force=False):
    """
    Start OpenVZ containers.

    + ctid: CTID of the container to start
    + force: whether to force container start
    """
    operargs = {
        "ctid": repr(ctid),
        "force": repr(force),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import vzctl", "vzctl.start", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def stop(ctid):
    """
    Stop OpenVZ containers.

    + ctid: CTID of the container to stop
    """
    operargs = {
        "ctid": repr(ctid),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import vzctl", "vzctl.stop", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def restart(ctid, force=False):
    """
    Restart OpenVZ containers.

    + ctid: CTID of the container to restart
    + force: whether to force container start
    """
    operargs = {
        "ctid": repr(ctid),
        "force": repr(force),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import vzctl", "vzctl.restart", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def mount(ctid):
    """
    Mount OpenVZ container filesystems.

    + ctid: CTID of the container to mount
    """
    operargs = {
        "ctid": repr(ctid),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import vzctl", "vzctl.mount", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def unmount(ctid):
    """
    Unmount OpenVZ container filesystems.

    + ctid: CTID of the container to unmount
    """
    operargs = {
        "ctid": repr(ctid),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import vzctl", "vzctl.unmount", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def delete(ctid):
    """
    Delete OpenVZ containers.

    + ctid: CTID of the container to delete
    """
    operargs = {
        "ctid": repr(ctid),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import vzctl", "vzctl.delete", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def create(ctid, template=None):
    """
    Create OpenVZ containers.

    + ctid: CTID of the container to create
    """
    operargs = {
        "ctid": repr(ctid),
        "template": repr(template),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import vzctl", "vzctl.create", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def set(ctid, save=True, **settings):
    """
    Set OpenVZ container details.

    + ctid: CTID of the container to set
    + save: whether to save the changes
    + settings: settings/arguments to apply to the container

    Settings/arguments:
        these are mapped directly to ``vztctl`` arguments, eg
        ``hostname='my-host.net'`` becomes ``--hostname my-host.net``.
    """
    operargs = {
        "ctid": repr(ctid),
        "save": repr(save),
    }

    result = _run_pyinfra("from pyinfra.operations import vzctl", "vzctl.set", operargs)

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)
