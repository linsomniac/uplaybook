#!/usr/bin/env python3

from uplaybook import fs, core

secret = "xyzzy"

fs.rm(path="testdir", recursive=True)
fs.mkdir(path="testdir")
with fs.cd(path="testdir"):
    fs.cp(src="src", path=".", recursive=True)
assert core.grep("testdir/src_template", "secret=xyzzy")
