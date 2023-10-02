#!/usr/bin/env python3

from .internals import Return
from typing import Union, Optional
import symbolicmode
import os
import stat


class mkdirClass:
    name = "mkdir"

    def __init__(self):
        pass

    def __call__(self, path: str, mode: Optional[Union[str, int]] = None) -> Return:
        new_mode = mode
        if not os.path.exists(path):
            if type(new_mode) == str:
                new_mode = symbolicmode.symbolic_to_numeric_permissions(
                    new_mode, is_directory=True
                )

            if new_mode is None:
                os.mkdir(path)
            else:
                os.mkdir(path, new_mode)

            return Return(changed=True)

        if not new_mode:
            return Return(changed=False)

        current_mode = stat.S_IMODE(os.stat(path).st_mode)
        if type(new_mode) == str:
            new_mode = symbolicmode.symbolic_to_numeric_permissions(
                new_mode, initial_mode=current_mode, is_directory=True
            )
        if current_mode != new_mode:
            os.chmod(path, new_mode)
            return Return(changed=True, msg="Changed permissions")

        return Return(changed=False)


mkdir = mkdirClass()
