#!/usr/bin/env python3

from uplaybook import fs, core, up_context

assert core.render("{{ include_test_main }}") == "xyzzy"
include_test_sub2 = "xyzzy2"
assert core.render("{{ include_test_sub2 }}") == "xyzzy2"
