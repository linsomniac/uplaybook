#!/usr/bin/env python3

from . import internals
from . import fs

up_context = internals.up_context


class IgnoreFailure:
    """A context-manager to ignore failures in wrapped tasks"""

    def __enter__(self):
        up_context.ignore_failure_count += 1
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        up_context.ignore_failure_count -= 1
        assert up_context.ignore_failure_count >= 0
