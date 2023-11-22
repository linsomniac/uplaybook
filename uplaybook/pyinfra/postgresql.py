#!/usr/bin/env python3

"""
## Postgresql Database tasks

This module provides tasks for working with PostgreSQL databases.
"""

from . import _run_pyinfra, PyInfraFailed, PyInfraResults
from typing import Optional, List
from ..internals import task, TemplateStr, Return


@task
def _translate_legacy_args(func):
    operargs = {
        "func": repr(func),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import postgresql",
        "postgresql._translate_legacy_args",
        operargs,
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def sql(
    sql,
    database=None,
    psql_user=None,
    psql_password=None,
    psql_host=None,
    psql_port=None,
):
    """
    Execute arbitrary SQL against PostgreSQL.

    + sql: SQL command(s) to execute
    + database: optional database to execute against
    + psql_*: global module arguments, see above
    """
    operargs = {
        "sql": repr(sql),
        "database": repr(database),
        "psql_user": repr(psql_user),
        "psql_password": repr(psql_password),
        "psql_host": repr(psql_host),
        "psql_port": repr(psql_port),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import postgresql", "postgresql.sql", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def role(
    role,
    present=True,
    password=None,
    login=True,
    superuser=False,
    inherit=False,
    createdb=False,
    createrole=False,
    replication=False,
    connection_limit=None,
    psql_user=None,
    psql_password=None,
    psql_host=None,
    psql_port=None,
):
    """
    Add/remove PostgreSQL roles.

    + role: name of the role
    + present: whether the role should be present or absent
    + password: the password for the role
    + login: whether the role can login
    + superuser: whether role will be a superuser
    + inherit: whether the role inherits from other roles
    + createdb: whether the role is allowed to create databases
    + createrole: whether the role is allowed to create new roles
    + replication: whether this role is allowed to replicate
    + connection_limit: the connection limit for the role
    + psql_*: global module arguments, see above

    Updates:
        pyinfra will not attempt to change existing roles - it will either
        create or drop roles, but not alter them (if the role exists this
        operation will make no changes).

    **Example:**

    .. code:: python

        postgresql.role(
            name="Create the pyinfra PostgreSQL role",
            role="pyinfra",
            password="somepassword",
            superuser=True,
            login=True,
            sudo_user="postgres",
        )
    """
    operargs = {
        "role": repr(role),
        "present": repr(present),
        "password": repr(password),
        "login": repr(login),
        "superuser": repr(superuser),
        "inherit": repr(inherit),
        "createdb": repr(createdb),
        "createrole": repr(createrole),
        "replication": repr(replication),
        "connection_limit": repr(connection_limit),
        "psql_user": repr(psql_user),
        "psql_password": repr(psql_password),
        "psql_host": repr(psql_host),
        "psql_port": repr(psql_port),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import postgresql", "postgresql.role", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def database(
    database,
    present=True,
    owner=None,
    template=None,
    encoding=None,
    lc_collate=None,
    lc_ctype=None,
    tablespace=None,
    connection_limit=None,
    psql_user=None,
    psql_password=None,
    psql_host=None,
    psql_port=None,
):
    """
    Add/remove PostgreSQL databases.

    + name: name of the database
    + present: whether the database should exist or not
    + owner: the PostgreSQL role that owns the database
    + template: name of the PostgreSQL template to use
    + encoding: encoding of the database
    + lc_collate: lc_collate of the database
    + lc_ctype: lc_ctype of the database
    + tablespace: the tablespace to use for the template
    + connection_limit: the connection limit to apply to the database
    + psql_*: global module arguments, see above

    Updates:
        pyinfra will not attempt to change existing databases - it will either
        create or drop databases, but not alter them (if the db exists this
        operation will make no changes).

    **Example:**

    .. code:: python

        postgresql.database(
            name="Create the pyinfra_stuff database",
            database="pyinfra_stuff",
            owner="pyinfra",
            encoding="UTF8",
            sudo_user="postgres",
        )
    """
    operargs = {
        "database": repr(database),
        "present": repr(present),
        "owner": repr(owner),
        "template": repr(template),
        "encoding": repr(encoding),
        "lc_collate": repr(lc_collate),
        "lc_ctype": repr(lc_ctype),
        "tablespace": repr(tablespace),
        "connection_limit": repr(connection_limit),
        "psql_user": repr(psql_user),
        "psql_password": repr(psql_password),
        "psql_host": repr(psql_host),
        "psql_port": repr(psql_port),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import postgresql", "postgresql.database", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def dump(
    dest,
    database=None,
    psql_user=None,
    psql_password=None,
    psql_host=None,
    psql_port=None,
):
    """
    Dump a PostgreSQL database into a ``.sql`` file. Requires ``pg_dump``.

    + dest: name of the file to dump the SQL to
    + database: name of the database to dump
    + psql_*: global module arguments, see above

    **Example:**

    .. code:: python

        postgresql.dump(
            name="Dump the pyinfra_stuff database",
            dest="/tmp/pyinfra_stuff.dump",
            database="pyinfra_stuff",
            sudo_user="postgres",
        )
    """
    operargs = {
        "dest": repr(dest),
        "database": repr(database),
        "psql_user": repr(psql_user),
        "psql_password": repr(psql_password),
        "psql_host": repr(psql_host),
        "psql_port": repr(psql_port),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import postgresql", "postgresql.dump", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def load(
    src,
    database=None,
    psql_user=None,
    psql_password=None,
    psql_host=None,
    psql_port=None,
):
    """
    Load ``.sql`` file into a database.

    + src: the filename to read from
    + database: name of the database to import into
    + psql_*: global module arguments, see above

    **Example:**

    .. code:: python

        postgresql.load(
            name="Import the pyinfra_stuff dump into pyinfra_stuff_copy",
            src="/tmp/pyinfra_stuff.dump",
            database="pyinfra_stuff_copy",
            sudo_user="postgres",
        )
    """
    operargs = {
        "src": repr(src),
        "database": repr(database),
        "psql_user": repr(psql_user),
        "psql_password": repr(psql_password),
        "psql_host": repr(psql_host),
        "psql_port": repr(psql_port),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import postgresql", "postgresql.load", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def decorated_func(*args, **kwargs):
    operargs = {}

    result = _run_pyinfra(
        "from pyinfra.operations import postgresql",
        "postgresql.decorated_func",
        operargs,
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)
