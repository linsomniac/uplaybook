##  About pyinfra

uPlaybook wrappers of pyinfra https://docs.pyinfra.com/en/2.x/ operators.

This set of tasks provides a rich set of system management routines.
This wraps the pyinfra application.

### Global Arguments

pyinfra has global arguments that can be set via the `pyinfra_global_args`
dictionary.  [pyinfra has a full list of the global arguments](https://docs.pyinfra.com/en/2.x/arguments.html)

Example:

```python
from uplaybook import pyinfra

pyinfra.pyinfra_global_args["sudo"] = True
pyinfra.systemd.service(service="apache2", restarted=True)
```
