"""
A collection of functional programming inspired tools for Python.
"""
import operator
import itertools
from six import moves
from fp.missing_six import ifilter


__version__ = "0.2"


####
# atoms
####
class atom(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        """
        >>> atom("test")
        test
        """
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

    >>> list(map(pp(str.lstrip, '/'), ['/foo', '/bar']))
    ['foo', 'bar']

This is the equivalence to these expressions

    >>> [item.lstrip("/") for item in ['/foo', '/bar']]
    ['foo', 'bar']

    >>> list(map(lambda x: x.lstrip('/'), ['/foo', '/bar']))
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

    >>> list(map(
    ...  c(str.lower, pp(operator.getitem, "word")),
    ...  [{"word": "Xray"}, {"word": "Young"}]
    ... ))
    ['xray', 'young']

    """
    return lambda x: f(g(x))


def const(x):
    """
..function::const(x) -> callable

Returns a function which always returns `x`
regardless of arguments

    >>> const('foo')(1, 2, foo='bar')
    'foo'
"""

    return lambda *args, **kwargs: x


def callreturn(method, obj, *args, **kwargs):
    """
..function::callreturn(method : callable, obj : a, *args, **kwargs) ->  a

Calls the method


    >>> from six.moves import reduce
    >>> reduce(
    ...    p(callreturn, set.add),
    ...    ["a", "b", "c"],
    ...    set()
    ... ) == set(["a", "b", "c"])
    True

    """
    method(obj, *args, **kwargs)
    return obj


def kwfunc(func, keys=None):
    """
..function::kwfunc(func[, keys=None : None | list]) -> callable

Returns a function which applies a dict as kwargs.

Useful for map functions.

    >>> def full_name(first=None, last=None):
    ...     return " ".join(
    ...        coalesce([first, last])
    ...     )
    ...
    >>> list(map(
    ...    kwfunc(full_name),
    ...    [
    ...        {"first": "Eric", "last": "Moritz"},
    ...        {"first": "John"},
    ...        {"last": "Cane"},
    ...    ]
    ... )) == ["Eric Moritz", "John", "Cane"]
    True

Optionally, needed keys can be passed in:


    >>> list(map(
    ...    kwfunc(full_name, ["first", "last"]),
    ...    [
    ...        {"first": "Eric", "last": "Moritz"},
    ...        {"first": "Gina", "dob": "1981-08-13"},
    ...    ]
    ... )) == ["Eric Moritz", "Gina"]
    True

"""

    if keys:
        def inner(dct):
            kwargs = dict(((k, dct[k]) for k in keys if k in dct))
            return func(**kwargs)
    else:
        def inner(dct):
            return func(**dct)

    return inner


def trampoline(f):
    """
    Use f() as a continuation of a tail-recursive funciton.

    trampoline() will continue to call the result of f() as long as it is
    callable.  Iteration will stop once f is no longer callable.

    >>> def counter(n):
    ...     return trampoline(counter_(0, 2000))

    >>> def counter_(acc, n):
    ...     if n == 0:
    ...         return acc
    ...     else:
    ...         return lambda: counter_(acc+1, n-1)

    >>> counter(2000)
    2000


    """
    while callable(f):
        f = f()
    return f


####
## Operators
####
def identity(x):
    """..function::identity(x) -> x

A function that returns what is passed to it.

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

    >>> list(itake(3, range(5)))
    [0, 1, 2]

    >>> list(itake(3, []))
    []
    """
    return itertools.islice(iterable, 0, n)


def idrop(n, iterable):
    """..function::idrop(n, iterable)

Drops the first `n` items off the iterator

    >>> list(idrop(3, range(6)))
    [3, 4, 5]

    >>> list(idrop(3, []))
    []
    """
    return itertools.islice(iterable, n, None)


def isplitat(i, iterable):
    """..function::isplitat(i, iterable)

yields two iterators split at index `i`

    >>> def materalize(chunks):
    ...    "Turns a iterator of iterators into a list of lists"
    ...    return list(map(list, chunks))
    >>> materalize(
    ...     isplitat(3, range(6))
    ... )
    [[0, 1, 2], [3, 4, 5]]
    """

    iterator = iter(iterable)
    yield itake(i, iterator)
    yield iterator


def izipwith(f, iterable1, iterable2):
    """
    Zips a function with two iterables

    >>> list(izipwith(lambda x,y: (x,y), [1,2], [3,4]))
    [(1, 3), (2, 4)]
    """
    return moves.map(f, iterable1, iterable2)


def coalesce(items):
    """
    Removes None values from the an iterator

    >>> list(coalesce([None, 1, None, 2]))
    [1, 2]
    """
    return ifilter(
        lambda x: x is not None,
        items)


####
## Reducers
####


def allmap(f, iterable):
    """returns True if all elements of the list satisfy the predicate,
    and False otherwise.

    >>> allmap(even, [1, 2, 3])
    False

    >>> allmap(even, [2, 4, 6, 8])
    True

    """
    return all(moves.map(f, iterable))


def anymap(f, iterable):
    """returns True if any of the elements of the list satisfy the
    predicate, and False otherwise

    >>> anymap(even, [1, 2, 3])
    True

    >>> anymap(even, [1, 3, 7])
    False
    """
    return any(moves.map(f, iterable))


####
## Predicates
####
def even(x):
    """
    True if x is even

    >>> even(1)
    False

    >>> even(2)
    True

    """
    return operator.mod(x, 2) == 0


def odd(x):
    """
    True if x is even

    >>> odd(1)
    True

    >>> odd(2)
    False
    """
    return operator.mod(x, 2) != 0
