#!/usr/bin/env python3

from uplaybook import fs, core

#  single handler
fs.rm(path="testdir", recursive=True)
fs.mkdir(path="testdir")

core.notify(lambda: fs.rm(path="testdir", recursive=True))
fs.cp(path="testdir/testfile")
assert fs.exists("testdir/testfile")
core.flush_handlers()
assert not fs.exists("testdir/testfile")

#  list of handlers
fs.rm(path="testdir", recursive=True)
fs.mkdir(path="testdir")

fs.mkfile(path="testdir/remove_me").notify([
    lambda: fs.rm(path="testdir/remove_me"),
    lambda: fs.mkfile(path="testdir/create_me")
    ])
assert fs.exists("testdir/remove_me")
assert not fs.exists("testdir/create_me")
core.flush_handlers()
assert not fs.exists("testdir/remove_me")
assert fs.exists("testdir/create_me")

#  clean up
fs.rm(path="testdir", recursive=True)
