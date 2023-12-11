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

core.playbook_args(
    core.Argument(name="module_name"),
)

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
fs.write(path="/etc/apache2/sites-available/my-website.conf").notify(restart_apache)
fs.ln(src="/etc/apache2/sites-available/my-website.conf",
      path="/etc/apache2/sites-enabled",
      symbolic=True).notify(restart_apache)

pyinfra.systemd.service(service="apache2", running=True, enabled=True)
```

Also write the file "my-website/my-website.conf.j2" with the following contents:

    #  My uwsgi website

Why do we call the file "my-website.conf.j2"?  By default, `fs.write()` will: use the base
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

## Playbook Search Path

## Playbook Documentation

## Playbook Magic

## fs.builder()

## Include Playbooks
