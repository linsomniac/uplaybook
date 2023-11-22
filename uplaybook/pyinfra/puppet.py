#!/usr/bin/env python3

"""
## puppet


"""

from . import _run_pyinfra, PyInfraFailed, PyInfraResults
from typing import Optional, List
from ..internals import task, TemplateStr, Return


@task
def agent(server=None, port=None):
    """
    Run puppet agent

    + server: master server URL
    + port: puppet master port

    Note: Either 'USE_SUDO_LOGIN=True' or 'USE_SU_LOGIN=True'
    for puppet.agent() as `puppet` is added to the path in
    the .bash_profile.

    **Example:**

    .. code:: python

        puppet.agent()

        # We also expect a return code of:
        # 0=no changes or 2=changes applied
        puppet.agent(
            name="Run the puppet agent",
            success_exit_codes=[0, 2],
        )
    """
    operargs = {
        "server": repr(server),
        "port": repr(port),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import puppet", "puppet.agent", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)
