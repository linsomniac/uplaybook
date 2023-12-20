#!/usr/bin/env -S python3 -m uplaybook.cli

from uplaybook import fs, core
import jinja2

include_test_main = "xyzzy"
core.include(playbook="sub1.pb")
assert core.render(s="{{ include_test_sub1 }}") == "xyzzy1"
core.include(playbook="sub2.pb", hoist_vars=False)
try:
    core.render(s="{{ include_test_sub2 }}")
    raise AssertionError("Variable 'include_test_sub2' was hoisted when hoist_vars=False")
except jinja2.exceptions.UndefinedError:
    pass
