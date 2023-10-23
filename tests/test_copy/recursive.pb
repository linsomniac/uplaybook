#!/usr/bin/env python3

from uplaybook import fs, core, up_context

secret = "xyzzy"

fs.rm(path="testdir", recursive=True)
fs.mkdir(path="testdir")
with fs.cd(path="testdir"):
    fs.cp(src="src", path=".", recursive=True)
