#!/usr/bin/env python3

from .internals import Return, BaseTask, make_task
from typing import Union, Optional
import symbolicmode
import os
import stat


def _mode_from_arg(mode: Optional[Union[str, int]] = None, initial_mode: Optional[int] = None, is_directory: bool=False) -> Optional[int]:
    if type(mode) is int or mode is None:
        return mode

    assert type(mode) is str

    mode_is_sym_str = type(mode) is str and not set(mode).issubset("01234567")
    if mode_is_sym_str:
        extra_args = {}
        if initial_mode:
            extra_args['initial_mode'] = initial_mode

        return symbolicmode.symbolic_to_numeric_permissions(mode, is_directory=is_directory, **extra_args)

    return int(mode, 8)

def _chmod(path: str, mode: Optional[Union[str, int]] = None, is_directory: bool=False) -> Return:
    if mode is None:
        return Return(changed=False)

    current_mode = stat.S_IMODE(os.stat(path).st_mode)
    mode = _mode_from_arg(mode, initial_mode=current_mode, is_directory=is_directory)
    if current_mode != mode:
        assert type(mode) is int
        os.chmod(path, mode)
        return Return(changed=True, extra_message="Changed permissions")

    return Return(changed=False)


@make_task
class mkdirClass(BaseTask):
    name = "mkdir"

    def __init__(self):
        pass

    def __call__(self, path: str, mode: Optional[Union[str, int]] = None) -> Return:
        new_mode = mode
        if not os.path.exists(path):
            new_mode = _mode_from_arg(new_mode, is_directory=True)

            mode_arg = {}
            if new_mode is not None:
                mode_arg = {'mode': new_mode}

            os.mkdir(path, **mode_arg)

            return Return(changed=True)

        return _chmod(path, new_mode, is_directory=True)
