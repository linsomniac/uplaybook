# What is a Playbook

There are two types of playbooks:

## Simple Playbooks

These are a file with a name ending in ".pb", for example `new-project.pb`.  This is a
good choice for a playbook that has no additional data associated with it, such as
templates, configuration files, data, or dependent playbooks.  Just a single file.

## Directory Playbooks

These are a directory with a `playbook` file within it.  For example
`new-project/playbook`.

This is a good choice for more complex plays, things which have file templates or other
data.  For example, in a playbook if you `cp(src="bashrc.j2", path="{{homedir}}/.bashrc")`,
it will look for the `bashrc.j2` file in the playbook directory.  In this way you can
contain all the associated data along side the playbook.

<!-- vim: set tw=90: -->
