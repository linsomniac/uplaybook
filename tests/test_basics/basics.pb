#!/usr/bin/env python3

from uplaybook import fs, core, up_context

fs.rm(dst="testdir", recursive=True)
fs.mkdir(dst="testdir")
with fs.cd(dst="testdir"):
    fs.cp(dst="testfile")
    assert fs.exists("testfile")

core.run(command="date")
r = core.run(command="true")
assert r
r = core.run(command="false", ignore_failures=True)
assert not r
