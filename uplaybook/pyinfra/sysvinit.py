#!/usr/bin/env python3

"""
## sysvinit


Manage sysvinit services (``/etc/init.d``).
"""

from . import _run_pyinfra, PyInfraFailed, PyInfraResults
from typing import Optional, List
from ..internals import task, TemplateStr, Return


@task
def service(
    service, running=True, restarted=False, reloaded=False, enabled=None, command=None
):
    """
    Manage the state of SysV Init (/etc/init.d) services.

    + service: name of the service to manage
    + running: whether the service should be running
    + restarted: whether the service should be restarted
    + reloaded: whether the service should be reloaded
    + enabled: whether this service should be enabled/disabled
    + command: command (eg. reload) to run like: ``/etc/init.d/<service> <command>``

    Enabled:
        Because managing /etc/rc.d/X files is a mess, only certain Linux distributions
        support enabling/disabling services:

        + Ubuntu/Debian (``update-rc.d``)
        + CentOS/Fedora/RHEL (``chkconfig``)
        + Gentoo (``rc-update``)

        For other distributions and more granular service control, see the
        ``sysvinit.enable`` operation.

    **Example:**

    .. code:: python

        sysvinit.service(
            name="Restart and enable rsyslog",
            service="rsyslog",
            restarted=True,
            enabled=True,
        )
    """
    operargs = {
        "service": repr(service),
        "running": repr(running),
        "restarted": repr(restarted),
        "reloaded": repr(reloaded),
        "enabled": repr(enabled),
        "command": repr(command),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import sysvinit", "sysvinit.service", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def enable(
    service,
    start_priority=20,
    stop_priority=80,
    start_levels=(2, 3, 4, 5),
    stop_levels=(0, 1, 6),
):
    """
    Manually enable /etc/init.d scripts by creating /etc/rcX.d/Y links.

    + service: name of the service to enable
    + start_priority: priority to start the service
    + stop_priority: priority to stop the service
    + start_levels: which runlevels should the service run when enabled
    + stop_levels: which runlevels should the service stop when enabled

    **Example:**

    .. code:: python

        init.d_enable(
            name="Finer control on which runlevels rsyslog should run",
            service="rsyslog",
            start_levels=(3, 4, 5),
            stop_levels=(0, 1, 2, 6),
        )
    """
    operargs = {
        "service": repr(service),
        "start_priority": repr(start_priority),
        "stop_priority": repr(stop_priority),
        "start_levels": repr(start_levels),
        "stop_levels": repr(stop_levels),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import sysvinit", "sysvinit.enable", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)
