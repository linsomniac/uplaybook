#!/usr/bin/env -S python3 -m uplaybook.cli

from uplaybook import fs, core
import os

fs.rm(path="testdir", recursive=True)
fs.mkdir(path="testdir")
with fs.cd(path="testdir"):

    fs.fs(path="foo", state="exists")
    assert os.path.exists("foo")
    fs.fs(path="foo", state="absent")
    assert not os.path.exists("foo")

    fs.builder(items=[
        core.Item(path="bar", state="exists"),
        core.Item(path="bardir", state="directory"),
        ])
    fs.builder(defaults=core.Item(mode="a=rX"),
        items=[
            core.Item(path="bar", state="exists"),
            core.Item(path="bardir", state="directory"),
        ])
