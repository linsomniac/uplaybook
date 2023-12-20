#!/usr/bin/env -S python3 -m uplaybook.cli

from uplaybook import fs, core

assert core.render("{{ include_test_main }}") == "xyzzy"
include_test_sub1 = "xyzzy1"
assert core.render("{{ include_test_sub1 }}") == "xyzzy1"
