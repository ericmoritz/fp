"""
A collection of functional programming inspired tools for Python.
"""
import sys
import operator
import itertools


####
# atoms
####
undefined = object()


####
## Operators
####


def getitem(obj, *args, **kwargs):
    default = kwargs.pop("default", None)

    try:
        return operator.getitem(obj, *args, **kwargs)
    except (KeyError, IndexError):
        return default


def setitem(obj, *args, **kwargs):
    inner = callreturn(operator.setitem)
    return inner(obj, *args, **kwargs)


def delitem(obj, *args, **kwargs):
    try:
        operator.delitem(obj, *args, **kwargs)
    except KeyError:
        pass
    return obj


def dictupdate(dct, kv_iterable):
    inner = callreturn(dict.update)
    return inner(dct, kv_iterable)


###
# Higher-Order functions
###

from functools import partial as p

def pp(func, *args0, **kwargs0):
    """..function::pp(func : callable[, *args][, **keywords]) -> partial callable

Returns an prepended partial function which when called will behave
like `func` called with the positional arguments `args` and `keywords`

If more arguments are supplied to the call, they are prepended to
args. If additional keyword arguments are supplied, they extend and
override keywords.

This is useful for converting mapping functions whose first argument
is the subject of mapper.

    >>> from fp import pp
    >>> map(pp(str.lstrip, '/'), ['/foo', '/bar'])
    ['foo', 'bar']

This is the equivalence to these expressions

    >>> [item.lstrip("/") for item in ['/foo', '/bar']]
    ['foo', 'bar']

    >>> map(lambda x: x.lstrip('/'), ['/foo', '/bar'])
    ['foo', 'bar']

    """

    def inner(*args1, **kwargs1):
        args = args1 + args0
        kwargs = dict(kwargs0, **kwargs1)
        return func(*args, **kwargs)
    return inner


def c(f, g):
    """..py:function::c(f : callable, g : callable) -> callable
Returns a new function which is the equivalent to
`f(g(*args, **kwargs))``

Example:

    >>> from fp import pp, c, getitem
    >>> map(
    ...  c(str.lower, pp(getitem, "word")),
    ...  [{"word": "Xray"}, {"word": "Young"}]
    ... )
    ['xray', 'young']

    """
    return lambda x: f(g(x))


def t(fs):
    """..function::f(fs : [callable]) -> callable

Returns a unary thrush function which composes a list of unary functions.

A thrush provides a left associative alternative to `c()`:

    >>> t([f, g, h])(x) == c(h, c(g, f))(x) == f(g(h(x))) # doctest: +SKIP
    True

Where compose is right associative


    >>> from fp import p, c
    >>> from operator import add, mul
    >>> c(p(mul, 2), p(add, 3))(2)
    10

A thrush partial is left associative

    >>> from fp import p, c, t
    >>> from operator import add, mul
    >>> t([
    ... p(add, 3),
    ... p(mul, 2)
    ... ])(2)
    10
    """
    head = first(fs)
    tail = irest(fs)

    return reduce(
        lambda composed, f: c(f, composed),
        tail, head)


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
        raise RuntimeError("unmatched case")
    return inner


def const(x):
    return lambda *args, **kwargs: x


def flip(f):
    return lambda x, y: f(y, x)


def identity(x):
    return x


def callreturn(func):
    """create a function which takes an object with args and kwargs,
applys func(object, *args, **kwargs) and return object

Useful for non-pure functions which return None instead of the object.

These functions makes compositions difficult.

    dictupdate = callreturn(dict.update)
    assert {"foo": "bar"} = dictupdate({}, [("foo", "bar")])
    """

    def inner(obj, *args, **kwargs):
        func(obj, *args, **kwargs)
        return obj
    return inner


def kwfunc(func, *keys):
    if keys:
        def inner(dct):
            kwargs = {k:dct[k] for k in keys}
            return func(**kwargs)
    else:
        def inner(dct):
            return func(**dct)

    return inner


def getter(*args, **kwargs):
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
    default = kwargs.pop("default", None)

    def inner(obj):
        for arg in args:
            obj = getitem(obj, arg, default=undefined)
            if obj is undefined:
                return default
        return obj

    return inner


###
## generators
###


def islice(*args):
    arg_len = len(args)
    start, stop, step = None, None, None

    if arg_len == 2:
        start, iterable = args
    elif arg_len == 3:
        start, stop, iterable = args
    elif arg_len == 4:
        start, stop, step, iterable = args
    else:
        raise TypeError(
            ("islice() takes at between 2 and 4 arguments"
             " %s given") % (arg_len)
        )
    return itertools.islice(iterable, start, stop, step)


def itake(n, iterable):
    return islice(0, n, iterable)


def idrop(n, iterable):
    return itertools.islice(iterable, n, None)


def first(iterable):
    return iter(iterable).next()


def irest(iterable):
    return idrop(1, iterable)


def isplitat(i, iterable):
    iterator = iter(iterable)
    yield itake(i, iterator)
    yield iterator


def izipwith(f, iterable1, iterable2):
    return itertools.imap(f, iterable1, iterable2)


def ichunk(size, iterable, fillvalue=undefined):
    if fillvalue is undefined:
        def chunker():
            it = iter(iterable)

            while True:
                chunk = tuple(itake(size, it))
                if chunk:
                    yield chunk
                else:
                    break
        return chunker()
    else:
        args = [iter(iterable)] * size
        return itertools.izip_longest(fillvalue=fillvalue, *args)


####
## Reducers
####


def allmap(f, iterable):
    """returns True if all elements of the list satisfy the predicate,
    and False otherwise."""
    return all(itertools.imap(f, iterable))


def anymap(f, iterable):
    """returns True if any of the elements of the list satisfy the
    predicate, and False otherwise"""
    return any(itertools.imap(f, iterable))


####
## Predicates
####
def even(x):
    return operator.mod(x, 2) == 0


def odd(x):
    return operator.mod(x, 2) != 0


def is_none(x):
    return x is None


def not_none(x):
    return x is not None
