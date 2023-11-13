# Hacking uPlaybook

If you wish to develop for uPlaybook, here is some information you may find useful.

## Developing Tasks

Tasks in uPlaybook must abide by certain rules to be a good citizen.

### Saving the Calling Context

The `internals.calling_context` decorator will automatically save off the calling
context for use in templating.

Example:

```python
@calling_context
def my_task():
    ...
```

### Template Expanding Arguments

Many arguments will benefit from being template expanded.  uPlaybook provides a helper to
handle this for you.  Use the `internals.template_args` decorator (after `calling_context`
handler), and use type-hints to define the arguments which should be templated as a
`TemplateStr`.

Example:

```python
@calling_context
@template_args
def my_task(dst: TemplateStr, mode: Optional[TemplateStr] = None) -> Return:
    ...
```

### Template Return

Basically all tasks should returne a
[internals.Return](tasks/internals.md#uplaybook.internals.Return) object.  This provides
information to uPlaybook about:

- Whether the task has changed the system state.
- If the task succeeded or failed.
- Additional information such as output, exit codes, or other information related to the
  task.

### Detecting and Flagging Changes

It is a tasks responsibility to determine if the arguments to it specify the existing
system state, or if a change will be made.  For example, the
[fs.cp()](tasks/fs.md#uplaybook.fs.cp) task will check the destination file permissions,
template the source file and compare it's hash with the existing file, and only apply the
changes if they are meaningful.

### Argument Modification



### Secret Arguments

<!-- vim: set tw=90: -->
