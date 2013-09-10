"""
A collection of functional programming inspired tools for Python.
"""
import sys
import operator
import itertools
from six import moves
import six

if six.PY3:
    izip_longest = itertools.zip_longest
else:
    izip_longest = itertools.izip_longest


####
# atoms
####
class atom(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

undefined = atom("undefined")

###
# Higher-Order functions
###


from functools import partial as p

def pp(func, *args0, **kwargs0):
    """
..function::pp(func : callable[, *args][, **keywords]) -> partial callable

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
    """..function::c(f : callable, g : callable) -> callable
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


def constantly(x):
    """
..function::constantly(x) -> callable

Returns a function which always returns `x`
regardless of arguments

    >>> from fp import constantly
    >>> constantly('foo')(1, 2, foo='bar')
    'foo'
"""

    return lambda *args, **kwargs: x


def callreturn(func):
    """..function::callreturn(func : callable) -> callable

create a function which applies `func(object, *args, **kwargs)` and
returns object

Useful for mutation functions which return None instead of the object.

These mutation function normally make use with higher-order function
difficult.

    >>> from fp import callreturn
    >>> reduce(
    ...    callreturn(set.add),
    ...    ["a", "b", "c"],
    ...    set()
    ... ) == {"a", "b", "c"}
    True

    """

    def inner(obj, *args, **kwargs):
        func(obj, *args, **kwargs)
        return obj
    return inner


def kwfunc(func, keys=None):
    """
..function::kwfunc(func[, keys=None : None | list]) -> callable

Returns a function which applies a dict as kwargs.

Useful for map functions.

    >>> from fp import coalesce, kwfunc
    >>> def full_name(first=None, last=None):
    ...     return " ".join(
    ...        coalesce([first, last])
    ...     )
    ...
    >>> map(
    ...    kwfunc(full_name),
    ...    [
    ...        {"first": "Eric", "last": "Moritz"},
    ...        {"first": "John"},
    ...        {"last": "Cane"},
    ...    ]
    ... ) == ["Eric Moritz", "John", "Cane"]
    True

Optionally, needed keys can be passed in:


    >>> map(
    ...    kwfunc(full_name, ["first", "last"]),
    ...    [
    ...        {"first": "Eric", "last": "Moritz"},
    ...        {"first": "Gina", "dob": "1981-08-13"},
    ...    ]
    ... ) == ["Eric Moritz", "Gina"]
    True

"""

    if keys:
        def inner(dct):
            kwargs = {k:dct[k] for k in keys if k in dct}
            return func(**kwargs)
    else:
        def inner(dct):
            return func(**dct)

    return inner


def getter(*args):
    """
..function::getter(*keys) ->  callable(object[, default=None])
Creates a function that digs into a nested data structure or returns
default if any of the keys are missing or the key references an
object without __getitem__ (list, dict, etc)

    >>> from fp import getter
    >>> get_city = getter("cities", 0, "name")
    >>> get_city(
    ...    {
    ...      "cities": [{"name": 'Reston'}]
    ...    }
    ... )
    'Reston'
    >>> get_city(
    ...    {
    ...      "cities": [{}]
    ...    }
    ... ) is None
    True
    >>> get_city(
    ...    {
    ...      "cities": [{}]
    ...    },
    ...    default="not found"
    ... ) is "not found"
    True
    """
    def inner(obj, default=None):
        for arg in args:
            # If we hit a non-container object, return default
            if not hasattr(obj, "__getitem__"):
                return default

            obj = getitem(obj, arg, default=undefined)
            if obj is undefined:
                return default
        return obj

    return inner


####
## Operators
####


def getitem(obj, key, default=None):
    """..function::getitem(obj, key[, default=None]) -> value

Returns the value indexed at "key" or returns `default`

This differs from `operator.getitem` in that it never returns a
KeyError or IndexError, which could be problematic when used with
map() or other higher-ordered functions.

    >>> getitem({"foo": "bar"}, "foo")
    'bar'

    >>> getitem({"foo": "bar"}, "baz") is None
    True

    >>> getitem({"foo": "bar"}, "baz", default="not-here")
    'not-here'

    >>> getitem([1], 0)
    1

    >>> getitem([1], 1) is None
    True

    >>> getitem([1], 1, default="not-here")
    'not-here'

    """
    try:
        return operator.getitem(obj, key)
    except (KeyError, IndexError):
        return default


def setitem(obj, key, value):
    """..function::setitem(obj, key, value) -> obj

Sets the `key` to `value` and returns the mutated object

    >>> from fp import setitem
    >>> setitem({}, "foo", "bar")
    {'foo': 'bar'}

Unlike functional languages, the returned object is not a copy of the
inputted object:

    >>> data = {}
    >>> setitem(data, "foo", "bar") is data
    True

This differs from `operator.setitem` in that it returns the mutated
object rather than None.  This helps when mutating a lis

    """

    inner = callreturn(operator.setitem)
    return inner(obj, key, value)


def delitem(obj, key):
    """
..function::delitem(obj, key) -> obj

Deletes the key from the `obj` and returns `obj`

Unlike `del obj[key]`, this function silently suppresses
the KeyError when a key does not exist. If you need that functionality
use `operator.delitem`

Example:

    >>> from fp import delitem
    >>> delitem({"foo": "bar"}, "foo")
    {}

    >>> delitem({"foo": "bar"}, "baz")
    {'foo': 'bar'}

Just like setitem, the returned object is the same object:

    >>> data = {"foo": "bar"}
    >>> delitem(data, "foo") is data
    True
"""

    try:
        operator.delitem(obj, key)
    except KeyError:
        pass
    return obj


def identity(x):
    """..function::identity(x) -> x

A function that returns what is passed to it.

    >>> from fp import identity
    >>> identity(1)
    1
    """
    return x


###
## iterators
###


def itake(n, iterable):
    """
Takes n items off the iterable:

    >>> from fp import itake
    >>> list(itake(3, xrange(5)))
    [0, 1, 2]

    >>> list(itake(3, []))
    []
    """
    return itertools.islice(iterable, 0, n)


def idrop(n, iterable):
    """..function::idrop(n, iterable)

Drops the first `n` items off the iterator

    >>> from fp import idrop
    >>> list(idrop(3, xrange(6)))
    [3, 4, 5]

    >>> list(idrop(3, []))
    []
    """
    return itertools.islice(iterable, n, None)


def isplitat(i, iterable):
    """..function::isplitat(i, iterable)

yields two iterators split at index `i`

    >>> from fp import isplitat
    >>> def materalize(chunks):
    ...    "Turns a iterator of iterators into a list of lists"
    ...    return map(list, chunks)
    >>> materalize(
    ...     isplitat(3, range(6))
    ... )
    [[0, 1, 2], [3, 4, 5]]
    """

    iterator = iter(iterable)
    yield itake(i, iterator)
    yield iterator


def izipwith(f, iterable1, iterable2):
    return moves.map(f, iterable1, iterable2)


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
        return izip_longest(fillvalue=fillvalue, *args)


def coalesce(items):
    return itertools.ifilter(
        lambda x: x is not None,
        items)


####
## Reducers
####


def allmap(f, iterable):
    """returns True if all elements of the list satisfy the predicate,
    and False otherwise."""
    return all(moves.map(f, iterable))


def anymap(f, iterable):
    """returns True if any of the elements of the list satisfy the
    predicate, and False otherwise"""
    return any(moves.map(f, iterable))


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
