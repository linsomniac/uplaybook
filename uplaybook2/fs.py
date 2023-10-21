#!/usr/bin/env python3

"""
Filesystem related tasks.
"""

from .internals import (
    Return,
    Failure,
    TemplateStr,
    template_args,
    calling_context,
    up_context,
    CallDepth,
)
from . import internals
from typing import Union, Optional, Callable
from types import SimpleNamespace
import symbolicmode
import os
import stat
import random
import string
import hashlib
import pwd
import grp
import shutil


def _mode_from_arg(
    mode: Optional[Union[str, int]] = None,
    initial_mode: Optional[int] = None,
    is_directory: Optional[bool] = None,
) -> Optional[int]:
    """
    Helper function to convert a task `mode` argument into an int, if necessary.

    If `mode` is a string, it is converted using the symbolicmode module.
    If `mode` is None, it is kept as None (meaning no mode change to be done).
    If `mode` is an int, it is kept.

    Arguments:
        - **mode**: Mode to convert, if it is a string.
        - **initial_mode**: The existing mode of the file (used for +/-/X).
        - **is_directory**: If the path to set the mode on is a directory (used for X).
    """
    if type(mode) is int or mode is None:
        return mode

    assert type(mode) is str

    mode_is_sym_str = type(mode) is str and not set(mode).issubset("01234567")
    if mode_is_sym_str:
        extra_args = {}
        if is_directory is not None:
            extra_args["is_directory"] = is_directory
        if initial_mode is not None:
            extra_args["initial_mode"] = initial_mode

        return symbolicmode.symbolic_to_numeric_permissions(mode, **extra_args)

    return int(mode, 8)


@calling_context
@template_args
def chmod(
    path: str,
    mode: Optional[Union[str, int]] = None,
    is_directory: Optional[bool] = None,
) -> Return:
    """
    Change permissions of path.

    Arguments:

    - **path**: Path to change (templateable).
    - **mode**: Permissions of path (optional, templatable string or int).
    - **is_directory**: Treat path as a directory, impacts "X".  If not specified
            `path` is examined to determine if it is a directory.
            (optional, bool).

    Examples:

        fs.chmod(path="/tmp/foo", mode="a=rX,u+w")
        fs.chmod(path="/tmp/foo", mode=0o755)

    #taskdoc
    """
    if mode is None:
        return Return(
            changed=False, secret_args={"decrypt_password", "encrypt_password"}
        )

    path_stats = os.stat(path)
    current_mode = stat.S_IMODE(path_stats.st_mode)
    extra_args = {}
    if is_directory is not None:
        extra_args["is_directory"] = is_directory
    mode = _mode_from_arg(mode, initial_mode=current_mode, **extra_args)
    if current_mode != mode:
        assert type(mode) is int
        os.chmod(path, mode)
        return Return(
            changed=True,
            secret_args={"decrypt_password", "encrypt_password"},
            extra_message=f"Changed permissions: {current_mode:o} -> {mode:o}",
        )

    return Return(changed=False, secret_args={"decrypt_password", "encrypt_password"})


@calling_context
@template_args
def chown(
    path: str,
    user: Optional[TemplateStr] = None,
    group: Optional[TemplateStr] = None,
) -> Return:
    """
    Change ownership/group of path.

    Arguments:

    - **path**: Path to change (templateable).
    - **user**: User to set on `path`. (optional, templatable).
    - **group**: Group to set on `path`. (optional, templatable).

    Examples:

        fs.chown(path="/tmp", owner="root")
        fs.chown(path="/tmp", group="wheel")
        fs.chown(path="/tmp", owner="nobody", group="nobody")

    #taskdoc
    """
    changed = False
    extra_messages = []

    before_stats = os.stat(path)
    shutil.chown(path, user=user, group=group)
    after_stats = os.stat(path)

    extra_messages = []
    if before_stats.st_uid != after_stats.st_uid:
        extra_messages.append(f"User changed from {before_stats.st_uid}")
    if before_stats.st_gid != after_stats.st_gid:
        extra_messages.append(f"Group changed from {before_stats.st_gid}")
    changed = len(extra_messages) != 0

    return Return(
        changed=changed,
        extra_message=", ".join(extra_messages) if extra_messages else None,
    )


