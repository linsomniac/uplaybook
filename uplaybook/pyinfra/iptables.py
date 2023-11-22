#!/usr/bin/env python3

"""
## iptables tasks

This module provides tasks for manipulating the system firewall.
"""

from . import _run_pyinfra, PyInfraFailed, PyInfraResults
from typing import Optional, List
from ..internals import task, TemplateStr, Return


@task
def chain(chain, present=True, table=filter, policy=None, version=4):
    """
    Add/remove/update iptables chains.

    + chain: the name of the chain
    + present: whether the chain should exist
    + table: the iptables table this chain should belong to
    + policy: the policy this table should have
    + version: whether to target iptables or ip6tables

    Policy:
        These can only be applied to system chains (FORWARD, INPUT, OUTPUT, etc).
    """
    operargs = {
        "chain": repr(chain),
        "present": repr(present),
        "table": repr(table),
        "policy": repr(policy),
        "version": repr(version),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import iptables", "iptables.chain", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def rule(
    chain,
    jump,
    present=True,
    table="filter",
    append=True,
    version=4,
    protocol=None,
    not_protocol=None,
    source=None,
    not_source=None,
    destination=None,
    not_destination=None,
    in_interface=None,
    not_in_interface=None,
    out_interface=None,
    not_out_interface=None,
    to_destination=None,
    to_source=None,
    to_ports=None,
    log_prefix=None,
    destination_port=None,
    source_port=None,
    extras="",
):
    """
    Add/remove iptables rules.

    + chain: the chain this rule should live in
    + jump: the target of the rule
    + table: the iptables table this rule should belong to
    + append: whether to append or insert the rule (if not present)
    + version: whether to target iptables or ip6tables

    Iptables args:

    + protocol/not_protocol: filter by protocol (tcp or udp)
    + source/not_source: filter by source IPs
    + destination/not_destination: filter by destination IPs
    + in_interface/not_in_interface: filter by incoming interface
    + out_interface/not_out_interface: filter by outgoing interface
    + to_destination: where to route to when jump=DNAT
    + to_source: where to route to when jump=SNAT
    + to_ports: where to route to when jump=REDIRECT
    + log_prefix: prefix for the log of this rule when jump=LOG

    Extras:

    + extras: a place to define iptables extension arguments (eg --limit, --physdev)
    + destination_port: destination port (requires protocol)
    + source_port: source port (requires protocol)

    **Examples:**

    .. code:: python

        iptables.rule(
            name="Block SSH traffic",
            chain="INPUT",
            jump="DROP",
            destination_port=22,
        )

        iptables.rule(
            name="NAT traffic on from 8.8.8.8:53 to 8.8.4.4:8080",
            chain="PREROUTING",
            jump="DNAT",
            table="nat",
            source="8.8.8.8",
            destination_port=53,
            to_destination="8.8.4.4:8080",
        )
    """
    operargs = {
        "chain": repr(chain),
        "jump": repr(jump),
        "present": repr(present),
        "table": repr(table),
        "append": repr(append),
        "version": repr(version),
        "protocol": repr(protocol),
        "not_protocol": repr(not_protocol),
        "source": repr(source),
        "not_source": repr(not_source),
        "destination": repr(destination),
        "not_destination": repr(not_destination),
        "in_interface": repr(in_interface),
        "not_in_interface": repr(not_in_interface),
        "out_interface": repr(out_interface),
        "not_out_interface": repr(not_out_interface),
        "to_destination": repr(to_destination),
        "to_source": repr(to_source),
        "to_ports": repr(to_ports),
        "log_prefix": repr(log_prefix),
        "destination_port": repr(destination_port),
        "source_port": repr(source_port),
        "extras": repr(extras),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import iptables", "iptables.rule", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)
