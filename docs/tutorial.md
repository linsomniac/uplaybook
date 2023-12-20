# Tutorial

## Installing

Typically you are able to install uPlaybook by running: `python3 -m pip install uplaybook`

For more detailed installation instructions, see [Installing uPlaybook](installing.md)

## Your First Playbook

"Playbooks" are the main artifact of uPlaybook.  A playbook contains the recipe that
declares the desired state of the system.

Playbooks are Python code, with some features and conventions to make it more ergonomic
for configuration management operations.

For our first example, let's set up an Apache server:

```python
from uplaybook import pyinfra, fs

pyinfra.apt.packages(packages=["apache2"])
fs.ln(src="/etc/apache2/mods-available/proxy.load",
      path="/etc/apache2/mods-enabled",
      symbolic=True)
fs.ln(src="/etc/apache2/mods-available/proxy_http.load",
      path="/etc/apache2/mods-enabled",
      symbolic=True)
pyinfra.systemd.service(service="apache2", running=True, enabled=True)
```

This playbook installs the "apache2" package and creates a symlink to enable the
`proxy` and `proxy_http` modules.  It also ensures that Apache2 is enabled at boot and running.

Run the above with: `up apache-module.pb` (if you saved the above to the file
"apache-module.pb":

```shell
$ sudo up apache-module.pb
=# packages(packages=['apache2'], present=True, latest=False, update=False, upgrade=False, force=False,
no_recommends=False, allow_downgrades=False)
=> ln(path=/etc/apache2/mods-enabled, src=/etc/apache2/mods-available/proxy.load, symbolic=True)
=> ln(path=/etc/apache2/mods-enabled, src=/etc/apache2/mods-available/proxy_http.load, symbolic=True)
=# service(service=apache2, running=True, restarted=False, reloaded=False, enabled=True, daemon_reload=False,
user_mode=False)

*** RECAP:  total=4 changed=2 failure=0
```

The ">" shows that action was taken, "#" means no action required, the system state
already matches the declaration.

## Declarative Config Management

uPlaybook implements "declarative configuration management", meaning statements declare
the desired state.  In the above playbook, you are declaring that the "apache2" package is
installed, and that the `proxy.load` and `proxy_http.load` symlinks exist.

This differs from shell scripting which specify actions: some actions may be safe to run
if previously run (such as changing ownership, a noop if the owner is already the desired
owner), but some may not (re-adding a user to a system will fail).

One benefit of this is that uPlaybook understand when an action changes the system.  We
can use this to trigger additional actions in this case.  We call this "notifying a
handler".

## Notifying Handlers

Handlers and notifying them is an idea taken from Ansible.  Let's modify the above
playbook:

```python
from uplaybook import pyinfra, fs

def restart_apache():
    pyinfra.systemd.service(service="apache2", restarted=True)

pyinfra.apt.packages(packages=["apache2"])
fs.ln(src="/etc/apache2/mods-available/proxy.load",
      path="/etc/apache2/mods-enabled",
      symbolic=True).notify(restart_apache)     #   <-- Added notify here
fs.ln(src="/etc/apache2/mods-available/proxy_http.load",
      path="/etc/apache2/mods-enabled",
      symbolic=True).notify(restart_apache)     #   <-- Added notify here
pyinfra.systemd.service(service="apache2", running=True, enabled=True)
```

A handler is a python function, and you chain `.notify(retart_apache)` to the `fs.ln`
task.

Notifications are deferred until the end of the playbook, or until `core.flush_handlers()`
is called.  Multiple notifys of the same handler will be deduplicated.  You can perform
multiple tasks that notify the apache restart, but only one restart will be done.

In other words, you can enable multiple modules, copy or update configuration files, and
any (or all) of them will later restart apache to make the changes take effect.

On the other hand, if you re-run the playbook later, and no changes are necessary (the
playbook already reflects system state), no restart will be done.

Running the above produces:

```shell
$ sudo up apache-module.pb
=# packages(packages=['apache2'], present=True, latest=False, update=False, upgrade=False, force=False,
no_recommends=False, allow_downgrades=False)
=> ln(path=/etc/apache2/mods-enabled, src=/etc/apache2/mods-available/proxy.load, symbolic=True)
=> ln(path=/etc/apache2/mods-enabled, src=/etc/apache2/mods-available/proxy_http.load, symbolic=True)
=# service(service=apache2, running=True, restarted=False, reloaded=False, enabled=True, daemon_reload=False,
user_mode=False)
>> *** Starting handler: restart_apache
=> service(service=apache2, running=True, restarted=True, reloaded=False, daemon_reload=False, user_mode=False)
>> *** Done with handlers

*** RECAP:  total=5 changed=3 failure=0
```

## fs.builder()

[`fs.builder()`](tasks/fs/#uplaybook.fs.builder) is a powerful way to create a large
set of filesystem objects.  It takes a list of operations to perform, and optionally a set
of defaults.  So you can specify defaults for permissions, ownership, etc, and then
optionally override them in the specific items.

For example, to set up headscale:

```python
from uplaybook.core import Item

def restart_headscale():
    pyinfra.systemd.service(service="headscale", restarted=True)

fs.builder(defaults=Item(owner="headscale", group="headscale", mode="a=-,ug+rwX"),
           items=[
               Item(path="/etc/headscale", state="directory"),
               Item(path="/etc/headscale/config.yaml", notify=restart_headscale),
               Item(path="/etc/headscale/acls.yaml", notify=restart_headscale),
               Item(path="/etc/headscale/derp.yaml", notify=restart_headscale),
               ])
```

## Reading Docs

How do you know what tasks and arguments are available?  uPlaybook includes an "--up-docs"
argument that will display documentation:

```shell
$ up --up-docs
[lists available modules]
$ up --up-doc fs
[lists available "fs" tasks]
$ up --up-docs fs.
# fs.ln

    Create a link from `src` to `path`.

    Args:
        path: Name of destination of link. (templateable).
        src: Name of location of source to create link from. (templateable).
        symbolic: If True, makes a symbolic link. (bool, default: False)
    [...]
```

Additionally, documentation is available at:
[uPlaybook Documentation](https://linsomniac.github.io/uplaybook)

## Playbook Arguments

Playbooks can also take arguments on the command line to "parameterize" playbooks.  Let's
say, for example, that we want to have a generic playbook that enables the module
specified on the command-line:

```python
from uplaybook import pyinfra, fs, core, ARGS   # <-- Need "core, ARGS" now

core.playbook_args(options=[
    core.Argument(name="module_name"),
])

def restart_apache():
    pyinfra.systemd.service(service="apache2", restarted=True)

pyinfra.apt.packages(packages=["apache2"])
fs.ln(src="/etc/apache2/mods-available/{{ ARGS.module_name }}.load",
    path="/etc/apache2/mods-enabled",
    symbolic=True).notify(restart_apache)
pyinfra.systemd.service(service="apache2", running=True, enabled=True)
```

If we run `up apache-module.pb`, we now get:

```shell
$ sudo up apache-module
usage: up:apache-module.pb [-h] module_name
up:apache-module.pb: error: the following arguments are required: module_name
```

So now we can run:

```shell
$ sudo up apache-module.pb proxy
=# packages(packages=['apache2'], present=True, latest=False, update=False, upgrade=False, force=False,
no_recommends=False, allow_downgrades=False)
=> ln(path=/etc/apache2/mods-enabled, src=/etc/apache2/mods-available/{{ ARGS.module_name }}.load, symbolic=True)
=# service(service=apache2, running=True, restarted=False, reloaded=False, enabled=True, daemon_reload=False,
user_mode=False)
>> *** Starting handler: restart_apache
=> service(service=apache2, running=True, restarted=True, reloaded=False, daemon_reload=False, user_mode=False)
>> *** Done with handlers

*** RECAP:  total=4 changed=2 failure=0
```

## Directory Playbooks

Once playbooks start getting more complex, it can become useful to make "directory
playbooks", which combines the playbook with additional files the playbook may need such
as templates or files.

If we create a "my-website" directory and create a "playbook" file within it, we now have
a directory playbook.

```shell
$ mkdir my-website
$ nano my-website/playbook
```

In the "playbook" file put the following:

```python
from uplaybook import pyinfra, fs, core

def restart_apache():
    pyinfra.systemd.service(service="apache2", restarted=True)

pyinfra.apt.packages(packages=["apache2", "libapache2-mod-uwsgi"])
for module_name in ["proxy", "uwsgi"]:
    fs.ln(src="/etc/apache2/mods-available/{{ module_name }}.load",
          path="/etc/apache2/mods-enabled",
          symbolic=True).notify(restart_apache)
fs.cp(path="/etc/apache2/sites-available/my-website.conf").notify(restart_apache)
fs.ln(src="/etc/apache2/sites-available/my-website.conf",
      path="/etc/apache2/sites-enabled",
      symbolic=True).notify(restart_apache)

pyinfra.systemd.service(service="apache2", running=True, enabled=True)
```

Also write the file "my-website/my-website.conf.j2" with the following contents:

    #  My uwsgi website

Why do we call the file "my-website.conf.j2"?  By default, `fs.cp()` will: use the base
name of the resulting file as the source, and add ".j2" because by default it will do
Jinja2 template expansion on the file contents.  It can also Jinja2 expand file names as
well, if doing a recursive write.

Now, if we run it:

```shell
$ sudo up my-website
=# packages(packages=['apache2', 'libapache2-mod-uwsgi'], present=True, latest=False, update=False, upgrade=False,
force=False, no_recommends=False, allow_downgrades=False)
=# ln(path=/etc/apache2/mods-enabled, src=/etc/apache2/mods-available/{{ module_name }}.load, symbolic=True)
=# ln(path=/etc/apache2/mods-enabled, src=/etc/apache2/mods-available/{{ module_name }}.load, symbolic=True)
=> cp(path=/etc/apache2/sites-available/my-website.conf, src=/tmp/my-website/my-website.conf.j2, template=True,
template_filenames=True, recursive=True) (Contents)
=> ln(path=/etc/apache2/sites-enabled, src=/etc/apache2/sites-available/my-website.conf, symbolic=True)
=# service(service=apache2, running=True, restarted=False, reloaded=False, enabled=True, daemon_reload=False,
user_mode=False)
>> *** Starting handler: restart_apache
=> service(service=apache2, running=True, restarted=True, reloaded=False, daemon_reload=False, user_mode=False)
>> *** Done with handlers

*** RECAP:  total=7 changed=3 failure=0
```

It makes sure apache2 and mod-uwsgi are installed, enables the "proxy" and "proxy-uwsgi"
modules, writes a "my-website.conf" file and symlinks it into the "sites-enabled"
directory.

## Templates

Your playbooks can include [Jinja2](https://jinja.palletsprojects.com/en/3.1.x/templates/)
template files, which are a convenient way to provide configuration files and similar.
When you `fs.cp()` files with the "template" argument set to True (the default),
the files are rendered using Jinja2, and pick up values from the uplaybook variables.

uPlaybook includes some "magic" that causes variables in your playbooks, arguments, and
[platform special variables](templating/#platform-info).

For example, if you have a "setup.conf.j2":

```
{% if platform.release_id == 'ubuntu' %}
memory_mb = {{ ((platform.memory_total / (1024 * 1024)) * 0.5) | int}}
{% endif %}
```

And your playbook has:

```python
fs.cp(src="setup.conf.j2", path="/etc/myservice/setup.conf")
```

Then on the ubuntu platform, the file will contain (on a system with 32GB of memory):

```
memory_mb = 16000
```

(or so).

## Playbook Magic

Playbooks are largely Python, but there are some conventions and customizations to make it
more suiltable for an Ansible-like use case.  Here are the things that diverge from normal
Python semantics:

### "Global" Variables

Variables set in your playbooks become available to the other playbooks and also (most
importantly) to file and argument templates.  The primary reason for this is to allow
including "settings" files:

```python
core.include(playbook="{{ environment }}")
debug(msg="This is a {{ env_type | default('development') }} environment")
```

In programming having this sort of flat name-space is discouraged, but for playbooks it
seems more ergonomic.

### Templating Arguments

Many arguments (denoted as "templatable" in the documentation) can take Jinja2 template
expressions.  This is partly a hold-over from Ansible, where you can't do "f strings" in
YAML, but also can be useful for situations like picking up default values:

```python
fs.cp(dst="{{ dirname | default('/var/lib/my_project') }}/my_project.config")
```

### Keyword Arguments

To make playbooks more clear, it's required to always use the argument keyword name:

```python
fs.cp(src="foo", dst="bar")
```

This is another hold-over from Ansible, where the YAML **requires** that you have the
argument names.  It just makes the playbooks more self-explanatory.

## Playbook Search Path

uPlaybook searches for playbooks through multiple directories (specified by the
"UP_PLAYBOOK_PATH" environment variable), which defaults to:
`.:.uplaybooks:~/.config/uplaybook:~/.config/uplaybook/library:/etc/uplaybook"`.

This allows you to have playbooks in directories that are local to that project and
available an discoverable when you are in the project, but also have per-user and
system-wide playbook as well.

When you run `up` without any arguments, it displays a list of playbooks it finds
in the search path, along with short descriptions of them.  You can then run `up
[PLAYBOOK_NAME] --help` to get more detailed information about the playbook and the
arguments it takes.

For example, I have playbooks in my "release" project which create a new release, and
archive old releases.  This makes use of templating files in the project, running git
commands, etc.  In my Ansible project, I had a playbook that creates a new "role", using
templating to set up the scaffolding.

## Playbook Documentation

Playbooks can include a docstring.  The first line of the docstring should contain a
short description of the playbook, and the remainder of the docstring should go into
further detail about the playbook.  The description is used when playbooks are listed and
the additional documentation is displayed with "--help":

For example, if you have the file "new_blog.pb":

```python
#!/usr/bin/env python3

"""Create and edit a new blog entry
Add a new blog entry, and optionally commit it to the git repo and publish it
to the blog webserver.
"""

from uplaybook import core

#  this is needed for "--help" to work
core.playbook_args()

[...]
```

You get the following output when running uPlaybook:

```bash
$ up
usage: up [--help] [--up-full-traceback] [--up-list-playbooks] [--up-debug] [--up-docs [DOCS_ARG]] [playbook]

Available playbooks:
  - new_blog.pb (.)
      Create and edit a new blog entry

$ up new_blog --help
usage: up:new_blog [-h]

Create and edit a new blog entry Add a new blog entry, and optionally commit it to the
git repo and publish it to the blog webserver.

options:
  -h, --help  show this help message and exit
```


## She-bang

uPlaybook can be run as a "script" on Unix-like OSes by adding a "she-bang" line
`#!/usr/bin/env -S python3 -m uplaybook.cli`.

    #!/usr/bin/env -S python3 -m uplaybook.cli
    [rest of playbook here]

If you `chmod 755` the playbook file, you can then directly run the playbook file as a
command.  For example if your playbook is in a file called "myplaybook", you can now run
`myplaybook` instead of `up myplaybook`.  This would primarily be used for file-based
playbooks, not directory-based, as for directory playbooks you'd need to do
`path/to/directory/playbook`; that will work it just isn't conventional.

## Include Other Playbooks


<!-- vim: set tw=90: -->
