#!/usr/bin/env python3

"""
## windows


The windows module handles misc windows operations.
"""

from . import _run_pyinfra, PyInfraFailed, PyInfraResults
from typing import Optional, List
from ..internals import task, TemplateStr, Return


@task
def service(service, running=True, restart=False, suspend=False):
    """
    Stop/Start a Windows service.

    + service: name of the service to manage
    + running: whether the the service should be running or stopped
    + restart: whether the the service should be restarted
    + suspend: whether the the service should be suspended

    **Example:**

    .. code:: python

        windows.service(
            name="Stop the spooler service",
            service="service",
            running=False,
        )
    """
    operargs = {
        "service": repr(service),
        "running": repr(running),
        "restart": repr(restart),
        "suspend": repr(suspend),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import windows", "windows.service", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def reboot():
    """
    Restart the server.
    """
    operargs = {}

    result = _run_pyinfra(
        "from pyinfra.operations import windows", "windows.reboot", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)
