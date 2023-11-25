# uPlaybook for Ansible Users

If you are an Ansible user here are some things to help bring you up to speed.

## Forklifting Variables

uPlaybook does some magic so that variables set in your Python code become available in
the context for use in templating.  This is how the looping example works, `item` gets
forklifted into the Jinja2 context.

## with_items / loop

Looping with uPlaybook is done via a Python `for` loop.  However, you want to use the
[core.Item()](tasks/core.md#uplaybook.core.Item> helper to define each item.

In Ansible:

```yaml
---
- name: Config files
  template:
    src: "{{ item.src }}"
    dest: "{{ item.dest }}"
  with_items:
    - src: foo.cfg.j2
      dest: /etc/foo/foo.cfg
    - src: bar.cfg.j2
      dest: /etc/foo/bar.cfg
```

Would be the following in uPlaybook:

```python
for item in [
        core.Item(src="foo.cfg.j2", path="/etc/foo/foo.cfg"),
        core.Item(src="bar.cfg.j2", path="/etc/foo/bar.cfg"),
        ]:
    fs.cp(**item)
    #  or:
    fs.cp(src=item.src, path=item.dst)
    #  or:
    fs.cp(src="{{item.src}}", path="{{item.dst}}")
```

The `**item` syntax applies the attributes from `item` as if they are arguments to the
function.

## Common File Arguments

Many tasks in Ansible take these common arguments: owner, group, mode.  uPlaybook provides
the [fs.builder()](tasks/fs.md#uplaybook.fs.builder) meta-task to do simiar functionality.

Example:

for item in [
        core.Item(path="dest", action="directory"),
        core.Item(src="foo", path="dest/foo", owner="root"),
        core.Item(src="bar", path="dest/bar", owner="root"),
        core.Item(path="dest/user-config", group="nobody", mode="a=rX", action="exists"),
        core.Item(path="dest/legacy-file", action="absent"),
        ]:
    fs.builder(**items)

<!-- vim: set tw=90: -->
