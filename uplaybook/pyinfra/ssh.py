#!/usr/bin/env python3

"""
## SSH (Secure SHell) tasks

This module provides tasks for using SSH to copy files to/from remote machines and running commands.
"""

from . import _run_pyinfra, PyInfraFailed, PyInfraResults
from typing import Optional, List
from ..internals import task, TemplateStr, Return


@task
def keyscan(hostname, force=False, port=22):
    """
    Check/add hosts to the ``~/.ssh/known_hosts`` file.

    + hostname: hostname that should have a key in ``known_hosts``
    + force: if the key already exists, remove and rescan

    **Example:**

    .. code:: python

        ssh.keyscan(
            name="Set add server two to known_hosts on one",
            hostname="two.example.com",
        )
    """
    operargs = {
        "hostname": repr(hostname),
        "force": repr(force),
        "port": repr(port),
    }

    result = _run_pyinfra("from pyinfra.operations import ssh", "ssh.keyscan", operargs)

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def command(hostname, command, user=None, port=22):
    """
    Execute commands on other servers over SSH.

    + hostname: the hostname to connect to
    + command: the command to execute
    + user: connect with this user
    + port: connect to this port

    **Example:**

    .. code:: python

        ssh.command(
            name="Create file by running echo from host one to host two",
            hostname="two.example.com",
            command="echo 'one was here' > /tmp/one.txt",
            user="vagrant",
        )
    """
    operargs = {
        "hostname": repr(hostname),
        "command": repr(command),
        "user": repr(user),
        "port": repr(port),
    }

    result = _run_pyinfra("from pyinfra.operations import ssh", "ssh.command", operargs)

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def upload(
    hostname,
    filename,
    remote_filename=None,
    port=22,
    user=None,
    use_remote_sudo=False,
    ssh_keyscan=False,
):
    """
    Upload files to other servers using ``scp``.

    + hostname: hostname to upload to
    + filename: file to upload
    + remote_filename: where to upload the file to (defaults to ``filename``)
    + port: connect to this port
    + user: connect with this user
    + use_remote_sudo: upload to a temporary location and move using sudo
    + ssh_keyscan: execute ``ssh.keyscan`` before uploading the file
    """
    operargs = {
        "hostname": repr(hostname),
        "filename": repr(filename),
        "remote_filename": repr(remote_filename),
        "port": repr(port),
        "user": repr(user),
        "use_remote_sudo": repr(use_remote_sudo),
        "ssh_keyscan": repr(ssh_keyscan),
    }

    result = _run_pyinfra("from pyinfra.operations import ssh", "ssh.upload", operargs)

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def download(
    hostname,
    filename,
    local_filename=None,
    force=False,
    port=22,
    user=None,
    ssh_keyscan=False,
):
    """
    Download files from other servers using ``scp``.

    + hostname: hostname to upload to
    + filename: file to download
    + local_filename: where to download the file to (defaults to ``filename``)
    + force: always download the file, even if present locally
    + port: connect to this port
    + user: connect with this user
    + ssh_keyscan: execute ``ssh.keyscan`` before uploading the file
    """
    operargs = {
        "hostname": repr(hostname),
        "filename": repr(filename),
        "local_filename": repr(local_filename),
        "force": repr(force),
        "port": repr(port),
        "user": repr(user),
        "ssh_keyscan": repr(ssh_keyscan),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import ssh", "ssh.download", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)
