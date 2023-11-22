#!/usr/bin/env python3

"""
## bsdinit


Manage BSD init services (``/etc/rc.d``, ``/usr/local/etc/rc.d``).
"""

from . import _run_pyinfra, PyInfraFailed, PyInfraResults
from typing import Optional, List
from ..internals import task, TemplateStr, Return


@task
def service(
    service, running=True, restarted=False, reloaded=False, command=None, enabled=None
):
    """
    Manage the state of BSD init services.

    + service: name of the service to manage
    + running: whether the service should be running
    + restarted: whether the service should be restarted
    + reloaded: whether the service should be reloaded
    + command: custom command to pass like: ``/etc/rc.d/<service> <command>``
    + enabled: whether this service should be enabled/disabled on boot
    """
    operargs = {
        "service": repr(service),
        "running": repr(running),
        "restarted": repr(restarted),
        "reloaded": repr(reloaded),
        "command": repr(command),
        "enabled": repr(enabled),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import bsdinit", "bsdinit.service", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)
