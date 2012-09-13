"""
functools2

Provides a number of operator and higher-order functions for FP fun
"""
from operator import (
    add, concat, contains, truediv as div,
    floordiv, and_, xor
)
from functools import partial as p


def in_(item, container):
    """This mimics the signature of Haskell's `elem` function and the
Python "in" operator."""
    return contains(container, item)


# exports
__all__ = [add, concat, p, div, floordiv, in_, and_, xor]
