#!/usr/bin/env python3

from uplaybook import fs, core

#  single handler
fs.rm(dst="testdir", recursive=True)
fs.mkdir(dst="testdir")

core.notify(lambda: fs.rm(dst="testdir", recursive=True))
fs.cp(dst="testdir/testfile")
assert fs.exists("testdir/testfile")
core.flush_handlers()
assert not fs.exists("testdir/testfile")

#  list of handlers
fs.rm(dst="testdir", recursive=True)
fs.mkdir(dst="testdir")

fs.mkfile(dst="testdir/remove_me").notify([
    lambda: fs.rm(dst="testdir/remove_me"),
    lambda: fs.mkfile(dst="testdir/create_me")
    ])
assert fs.exists("testdir/remove_me")
assert not fs.exists("testdir/create_me")
core.flush_handlers()
assert not fs.exists("testdir/remove_me")
assert fs.exists("testdir/create_me")

#  clean up
fs.rm(dst="testdir", recursive=True)
