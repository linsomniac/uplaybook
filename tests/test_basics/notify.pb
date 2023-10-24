#!/usr/bin/env python3

from uplaybook import fs, core, up_context

fs.rm(path="testdir", recursive=True)
fs.mkdir(path="testdir")

core.notify(lambda: fs.rm(path="testdir", recursive=True))
fs.cp(path="testdir/testfile")
assert fs.exists("testdir/testfile")
core.flush_handlers()
assert not fs.exists("testdir/testfile")
