# Templating

## Overview

uPlaybook makes extensive use of
[Jinja2 templating](https://jinja.palletsprojects.com/en/2.10.x/templates/).  Python
variables in your playbook will be "forklifted" into the template context.  Additionaly,
context is added to make the playbook arguments, shell environment, platform information
available to templates.

## Template Context

The Jinja2 context defines values that can be used in templates.  The context includes:

- Any variables set in the playbook.  (`playbook_name = "my_project"` allows `{{
  playbook_name }}`).
- Playbook arguments are available in the `ARGS` namespace.  (`{{ ARGS.project_name }}`).
- The shell environment is available in the `environ` dictionary.  (`{{ environ["HOME"] }}`).
- The `platform` namespace contains a lot of information about the system uPlaybook is
  running on.

## Platform Info

The following information is available in the `platform` namespace on the following
platforms:

- Linux:
  - arch: 'x86_64',
  - release_codename: 'jammy',
  - release_id: 'ubuntu',
  - os_family: 'debian',
  - release_name: 'Ubuntu',
  - release_version: '22.04',
  - system: 'Linux'
- MacOS:
  - arch: 'arm64',
  - release_version: '13.0.1',
  - system: 'Darwin'
- Windows:
  - arch: 'AMD64',
  - release_edition: 'ServerStandard',
  - release_name: '10',
  - release_version: '10.0.17763',
  - system: 'Windows'
- Platforms with "psutil" module available:
  - memory_total = Total memory
  - memory_available = Available memory
  - memory_used = Used memory
  - memory_percent_used = Percent used

## Additional Filters

The following additional filters are added to the stock set of [Jinja2
filters](https://tedboy.github.io/jinja2/templ14.html):

- basename: The basename of a filesystem path.  ("{{'/foo/bar/baz'|basename}}" -> "baz")
- dirname: Everything but the basename.  ("{{'/foo/bar/baz'|dirname}}" -> "/foo/bar")
- abspath: The absolute path of a filesystem object.  ("{{'foo'|abspath}}" ->
  "$PWD/foo")

## Task Arguments

Many arguments to tasks can take templateable strings.  In the task documentation, these
argument will be denoted as "templatable".

This can lead to a somewhat awkward situation if you ever want to have a literal "{{" in
an argument of a task.  Rare should be the situation where you need a file name with "{{"
in it, but if you do you have these options:

- Use a RawStr
    ```
    fs.cp(src="template.j2", dst=core.RawStr("{{filename}}"))
    ```
- Put the value in a variable that is template expanded:
    ```
    filename = "{{ my weird filename"
    fs.cp(src="template.j2", dst="{{filename}}")
    ```
- Use the "raw" Jinja2 tag:
    ```
    fs.cp(src="template.j2", dst="{{raw}}{{filename}}{{endraw}}")
    ```

## Files with cp()

The `src` file in `fs.cp()` will be template expanded (if `template` argument is set to
True, the default).

!!! For Ansible Users

    uPlaybook doesn't separate `copy()` and `template()` endpoints, it is just a flag on
    the `cp()` endpoint.

<!-- vim: set tw=90: -->
