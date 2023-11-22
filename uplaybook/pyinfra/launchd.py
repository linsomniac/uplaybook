#!/usr/bin/env python3

"""
## launchd


Manage launchd services.
"""

from . import _run_pyinfra, PyInfraFailed, PyInfraResults
from typing import Optional, List
from ..internals import task, TemplateStr, Return


@task
def service(service, running=True, restarted=False, command=None):
    """
    Manage the state of systemd managed services.

    + service: name of the service to manage
    + running: whether the service should be running
    + restarted: whether the service should be restarted
    + command: custom command to pass like: ``launchctl <command> <service>``
    + enabled: whether this service should be enabled/disabled on boot
    """
    operargs = {
        "service": repr(service),
        "running": repr(running),
        "restarted": repr(restarted),
        "command": repr(command),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import launchd", "launchd.service", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)
