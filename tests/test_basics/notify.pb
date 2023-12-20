#!/usr/bin/env -S python3 -m uplaybook.cli

from uplaybook import fs, core

#  single handler
fs.rm(path="testdir", recursive=True)
fs.mkdir(path="testdir")

core.notify(handler=lambda: fs.rm(path="testdir", recursive=True))
fs.cp(path="testdir/testfile")
assert fs.exists(path="testdir/testfile")
core.flush_handlers()
assert not fs.exists(path="testdir/testfile")

#  list of handlers
fs.rm(path="testdir", recursive=True)
fs.mkdir(path="testdir")

fs.mkfile(path="testdir/remove_me").notify(handler=[
    lambda: fs.rm(path="testdir/remove_me"),
    lambda: fs.mkfile(path="testdir/create_me")
    ])
assert fs.exists(path="testdir/remove_me")
assert not fs.exists(path="testdir/create_me")
core.flush_handlers()
assert not fs.exists(path="testdir/remove_me")
assert fs.exists(path="testdir/create_me")

#  clean up
fs.rm(path="testdir", recursive=True)
