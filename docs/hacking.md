# Hacking uPlaybook

If you wish to develop for uPlaybook, here is some information you may find useful.

## Developing Tasks

Tasks in uPlaybook must abide by certain rules to be a good citizen.

### Saving the Calling Context

The `internals.calling_context` decorator will automatically save off the calling
context for use in templating.

Example:

```python
@task
def my_task():
    ...
```

### Template Expanding Arguments

Many arguments will benefit from being template expanded.  uPlaybook provides a helper to
handle this for you.  Use the `internals.task` decorator and use type-hints to define the
arguments which should be templated as a `TemplateStr`.

Example:

```python
from uplaybook.internals import task

@task
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
[fs.write()](tasks/fs.md#uplaybook.fs.write) task will check the destination file permissions,
template the source file and compare it's hash with the existing file, and only apply the
changes if they are meaningful.

### Argument Modification

Do not assign new values to arguments of a task.  Always copy them to a new name.  This is
because the "status" output examines the call stack to display the task call information,
and will be confusing if it picks up the modified values.

Example:

```python
def task(src):
    #  WRONG:
    src = os.path.basename(src)
    #  Right:
    final_src = os.path.basename(src)

### Secret Arguments

Arguments to a task which may contain "secret" values such as encryption keys should be
marked in the Return() object as secrets.

Example:

```python
def task(password):
    return Return(secret_args={"password"})
```

### Writing Documentation

If working on the documentation, run the following command to set up a "mkdocs"
documentation development server with live reloading:  `mkdocs serve --livereload -a
0.0.0.0:8080`

<!-- vim: set tw=90: -->
