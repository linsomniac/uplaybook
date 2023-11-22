#!/usr/bin/env python3

"""
## Mysql tasks

This module provides tasks for working with mysql databases.
"""

from . import _run_pyinfra, PyInfraFailed, PyInfraResults
from typing import Optional, List
from ..internals import task, TemplateStr, Return


@task
def sql(
    sql,
    database=None,
    mysql_user=None,
    mysql_password=None,
    mysql_host=None,
    mysql_port=None,
):
    """
    Execute arbitrary SQL against MySQL.

    + sql: SQL command(s) to execute
    + database: optional database to open the connection with
    + mysql_*: global module arguments, see above
    """
    operargs = {
        "sql": repr(sql),
        "database": repr(database),
        "mysql_user": repr(mysql_user),
        "mysql_password": repr(mysql_password),
        "mysql_host": repr(mysql_host),
        "mysql_port": repr(mysql_port),
    }

    result = _run_pyinfra("from pyinfra.operations import mysql", "mysql.sql", operargs)

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def user(
    user,
    present=True,
    user_hostname="localhost",
    password=None,
    privileges=None,
    require=None,
    require_cipher=False,
    require_issuer=False,
    require_subject=False,
    max_connections=None,
    max_queries_per_hour=None,
    max_updates_per_hour=None,
    max_connections_per_hour=None,
    mysql_user=None,
    mysql_password=None,
    mysql_host=None,
    mysql_port=None,
):
    """
    Add/remove/update MySQL users.

    + user: the name of the user
    + present: whether the user should exist or not
    + user_hostname: the hostname of the user
    + password: the password of the user (if created)
    + privileges: the global privileges for this user
    + mysql_*: global module arguments, see above

    Hostname:
        this + ``name`` makes the username - so changing this will create a new
        user, rather than update users with the same ``name``.

    Password:
        will only be applied if the user does not exist - ie pyinfra cannot
        detect if the current password doesn't match the one provided, so won't
        attempt to change it.

    **Example:**

    .. code:: python

        mysql.user(
            name="Create the pyinfra@localhost MySQL user",
            user="pyinfra",
            password="somepassword",
        )

        # Create a user with resource limits
        mysql.user(
            name="Create the pyinfra@localhost MySQL user",
            user="pyinfra",
            max_connections=50,
            max_updates_per_hour=10,
        )

        # Create a user that requires SSL for connections
        mysql.user(
            name="Create the pyinfra@localhost MySQL user",
            user="pyinfra",
            password="somepassword",
            require="SSL",
        )

        # Create a user that requires a specific certificate
        mysql.user(
            name="Create the pyinfra@localhost MySQL user",
            user="pyinfra",
            password="somepassword",
            require="X509",
            require_issuer="/C=SE/ST=Stockholm...",
            require_cipher="EDH-RSA-DES-CBC3-SHA",
        )
    """
    operargs = {
        "user": repr(user),
        "present": repr(present),
        "user_hostname": repr(user_hostname),
        "password": repr(password),
        "privileges": repr(privileges),
        "require": repr(require),
        "require_cipher": repr(require_cipher),
        "require_issuer": repr(require_issuer),
        "require_subject": repr(require_subject),
        "max_connections": repr(max_connections),
        "max_queries_per_hour": repr(max_queries_per_hour),
        "max_updates_per_hour": repr(max_updates_per_hour),
        "max_connections_per_hour": repr(max_connections_per_hour),
        "mysql_user": repr(mysql_user),
        "mysql_password": repr(mysql_password),
        "mysql_host": repr(mysql_host),
        "mysql_port": repr(mysql_port),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import mysql", "mysql.user", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def database(
    database,
    present=True,
    collate=None,
    charset=None,
    user=None,
    user_hostname="localhost",
    user_privileges="ALL",
    mysql_user=None,
    mysql_password=None,
    mysql_host=None,
    mysql_port=None,
):
    """
    Add/remove MySQL databases.

    + name: the name of the database
    + present: whether the database should exist or not
    + collate: the collate to use when creating the database
    + charset: the charset to use when creating the database
    + user: MySQL user to grant privileges on this database to
    + user_hostname: the hostname of the MySQL user to grant
    + user_privileges: privileges to grant to any specified user
    + mysql_*: global module arguments, see above

    Collate/charset:
        these will only be applied if the database does not exist - ie pyinfra
        will not attempt to alter the existing databases collate/character sets.

    **Example:**

    .. code:: python

        mysql.database(
            name="Create the pyinfra_stuff database",
            database="pyinfra_stuff",
            user="pyinfra",
            user_privileges=["SELECT", "INSERT"],
            charset="utf8",
        )
    """
    operargs = {
        "database": repr(database),
        "present": repr(present),
        "collate": repr(collate),
        "charset": repr(charset),
        "user": repr(user),
        "user_hostname": repr(user_hostname),
        "user_privileges": repr(user_privileges),
        "mysql_user": repr(mysql_user),
        "mysql_password": repr(mysql_password),
        "mysql_host": repr(mysql_host),
        "mysql_port": repr(mysql_port),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import mysql", "mysql.database", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def privileges(
    user,
    privileges,
    user_hostname="localhost",
    database="*",
    table="*",
    flush=True,
    with_grant_option=False,
    mysql_user=None,
    mysql_password=None,
    mysql_host=None,
    mysql_port=None,
):
    """
    Add/remove MySQL privileges for a user, either global, database or table specific.

    + user: name of the user to manage privileges for
    + privileges: list of privileges the user should have (see also: ``with_grant_option`` argument)
    + user_hostname: the hostname of the user
    + database: name of the database to grant privileges to (defaults to all)
    + table: name of the table to grant privileges to (defaults to all)
    + flush: whether to flush (and update) the privileges table after any changes
    + with_grant_option: whether the grant option privilege should be set
    + mysql_*: global module arguments, see above
    """
    operargs = {
        "user": repr(user),
        "privileges": repr(privileges),
        "user_hostname": repr(user_hostname),
        "database": repr(database),
        "table": repr(table),
        "flush": repr(flush),
        "with_grant_option": repr(with_grant_option),
        "mysql_user": repr(mysql_user),
        "mysql_password": repr(mysql_password),
        "mysql_host": repr(mysql_host),
        "mysql_port": repr(mysql_port),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import mysql", "mysql.privileges", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def dump(
    dest,
    database=None,
    mysql_user=None,
    mysql_password=None,
    mysql_host=None,
    mysql_port=None,
):
    """
    Dump a MySQL database into a ``.sql`` file. Requires ``mysqldump``.

    + dest: name of the file to dump the SQL to
    + database: name of the database to dump
    + mysql_*: global module arguments, see above

    **Example:**

    .. code:: python

        mysql.dump(
            name="Dump the pyinfra_stuff database",
            dest="/tmp/pyinfra_stuff.dump",
            database="pyinfra_stuff",
        )
    """
    operargs = {
        "dest": repr(dest),
        "database": repr(database),
        "mysql_user": repr(mysql_user),
        "mysql_password": repr(mysql_password),
        "mysql_host": repr(mysql_host),
        "mysql_port": repr(mysql_port),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import mysql", "mysql.dump", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def load(
    src,
    database=None,
    mysql_user=None,
    mysql_password=None,
    mysql_host=None,
    mysql_port=None,
):
    """
    Load ``.sql`` file into a database.

    + src: the filename to read from
    + database: name of the database to import into
    + mysql_*: global module arguments, see above

    **Example:**

    .. code:: python

        mysql.load(
            name="Import the pyinfra_stuff dump into pyinfra_stuff_copy",
            src="/tmp/pyinfra_stuff.dump",
            database="pyinfra_stuff_copy",
        )
    """
    operargs = {
        "src": repr(src),
        "database": repr(database),
        "mysql_user": repr(mysql_user),
        "mysql_password": repr(mysql_password),
        "mysql_host": repr(mysql_host),
        "mysql_port": repr(mysql_port),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import mysql", "mysql.load", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def handle_privileges(action, target, privileges_to_apply, with_statement=None):
    operargs = {
        "action": repr(action),
        "target": repr(target),
        "privileges_to_apply": repr(privileges_to_apply),
        "with_statement": repr(with_statement),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import mysql", "mysql.handle_privileges", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def sql(
    sql,
    database=None,
    mysql_user=None,
    mysql_password=None,
    mysql_host=None,
    mysql_port=None,
):
    """
    Execute arbitrary SQL against MySQL.

    + sql: SQL command(s) to execute
    + database: optional database to open the connection with
    + mysql_*: global module arguments, see above
    """
    operargs = {
        "sql": repr(sql),
        "database": repr(database),
        "mysql_user": repr(mysql_user),
        "mysql_password": repr(mysql_password),
        "mysql_host": repr(mysql_host),
        "mysql_port": repr(mysql_port),
    }

    result = _run_pyinfra("from pyinfra.operations import mysql", "mysql.sql", operargs)

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def user(
    user,
    present=True,
    user_hostname="localhost",
    password=None,
    privileges=None,
    require=None,
    require_cipher=False,
    require_issuer=False,
    require_subject=False,
    max_connections=None,
    max_queries_per_hour=None,
    max_updates_per_hour=None,
    max_connections_per_hour=None,
    mysql_user=None,
    mysql_password=None,
    mysql_host=None,
    mysql_port=None,
):
    """
    Add/remove/update MySQL users.

    + user: the name of the user
    + present: whether the user should exist or not
    + user_hostname: the hostname of the user
    + password: the password of the user (if created)
    + privileges: the global privileges for this user
    + mysql_*: global module arguments, see above

    Hostname:
        this + ``name`` makes the username - so changing this will create a new
        user, rather than update users with the same ``name``.

    Password:
        will only be applied if the user does not exist - ie pyinfra cannot
        detect if the current password doesn't match the one provided, so won't
        attempt to change it.

    **Example:**

    .. code:: python

        mysql.user(
            name="Create the pyinfra@localhost MySQL user",
            user="pyinfra",
            password="somepassword",
        )

        # Create a user with resource limits
        mysql.user(
            name="Create the pyinfra@localhost MySQL user",
            user="pyinfra",
            max_connections=50,
            max_updates_per_hour=10,
        )

        # Create a user that requires SSL for connections
        mysql.user(
            name="Create the pyinfra@localhost MySQL user",
            user="pyinfra",
            password="somepassword",
            require="SSL",
        )

        # Create a user that requires a specific certificate
        mysql.user(
            name="Create the pyinfra@localhost MySQL user",
            user="pyinfra",
            password="somepassword",
            require="X509",
            require_issuer="/C=SE/ST=Stockholm...",
            require_cipher="EDH-RSA-DES-CBC3-SHA",
        )
    """
    operargs = {
        "user": repr(user),
        "present": repr(present),
        "user_hostname": repr(user_hostname),
        "password": repr(password),
        "privileges": repr(privileges),
        "require": repr(require),
        "require_cipher": repr(require_cipher),
        "require_issuer": repr(require_issuer),
        "require_subject": repr(require_subject),
        "max_connections": repr(max_connections),
        "max_queries_per_hour": repr(max_queries_per_hour),
        "max_updates_per_hour": repr(max_updates_per_hour),
        "max_connections_per_hour": repr(max_connections_per_hour),
        "mysql_user": repr(mysql_user),
        "mysql_password": repr(mysql_password),
        "mysql_host": repr(mysql_host),
        "mysql_port": repr(mysql_port),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import mysql", "mysql.user", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def database(
    database,
    present=True,
    collate=None,
    charset=None,
    user=None,
    user_hostname="localhost",
    user_privileges="ALL",
    mysql_user=None,
    mysql_password=None,
    mysql_host=None,
    mysql_port=None,
):
    """
    Add/remove MySQL databases.

    + name: the name of the database
    + present: whether the database should exist or not
    + collate: the collate to use when creating the database
    + charset: the charset to use when creating the database
    + user: MySQL user to grant privileges on this database to
    + user_hostname: the hostname of the MySQL user to grant
    + user_privileges: privileges to grant to any specified user
    + mysql_*: global module arguments, see above

    Collate/charset:
        these will only be applied if the database does not exist - ie pyinfra
        will not attempt to alter the existing databases collate/character sets.

    **Example:**

    .. code:: python

        mysql.database(
            name="Create the pyinfra_stuff database",
            database="pyinfra_stuff",
            user="pyinfra",
            user_privileges=["SELECT", "INSERT"],
            charset="utf8",
        )
    """
    operargs = {
        "database": repr(database),
        "present": repr(present),
        "collate": repr(collate),
        "charset": repr(charset),
        "user": repr(user),
        "user_hostname": repr(user_hostname),
        "user_privileges": repr(user_privileges),
        "mysql_user": repr(mysql_user),
        "mysql_password": repr(mysql_password),
        "mysql_host": repr(mysql_host),
        "mysql_port": repr(mysql_port),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import mysql", "mysql.database", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def privileges(
    user,
    privileges,
    user_hostname="localhost",
    database="*",
    table="*",
    flush=True,
    with_grant_option=False,
    mysql_user=None,
    mysql_password=None,
    mysql_host=None,
    mysql_port=None,
):
    """
    Add/remove MySQL privileges for a user, either global, database or table specific.

    + user: name of the user to manage privileges for
    + privileges: list of privileges the user should have (see also: ``with_grant_option`` argument)
    + user_hostname: the hostname of the user
    + database: name of the database to grant privileges to (defaults to all)
    + table: name of the table to grant privileges to (defaults to all)
    + flush: whether to flush (and update) the privileges table after any changes
    + with_grant_option: whether the grant option privilege should be set
    + mysql_*: global module arguments, see above
    """
    operargs = {
        "user": repr(user),
        "privileges": repr(privileges),
        "user_hostname": repr(user_hostname),
        "database": repr(database),
        "table": repr(table),
        "flush": repr(flush),
        "with_grant_option": repr(with_grant_option),
        "mysql_user": repr(mysql_user),
        "mysql_password": repr(mysql_password),
        "mysql_host": repr(mysql_host),
        "mysql_port": repr(mysql_port),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import mysql", "mysql.privileges", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def dump(
    dest,
    database=None,
    mysql_user=None,
    mysql_password=None,
    mysql_host=None,
    mysql_port=None,
):
    """
    Dump a MySQL database into a ``.sql`` file. Requires ``mysqldump``.

    + dest: name of the file to dump the SQL to
    + database: name of the database to dump
    + mysql_*: global module arguments, see above

    **Example:**

    .. code:: python

        mysql.dump(
            name="Dump the pyinfra_stuff database",
            dest="/tmp/pyinfra_stuff.dump",
            database="pyinfra_stuff",
        )
    """
    operargs = {
        "dest": repr(dest),
        "database": repr(database),
        "mysql_user": repr(mysql_user),
        "mysql_password": repr(mysql_password),
        "mysql_host": repr(mysql_host),
        "mysql_port": repr(mysql_port),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import mysql", "mysql.dump", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def load(
    src,
    database=None,
    mysql_user=None,
    mysql_password=None,
    mysql_host=None,
    mysql_port=None,
):
    """
    Load ``.sql`` file into a database.

    + src: the filename to read from
    + database: name of the database to import into
    + mysql_*: global module arguments, see above

    **Example:**

    .. code:: python

        mysql.load(
            name="Import the pyinfra_stuff dump into pyinfra_stuff_copy",
            src="/tmp/pyinfra_stuff.dump",
            database="pyinfra_stuff_copy",
        )
    """
    operargs = {
        "src": repr(src),
        "database": repr(database),
        "mysql_user": repr(mysql_user),
        "mysql_password": repr(mysql_password),
        "mysql_host": repr(mysql_host),
        "mysql_port": repr(mysql_port),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import mysql", "mysql.load", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def handle_privileges(action, target, privileges_to_apply, with_statement=None):
    operargs = {
        "action": repr(action),
        "target": repr(target),
        "privileges_to_apply": repr(privileges_to_apply),
        "with_statement": repr(with_statement),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import mysql", "mysql.handle_privileges", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)
