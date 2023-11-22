#!/usr/bin/env python3

"""
## lxd tasks

This module provides tasks for managing lxd containers.
"""

from . import _run_pyinfra, PyInfraFailed, PyInfraResults
from typing import Optional, List
from ..internals import task, TemplateStr, Return


@task
def get_container_named(name, containers):
    operargs = {
        "name": repr(name),
        "containers": repr(containers),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import lxd", "lxd.get_container_named", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def container(id, present=True, image="ubuntu:16.04"):
    """
    Add/remove LXD containers.

    Note: does not check if an existing container is based on the specified
    image.

    + id: name/identifier for the container
    + image: image to base the container on
    + present: whether the container should be present or absent

    **Example:**

    .. code:: python

        lxd.container(
            name="Add an ubuntu container",
            id="ubuntu19",
            image="ubuntu:19.10",
        )
    """
    operargs = {
        "id": repr(id),
        "present": repr(present),
        "image": repr(image),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import lxd", "lxd.container", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)
