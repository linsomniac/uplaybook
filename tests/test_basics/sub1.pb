#!/usr/bin/env python3

from uplaybook import fs, core

assert core.render("{{ include_test_main }}") == "xyzzy"
include_test_sub1 = "xyzzy1"
assert core.render("{{ include_test_sub1 }}") == "xyzzy1"
