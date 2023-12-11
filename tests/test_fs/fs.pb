#!/usr/bin/env python3

from uplaybook import fs, core
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

    #  test templating file names
    project_name = "my_project"
    fs.write(src="project", path=".")
    assert os.path.exists("my_project/my_project_test")
    core.grep(path="my_project/my_project_test", search="This is a test")
    core.grep(path="my_project/my_project_subdir/my_project_subfile", search="Another test")
    assert not os.path.exists("{{project_name}}/{{project_name}}_subdir/{{project_name}}_subfile")

    #  test NOT-templating file names
    project_name = "my_project"
    fs.write(src="project", path=".", template_filenames=False)
    assert os.path.exists("{{project_name}}/{{project_name}}_subdir/{{project_name}}_subfile")
