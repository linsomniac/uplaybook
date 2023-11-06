#!/usr/bin/env python3

from uplaybook import fs, core

secret = "xyzzy"

fs.rm(dst="testdir", recursive=True)
fs.mkdir(dst="testdir")
with fs.cd(dst="testdir"):
    fs.cp(src="src", dst=".", recursive=True)
assert core.grep("testdir/src_template", "secret=xyzzy")
