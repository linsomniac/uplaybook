#!/usr/bin/env -S python3 -m uplaybook.cli

from uplaybook import core

msg = "".join(("x", "y", "z", "z", "y"))
core.debug(msg=msg)
