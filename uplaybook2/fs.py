#!/usr/bin/env python3

from .internals import Return, TemplateStr, template_args, calling_context, up_context
from typing import Union, Optional
import symbolicmode
import os
import stat
import random
import string
import hashlib


def _mode_from_arg(
    mode: Optional[Union[str, int]] = None,
    initial_mode: Optional[int] = None,
    is_directory: bool = False,
) -> Optional[int]:
    if type(mode) is int or mode is None:
        return mode

    assert type(mode) is str

    mode_is_sym_str = type(mode) is str and not set(mode).issubset("01234567")
    if mode_is_sym_str:
        extra_args = {}
        if initial_mode:
            extra_args["initial_mode"] = initial_mode

        return symbolicmode.symbolic_to_numeric_permissions(
            mode, is_directory=is_directory, **extra_args
        )

    return int(mode, 8)


def _chmod(
    path: str, mode: Optional[Union[str, int]] = None, is_directory: bool = False
) -> Return:
    if mode is None:
        return Return(
            changed=False, secret_args={"decrypt_password", "encrypt_password"}
        )

    current_mode = stat.S_IMODE(os.stat(path).st_mode)
    mode = _mode_from_arg(mode, initial_mode=current_mode, is_directory=is_directory)
    if current_mode != mode:
        assert type(mode) is int
        os.chmod(path, mode)
        return Return(
            changed=True,
            extra_message="Changed permissions",
            secret_args={"decrypt_password", "encrypt_password"},
        )

    return Return(changed=False, secret_args={"decrypt_password", "encrypt_password"})


@calling_context
@template_args
def cd(path: TemplateStr) -> Return:
    """
    Change working directory to `path`.

    Arguments:

    - **path**: Directory to change into (templateable).

    Examples:

        fs.cd(path="/tmp")

    #taskdoc
    """
    os.chdir(path)
    return Return(changed=False)


@calling_context
@template_args
def mkfile(path: TemplateStr, mode: Optional[Union[TemplateStr, int]] = None) -> Return:
    """
    Create an empty file if it does not already exist.

    Arguments:

    - **path**: Name of file to create (templateable).
    - **mode**: Permissions of file (optional, templatable string or int).

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

    return _chmod(path, new_mode)


@calling_context
@template_args
def mkdir(
    path: TemplateStr,
    mode: Optional[Union[TemplateStr, int]] = None,
    parents: Optional[bool] = None,
) -> Return:
    """
    Create a directory.

    Arguments:

    - **path**: Name of file to create (templateable).
    - **mode**: Permissions of directory (optional, templatable string or int).
    - **parents**: Make parent directories if needed.

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
        os.makedirs(path, **mode_arg)

        return Return(changed=True)

    return _chmod(path, new_mode, is_directory=True)


def _random_ext(i: int = 8) -> str:
    "Return a random string of length 'i'"
    return "".join(
        random.choices(
            string.ascii_lowercase + string.ascii_uppercase + string.digits, k=i
        )
    )


@calling_context
@template_args
def template(
    dst: TemplateStr,
    src: Optional[TemplateStr] = None,
    encrypt_password: Optional[TemplateStr] = None,
    decrypt_password: Optional[TemplateStr] = None,
    mode: Optional[Union[TemplateStr, int]] = None,
) -> Return:
    """
    Jinja2 templating is used to fill in `src` file to write to `dst`.

    Arguments:

    - **dst**: Name of destination file. (templateable).
    - **src**: Name of template to use as source (optional, templateable).
           Defaults to the basename of `dst` + ".j2".
    - **mode**: Permissions of file (optional, templatable string or int).

    Examples:

        fs.template("/tmp/foo")
        fs.mkfile("/tmp/bar", 0o755)

    #taskdoc
    """

    if encrypt_password or decrypt_password:
        raise NotImplemented("Crypto not implemented yet")

    new_mode = _mode_from_arg(mode, is_directory=False)

    hash_before = None
    if os.path.exists(dst):
        with open(dst, "rb") as fp_in:
            sha = hashlib.sha256()
            sha.update(fp_in.read())
            hash_before = sha.digest()

    new_src = src
    if new_src is None:
        new_src = os.path.basename(dst) + ".j2"
    with open(new_src, "r") as fp_in:
        data = up_context.jinja_env.from_string(fp_in.read()).render(
            up_context.get_env()
        )

    sha = hashlib.sha256()
    sha.update(data.encode("latin-1"))
    hash_after = sha.digest()

    if hash_before == hash_after:
        return _chmod(dst, new_mode, is_directory=False)

    dstTmp = dst + ".tmp." + _random_ext()
    with open(dstTmp, "w") as fp_out:
        fp_out.write(data)
    if new_mode is not None:
        os.chmod(dstTmp, new_mode)
    os.rename(dstTmp, dst)

    return Return(changed=True, secret_args={"decrypt_password", "encrypt_password"})
