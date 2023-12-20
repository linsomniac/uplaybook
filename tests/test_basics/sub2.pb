#!/usr/bin/env -S python3 -m uplaybook.cli

from uplaybook import fs, core, up_context

assert core.render(s="{{ include_test_main }}") == "xyzzy"
include_test_sub2 = "xyzzy2"
assert core.render(s="{{ include_test_sub2 }}") == "xyzzy2"
