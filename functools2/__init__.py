"""
functools2

Provides a number of operator and higher-order functions for FP fun
"""

####
## Operators
####
from operator import (
    # arithmatic
    add, sub, mul, truediv as div, pow, mod, neg,

    # bitwise ops
    and_, xor, or_, invert, not_,

    concat, contains,

    # comparison
    lt, le, eq, ne, gt, ge
)
import operator


def quot(x, y):
    """returns the quotient after dividing the its first integral
    argument by its second integral argument"""
    return operator.floordiv(x, y)


def in_(item, container):

    """This mimics the signature of Haskell's `elem` function and the
Python "in" operator."""
    return item in container


def not_in(item, container):
    return item not in container
###
# Partials
###

from functools import partial as p


def c(f, g):
    return lambda x: f(g(x))


def const(x):
    return lambda: x


def flip(f):
    return lambda x, y: f(y, x)


def identity(x):
    return x


def get(key, obj):
    if obj is None:
        return None
    # treat set membership differently
    if hasattr(obj, "issubset") and key in obj:
        return key
    # handle lists and dicts
    try:
        return obj[key]
    except (KeyError, IndexError, TypeError):
        return None


def getter(*args):
    """Creates a function that digs into a nested data structure or returns
default if any of the keys are missing

    >>> addresses = [{"address": {"city": "Reston"}},
    ...              {"address": {"city": "Herndon"}},
    ...              {"address": {}}]
    >>>
    >>> get_city = getter("address", "city")
    >>> get_cities = p(imap, get_city)
    >>> list(get_cities(addresses))
    ["Reston", "Herndon", None]
    """
    if not args:
        return const(None)

    # start with a partial of the first key
    first = p(get, args[0])
    # if we don't have any more keys,
    # return the first partial
    if len(args) == 1:
        return first
    else:
        # if we have more keys,
        # compose get partials using the other keys
        return reduce(
            lambda f, key: c(p(get, key), f),
            args[1:], first)


###
## lazy evaluating functions
###
from itertools import (
    imap, ifilter, cycle as icycle, repeat as irepeat,
    dropwhile as idropwhile, izip
)


def iand(iterable):
    """takes the logical conjunction of a iterable of boolean values"""
    # The built-in all function does the same thing as iand
    return all(iterable)


def iall(f, iterable):
    """returns True if all elements of the list satisfy the predicate,
    and False otherwise."""
    return iand(imap(f, iterable))


def ior(iterable):
    """takes the logical disjunction of a iterable of boolean values"""
    # The built-in any function does the same thing as ior
    return any(iterable)


def iany(f, iterable):
    """returns True if any of the elements of the list satisfy the
    predicate, and False otherwise"""
    return ior(imap(f, iterable))


def iadd(iterable):
    return reduce(add, iterable)


def iconcat_map(f, iterable):
    return reduce(add, (imap(f, iterable)))


def itake(n, iterable):
    for item in iterable:
        if n > 0:
            yield item
            n = n - 1
        else:
            return


def itake_while(predicate, iterable):
    for item in iterable:
        if predicate(item):
            yield item
        else:
            return


def idrop(n, iterable):
    for item in iterable:
        if n > 0:
            n = n - 1
        else:
            yield item


def isplit_at(i, iterable):
    yield itake(i, iterable)
    yield iterable


def izip_with(f, iterable1, iterable2):
    return imap(f, iterable1, iterable2)


####
## Predicates
####
def even(x):
    return mod(x, 2) == 0


odd = c(not_, even)


def is_none(x):
    return x is None

not_none = c(not_, is_none)
