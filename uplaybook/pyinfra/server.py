#!/usr/bin/env python3

"""
## Server tasks

This module provides tasks for working with OS services.
"""

from . import _run_pyinfra, PyInfraFailed, PyInfraResults
from typing import Optional, List
from ..internals import task, TemplateStr, Return


@task
def reboot(delay=10, interval=1, reboot_timeout=300):
    """
    Reboot the server and wait for reconnection.

    + delay: number of seconds to wait before attempting reconnect
    + interval: interval (s) between reconnect attempts
    + reboot_timeout: total time before giving up reconnecting

    **Example:**

    .. code:: python

        server.reboot(
            name="Reboot the server and wait to reconnect",
            delay=60,
            reboot_timeout=600,
        )
    """
    operargs = {
        "delay": repr(delay),
        "interval": repr(interval),
        "reboot_timeout": repr(reboot_timeout),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import server", "server.reboot", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def wait(port):
    """
    Waits for a port to come active on the target machine. Requires netstat, checks every
    second.

    + port: port number to wait for

    **Example:**

    .. code:: python

        server.wait(
            name="Wait for webserver to start",
            port=80,
        )
    """
    operargs = {
        "port": repr(port),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import server", "server.wait", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def shell(commands):
    """
    Run raw shell code on server during a deploy. If the command would
    modify data that would be in a fact, the fact would not be updated
    since facts are only run at the start of a deploy.

    + commands: command or list of commands to execute on the remote server

    **Example:**

    .. code:: python

        server.shell(
            name="Run lxd auto init",
            commands=["lxd init --auto"],
        )
    """
    operargs = {
        "commands": repr(commands),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import server", "server.shell", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def script(src, args=()):
    """
    Upload and execute a local script on the remote host.

    + src: local script filename to upload & execute
    + args: iterable to pass as arguments to the script

    **Example:**

    .. code:: python

        # Note: This assumes there is a file in files/hello.bash locally.
        server.script(
            name="Hello",
            src="files/hello.bash",
        )

        # Example passing arguments to the script
        server.script(
            name="Hello",
            src="files/hello.bash",
            args=("do-something", "with-this"),
        )
    """
    operargs = {
        "src": repr(src),
        "args": repr(args),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import server", "server.script", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def script_template(src, args=(), **data):
    """
    Generate, upload and execute a local script template on the remote host.

    + src: local script template filename

    **Example:**

    .. code:: python

        # Example showing how to pass python variable to a script template file.
        # The .j2 file can use `{{ some_var }}` to be interpolated.
        # To see output need to run pyinfra with '-v'
        # Note: This assumes there is a file in templates/hello2.bash.j2 locally.
        some_var = 'blah blah blah '
        server.script_template(
            name="Hello from script",
            src="templates/hello2.bash.j2",
            some_var=some_var,
        )
    """
    operargs = {
        "src": repr(src),
        "args": repr(args),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import server", "server.script_template", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def modprobe(module, present=True, force=False):
    """
    Load/unload kernel modules.

    + module: name of the module to manage
    + present: whether the module should be loaded or not
    + force: whether to force any add/remove modules

    **Example:**

    .. code:: python

        server.modprobe(
            name="Silly example for modprobe",
            module="floppy",
        )
    """
    operargs = {
        "module": repr(module),
        "present": repr(present),
        "force": repr(force),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import server", "server.modprobe", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def mount(path, mounted=True, options=None, device=None, fs_type=None):
    """
    Manage mounted filesystems.

    + path: the path of the mounted filesystem
    + mounted: whether the filesystem should be mounted
    + options: the mount options

    Options:
        If the currently mounted filesystem does not have all of the provided
        options it will be remounted with the options provided.

    ``/etc/fstab``:
        This operation does not attempt to modify the on disk fstab file - for
        that you should use the `files.line operation <./files.html#files-line>`_.
    """
    operargs = {
        "path": repr(path),
        "mounted": repr(mounted),
        "options": repr(options),
        "device": repr(device),
        "fs_type": repr(fs_type),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import server", "server.mount", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def hostname(hostname, hostname_file=None):
    """
    Set the system hostname using ``hostnamectl`` or ``hostname`` on older systems.

    + hostname: the hostname that should be set
    + hostname_file: the file that permanently sets the hostname

    Hostname file:
        The hostname file only matters no systems that do not have ``hostnamectl``,
        which is part of ``systemd``.

        By default pyinfra will auto detect this by targeting ``/etc/hostname``
        on Linux and ``/etc/myname`` on OpenBSD.

        To completely disable writing the hostname file, set ``hostname_file=False``.

    **Example:**

    .. code:: python

        server.hostname(
            name="Set the hostname",
            hostname="server1.example.com",
        )
    """
    operargs = {
        "hostname": repr(hostname),
        "hostname_file": repr(hostname_file),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import server", "server.hostname", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def sysctl(key, value, persist=False, persist_file="/etc/sysctl.conf"):
    """
    Edit sysctl configuration.

    + key: name of the sysctl setting to ensure
    + value: the value or list of values the sysctl should be
    + persist: whether to write this sysctl to the config
    + persist_file: file to write the sysctl to persist on reboot

    **Example:**

    .. code:: python

        server.sysctl(
            name="Change the fs.file-max value",
            key="fs.file-max",
            value=100000,
            persist=True,
        )
    """
    operargs = {
        "key": repr(key),
        "value": repr(value),
        "persist": repr(persist),
        "persist_file": repr(persist_file),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import server", "server.sysctl", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def service(
    service, running=True, restarted=False, reloaded=False, command=None, enabled=None
):
    """
    Manage the state of services. This command checks for the presence of all the
    Linux init systems ``pyinfra`` can handle and executes the relevant operation.

    + service: name of the service to manage
    + running: whether the service should be running
    + restarted: whether the service should be restarted
    + reloaded: whether the service should be reloaded
    + command: custom command execute
    + enabled: whether this service should be enabled/disabled on boot

    **Example:**

    .. code:: python

        server.service(
            name="Enable open-vm-tools service",
            service="open-vm-tools",
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
    }

    result = _run_pyinfra(
        "from pyinfra.operations import server", "server.service", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def packages(packages, present=True):
    """
    Add or remove system packages. This command checks for the presence of all the
    system package managers ``pyinfra`` can handle and executes the relevant operation.

    + packages: list of packages to ensure
    + present: whether the packages should be installed

    **Example:**

    .. code:: python

        server.packages(
            name="Install Vim and vimpager",
            packages=["vimpager", "vim"],
        )
    """
    operargs = {
        "packages": repr(packages),
        "present": repr(present),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import server", "server.packages", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def crontab(
    command,
    present=True,
    user=None,
    cron_name=None,
    minute="*",
    hour="*",
    month="*",
    day_of_week="*",
    day_of_month="*",
    special_time=None,
    interpolate_variables=False,
):
    """
    Add/remove/update crontab entries.

    + command: the command for the cron
    + present: whether this cron command should exist
    + user: the user whose crontab to manage
    + cron_name: name the cronjob so future changes to the command will overwrite
    + minute: which minutes to execute the cron
    + hour: which hours to execute the cron
    + month: which months to execute the cron
    + day_of_week: which day of the week to execute the cron
    + day_of_month: which day of the month to execute the cron
    + special_time: cron "nickname" time (@reboot, @daily, etc), overrides others
    + interpolate_variables: whether to interpolate variables in ``command``

    Cron commands:
        Unless ``name`` is specified the command is used to identify crontab entries.
        This means commands must be unique within a given users crontab. If you require
        multiple identical commands, provide a different name argument for each.

    Special times:
        When provided, ``special_time`` will be used instead of any values passed in
        for ``minute``/``hour``/``month``/``day_of_week``/``day_of_month``.

    **Example:**

    .. code:: python

        # simple example for a crontab
        server.crontab(
            name="Backup /etc weekly",
            command="/bin/tar cf /tmp/etc_bup.tar /etc",
            name="backup_etc",
            day_of_week=0,
            hour=1,
            minute=0,
        )
    """
    operargs = {
        "command": repr(command),
        "present": repr(present),
        "user": repr(user),
        "cron_name": repr(cron_name),
        "minute": repr(minute),
        "hour": repr(hour),
        "month": repr(month),
        "day_of_week": repr(day_of_week),
        "day_of_month": repr(day_of_month),
        "special_time": repr(special_time),
        "interpolate_variables": repr(interpolate_variables),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import server", "server.crontab", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def group(group, present=True, system=False, gid=None):
    """
    Add/remove system groups.

    + group: name of the group to ensure
    + present: whether the group should be present or not
    + system: whether to create a system group
    + gid: use a specific groupid number

    System users:
        System users don't exist on BSD, so the argument is ignored for BSD targets.

    **Examples:**

    .. code:: python

        server.group(
            name="Create docker group",
            group="docker",
        )

        # multiple groups
        for group in ["wheel", "lusers"]:
            server.group(
                name=f"Create the group {group}",
                group=group,
            )
    """
    operargs = {
        "group": repr(group),
        "present": repr(present),
        "system": repr(system),
        "gid": repr(gid),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import server", "server.group", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def user_authorized_keys(
    user,
    public_keys,
    group=None,
    delete_keys=False,
    authorized_key_directory=None,
    authorized_key_filename=None,
):
    """
    Manage `authorized_keys` of system users.

    + user: name of the user to ensure
    + public_keys: list of public keys to attach to this user, ``home`` must be specified
    + group: the users primary group
    + delete_keys: whether to remove any keys not specified in ``public_keys``

    Public keys:
        These can be provided as strings containing the public key or as a path to
        a public key file which ``pyinfra`` will read.

    **Examples:**

    .. code:: python

        server.user_authorized_keys(
            name="Ensure user has a public key",
            user="kevin",
            public_keys=["ed25519..."],
        )
    """
    operargs = {
        "user": repr(user),
        "public_keys": repr(public_keys),
        "group": repr(group),
        "delete_keys": repr(delete_keys),
        "authorized_key_directory": repr(authorized_key_directory),
        "authorized_key_filename": repr(authorized_key_filename),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import server", "server.user_authorized_keys", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def user(
    user,
    present=True,
    home=None,
    shell=None,
    group=None,
    groups=None,
    public_keys=None,
    delete_keys=False,
    ensure_home=True,
    create_home=False,
    system=False,
    uid=None,
    comment=None,
    add_deploy_dir=True,
    unique=True,
):
    """
    Add/remove/update system users & their ssh `authorized_keys`.

    + user: name of the user to ensure
    + present: whether this user should exist
    + home: the users home directory
    + shell: the users shell
    + group: the users primary group
    + groups: the users secondary groups
    + public_keys: list of public keys to attach to this user, ``home`` must be specified
    + delete_keys: whether to remove any keys not specified in ``public_keys``
    + ensure_home: whether to ensure the ``home`` directory exists
    + create_home: whether to new user create home directories from the system skeleton
    + system: whether to create a system account
    + uid: use a specific userid number
    + comment: the user GECOS comment
    + add_deploy_dir: any public_key filenames are relative to the deploy directory
    + unique: prevent creating users with duplicate UID

    Home directory:
        When ``ensure_home`` or ``public_keys`` are provided, ``home`` defaults to
        ``/home/{name}``. When ``create_home`` is ``True`` any newly created users
        will be created with the ``-m`` flag to build a new home directory from the
        systems skeleton directory.

    Public keys:
        These can be provided as strings containing the public key or as a path to
        a public key file which ``pyinfra`` will read.

    **Examples:**

    .. code:: python

        server.user(
            name="Ensure user is removed",
            user="kevin",
            present=False,
        )

        server.user(
            name="Ensure myweb user exists",
            user="myweb",
            shell="/bin/bash",
        )

        # multiple users
        for user in ["kevin", "bob"]:
            server.user(
                name=f"Ensure user {user} is removed",
                user=user,
                present=False,
            )
    """
    operargs = {
        "user": repr(user),
        "present": repr(present),
        "home": repr(home),
        "shell": repr(shell),
        "group": repr(group),
        "groups": repr(groups),
        "public_keys": repr(public_keys),
        "delete_keys": repr(delete_keys),
        "ensure_home": repr(ensure_home),
        "create_home": repr(create_home),
        "system": repr(system),
        "uid": repr(uid),
        "comment": repr(comment),
        "add_deploy_dir": repr(add_deploy_dir),
        "unique": repr(unique),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import server", "server.user", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def locale(locale, present=True):
    """
    Enable/Disable locale.

    + locale: name of the locale to enable/disable
    + present: whether this locale should be present or not

    **Examples:**

    .. code:: python

        server.locale(
            name="Ensure en_GB.UTF-8 locale is not present",
            locale="en_GB.UTF-8",
            present=False,
        )

        server.locale(
            name="Ensure en_GB.UTF-8 locale is present",
            locale="en_GB.UTF-8",
        )
    """
    operargs = {
        "locale": repr(locale),
        "present": repr(present),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import server", "server.locale", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def remove_any_askpass_file(state, host):
    operargs = {
        "state": repr(state),
        "host": repr(host),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import server",
        "server.remove_any_askpass_file",
        operargs,
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def wait_and_reconnect(state, host):
    operargs = {
        "state": repr(state),
        "host": repr(host),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import server", "server.wait_and_reconnect", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def partition(predicate, iterable):
    operargs = {
        "predicate": repr(predicate),
        "iterable": repr(iterable),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import server", "server.partition", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def comma_sep(value):
    operargs = {
        "value": repr(value),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import server", "server.comma_sep", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def read_any_pub_key_file(key):
    operargs = {
        "key": repr(key),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import server",
        "server.read_any_pub_key_file",
        operargs,
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)
