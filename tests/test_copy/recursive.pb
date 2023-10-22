#!/usr/bin/env python3

from uplaybook2 import fs, core, up_context

fs.rm(path="testdir", recursive=True)
fs.mkdir(path="testdir")
with fs.cd(path="testdir"):
    fs.cp(src="src", path=".", recursive=True)
