# uPlaybook2

An experiment into a python-centric ansible-like system.  Currently not usable except
by the author.

Example showing what a playbook might look like, and the output of running it
including detecting when no changes are made and updating permissions:

    #!/usr/bin/env python3

    from uplaybook2 import fs, core, IgnoreFailure

    foo = "test"
    fs.mkfile("foo{{foo}}")
    print(core.render("foo{{platform.fqdn}}"))
    r = fs.mkfile("foo{{platform.fqdn}}")
    core.debug(msg="Test message {{foo}}")
    core.debug(var=r)
    core.debug(var=core.lookup('platform'))
    r = core.run("date")
    core.debug(var=r)
    r = core.run("head -5 /etc/services")
    core.debug(var=r)
    with IgnoreFailure():
        r = core.run("false")
    core.debug(var=r)

Which produces the following output:

    => mkfile(path=footest, mode=None)
    fooseans-laptop
    => mkfile(path=fooseans-laptop, mode=None)
    =# debug(...)
    Test message test
    =# debug(...)
        Return(changed=True)
    =# debug(...)
        namespace(system='Linux',
                  release_name='Ubuntu',
                  release_id='ubuntu',
                  release_version='22.04',
                  release_like='debian',
                  release_codename='jammy',
                  arch='x86_64',
                  cpu_count=12,
                  fqdn='seans-laptop',
                  memory_total=33246973952,
                  memory_available=19445350400,
                  memory_used=10147008512,
                  memory_percent_used=41.5)
    => run(command=date, shell=True)
    Thu Oct  5 07:42:03 AM MDT 2023

    =# debug(...)
        Return(changed=True, extra.stderr='', extra.returncode=0, output='Thu Oct  5 07:42:03 AM MDT 2023\n')
    => run(command=head -5 /etc/services, shell=True)
    # Network services, Internet style
    #
    # Updated from https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml .
    #
    # New ports will be added on request if they have been officially assigned

    =# debug(...)
        Return(changed=True, extra.stderr='', extra.returncode=0,
        output="""
        # Network services, Internet style
        #
        # Updated from https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml .
        #
        # New ports will be added on request if they have been officially assigned
        """)
    => run(command=false, shell=True)
    =# debug(...)
        Return(changed=True, extra.stderr='', extra.returncode=1, output='')

    *** RECAP:  total=11 changed=5 failure=0
