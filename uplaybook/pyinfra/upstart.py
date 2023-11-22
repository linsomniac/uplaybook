#!/usr/bin/env python3

"""
## upstart


Manage upstart services.
"""

from . import _run_pyinfra, PyInfraFailed, PyInfraResults
from typing import Optional, List
from ..internals import task, TemplateStr, Return


@task
def service(
    service, running=True, restarted=False, reloaded=False, command=None, enabled=None
):
    """
    Manage the state of upstart managed services.

    + service: name of the service to manage
    + running: whether the service should be running
    + restarted: whether the service should be restarted
    + reloaded: whether the service should be reloaded
    + command: custom command to pass like: ``/etc/rc.d/<service> <command>``
    + enabled: whether this service should be enabled/disabled on boot

    Enabling/disabling services:
        Upstart jobs define runlevels in their config files - as such there is no way to
        edit/list these without fiddling with the config. So pyinfra simply manages the
        existence of a ``/etc/init/<service>.override`` file, and sets its content to
        "manual" to disable automatic start of services.
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
        "from pyinfra.operations import upstart", "upstart.service", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)
