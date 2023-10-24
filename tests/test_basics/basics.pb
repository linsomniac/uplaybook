#!/usr/bin/env python3

from uplaybook import fs, core, up_context

fs.rm(path="testdir", recursive=True)
fs.mkdir(path="testdir")
with fs.cd(path="testdir"):
    fs.cp(path="testfile")
    assert fs.exists("testfile")
