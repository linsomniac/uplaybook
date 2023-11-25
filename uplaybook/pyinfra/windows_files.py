#!/usr/bin/env python3

"""
## windows_files


The windows_files module handles windows filesystem state, file uploads and template generation.
"""

from . import _run_pyinfra, PyInfraFailed, PyInfraResults
from typing import Optional, List
from ..internals import task, TemplateStr, Return


@task
def download(
    src,
    dest,
    user=None,
    group=None,
    mode=None,
    cache_time=None,
    force=False,
    sha256sum=None,
    sha1sum=None,
    md5sum=None,
):
    r"""
    Download files from remote locations using curl or wget.

    + src: source URL of the file
    + dest: where to save the file
    + user: user to own the files
    + group: group to own the files
    + mode: permissions of the files
    + cache_time: if the file exists already, re-download after this time (in seconds)
    + force: always download the file, even if it already exists
    + sha256sum: sha256 hash to checksum the downloaded file against
    + sha1sum: sha1 hash to checksum the downloaded file against
    + md5sum: md5 hash to checksum the downloaded file against

    **Example:**

    .. code:: python

        windows_files.download(
            name="Download the Docker repo file",
            src="https://download.docker.com/linux/centos/docker-ce.repo",
            dest="C:\docker",
        )
    """
    operargs = {
        "src": repr(src),
        "dest": repr(dest),
        "user": repr(user),
        "group": repr(group),
        "mode": repr(mode),
        "cache_time": repr(cache_time),
        "force": repr(force),
        "sha256sum": repr(sha256sum),
        "sha1sum": repr(sha1sum),
        "md5sum": repr(md5sum),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import windows_files",
        "windows_files.download",
        operargs,
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def put(
    src,
    dest,
    user=None,
    group=None,
    mode=None,
    add_deploy_dir=True,
    create_remote_dir=True,
    force=False,
    assume_exists=False,
):
    r"""
    Upload a local file to the remote system.

    + src: local filename to upload
    + dest: remote filename to upload to
    + user: user to own the files
    + group: group to own the files
    + mode: permissions of the files
    + add_deploy_dir: src is relative to the deploy directory
    + create_remote_dir: create the remote directory if it doesn't exist
    + force: always upload the file, even if the remote copy matches
    + assume_exists: whether to assume the local file exists

    ``create_remote_dir``:
        If the remote directory does not exist it will be created using the same
        user & group as passed to ``files.put``. The mode will *not* be copied over,
        if this is required call ``files.directory`` separately.

    Note:
        This operation is not suitable for large files as it may involve copying
        the file before uploading it.

    **Examples:**

    .. code:: python

        # Note: This requires a 'files/motd' file on the local filesystem
        files.put(
            name="Update the message of the day file",
            src="data/content.json",
            dest="C:\data\content.json",
        )
    """
    operargs = {
        "src": repr(src),
        "dest": repr(dest),
        "user": repr(user),
        "group": repr(group),
        "mode": repr(mode),
        "add_deploy_dir": repr(add_deploy_dir),
        "create_remote_dir": repr(create_remote_dir),
        "force": repr(force),
        "assume_exists": repr(assume_exists),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import windows_files", "windows_files.put", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def file(
    path,
    present=True,
    assume_present=False,
    user=None,
    group=None,
    mode=None,
    touch=False,
    create_remote_dir=True,
):
    r"""
    Add/remove/update files.

    + path: path of the remote file
    + present: whether the file should exist
    + assume_present: whether to assume the file exists
    + TODO: user: user to own the files
    + TODO: group: group to own the files
    + TODO: mode: permissions of the files as an integer, eg: 755
    + touch: whether to touch the file
    + create_remote_dir: create the remote directory if it doesn't exist

    ``create_remote_dir``:
        If the remote directory does not exist it will be created using the same
        user & group as passed to ``files.put``. The mode will *not* be copied over,
        if this is required call ``files.directory`` separately.

    **Example:**

    .. code:: python

        files.file(
            name="Create c:\temp\hello.txt",
            path="c:\temp\hello.txt",
            touch=True,
        )
    """
    operargs = {
        "path": repr(path),
        "present": repr(present),
        "assume_present": repr(assume_present),
        "user": repr(user),
        "group": repr(group),
        "mode": repr(mode),
        "touch": repr(touch),
        "create_remote_dir": repr(create_remote_dir),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import windows_files", "windows_files.file", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def _create_remote_dir(state, host, remote_filename, user, group):
    operargs = {
        "state": repr(state),
        "host": repr(host),
        "remote_filename": repr(remote_filename),
        "user": repr(user),
        "group": repr(group),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import windows_files",
        "windows_files._create_remote_dir",
        operargs,
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def directory(
    path,
    present=True,
    assume_present=False,
    user=None,
    group=None,
    mode=None,
    recursive=False,
):
    r"""
    Add/remove/update directories.

    + path: path of the remote folder
    + present: whether the folder should exist
    + assume_present: whether to assume the directory exists
    + TODO: user: user to own the folder
    + TODO: group: group to own the folder
    + TODO: mode: permissions of the folder
    + TODO: recursive: recursively apply user/group/mode

    **Examples:**

    .. code:: python

        files.directory(
            name="Ensure the c:\temp\dir_that_we_want_removed is removed",
            path="c:\temp\dir_that_we_want_removed",
            present=False,
        )

        files.directory(
            name="Ensure c:\temp\foo\foo_dir exists",
            path="c:\temp\foo\foo_dir",
            recursive=True,
        )

        # multiple directories
        dirs = ["c:\temp\foo_dir1", "c:\temp\foo_dir2"]
        for dir in dirs:
            files.directory(
                name="Ensure the directory `{}` exists".format(dir),
                path=dir,
            )
    """
    operargs = {
        "path": repr(path),
        "present": repr(present),
        "assume_present": repr(assume_present),
        "user": repr(user),
        "group": repr(group),
        "mode": repr(mode),
        "recursive": repr(recursive),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import windows_files",
        "windows_files.directory",
        operargs,
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def _validate_path(path):
    operargs = {
        "path": repr(path),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import windows_files",
        "windows_files._validate_path",
        operargs,
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def link(
    path,
    target=None,
    present=True,
    assume_present=False,
    user=None,
    group=None,
    symbolic=True,
    force=True,
    create_remote_dir=True,
):
    r"""
    Add/remove/update links.

    + path: the name of the link
    + target: the file/directory the link points to
    + present: whether the link should exist
    + assume_present: whether to assume the link exists
    + user: user to own the link
    + group: group to own the link
    + symbolic: whether to make a symbolic link (vs hard link)
    + create_remote_dir: create the remote directory if it doesn't exist

    ``create_remote_dir``:
        If the remote directory does not exist it will be created using the same
        user & group as passed to ``files.put``. The mode will *not* be copied over,
        if this is required call ``files.directory`` separately.

    Source changes:
        If the link exists and points to a different target, pyinfra will remove it and
        recreate a new one pointing to then new target.

    **Examples:**

    .. code:: python

        # simple example showing how to link to a file
        files.link(
            name=r"Create link C:\issue2 that points to C:\issue",
            path=r"C:\issue2",
            target=r"C\issue",
        )
    """
    operargs = {
        "path": repr(path),
        "target": repr(target),
        "present": repr(present),
        "assume_present": repr(assume_present),
        "user": repr(user),
        "group": repr(group),
        "symbolic": repr(symbolic),
        "force": repr(force),
        "create_remote_dir": repr(create_remote_dir),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import windows_files", "windows_files.link", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)
