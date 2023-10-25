#!/usr/bin/env python3

"""
Filesystem related tasks.
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
    current_mode = stat_module.S_IMODE(path_stats.st_mode)
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
        context_manager=lambda: cd(old_dir),
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
        except OSError:
            raise Failure(
                f"Path {path} is a directory, will not remove without `recursive` option"
            )
    else:
        shutil.rmtree(path)

    return Return(changed=True)


@calling_context
@template_args
def stat(
    path: TemplateStr,
    follow_symlinks: bool = True,
) -> Return:
    """
    Get information about `path`.

    Arguments:

    - **path**: Path to stat.  (templateable).
    - **follow_symlinks**: If True (default), the result will be on the destination of
            a symlink, if False the result will be about the symlink itself.
            (bool, default: True)

    Extra:

    - **perms**: The permissions of `path` (st_mode & 0o777).
    - **st_mode**: Full mode of `path` (permissions, object type).  You probably want the
            "perms" field if you just want the permissions of `path`.
    - **st_ino**: Inode number.
    - **st_dev**: ID of the device containing `path`.
    - **st_nlink**: Number of hard links.
    - **st_uid**: User ID of owner.
    - **st_gid**: Group ID of owner.
    - **st_size**: Total size in bytes.
    - **st_atime**: The time of the last access of file data.
    - **st_mtime**: The time of last modification of file data.
    - **st_ctime**: The time of the last change of status/inode.
    - **S_ISBLK**: Is `path` a block special device file?
    - **S_ISCHR**: Is `path` a character special device file?
    - **S_ISDIR**: Is `path` a directory?
    - **S_ISDOOR**: Is `path` a door?
    - **S_ISFIFO**: Is `path` a named pipe?
    - **S_ISLNK**: Is `path` a symbolic link?
    - **S_ISPORT**: Is `path` an event port?
    - **S_ISREG**: Is `path` a regular file?
    - **S_ISSOCK**: Is `path` a socket?
    - **S_ISWHT**: Is `path` a whiteout?

    Examples:

        stat = fs.stat(path="/tmp/foo")
        print(f"UID: {{stat.extra.st_uid}}")
        fs.stat(path="/tmp/foo", follow_symlinks=False)

    #taskdoc
    """

    s = os.stat(path, follow_symlinks=follow_symlinks)

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
def ln(
    path: TemplateStr,
    src: TemplateStr,
    symbolic: bool = False,
) -> Return:
    """
    Create a link from `src` to `path`.

    Arguments:

    - **path**: Name of destination of link. (templateable).
    - **src**: Name of location of source to create link from. (templateable).
    - **symbolic**: If True, makes a symbolic link. (bool, default: False)

    Examples:

        fs.ln(path="/tmp/foo", src="/tmp/bar")
        fs.ln(path="/tmp/foo", src="/tmp/bar", symbolic=True)

    #taskdoc
    """

    if symbolic:
        if os.path.islink(path) and os.readlink(path) == src:
            return Return(changed=False)
        if os.path.exists(path):
            os.remove(path)
        os.symlink(src, path)
    else:
        if os.path.exists(path):
            src_stat = os.stat(src)
            path_stat = os.stat(path)

            if (
                src_stat.st_dev == path_stat.st_dev
                and src_stat.st_ino == path_stat.st_ino
            ):
                return Return(changed=False)

            os.remove(path)

        os.link(src=src, dst=path)

    return Return(changed=True)


@calling_context
@template_args
def cp(
    path: TemplateStr,
    src: Optional[TemplateStr] = None,
    mode: Optional[Union[TemplateStr, int]] = None,
    encrypt_password: Optional[TemplateStr] = None,
    decrypt_password: Optional[TemplateStr] = None,
    template: bool = True,
    template_filenames: bool = True,
    recursive: bool = True,
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
    - **template_filenames**: If True, filenames found during recursive copy are
            jinja2 template expanded. (default: True)
    - **recursive**: If True and `src` is a directory, recursively copy it and
            everything below it to the `path`.  If `path` ends in a "/",
            the last component of `src` is created under `path`, otherwise
            the contents of `src` are written into `path`. (default: True)

    Examples:

        fs.cp(path="/tmp/foo")
        fs.cp(src="bar-{{ fqdn }}.j2", path="/tmp/bar", template=False)

    #taskdoc
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
            old_mode = stat.S_IMODE(os.stat(dst).st_mode)
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

    new_src = src if src is not None else os.path.basename(path) + ".j2"
    new_src = internals.find_file(new_src)

    if encrypt_password or decrypt_password:
        raise NotImplementedError("Crypto not implemented yet")

    changes_made = set()
    src_is_dir = stat_module.S_ISDIR(os.stat(new_src).st_mode)
    if recursive and src_is_dir:
        with CallDepth():
            for dirpath, dirnames, filenames in os.walk(new_src):
                dst_dir = os.path.join(path, os.path.relpath(dirpath, new_src))

                r = mkdir(path=dst_dir, mode=mode)
                if r.changed:
                    changes_made.add("Subdir")

                for filename in filenames:
                    src_file = RawStr(os.path.join(dirpath, filename))
                    dst_file = os.path.join(dst_dir, filename)
                    r = cp(src=src_file, path=dst_file)
                    if r.changed:
                        changes_made.add("Subfile")
    else:
        change = _copy_file(new_src, path, mode)
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
    - **action**: Type of `path` to build, can be: "directory", "template", "exists",
            "copy", "absent", "link", "symlink". (optional, templatable, default="template")
    - **notify**:  Handler to notify of changes.
            (optional, Callable)

    Examples:

        fs.builder("/tmp/foo")
        fs.builder("/tmp/bar", action="directory")
        for _ in [
                Item(path="/tmp/{{ modname }}", action="directory"),
                Item(path="/tmp/{{ modname }}/__init__.py"),
                ]:
            builder()

    #taskdoc
    """

    with CallDepth():
        if action == "template":
            r = cp(src=src, path=path)
        elif action == "copy":
            r = cp(src=src, path=path, template=False)
        elif action == "directory":
            r = mkdir(path=path, mode=mode)
        elif action == "exists":
            r = mkfile(path=path, mode=mode)
        elif action == "link":
            r = ln(src=src, path=path)
        elif action == "symlink":
            r = ln(src=src, path=path, symbolic=True)
        elif action == "absent":
            r = rm(path=path)
        else:
            raise ValueError(f"Unknown action: {action}")

        if mode is not None:
            chmod(path, mode)
        if owner is not None or group is not None:
            chown(path, owner, group)

    if notify is not None:
        r = r.notify(notify)

    return Return(changed=r.changed)


@calling_context
@template_args
def exists(
    path: TemplateStr,
    ignore_failures: bool = True,
) -> object:
    """
    Does `path` exist?

    Arguments:

    - **path**: File location to see if it exists. (templateable).
    - **ignore_failures**: If True, do not treat file absence as a fatal failure.
             (optional, bool, default=True)

    Examples:

        fs.exists(path="/tmp/foo")
        if fs.exists(path="/tmp/foo"):
            #  code for when file exists

    #taskdoc
    """
    if os.path.exists(path):
        return Return(changed=False)

    return Return(
        changed=False,
        failure=True,
        ignore_failure=ignore_failures,
        raise_exc=Failure(f"File does not exist: {path}")
        if not ignore_failures
        else None,
    )
