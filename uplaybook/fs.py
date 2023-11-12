#!/usr/bin/env python3

"""
Filesystem Related Tasks

This module contains uPlaybook tasks that are related to file system operations.

"""

from .internals import (
    Return,
    Failure,
    TemplateStr,
    RawStr,
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
import stat as stat_module
import random
import string
import hashlib
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

    Args:
        mode: Mode to convert, if it is a string.
        initial_mode: The existing mode of the file (used for +/-/X).
        is_directory: If the path to set the mode on is a directory (used for X).
    """
    if isinstance(mode, int) or mode is None:
        return mode

    assert isinstance(mode, str)

    mode_is_sym_str = isinstance(mode, str) and not set(mode).issubset("01234567")
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
    dst: str,
    mode: Optional[Union[str, int]] = None,
    is_directory: Optional[bool] = None,
) -> Return:
    """
    Change permissions of `dst`.

    Args:
        dst: Path to change (templateable).
        mode: Permissions of `dst` (optional, templatable string or int).
        is_directory: Treat `dst` as a directory, impacts "X".  If not specified
            `dst` is examined to determine if it is a directory.
            (optional, bool).

    Examples:

    ```python
    fs.chmod(dst="/tmp/foo", mode="a=rX,u+w")
    fs.chmod(dst="/tmp/foo", mode=0o755)
    ```

    <!-- #taskdoc -->
    """
    if mode is None:
        return Return(
            changed=False, secret_args={"decrypt_password", "encrypt_password"}
        )

    dst_stats = os.stat(dst)
    current_mode = stat_module.S_IMODE(dst_stats.st_mode)
    extra_args = {}
    if is_directory is not None:
        extra_args["is_directory"] = is_directory
    mode = _mode_from_arg(mode, initial_mode=current_mode, **extra_args)
    if current_mode != mode:
        assert isinstance(mode, int)
        os.chmod(dst, mode)
        return Return(
            changed=True,
            secret_args={"decrypt_password", "encrypt_password"},
            extra_message=f"Changed permissions: {current_mode:o} -> {mode:o}",
        )

    return Return(changed=False, secret_args={"decrypt_password", "encrypt_password"})


@calling_context
@template_args
def chown(
    dst: str,
    user: Optional[TemplateStr] = None,
    group: Optional[TemplateStr] = None,
) -> Return:
    """
    Change ownership/group of `dst`.

    Args:
        dst: Path to change (templateable).
        user: User to set on `dst`. (optional, templatable).
        group: Group to set on `dst`. (optional, templatable).

    Examples:

    ```python
    fs.chown(dst="/tmp", owner="root")
    fs.chown(dst="/tmp", group="wheel")
    fs.chown(dst="/tmp", owner="nobody", group="nobody")
    ```

    <!-- #taskdoc -->
    """
    changed = False
    extra_messages = []

    before_stats = os.stat(dst)
    shutil.chown(dst, user=user, group=group)
    after_stats = os.stat(dst)

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
def cd(dst: TemplateStr) -> Return:
    """
    Change working directory to `dst`.

    Sets "extra.old_dir" on the return object to the directory before the `cd`
    is done.  Can also be used as a context manager and when the context is
    exited you are returned to the previous directory.

    Args:
        dst: Directory to change into (templateable).

    Examples:

    ```python
    fs.cd(dst="/tmp")

    #  As context manager:
    with fs.cd(dst="/tmp"):
        #  creates /tmp/tempfile
        fs.mkfile("tempfile")
    #  now are back in previous directory
    ```

    <!-- #taskdoc -->
    """
    old_dir = os.getcwd()
    os.chdir(dst)

    return Return(
        changed=False,
        extra=SimpleNamespace(old_dir=old_dir),
        context_manager=lambda: cd(old_dir),
    )


@calling_context
@template_args
def mkfile(
    dst: TemplateStr,
    mode: Optional[Union[TemplateStr, int]] = None,
) -> Return:
    """
    Create an empty file if it does not already exist.

    Args:
        dst: Name of file to create (templateable).
        mode: Permissions of file (optional, templatable string or int).
       Atomically sets mode on creation.

    Examples:

    ```python
    fs.mkfile(dst="/tmp/foo")
    fs.mkfile(dst="/tmp/bar", mode="a=rX,u+w")
    fs.mkfile(dst="/tmp/baz", mode=0o755)
    ```

    <!-- #taskdoc -->
    """
    new_mode = mode
    if not os.path.exists(dst):
        new_mode = _mode_from_arg(new_mode)
        mode_arg = {} if new_mode is None else {"mode": new_mode}
        fd = os.open(dst, os.O_CREAT, **mode_arg)
        os.close(fd)

        return Return(changed=True)

    if mode is not None:
        with CallDepth():
            chmod(dst, new_mode)

    return Return(changed=False)


@calling_context
@template_args
def mkdir(
    dst: TemplateStr,
    mode: Optional[Union[TemplateStr, int]] = None,
    parents: Optional[bool] = True,
) -> Return:
    """
    Create a directory.  Defaults to creating necessary parent directories.

    Args:
        dst: Name of file to create (templateable).
        mode: Permissions of directory (optional, templatable string or int).
                Sets mode on creation.
        parents: Make parent directories if needed.  (optional, default=True)

    Examples:

    ```python

    fs.mkdir(dst="/tmp/foo")
    fs.mkdir(dst="/tmp/bar", mode="a=rX,u+w")
    fs.mkdir(dst="/tmp/baz/qux", mode=0o755, parents=True)
    ```

    <!-- #taskdoc -->
    """
    new_mode = mode
    if not os.path.exists(dst):
        new_mode = _mode_from_arg(new_mode, is_directory=True)
        mode_arg = {} if new_mode is None else {"mode": new_mode}
        if parents:
            os.makedirs(dst, **mode_arg)
        else:
            os.mkdir(dst, **mode_arg)

        return Return(changed=True)

    with CallDepth():
        chmod(dst, new_mode, is_directory=True)

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
    dst: TemplateStr,
    recursive: bool = False,
) -> Return:
    """
    Remove a file or recursively remove a directory.

    Args:
        dst: Name of file/directory to remove. (templateable).
        recursive: If True, recursively remove directory and all contents of `dst`.
            Otherwise only remove if `dst` is a file.  (default: False)

    Examples:

    ```python
    fs.rm(dst="/tmp/foo")
    fs.rm(dst="/tmp/foo-dir", recursive=True)
    ```

    <!-- #taskdoc -->
    """

    if not os.path.exists(dst):
        return Return(changed=False)

    if not recursive:
        try:
            os.remove(dst)
        except OSError:
            return Return(
                changed=False,
                failure=True,
                raise_exc=Failure(
                    f"Path {dst} is a directory, will not remove without `recursive` option"
                ),
            )
    else:
        shutil.rmtree(dst)

    return Return(changed=True)


@calling_context
@template_args
def stat(
    dst: TemplateStr,
    follow_symlinks: bool = True,
) -> Return:
    """
    Get information about `dst`.

    Args:
        dst: Path to stat.  (templateable).
        follow_symlinks: If True (default), the result will be on the destination of
            a symlink, if False the result will be about the symlink itself.
            (bool, default: True)

    Extra Data:

        perms: The permissions of `dst` (st_mode & 0o777).
        st_mode: Full mode of `dst` (permissions, object type).  You probably want the
            "perms" field if you just want the permissions of `dst`.
        st_ino: Inode number.
        st_dev: ID of the device containing `dst`.
        st_nlink: Number of hard links.
        st_uid: User ID of owner.
        st_gid: Group ID of owner.
        st_size: Total size in bytes.
        st_atime: The time of the last access of file data.
        st_mtime: The time of last modification of file data.
        st_ctime: The time of the last change of status/inode.
        S_ISBLK: Is `dst` a block special device file?
        S_ISCHR: Is `dst` a character special device file?
        S_ISDIR: Is `dst` a directory?
        S_ISDOOR: Is `dst` a door?
        S_ISFIFO: Is `dst` a named pipe?
        S_ISLNK: Is `dst` a symbolic link?
        S_ISPORT: Is `dst` an event port?
        S_ISREG: Is `dst` a regular file?
        S_ISSOCK: Is `dst` a socket?
        S_ISWHT: Is `dst` a whiteout?

    Examples:

    ```python
    stat = fs.stat(dst="/tmp/foo")
    print(f"UID: {{stat.extra.st_uid}}")
    fs.stat(dst="/tmp/foo", follow_symlinks=False)
    ```

    <!-- #taskdoc -->
    """

    s = os.stat(dst, follow_symlinks=follow_symlinks)

    ret = SimpleNamespace(
        perms=stat.s_IMODE(s.st_mode),
        st_mode=s.st_mode,
        st_ino=s.st_ino,
        st_dev=s.st_dev,
        st_nlink=s.st_nlink,
        st_uid=s.st_uid,
        st_gid=s.st_gid,
        st_size=s.st_size,
        st_atime=s.st_atime,
        st_mtime=s.st_mtime,
        st_ctime=s.st_ctime,
        S_ISBLK=stat_module.S_ISBLK(s.st_mode),
        S_ISCHR=stat_module.S_ISCHR(s.st_mode),
        S_ISDIR=stat_module.S_ISDIR(s.st_mode),
        S_ISDOOR=stat_module.S_ISDOOR(s.st_mode),
        S_ISFIFO=stat_module.S_ISFIFO(s.st_mode),
        S_ISLNK=stat_module.S_ISLNK(s.st_mode),
        S_ISPORT=stat_module.S_ISPORT(s.st_mode),
        S_ISREG=stat_module.S_ISREG(s.st_mode),
        S_ISSOCK=stat_module.S_ISSOCK(s.st_mode),
        S_ISWHT=stat_module.S_ISWHT(s.st_mode),
    )

    return Return(changed=False, extra=ret)


@calling_context
@template_args
def mv(
    dst: TemplateStr,
    src: TemplateStr,
) -> Return:
    """
    Rename `src` to `dst`.  If `src` does not exist but `dst` does,
    it is considered successful without change.  If neither exists,
    it is failed.

    Args:
        dst: New name. (templateable).
        src: Old name. (templateable).

    Examples:

    ```python
    fs.mv(dst="/tmp/foo", src="/tmp/bar")
    ```

    <!-- #taskdoc -->
    """

    if os.path.exists(src):
        shutil.move(src, dst)
        return Return(changed=True)

    if os.path.exists(dst):
        return Return(changed=False)

    return Return(
        changed=False,
        failure=True,
        raise_exc=Failure(f"No file to move: src={src} dst={dst}"),
    )


@calling_context
@template_args
def ln(
    dst: TemplateStr,
    src: TemplateStr,
    symbolic: bool = False,
) -> Return:
    """
    Create a link from `src` to `dst`.

    Args:
        dst: Name of destination of link. (templateable).
        src: Name of location of source to create link from. (templateable).
        symbolic: If True, makes a symbolic link. (bool, default: False)

    Examples:

    ```python
    fs.ln(dst="/tmp/foo", src="/tmp/bar")
    fs.ln(dst="/tmp/foo", src="/tmp/bar", symbolic=True)
    ```

    <!-- #taskdoc -->
    """

    if symbolic:
        if os.path.islink(dst) and os.readlink(dst) == src:
            return Return(changed=False)
        if os.path.exists(dst):
            os.remove(dst)
        os.symlink(src, dst)
    else:
        if os.path.exists(dst):
            src_stat = os.stat(src)
            dst_stat = os.stat(dst)

            if (
                src_stat.st_dev == dst_stat.st_dev
                and src_stat.st_ino == dst_stat.st_ino
            ):
                return Return(changed=False)

            os.remove(dst)

        os.link(src=src, dst=dst)

    return Return(changed=True)


@calling_context
@template_args
def cp(
    dst: TemplateStr,
    src: Optional[TemplateStr] = None,
    mode: Optional[Union[TemplateStr, int]] = None,
    encrypt_password: Optional[TemplateStr] = None,
    decrypt_password: Optional[TemplateStr] = None,
    template: bool = True,
    template_filenames: bool = True,
    recursive: bool = True,
) -> Return:
    """
    Copy the `src` file to `dst`, optionally templating the contents in `src`.

    Args:
        dst: Name of destination file. (templateable).
        src: Name of template to use as source (optional, templateable).
            Defaults to the basename of `dst` + ".j2".
        mode: Permissions of directory (optional, templatable string or int).
            Sets mode on creation.
        template: If True, apply Jinja2 templating to the contents of `src`,
            otherwise copy verbatim.  (default: True)
        template_filenames: If True, filenames found during recursive copy are
            jinja2 template expanded. (default: True)
        recursive: If True and `src` is a directory, recursively copy it and
            everything below it to the `dst`.  If `dst` ends in a "/",
            the last component of `src` is created under `dst`, otherwise
            the contents of `src` are written into `dst`. (default: True)

    Examples:

    ```python
    fs.cp(dst="/tmp/foo")
    fs.cp(src="bar-{{ fqdn }}.j2", dst="/tmp/bar", template=False)
    ```

    <!-- #taskdoc -->
    """

    def _copy_file(
        src: str,
        dst: str,
        mode: Optional[Union[str, int]] = None,
        decrypt_password: Union[str, None] = None,
        encrypt_password: Union[str, None] = None,
    ) -> Optional[str]:
        """
        The workhorse of the copy function, copy one file.

        Returns:
            A string describing the change made, or None if no change made.
        """
        new_mode = mode
        old_mode = None

        hash_before = None
        if os.path.exists(dst):
            old_mode = stat_module.S_IMODE(os.stat(dst).st_mode)
            with open(dst, "rb") as fp_in:
                sha = hashlib.sha256()
                sha.update(fp_in.read())
                hash_before = sha.hexdigest()

        with open(src, "r") as fp_in:
            data = fp_in.read()
            if template:
                data = up_context.jinja_env.from_string(data).render(
                    up_context.get_env()
                )

        sha = hashlib.sha256()
        sha.update(data.encode("latin-1"))
        hash_after = sha.hexdigest()

        if new_mode is not None:
            new_mode = _mode_from_arg(new_mode, initial_mode=old_mode)

        if hash_before == hash_after and (new_mode is None or new_mode == old_mode):
            return None
        if hash_before == hash_after and (new_mode is not None or new_mode != old_mode):
            return "Permissions"

        dstTmp = dst + ".tmp." + _random_ext()
        mode_arg = {} if new_mode is None else {"mode": new_mode}
        fd = os.open(dstTmp, os.O_WRONLY | os.O_CREAT, **mode_arg)
        with os.fdopen(fd, "w") as fp_out:
            fp_out.write(data)
        os.rename(dstTmp, dst)

        return "Contents"

    new_src = src if src is not None else os.path.basename(dst) + ".j2"
    new_src = internals.find_file(new_src)

    if encrypt_password or decrypt_password:
        raise NotImplementedError("Crypto not implemented yet")

    changes_made = set()
    src_is_dir = stat_module.S_ISDIR(os.stat(new_src).st_mode)
    if recursive and src_is_dir:
        with CallDepth():
            for dirpath, dirnames, filenames in os.walk(new_src):
                dst_dir = os.path.join(dst, os.path.relpath(dirpath, new_src))

                r = mkdir(dst=dst_dir, mode=mode)
                if r.changed:
                    changes_made.add("Subdir")

                for filename in filenames:
                    src_file = RawStr(os.path.join(dirpath, filename))
                    dst_file = os.path.join(dst_dir, filename)
                    r = cp(src=src_file, dst=dst_file)
                    if r.changed:
                        changes_made.add("Subfile")
    else:
        change = _copy_file(new_src, dst, mode)
        if change:
            changes_made.add(change)

    if not changes_made:
        return Return(
            changed=False, secret_args={"decrypt_password", "encrypt_password"}
        )
    return Return(
        changed=True,
        extra_message=", ".join(changes_made),
        secret_args={"decrypt_password", "encrypt_password"},
    )


@calling_context
@template_args
def builder(
    dst: TemplateStr,
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

    Args:
        dst: Name of destination filesystem object. (templateable).
        src: Name of template to use as source (optional, templateable).
            Defaults to the basename of `dst` + ".j2".
        mode: Permissions of file (optional, templatable string or int).
        owner: Ownership to set on `dst`. (optional, templatable).
        group: Group to set on `dst`. (optional, templatable).
        action: Type of `dst` to build, can be: "directory", "template", "exists",
            "copy", "absent", "link", "symlink". (optional, templatable, default="template")
        notify:  Handler to notify of changes.
            (optional, Callable)

    Examples:

    ```python
    fs.builder("/tmp/foo")
    fs.builder("/tmp/bar", action="directory")
    for _ in [
            Item(dst="/tmp/{{ modname }}", action="directory"),
            Item(dst="/tmp/{{ modname }}/__init__.py"),
            ]:
        builder()
    ```

    <!-- #taskdoc -->
    """

    with CallDepth():
        if action == "template":
            r = cp(src=src, dst=dst)
        elif action == "copy":
            r = cp(src=src, dst=dst, template=False)
        elif action == "directory":
            r = mkdir(dst=dst, mode=mode)
        elif action == "exists":
            r = mkfile(dst=dst, mode=mode)
        elif action == "link":
            r = ln(src=src, dst=dst)
        elif action == "symlink":
            r = ln(src=src, dst=dst, symbolic=True)
        elif action == "absent":
            r = rm(dst=dst)
        else:
            raise ValueError(f"Unknown action: {action}")

        if mode is not None:
            chmod(dst, mode)
        if owner is not None or group is not None:
            chown(dst, owner, group)

    if notify is not None:
        r = r.notify(notify)

    return Return(changed=r.changed)


@calling_context
@template_args
def exists(
    dst: TemplateStr,
    ignore_failure: bool = True,
) -> object:
    """
    Does `dst` exist?

    Args:
        dst: File location to see if it exists. (templateable).
        ignore_failure: If True, do not treat file absence as a fatal failure.
             (optional, bool, default=True)

    Examples:

    ```python
    fs.exists(dst="/tmp/foo")
    if fs.exists(dst="/tmp/foo"):
        #  code for when file exists
    ```

    <!-- #taskdoc -->
    """
    if os.path.exists(dst):
        return Return(changed=False)

    return Return(
        changed=False,
        failure=True,
        ignore_failure=ignore_failure,
        raise_exc=Failure(f"File does not exist: {dst}")
        if not ignore_failure
        else None,
    )
