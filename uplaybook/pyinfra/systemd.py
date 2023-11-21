#!/usr/bin/env python3

"""
## Systemd tasks

This module provides tasks for interacting with systemd.
"""

from . import _run_pyinfra, PyInfraFailed, PyInfraResults
from typing import Optional, List
from ..internals import task, TemplateStr, Return


@task
def daemon_reload(user_mode=False, machine=None, user_name=None):
    """
    Reload the systemd daemon to read unit file changes.

    + user_mode: whether to use per-user systemd (systemctl --user) or not
    + machine: the machine name to connect to
    + user_name: connect to a specific user's systemd session
    """
    operargs = {
        "user_mode": repr(user_mode),
        "machine": repr(machine),
        "user_name": repr(user_name),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import systemd", "systemd.daemon_reload", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def service(
    service,
    running=True,
    restarted=False,
    reloaded=False,
    command=None,
    enabled=None,
    daemon_reload=False,
    user_mode=False,
    machine=None,
    user_name=None,
):
    """
    Manage the state of systemd managed units.

    + service: name of the systemd unit to manage
    + running: whether the unit should be running
    + restarted: whether the unit should be restarted
    + reloaded: whether the unit should be reloaded
    + command: custom command to pass like: ``/etc/rc.d/<name> <command>``
    + enabled: whether this unit should be enabled/disabled on boot
    + daemon_reload: reload the systemd daemon to read updated unit files
    + user_mode: whether to use per-user systemd (systemctl --user) or not
    + machine: the machine name to connect to
    + user_name: connect to a specific user's systemd session

    **Examples:**

    .. code:: python

        systemd.service(
            name="Restart and enable the dnsmasq service",
            service="dnsmasq.service",
            running=True,
            restarted=True,
            enabled=True,
        )

        systemd.service(
            name="Enable logrotate timer",
            service="logrotate.timer",
            running=True,
            enabled=True,
        )
    """
    operargs = {
        "service": repr(service),
        "running": repr(running),
        "restarted": repr(restarted),
        "reloaded": repr(reloaded),
        "command": repr(command),
        "enabled": repr(enabled),
        "daemon_reload": repr(daemon_reload),
        "user_mode": repr(user_mode),
        "machine": repr(machine),
        "user_name": repr(user_name),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import systemd", "systemd.service", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)
