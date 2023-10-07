# uPlaybook2

An experiment into a python-centric ansible/cookiecutter-like system.  Currently not usable except
by the author.

Some core ideas of it:

    - Python-like syntax
    - Declare the state you want to end up at.
    - Tasks communicate whether they have changed something.
    - Changed tasks can trigger a handler (if this file changes, restart a service).
    - Jinja2 templating of arguments and files delivered via fs.template()
    - Status output.

Example showing what a playbook might look like, and the output of running it
including detecting when no changes are made and updating permissions:

    #!/usr/bin/env python3

    from uplaybook2 import fs, core, up_context

    fs.mkdir("testdir", mode="a=rX,u+w")
    fs.cd('testdir')

    def test_handler2():
        global fs
        fs.mkfile('qux')
        fs.mkfile('xyzzy')

    def test_handler():
        global fs, test_handler2
        fs.mkfile('bar').notify(test_handler2)
        fs.mkfile('baz').notify(test_handler2)

    foo = "test"
    fs.mkfile("foo{{foo}}").notify(test_handler)

    fs.makedirs("foodir/bar/baz", mode="a=rX,u+w")
    core.run('date')
    if core.run('true'):
        print('Successfully ran true')
    if not core.run('false', ignore_failures=True):
        print('Successfully ran false')

Which produces the following output:

    [I] sean@seans-laptop ~/p/u/up2 (main)> up2 testpb
    => mkdir(path=testdir, mode=a=rX,u+w)
    =# cd(path=testdir)
    => mkfile(path=footest, mode=None)
    => makedirs(path=foodir/bar/baz, mode=a=rX,u+w)
    => run(command=date, shell=True, ignore_failures=False, change=True)
    Fri Oct  6 06:05:55 PM MDT 2023

    => run(command=true, shell=True, ignore_failures=False, change=True)
    Successfully ran true
    =! run(command=false, shell=True, ignore_failures=True, change=True) (failure ignored)
    Successfully ran false
    >> *** Starting handler: test_handler
    => mkfile(path=bar, mode=None)
    => mkfile(path=baz, mode=None)
    >> *** Starting handler: test_handler2
    => mkfile(path=qux, mode=None)
    => mkfile(path=xyzzy, mode=None)
    >> *** Done with handlers

    *** RECAP:  total=11 changed=10 failure=0
    [N] sean@seans-laptop ~/p/u/up2 (main)> up2 testpb
    =# mkdir(path=testdir, mode=a=rX,u+w)
    =# cd(path=testdir)
    =# mkfile(path=footest, mode=None)
    =# makedirs(path=foodir/bar/baz, mode=a=rX,u+w)
    => run(command=date, shell=True, ignore_failures=False, change=True)
    Fri Oct  6 06:05:57 PM MDT 2023

    => run(command=true, shell=True, ignore_failures=False, change=True)
    Successfully ran true
    =! run(command=false, shell=True, ignore_failures=True, change=True) (failure ignored)
    Successfully ran false

    *** RECAP:  total=7 changed=3 failure=0
