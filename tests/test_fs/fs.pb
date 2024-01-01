#!/usr/bin/env -S python3 -m uplaybook.cli

from uplaybook import fs, core
import os

fs.rm(path="testdir", recursive=True)
fs.mkdir(path="testdir")
with fs.cd(path="testdir"):
    with open("srcfile", "w") as fp:
        fp.write("Hello!")
    fs.mv(src="srcfile", path="dest")
    core.run(command="ls")
    assert not os.path.exists(path="srcfile")

    #  moving when dest exists
    with open("srcfile", "w") as fp:
        fp.write("Hello!")
    fs.mv(src="srcfile", path="dest")
    assert os.path.exists(path="dest")
    assert not os.path.exists(path="srcfile")

    #  moving when src does not exist
    fs.mv(src="srcfile", path="dest")
    assert os.path.exists(path="dest")

    #  test templating file names
    project_name = "my_project"
    fs.cp(src="project", path=".")
    assert os.path.exists(path="my_project/my_project_test")
    core.grep(path="my_project/my_project_test", search="This is a test")
    core.grep(path="my_project/my_project_subdir/my_project_subfile", search="Another test")
    assert not os.path.exists(path="{{project_name}}/{{project_name}}_subdir/{{project_name}}_subfile")

    #  test NOT-templating file names
    project_name = "my_project"
    fs.cp(src="project", path=".", template_filenames=False)
    assert os.path.exists(path="{{project_name}}/{{project_name}}_subdir/{{project_name}}_subfile")

    import time

    with open('older', 'w') as fp:
        fp.write('foo')
    time.sleep(0.01)
    with open('newer', 'w') as fp:
        fp.write('foo')

    assert fs.newer_than(src='older', path='nonexistant_file')
    assert not fs.newer_than(src='older', path='newer')
    assert fs.newer_than(src='newer', path='older')

    did_handler = False
    def handler():
        global did_handler
        did_handler = True
    fs.newer_than(src='newer', path='older').notify(handler)
    core.flush_handlers()
    assert did_handler

    assert not fs.exists(path="fs.pb")
    path="*.pb"
    fs.builder(items=list(fs.globitems(path="{{path}}", src="{{path}}")))
    assert fs.exists(path="fs.pb")
