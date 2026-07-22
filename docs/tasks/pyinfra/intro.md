##  About pyinfra

uPlaybook wrappers of pyinfra https://docs.pyinfra.com/en/3.x/ operators.

This set of tasks provides a rich set of system management routines.
This wraps the pyinfra application.

### Global Arguments

pyinfra has global arguments that can be set via the `pyinfra_global_args`
dictionary.  [pyinfra has a full list of the global arguments](https://docs.pyinfra.com/en/3.x/arguments.html)

Example:

```python
from uplaybook import pyinfra

pyinfra.pyinfra_global_args["sudo"] = True
pyinfra.systemd.service(service="apache2", restarted=True)
```

## pyinfra 3 compatibility

uPlaybook requires pyinfra 3.9.2 or newer. Parameters removed by pyinfra 3 remain in
uPlaybook's task signatures where a compatible default can be preserved. The former
`assume_present=True` file-operation behavior and `server.user(add_deploy_dir=False)` are
no longer available and raise a descriptive error.

pyinfra 3.9 declares Paramiko 4 as its supported dependency. Some downstream packages,
including the tested Nix build, provide Paramiko 5; uPlaybook does not call Paramiko
directly and its local pyinfra integration test also passes with that combination.
