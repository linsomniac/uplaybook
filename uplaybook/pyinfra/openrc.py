#!/usr/bin/env python3

"""
## openrc


Manage OpenRC init services.
"""

from . import _run_pyinfra, PyInfraFailed, PyInfraResults
from typing import Optional, List
from ..internals import task, TemplateStr, Return


@task
def service(
    service,
    running=True,
    restarted=False,
    reloaded=False,
    command=None,
    enabled=None,
    runlevel="default",
):
    """
    Manage the state of OpenRC services.

    + service: name of the service to manage
    + running: whether the service should be running
    + restarted: whether the service should be restarted
    + reloaded: whether the service should be reloaded
    + command: custom command to pass like: ``rc-service <service> <command>``
    + enabled: whether this service should be enabled/disabled on boot
    + runlevel: runlevel to manage services for
    """
    operargs = {
        "service": repr(service),
        "running": repr(running),
        "restarted": repr(restarted),
        "reloaded": repr(reloaded),
        "command": repr(command),
        "enabled": repr(enabled),
        "runlevel": repr(runlevel),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import openrc", "openrc.service", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)
