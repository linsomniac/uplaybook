#!/usr/bin/env python3

"""
## File-related tasks

This module provides tasks for manipulating the filesystem.
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
    headers=None,
    insecure=False,
):
    """
    Download files from remote locations using ``curl`` or ``wget``.

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
    + headers: optional dictionary of headers to set for the HTTP request
    + insecure: disable SSL verification for the HTTP request

    **Example:**

    ```python
    files.download(
        name="Download the Docker repo file",
        src="https://download.docker.com/linux/centos/docker-ce.repo",
        dest="/etc/yum.repos.d/docker-ce.repo",
    )
    ```
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
        "headers": repr(headers),
        "insecure": repr(insecure),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import files", "files.download", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def line(
    path,
    line,
    present=True,
    replace=None,
    flags=None,
    backup=False,
    interpolate_variables=False,
    escape_regex_characters=False,
    assume_present=False,
    ensure_newline=False,
):
    """
    Ensure lines in files using grep to locate and sed to replace.

    + path: target remote file to edit
    + line: string or regex matching the target line
    + present: whether the line should be in the file
    + replace: text to replace entire matching lines when ``present=True``
    + flags: list of flags to pass to sed when replacing/deleting
    + backup: whether to backup the file (see below)
    + interpolate_variables: whether to interpolate variables in ``replace``
    + assume_present: whether to assume a matching line already exists in the file
    + escape_regex_characters: whether to escape regex characters from the matching line
    + ensure_newline: ensures that the appended line is on a new line

    Regex line matching:
        Unless line matches a line (starts with ^, ends $), pyinfra will wrap it such that
        it does, like: ``^.*LINE.*$``. This means we don't swap parts of lines out. To
        change bits of lines, see ``files.replace``.

    Regex line escaping:
        If matching special characters (eg a crontab line containing *), remember to escape
        it first using Python's ``re.escape``.

    Backup:
        If set to ``True``, any editing of the file will place an old copy with the ISO
        date (taken from the machine running ``pyinfra``) appended as the extension. If
        you pass a string value this will be used as the extension of the backed up file.

    Append:
        If ``line`` is not in the file but we want it (``present`` set to ``True``), then
        it will be append to the end of the file.

    Ensure new line:
        This will ensure that the ``line`` being appended is always on a seperate new
        line in case the file doesn't end with a newline character.


    **Examples:**

    ```python
    # prepare to do some maintenance
    maintenance_line = "SYSTEM IS DOWN FOR MAINTENANCE"
    files.line(
        name="Add the down-for-maintenance line in /etc/motd",
        path="/etc/motd",
        line=maintenance_line,
    )

    # Then, after the maintenance is done, remove the maintenance line
    files.line(
        name="Remove the down-for-maintenance line in /etc/motd",
        path="/etc/motd",
        line=maintenance_line,
        replace="",
        present=False,
    )

    # example where there is '*' in the line
    files.line(
        name="Ensure /netboot/nfs is in /etc/exports",
        path="/etc/exports",
        line=r"/netboot/nfs .*",
        replace="/netboot/nfs *(ro,sync,no_wdelay,insecure_locks,no_root_squash,"
        "insecure,no_subtree_check)",
    )

    files.line(
        name="Ensure myweb can run /usr/bin/python3 without password",
        path="/etc/sudoers",
        line=r"myweb .*",
        replace="myweb ALL=(ALL) NOPASSWD: /usr/bin/python3",
    )

    # example when there are double quotes (")
    line = 'QUOTAUSER=""'
    files.line(
        name="Example with double quotes (")",
        path="/etc/adduser.conf",
        line="^{}$".format(line),
        replace=line,
    )
    ```
    """
    operargs = {
        "path": repr(path),
        "line": repr(line),
        "present": repr(present),
        "replace": repr(replace),
        "flags": repr(flags),
        "backup": repr(backup),
        "interpolate_variables": repr(interpolate_variables),
        "escape_regex_characters": repr(escape_regex_characters),
        "assume_present": repr(assume_present),
        "ensure_newline": repr(ensure_newline),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import files", "files.line", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def replace(
    path,
    text=None,
    replace=None,
    flags=None,
    backup=False,
    interpolate_variables=False,
    match=None,
):
    """
    Replace contents of a file using ``sed``.

    + path: target remote file to edit
    + text: text/regex to match against
    + replace: text to replace with
    + flags: list of flags to pass to sed
    + backup: whether to backup the file (see below)
    + interpolate_variables: whether to interpolate variables in ``replace``

    Backup:
        If set to ``True``, any editing of the file will place an old copy with the ISO
        date (taken from the machine running ``pyinfra``) appended as the extension. If
        you pass a string value this will be used as the extension of the backed up file.

    **Example:**

    ```python
    files.replace(
        name="Change part of a line in a file",
        path="/etc/motd",
        text="verboten",
        replace="forbidden",
    )
    ```
    """
    operargs = {
        "path": repr(path),
        "text": repr(text),
        "replace": repr(replace),
        "flags": repr(flags),
        "backup": repr(backup),
        "interpolate_variables": repr(interpolate_variables),
        "match": repr(match),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import files", "files.replace", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def sync(
    src,
    dest,
    user=None,
    group=None,
    mode=None,
    dir_mode=None,
    delete=False,
    exclude=None,
    exclude_dir=None,
    add_deploy_dir=True,
):
    r"""
    Syncs a local directory with a remote one, with delete support. Note that delete will
    remove extra files on the remote side, but not extra directories.

    + src: local directory to sync
    + dest: remote directory to sync to
    + user: user to own the files and directories
    + group: group to own the files and directories
    + mode: permissions of the files
    + dir_mode: permissions of the directories
    + delete: delete remote files not present locally
    + exclude: string or list/tuple of strings to match & exclude files (eg *.pyc)
    + exclude_dir: string or list/tuple of strings to match & exclude directories (eg node_modules)
    + add_deploy_dir: interpret src as relative to deploy directory instead of current directory

    **Example:**

    ```python
    # Sync local files/tempdir to remote /tmp/tempdir
    files.sync(
        name="Sync a local directory with remote",
        src="files/tempdir",
        dest="/tmp/tempdir",
    )
    ```

    Note: ``exclude`` and ``exclude_dir`` use ``fnmatch`` behind the scenes to do the filtering.

    + ``exclude`` matches against the filename.
    + ``exclude_dir`` matches against the path of the directory, relative to ``src``.
      Since fnmatch does not treat path separators (``/`` or ``\``) as special characters,
      excluding all directories matching a given name, however deep under ``src`` they are,
      can be done for example with ``exclude_dir=["__pycache__", "*/__pycache__"]``
    """
    operargs = {
        "src": repr(src),
        "dest": repr(dest),
        "user": repr(user),
        "group": repr(group),
        "mode": repr(mode),
        "dir_mode": repr(dir_mode),
        "delete": repr(delete),
        "exclude": repr(exclude),
        "exclude_dir": repr(exclude_dir),
        "add_deploy_dir": repr(add_deploy_dir),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import files", "files.sync", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def show_rsync_warning():
    operargs = {}

    result = _run_pyinfra(
        "from pyinfra.operations import files", "files.show_rsync_warning", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def rsync(src, dest, flags=["-ax", "--delete"]):
    """
    Use ``rsync`` to sync a local directory to the remote system. This operation will actually call
    the ``rsync`` binary on your system.

    .. important::
        The ``files.rsync`` operation is in alpha, and only supported using SSH
        or ``@local`` connectors. When using the SSH connector, rsync will automatically use the
        StrictHostKeyChecking setting, config and known_hosts file (when specified).

    .. caution::
        When using SSH, the ``files.rsync`` operation only supports the ``sudo`` and ``sudo_user``
        global arguments.
    """
    operargs = {
        "src": repr(src),
        "dest": repr(dest),
        "flags": repr(flags),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import files", "files.rsync", operargs
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
        "from pyinfra.operations import files", "files._create_remote_dir", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def get(src, dest, add_deploy_dir=True, create_local_dir=False, force=False):
    """
    Download a file from the remote system.

    + src: the remote filename to download
    + dest: the local filename to download the file to
    + add_deploy_dir: dest is relative to the deploy directory
    + create_local_dir: create the local directory if it doesn't exist
    + force: always download the file, even if the local copy matches

    Note:
        This operation is not suitable for large files as it may involve copying
        the remote file before downloading it.

    **Example:**

    ```python
    files.get(
        name="Download a file from a remote",
        src="/etc/centos-release",
        dest="/tmp/whocares",
    )
    ```
    """
    operargs = {
        "src": repr(src),
        "dest": repr(dest),
        "add_deploy_dir": repr(add_deploy_dir),
        "create_local_dir": repr(create_local_dir),
        "force": repr(force),
    }

    result = _run_pyinfra("from pyinfra.operations import files", "files.get", operargs)

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
    """
    Upload a local file, or file-like object, to the remote system.

    + src: filename or IO-like object to upload
    + dest: remote filename to upload to
    + user: user to own the files
    + group: group to own the files
    + mode: permissions of the files, use ``True`` to copy the local file
    + add_deploy_dir: src is relative to the deploy directory
    + create_remote_dir: create the remote directory if it doesn't exist
    + force: always upload the file, even if the remote copy matches
    + assume_exists: whether to assume the local file exists

    ``dest``:
        If this is a directory that already exists on the remote side, the local
        file will be uploaded to that directory with the same filename.

    ``mode``:
        When set to ``True`` the permissions of the local file are applied to the
        remote file after the upload is complete.

    ``create_remote_dir``:
        If the remote directory does not exist it will be created using the same
        user & group as passed to ``files.put``. The mode will *not* be copied over,
        if this is required call ``files.directory`` separately.

    Note:
        This operation is not suitable for large files as it may involve copying
        the file before uploading it.

    **Examples:**

    ```python
    files.put(
        name="Update the message of the day file",
        src="files/motd",
        dest="/etc/motd",
        mode="644",
    )

    files.put(
        name="Upload a StringIO object",
        src=StringIO("file contents"),
        dest="/etc/motd",
    )
    ```
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

    result = _run_pyinfra("from pyinfra.operations import files", "files.put", operargs)

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def template(
    src, dest, user=None, group=None, mode=None, create_remote_dir=True, **data
):
    """
    Generate a template using jinja2 and write it to the remote system.

    + src: template filename or IO-like object
    + dest: remote filename
    + user: user to own the files
    + group: group to own the files
    + mode: permissions of the files
    + create_remote_dir: create the remote directory if it doesn't exist

    ``create_remote_dir``:
        If the remote directory does not exist it will be created using the same
        user & group as passed to ``files.put``. The mode will *not* be copied over,
        if this is required call ``files.directory`` separately.

    Notes:
       Common convention is to store templates in a "templates" directory and
       have a filename suffix with '.j2' (for jinja2).

       For information on the template syntax, see
       `the jinja2 docs <https://jinja.palletsprojects.com>`_.

    **Examples:**

    ```python
    files.template(
        name="Create a templated file",
        src="templates/somefile.conf.j2",
        dest="/etc/somefile.conf",
    )

    files.template(
        name="Create service file",
        src="templates/myweb.service.j2",
        dest="/etc/systemd/system/myweb.service",
        mode="755",
        user="root",
        group="root",
    )

    # Example showing how to pass python variable to template file. You can also
    # use dicts and lists. The .j2 file can use `{{ foo_variable }}` to be interpolated.
    foo_variable = 'This is some foo variable contents'
    foo_dict = {
        "str1": "This is string 1",
        "str2": "This is string 2"
    }
    foo_list = [
        "entry 1",
        "entry 2"
    ]

    template = StringIO('''
    name: "{{ foo_variable }}"
    dict_contents:
        str1: "{{ foo_dict.str1 }}"
        str2: "{{ foo_dict.str2 }}"
    list_contents:
    {% for entry in foo_list %}
        - "{{ entry }}"
    {% endfor %}
    ''')

    files.template(
        name="Create a templated file",
        src=template,
        dest="/tmp/foo.yml",
        foo_variable=foo_variable,
        foo_dict=foo_dict,
        foo_list=foo_list
    )
    ```
    """
    operargs = {
        "src": repr(src),
        "dest": repr(dest),
        "user": repr(user),
        "group": repr(group),
        "mode": repr(mode),
        "create_remote_dir": repr(create_remote_dir),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import files", "files.template", operargs
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
        "from pyinfra.operations import files", "files._validate_path", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def _raise_or_remove_invalid_path(fs_type, path, force, force_backup, force_backup_dir):
    operargs = {
        "fs_type": repr(fs_type),
        "path": repr(path),
        "force": repr(force),
        "force_backup": repr(force_backup),
        "force_backup_dir": repr(force_backup_dir),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import files",
        "files._raise_or_remove_invalid_path",
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
    create_remote_dir=True,
    force=False,
    force_backup=True,
    force_backup_dir=None,
):
    """
    Add/remove/update links.

    + path: the name of the link
    + target: the file/directory the link points to
    + present: whether the link should exist
    + assume_present: whether to assume the link exists
    + user: user to own the link
    + group: group to own the link
    + symbolic: whether to make a symbolic link (vs hard link)
    + create_remote_dir: create the remote directory if it doesn't exist
    + force: if the target exists and is not a file, move or remove it and continue
    + force_backup: set to ``False`` to remove any existing non-file when ``force=True``
    + force_backup_dir: directory to move any backup to when ``force=True``

    ``create_remote_dir``:
        If the remote directory does not exist it will be created using the same
        user & group as passed to ``files.put``. The mode will *not* be copied over,
        if this is required call ``files.directory`` separately.

    Source changes:
        If the link exists and points to a different target, pyinfra will remove it and
        recreate a new one pointing to then new target.

    **Examples:**

    ```python
    files.link(
        name="Create link /etc/issue2 that points to /etc/issue",
        path="/etc/issue2",
        target="/etc/issue",
    )


    # Complex example demonstrating the assume_present option
    from pyinfra.operations import apt, files

    install_nginx = apt.packages(
        name="Install nginx",
        packages=["nginx"],
    )

    files.link(
        name="Remove default nginx site",
        path="/etc/nginx/sites-enabled/default",
        present=False,
        assume_present=install_nginx.changed,
    )
    ```
    """
    operargs = {
        "path": repr(path),
        "target": repr(target),
        "present": repr(present),
        "assume_present": repr(assume_present),
        "user": repr(user),
        "group": repr(group),
        "symbolic": repr(symbolic),
        "create_remote_dir": repr(create_remote_dir),
        "force": repr(force),
        "force_backup": repr(force_backup),
        "force_backup_dir": repr(force_backup_dir),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import files", "files.link", operargs
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
    force=False,
    force_backup=True,
    force_backup_dir=None,
):
    """
    Add/remove/update files.

    + path: name/path of the remote file
    + present: whether the file should exist
    + assume_present: whether to assume the file exists
    + user: user to own the files
    + group: group to own the files
    + mode: permissions of the files as an integer, eg: 755
    + touch: whether to touch the file
    + create_remote_dir: create the remote directory if it doesn't exist
    + force: if the target exists and is not a file, move or remove it and continue
    + force_backup: set to ``False`` to remove any existing non-file when ``force=True``
    + force_backup_dir: directory to move any backup to when ``force=True``

    ``create_remote_dir``:
        If the remote directory does not exist it will be created using the same
        user & group as passed to ``files.put``. The mode will *not* be copied over,
        if this is required call ``files.directory`` separately.

    **Example:**

    ```python
    # Note: The directory /tmp/secret will get created with the default umask.
    files.file(
        name="Create /tmp/secret/file",
        path="/tmp/secret/file",
        mode="600",
        user="root",
        group="root",
        touch=True,
        create_remote_dir=True,
    )
    ```
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
        "force": repr(force),
        "force_backup": repr(force_backup),
        "force_backup_dir": repr(force_backup_dir),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import files", "files.file", operargs
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
    force=False,
    force_backup=True,
    force_backup_dir=None,
    _no_check_owner_mode=False,
    _no_fail_on_link=False,
):
    """
    Add/remove/update directories.

    + path: path of the remote folder
    + present: whether the folder should exist
    + assume_present: whether to assume the directory exists
    + user: user to own the folder
    + group: group to own the folder
    + mode: permissions of the folder
    + recursive: recursively apply user/group/mode
    + force: if the target exists and is not a file, move or remove it and continue
    + force_backup: set to ``False`` to remove any existing non-file when ``force=True``
    + force_backup_dir: directory to move any backup to when ``force=True``

    **Examples:**

    ```python
    files.directory(
        name="Ensure the /tmp/dir_that_we_want_removed is removed",
        path="/tmp/dir_that_we_want_removed",
        present=False,
    )

    files.directory(
        name="Ensure /web exists",
        path="/web",
        user="myweb",
        group="myweb",
    )

    # Multiple directories
    for dir in ["/netboot/tftp", "/netboot/nfs"]:
        files.directory(
            name="Ensure the directory `{}` exists".format(dir),
            path=dir,
        )
    ```
    """
    operargs = {
        "path": repr(path),
        "present": repr(present),
        "assume_present": repr(assume_present),
        "user": repr(user),
        "group": repr(group),
        "mode": repr(mode),
        "recursive": repr(recursive),
        "force": repr(force),
        "force_backup": repr(force_backup),
        "force_backup_dir": repr(force_backup_dir),
        "_no_check_owner_mode": repr(_no_check_owner_mode),
        "_no_fail_on_link": repr(_no_fail_on_link),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import files", "files.directory", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def flags(path, flags=None, present=True):
    """
    Set/clear file flags.

    + path: path of the remote folder
    + flags: a list of the file flags to be set or cleared
    + present: whether the flags should be set or cleared

    **Examples:**

    ```python
    files.flags(
        name="Ensure ~/Library is visible in the GUI",
        path="~/Library",
        flags="hidden",
        present=False
    )

    files.directory(
        name="Ensure no one can change these files",
        path="/something/very/important",
        flags=["uchg", "schg"],
        present=True,
        _sudo=True
    )
    ```
    """
    operargs = {
        "path": repr(path),
        "flags": repr(flags),
        "present": repr(present),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import files", "files.flags", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def block(
    path,
    content=None,
    present=True,
    line=None,
    backup=False,
    escape_regex_characters=False,
    before=False,
    after=False,
    marker=None,
    begin=None,
    end=None,
):
    r"""
    Ensure content, surrounded by the appropriate markers, is present (or not) in the file.

    + path: target remote file
    + content: what should be present in the file (between markers).
    + present: whether the content should be present in the file
    + before: should the content be added before ``line`` if it doesn't exist
    + after: should the content be added after ``line`` if it doesn't exist
    + line: regex before or after which the content should be added if it doesn't exist.
    + backup: whether to backup the file (see ``files.line``). Default False.
    + escape_regex_characters: whether to escape regex characters from the matching line
    + marker: the base string used to mark the text.  Default is ``# {mark} PYINFRA BLOCK``
    + begin: the value for ``{mark}`` in the marker before the content. Default is ``BEGIN``
    + end: the value for ``{mark}`` in the marker after the content. Default is ``END``

    Content appended if ``line`` not found in the file
        If ``content`` is not in the file but is required (``present=True``) and ``line`` is not
        found in the file, ``content`` (surrounded by markers) will be appended to the file.  The
        file is created if necessary.

    Content prepended or appended if ``line`` not specified
        If ``content`` is not in the file but is required and ``line`` was not provided the content
        will either be  prepended to the file (if both ``before`` and ``after``
        are ``True``) or appended to the file (if both are ``False``).

    Removal ignores ``content`` and ``line``

    **Examples:**

    ```python
    # add entry to /etc/host
    files.marked_block(
        name="add IP address for red server",
        path="/etc/hosts",
        content="10.0.0.1 mars-one",
        before=True,
        regex=".*localhost",
    )

    # have two entries in /etc/host
    files.marked_block(
        name="add IP address for red server",
        path="/etc/hosts",
        content="10.0.0.1 mars-one\n10.0.0.2 mars-two",
        before=True,
        regex=".*localhost",
    )

    # remove marked entry from /etc/hosts
    files.marked_block(
        name="remove all 10.* addresses from /etc/hosts",
        path="/etc/hosts",
        present=False
    )

    # add out of date warning to web page
    files.marked_block(
        name="add out of date warning to web page",
        path="/var/www/html/something.html",
        content= "<p>Warning: this page is out of date.</p>",
        regex=".*<body>.*",
        after=True
        marker="<!-- {mark} PYINFRA BLOCK -->",
    )
    ```
    """
    operargs = {
        "path": repr(path),
        "content": repr(content),
        "present": repr(present),
        "line": repr(line),
        "backup": repr(backup),
        "escape_regex_characters": repr(escape_regex_characters),
        "before": repr(before),
        "after": repr(after),
        "marker": repr(marker),
        "begin": repr(begin),
        "end": repr(end),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import files", "files.block", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)
