#!/usr/bin/env python3

from uplaybook import fs, core
import os

fs.rm(dst="testdir", recursive=True)
fs.mkdir(dst="testdir")
with fs.cd(dst="testdir"):
    with open("srcfile", "w") as fp:
        fp.write("Hello!")
    fs.mv(src="srcfile", dst="dest")
    core.run("ls")
    assert not os.path.exists("srcfile")

    #  moving when dest exists
    with open("srcfile", "w") as fp:
        fp.write("Hello!")
    fs.mv(src="srcfile", dst="dest")
    assert os.path.exists("dest")
    assert not os.path.exists("srcfile")

    #  moving when src does not exist
    fs.mv(src="srcfile", dst="dest")
    assert os.path.exists("dest")
