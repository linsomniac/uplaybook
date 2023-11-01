#!/usr/bin/env python3

from uplaybook import fs, core, up_context

fs.rm(dst="testdir", recursive=True)
fs.mkdir(dst="testdir")

core.notify(lambda: fs.rm(dst="testdir", recursive=True))
fs.cp(dst="testdir/testfile")
assert fs.exists("testdir/testfile")
core.flush_handlers()
assert not fs.exists("testdir/testfile")