@calling_context
@template_args
def cd(path: TemplateStr) -> Return:
    """
    Change working directory to `path`.

    Sets "extra.old_dir" on the return object to the directory before the `cd`
    is done.  Can also be used as a context manager and when the context is
    exited you are returned to the previous directory.

    Arguments:

    - **path**: Directory to change into (templateable).

    Examples:

        fs.cd(path="/tmp")

        #  As context manager:
        with fs.cd(path="/tmp"):
            #  creates /tmp/tempfile
            fs.mkfile("tempfile")
        #  now are back in previous directory

    #taskdoc
    """
    old_dir = os.getcwd()
    os.chdir(path)

    return Return(
        changed=False,
        extra=SimpleNamespace(old_dir=old_dir),
        context=lambda: cd(old_dir),
    )


@calling_context
@template_args
def mkfile(
    path: TemplateStr,
    mode: Optional[Union[TemplateStr, int]] = None,
) -> Return:
    """
    Create an empty file if it does not already exist.

    Arguments:

    - **path**: Name of file to create (templateable).
    - **mode**: Permissions of file (optional, templatable string or int).
       Atomically sets mode on creation.

    Examples:

        fs.mkfile(path="/tmp/foo")
        fs.mkfile(path="/tmp/bar", mode="a=rX,u+w")
        fs.mkfile(path="/tmp/baz", mode=0o755)

    #taskdoc
    """
    new_mode = mode
    if not os.path.exists(path):
        new_mode = _mode_from_arg(new_mode)
        mode_arg = {} if new_mode is None else {"mode": new_mode}
        fd = os.open(path, os.O_CREAT, **mode_arg)
        os.close(fd)

        return Return(changed=True)

    if mode is not None:
        with CallDepth():
            chmod(path, new_mode)

    return Return(changed=False)


@calling_context
@template_args
def mkdir(
    path: TemplateStr,
    mode: Optional[Union[TemplateStr, int]] = None,
    parents: Optional[bool] = True,
) -> Return:
    """
    Create a directory.  Defaults to creating necessary parent directories.

    Arguments:

    - **path**: Name of file to create (templateable).
    - **mode**: Permissions of directory (optional, templatable string or int).
                Sets mode on creation.
    - **parents**: Make parent directories if needed.  (optional, default=True)

    Examples:

        fs.mkdir(path="/tmp/foo")
        fs.mkdir(path="/tmp/bar", mode="a=rX,u+w")
        fs.mkdir(path="/tmp/baz/qux", mode=0o755, parents=True)

    #taskdoc
    """
    new_mode = mode
    if not os.path.exists(path):
        new_mode = _mode_from_arg(new_mode, is_directory=True)
        mode_arg = {} if new_mode is None else {"mode": new_mode}
        if parents:
            os.makedirs(path, **mode_arg)
        else:
            os.mkdir(path, **mode_arg)

        return Return(changed=True)

    with CallDepth():
        chmod(path, new_mode, is_directory=True)

    return Return(changed=False)


def _random_ext(i: int = 8) -> str:
    "Return a random string of length 'i'"
    return "".join(
        random.choices(
            string.ascii_lowercase + string.ascii_uppercase + string.digits, k=i
        )
    )


@calling_context
@template_args
def rm(
    path: TemplateStr,
    recursive: bool = False,
) -> Return:
    """
    Remove a file or recursively remove a directory.

    Arguments:

    - **path**: Name of file/directory to remove. (templateable).
    - **recursive**: If True, recursively remove directory and all contents of `path`.
           Otherwise only remove if `path` is a file.  (default: False)

    Examples:

        fs.rm(path="/tmp/foo")
        fs.rm(path="/tmp/foo-dir", recursive=True)

    #taskdoc
    """

    if not os.path.exists(path):
        return Return(changed=False)

    if not recursive:
        try:
            os.remove(path)
        except OSError as e:
            raise Failure(
                f"Path {path} is a directory, will not remove without `recursive` option"
            )
    else:
        shutil.rmtree(path)

    return Return(changed=True)


