#!/usr/bin/env python3

"""
A Python-like declarative IT automation tool.

uPlaybook2 takes ideas from Ansible and Cookiecutter and gives it a
Python syntax rather than YAML. The desired state of the system is
specified via this "playbook" and associated templates and data. You
can then run this playbook, providing additional arguments for this run.

More documentation is available at: https://github.com/linsomniac/uplaybook2
"""

from . import internals
from . import fs
from . import core

up_context = internals.up_context
ARGS = up_context.context["ARGS"]
