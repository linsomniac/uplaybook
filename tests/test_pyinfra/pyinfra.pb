#!/usr/bin/env python3

from uplaybook import fs, core, pyinfra
import os

def cleanup():
    fs.rm(path="testdir", recursive=True)

fs.rm(path="testdir", recursive=True)
fs.mkdir(path="testdir")
with fs.cd(path="testdir"):
    pyinfra.files.directory(path="infradir")
    assert os.path.exists("infradir")
    pyinfra.files.directory(path="infradir")
    assert os.path.exists("infradir")
    pyinfra.files.directory(path="infradir", present=False)
    assert not os.path.exists("infradir")

    pyinfra.files.file(path="infrafile")
