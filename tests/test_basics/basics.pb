#!/usr/bin/env python3

from uplaybook import fs, core

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

var = "bar"
r = core.render("foo{{ var }}")
assert r == "foobar"
core.debug(msg="Expanding template: {{var}}")
core.print(msg="Expanding template: {{var}}")

class Handler:
    def __init__(self):
        self.ran = False

    def handler(self):
        self.ran = True

test_handler = Handler()
assert not test_handler.ran
core.run(command="true").notify(test_handler.handler)
assert not test_handler.ran
core.flush_handlers()
assert test_handler.ran

core.exit(0)
core.run("false")   #  if control gets here, the exit above didn't work
