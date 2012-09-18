"""
functools2

Provides a number of operator and higher-order functions for FP fun
"""

####
# atoms
####
undefined = object()

####
## Operators
####
import sys
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


def case(*rules):
    # If the args has a length of one, args[0] is an iterator
    if len(rules) == 1:
        rules = rules[0]

    def inner(*args, **kwargs):
        for pred, f in rules:
            if pred is True:
                return f(*args, **kwargs)
            elif pred(*args, **kwargs):
                return f(*args, **kwargs)
        return None
    return inner


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


def pp(f, *args0, **kwargs0):
    """Creates a partial where arguments are prepended to the partial
args"""

    def inner(*args1, **kwargs1):
        args = args1 + args0
        kwargs = dict(kwargs0, **kwargs1)
        return f(*args, **kwargs)
    return inner


def c(f, g):
    return lambda x: f(g(x))


def t(fs):
    """Creates a threaded function call

    Where compose is right associative

    >>> c(p(mul, 2), p(add, 3))(2)
    10

    The thread partial is left associative

    >>> t([p(add, 3), p(mul, 2)])(2)
    10

    """
    head = ifirst(fs)
    tail = irest(fs)

    return reduce(
        lambda composed, f: c(f, composed),
        tail, head)


def const(x):
    return lambda *args, **kwargs: x


def flip(f):
    return lambda x, y: f(y, x)


def identity(x):
    return x


def binfunc(f):
    """turns a binary function into an unary function which takes a pair

    >>> points = [(1,2), (110, 320)]
    >>> getx = binfunc(lambda x,y: x)
    >>> gety = binfunc(lambda x,y: y)

    >>> list(imap(getx, points))
    [1, 110]

    >>> list(imap(gety, points))
    [2, 320]
    """
    def inner(pair):
        x,y = pair
        return f(x,y)
    return inner


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
    # thread a list of get(key, obj) calls
    get_functions = [p(get, key) for key in args]
    return t(get_functions)


def kwunary(func, *keys):
    if keys:
        def inner(dct):
            kwargs = {k:dct[k] for k in keys}
            return func(**kwargs)
    else:
        def inner(dct):
            return func(**dct)
    return inner

###
## generators
###
from itertools import (
    izip,
    izip_longest,
    imap,
    ifilter,
    islice,
    cycle as icycle,
    repeat as irepeat,
    dropwhile as idropwhile,
    takewhile as itakewhile,
    compress as icompress,
)
import itertools


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


def itake(n, iterable):
    return islice(iterable, n)


def ifirst(iterable):
    return iter(iterable).next()


def irest(iterable):
    return idrop(1, iterable)


def idrop(n, iterable):
    return itertools.islice(iterable, n, None)


def isplit_at(i, iterable):
    yield itake(i, iterable)
    yield iterable


def izip_with(f, iterable1, iterable2):
    return imap(f, iterable1, iterable2)


def ichain(iterables):
    return itertools.chain.from_iterable(iterables)


def igroupby(keyfunc, iterable):
    return itertools.groupby(iterable, keyfunc)


def ichunk(size, iterable, fillvalue=undefined):
    args = [iter(iterable)] * size
    if fillvalue is undefined:
        return izip(*args)
    else:
        return izip_longest(fillvalue=fillvalue, *args)


####
## Reducers
####


def rsorted(keyfunc, iterable, **kwargs):
    return sorted(iterable, key=keyfunc, **kwargs)


####
## Partials
####

####
## Predicates
####


def even(x):
    return mod(x, 2) == 0


odd = c(not_, even)


def is_none(x):
    return x is None

not_none = c(not_, is_none)
