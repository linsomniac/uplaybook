# Including Sub-Playbooks

## Overview

Playbooks can include other playbooks, and are found by looking in the directory the
playbook was in.  This can be used for setting common code or values used by multiple
playbooks.

## Hoisting Variables

Variables defined in them are, by default, "hoisted" up to the main playbook.  This can
be used to set variables based on platform information.  For example:

```python
#  This includes a playbook called "vars-Linux.pb" on Linux machines
core.include(playbook="vars-{{platform.system}}.pb")
core.debug(msg="Username loaded from vars: {{username}}")
```

To override this hoisting, set `hoist_vars=False` in the call:

```python
include(playbook="common-tasks.pb", hoist_vars=False)
```

<!-- vim: set tw=90: -->
