#!/usr/bin/env python3

"""
## Git tasks

This module provides tasks for interfacing with git version control.
"""

from . import _run_pyinfra, PyInfraFailed, PyInfraResults
from typing import Optional, List
from ..internals import task, TemplateStr, Return


@task
def config(key, value, multi_value=False, repo=None):
    """
    Manage git config for a repository or globally.

    + key: the key of the config to ensure
    + value: the value this key should have
    + multi_value: Add the value rather than set it for settings that can have multiple values
    + repo: specify the git repo path to edit local config (defaults to global)

    **Example:**

    .. code:: python

        git.config(
            name="Ensure user name is set for a repo",
            key="user.name",
            value="Anon E. Mouse",
            repo="/usr/local/src/pyinfra",
        )
    """
    operargs = {
        "key": repr(key),
        "value": repr(value),
        "multi_value": repr(multi_value),
        "repo": repr(repo),
    }

    result = _run_pyinfra("from pyinfra.operations import git", "git.config", operargs)

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def repo(
    src,
    dest,
    branch=None,
    pull=True,
    rebase=False,
    user=None,
    group=None,
    ssh_keyscan=False,
    update_submodules=False,
    recursive_submodules=False,
):
    """
    Clone/pull git repositories.

    + src: the git source URL
    + dest: directory to clone to
    + branch: branch to pull/checkout
    + pull: pull any changes for the branch
    + rebase: when pulling, use ``--rebase``
    + user: chown files to this user after
    + group: chown files to this group after
    + ssh_keyscan: keyscan the remote host if not in known_hosts before clone/pull
    + update_submodules: update any git submodules
    + recursive_submodules: update git submodules recursively

    **Example:**

    .. code:: python

        git.repo(
            name="Clone repo",
            src="https://github.com/Fizzadar/pyinfra.git",
            dest="/usr/local/src/pyinfra",
        )
    """
    operargs = {
        "src": repr(src),
        "dest": repr(dest),
        "branch": repr(branch),
        "pull": repr(pull),
        "rebase": repr(rebase),
        "user": repr(user),
        "group": repr(group),
        "ssh_keyscan": repr(ssh_keyscan),
        "update_submodules": repr(update_submodules),
        "recursive_submodules": repr(recursive_submodules),
    }

    result = _run_pyinfra("from pyinfra.operations import git", "git.repo", operargs)

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def worktree(
    worktree,
    repo=None,
    detached=False,
    new_branch=None,
    commitish=None,
    pull=True,
    rebase=False,
    from_remote_branch=None,
    present=True,
    assume_repo_exists=False,
    force=False,
    user=None,
    group=None,
):
    """
    Manage git worktrees.

    + worktree: git working tree directory
    + repo: git main repository directory
    + detached: create a working tree with a detached HEAD
    + new_branch: local branch name created at the same time than the worktree
    + commitish: from which git commit, branch, ... the worktree is created
    + pull: pull any changes from a remote branch if set
    + rebase: when pulling, use ``--rebase``
    + from_remote_branch: a 2-tuple ``(remote, branch)`` that identifies a remote branch
    + present: whether the working tree should exist
    + assume_repo_exists: whether to assume the main repo exists
    + force: remove unclean working tree if should not exist
    + user: chown files to this user after
    + group: chown files to this group after

    **Examples:**

    .. code:: python

        git.worktree(
            name="Create a worktree from the current repo `HEAD`",
            repo="/usr/local/src/pyinfra/master",
            worktree="/usr/local/src/pyinfra/hotfix"
        )

        git.worktree(
            name="Create a worktree from the commit `4e091aa0`",
            repo="/usr/local/src/pyinfra/master",
            worktree="/usr/local/src/pyinfra/hotfix",
            commitish="4e091aa0"
        )

        git.worktree(
            name="Create a worktree with a new local branch `v1.0`",
            repo="/usr/local/src/pyinfra/master",
            worktree="/usr/local/src/pyinfra/hotfix",
            new_branch="v1.0",
        )

        git.worktree(
            name="Create a worktree from the commit 4e091aa0 with the new local branch `v1.0`",
            repo="/usr/local/src/pyinfra/master",
            worktree="/usr/local/src/pyinfra/hotfix",
            new_branch="v1.0",
            commitish="4e091aa0"
        )

        git.worktree(
            name="Create a worktree with a detached `HEAD`",
            repo="/usr/local/src/pyinfra/master",
            worktree="/usr/local/src/pyinfra/hotfix",
            detached=True,
        )

        git.worktree(
            name="Create a worktree with a detached `HEAD` from commit `4e091aa0`",
            repo="/usr/local/src/pyinfra/master",
            worktree="/usr/local/src/pyinfra/hotfix",
            commitish="4e091aa0",
            detached=True,
        )

        git.worktree(
            name="Create a worktree from the existing local branch `v1.0`",
            repo="/usr/local/src/pyinfra/master",
            worktree="/usr/local/src/pyinfra/hotfix",
            commitish="v1.0"
        )

        git.worktree(
            name="Create a worktree with a new branch `v1.0` that tracks `origin/v1.0`",
            repo="/usr/local/src/pyinfra/master",
            worktree="/usr/local/src/pyinfra/hotfix",
            new_branch="v1.0",
            commitish="v1.0"
        )

        git.worktree(
            name="Pull an existing worktree already linked to a tracking branch",
            repo="/usr/local/src/pyinfra/master",
            worktree="/usr/local/src/pyinfra/hotfix"
        )

        git.worktree(
            name="Pull an existing worktree from a specific remote branch",
            repo="/usr/local/src/pyinfra/master",
            worktree="/usr/local/src/pyinfra/hotfix",
            from_remote_branch=("origin", "master")
        )

        git.worktree(
            name="Remove a worktree",
            worktree="/usr/local/src/pyinfra/hotfix",
            present=False,
        )

        git.worktree(
            name="Remove an unclean worktree",
            worktree="/usr/local/src/pyinfra/hotfix",
            present=False,
            force=True,
        )
    """
    operargs = {
        "worktree": repr(worktree),
        "repo": repr(repo),
        "detached": repr(detached),
        "new_branch": repr(new_branch),
        "commitish": repr(commitish),
        "pull": repr(pull),
        "rebase": repr(rebase),
        "from_remote_branch": repr(from_remote_branch),
        "present": repr(present),
        "assume_repo_exists": repr(assume_repo_exists),
        "force": repr(force),
        "user": repr(user),
        "group": repr(group),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import git", "git.worktree", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)


@task
def bare_repo(path, user=None, group=None, present=True):
    """
    Create bare git repositories.

    + path: path to the folder
    + present: whether the bare repository should exist
    + user: chown files to this user after
    + group: chown files to this group after

    **Example:**

    .. code:: python

        git.bare_repo(
            name="Create bare repo",
            path="/home/git/test.git",
        )
    """
    operargs = {
        "path": repr(path),
        "user": repr(user),
        "group": repr(group),
        "present": repr(present),
    }

    result = _run_pyinfra(
        "from pyinfra.operations import git", "git.bare_repo", operargs
    )

    if result.errors:
        return Return(failure=True)
    return Return(changed=result.changed != 0)
