# uPlaybook2

An experiment into a python-centric ansible-like system.  Currently not usable except
by the author.

Example showing what a playbook might look like, and the output of running it
including detecting when no changes are made and updating permissions:

    #!/usr/bin/env python3

    from uplaybook2 import fs

    foo = "test"
    fs.mkfile("foo{{foo}}")
    fs.mkdir("testdir", mode="a=rX,u+w")
    fs.makedirs("foo/bar/baz", mode="a=rX,u+w")

Which produces the following output when run a few times:

    [I] seans-laptop ~/p/u/up2 (main)> up2 testpb
    => mkfile(path=footest, mode=None)
    => mkdir(path=testdir, mode=a=rX,u+w)
    => makedirs(path=foo/bar/baz, mode=a=rX,u+w)
    [N] seans-laptop ~/p/u/up2 (main)> up2 testpb
    =# mkfile(path=footest, mode=None)
    =# mkdir(path=testdir, mode=a=rX,u+w)
    =# makedirs(path=foo/bar/baz, mode=a=rX,u+w)
    [I] seans-laptop ~/p/u/up2 (main)> chmod 700 testdir foo/bar/baz
    [N] seans-laptop ~/p/u/up2 (main)> up2 testpb
    =# mkfile(path=footest, mode=None)
    => mkdir(path=testdir, mode=a=rX,u+w) (Changed permissions)
    => makedirs(path=foo/bar/baz, mode=a=rX,u+w) (Changed permissions)
    [N] seans-laptop ~/p/u/up2 (main)>