@calling_context
@template_args
def copy(
    path: TemplateStr,
    src: Optional[TemplateStr] = None,
    mode: Optional[Union[TemplateStr, int]] = None,
    encrypt_password: Optional[TemplateStr] = None,
    decrypt_password: Optional[TemplateStr] = None,
    template: bool = True,
) -> Return:
    """
    Copy the `src` file to `path`, optionally templating the contents in `src`.

    Arguments:

    - **path**: Name of destination file. (templateable).
    - **src**: Name of template to use as source (optional, templateable).
            Defaults to the basename of `path` + ".j2".
    - **mode**: Permissions of directory (optional, templatable string or int).
            Sets mode on creation.
    - **template**: If True, apply Jinja2 templating to the contents of `src`,
           otherwise copy verbatim.  (default: True)

    Examples:

        fs.copy(path="/tmp/foo")
        fs.copy(src="bar-{{ fqdn }}.j2", path="/tmp/bar", template=False)

    #taskdoc
    """

    if src is None:
        new_src = os.path.basename(path) + ".j2"
    else:
        new_src = src

    if encrypt_password or decrypt_password:
        raise NotImplementedError("Crypto not implemented yet")

    new_mode = mode
    old_mode = None

    hash_before = None
    if os.path.exists(path):
        old_mode = stat.S_IMODE(os.stat(path).st_mode)
        with open(path, "rb") as fp_in:
            sha = hashlib.sha256()
            sha.update(fp_in.read())
            hash_before = sha.hexdigest()

    with open(internals.find_file(new_src), "r") as fp_in:
        data = fp_in.read()
        if template:
            data = up_context.jinja_env.from_string(data).render(up_context.get_env())

    sha = hashlib.sha256()
    sha.update(data.encode("latin-1"))
    hash_after = sha.hexdigest()

    if new_mode is not None:
        new_mode = _mode_from_arg(new_mode, initial_mode=old_mode)

    if hash_before == hash_after and (new_mode is None or new_mode == old_mode):
        return Return(
            changed=False, secret_args={"decrypt_password", "encrypt_password"}
        )
    if hash_before == hash_after and (new_mode is not None or new_mode != old_mode):
        return Return(
            changed=True,
            secret_args={"decrypt_password", "encrypt_password"},
            extra_message="Permissions",
        )

    pathTmp = path + ".tmp." + _random_ext()
    mode_arg = {} if new_mode is None else {"mode": new_mode}
    fd = os.open(pathTmp, os.O_WRONLY | os.O_CREAT, **mode_arg)
    with os.fdopen(fd, "w") as fp_out:
        fp_out.write(data)
    os.rename(pathTmp, path)

    return Return(changed=True, secret_args={"decrypt_password", "encrypt_password"})


@calling_context
@template_args
def builder(
    path: TemplateStr,
    src: Optional[TemplateStr] = None,
    mode: Optional[Union[TemplateStr, int]] = None,
    owner: Optional[TemplateStr] = None,
    group: Optional[TemplateStr] = None,
    action: Union[TemplateStr, str] = "template",
    notify: Optional[Callable] = None,
) -> Return:
    """
    All-in-one filesystem builder.

    This is targeted for use with Items() loops, for easily populating or
    modifying many filesystem objects in compact declarations.

    Arguments:

    - **path**: Name of destination filesystem object. (templateable).
    - **src**: Name of template to use as source (optional, templateable).
            Defaults to the basename of `path` + ".j2".
    - **mode**: Permissions of file (optional, templatable string or int).
    - **owner**: Ownership to set on `path`. (optional, templatable).
    - **group**: Group to set on `path`. (optional, templatable).
    - **action**: Type of `path` to build, can be: "directory", "template", "exists", "copy".
            (optional, templatable, default="template")
    - **notify**:  Handler to notify of changes.
            (optional, Callable)

    Examples:

        fs.builder("/tmp/foo")
        fs.builder("/tmp/bar", action="directory")
        for _ in Items(
                Item(path="/tmp/{{ modname }}", action="directory"),
                Item(path="/tmp/{{ modname }}/__init__.py"),
                defaults=Item(mode="a=rX,u+w")
                ):
            builder()

    #taskdoc
    """

    with CallDepth():
        if action == "template":
            r = copy(src=src, path=path)
        elif action == "copy":
            r = copy(src=src, path=path, template=False)
        elif action == "directory":
            r = mkdir(path=path, mode=mode)
        elif action == "exists":
            r = mkfile(path=path, mode=mode)
        else:
            raise ValueError(f"Unknown action: {action}")

        if mode is not None:
            chmod(path, mode)
        if owner is not None or group is not None:
            chown(path, owner, group)

    if notify is not None:
        r = r.notify(notify)

    return Return(changed=r.changed)
