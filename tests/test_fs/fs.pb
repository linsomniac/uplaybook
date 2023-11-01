#!/usr/bin/env python3

from uplaybook import fs, core, up_context
import os

fs.rm(path="testdir", recursive=True)
fs.mkdir(path="testdir")
with fs.cd(path="testdir"):
    with open("srcfile", "w") as fp:
        fp.write("Hello!")
    fs.mv(src="srcfile", path="dest")
    core.run("ls")
    assert not os.path.exists("srcfile")

    #  moving when dest exists
    with open("srcfile", "w") as fp:
        fp.write("Hello!")
    fs.mv(src="srcfile", path="dest")
    assert os.path.exists("dest")
    assert not os.path.exists("srcfile")

    #  moving when src does not exist
    fs.mv(src="srcfile", path="dest")
    assert os.path.exists("dest")
