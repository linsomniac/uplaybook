#!/usr/bin/env python3

from uplaybook import fs, core, pyinfra
import os

def cleanup():
    fs.rm(dst="testdir", recursive=True)

fs.rm(dst="testdir", recursive=True)
fs.mkdir(dst="testdir")
with fs.cd(dst="testdir"):
    pyinfra.files.directory(path="infradir")
    assert os.path.exists("infradir")
    pyinfra.files.directory(path="infradir")
    assert os.path.exists("infradir")
    pyinfra.files.directory(path="infradir", present=False)
    assert not os.path.exists("infradir")

    pyinfra.files.file(path="infrafile")
