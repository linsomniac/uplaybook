#!/usr/bin/env -S python3 -m uplaybook.cli

from uplaybook import fs, core

secret = "xyzzy"

fs.rm(path="testdir", recursive=True)
fs.mkdir(path="testdir")
with fs.cd(path="testdir"):
    fs.cp(src="src", path=".", recursive=True)
assert core.grep(path="testdir/src_template", search="secret=xyzzy")
