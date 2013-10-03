"""
The fp.collections module provides utilities for working with collections.
"""

from fp import trampoline


def lookup(monad_cls, collection, key):
    """
    Lookup a value by a key

    >>> from fp.monads.maybe import Maybe
    >>> lookup(Maybe, {'foo': 'bar'}, 'foo')
    Just('bar')
    >>> lookup(Maybe, {}, 'foo')
    Nothing
    >>> lookup(Maybe, [1, 2, 3], 2)
    Just(3)
    >>> lookup(Maybe, [1, 2, 3], 4)
    Nothing
    >>> lookup(Maybe, [1, 2, 3], 'not a int')
    Nothing

    >>> from fp.monads.either import Either
    >>> lookup(Either, [1, 2, 3], 2)
    Right(3)
    >>> lookup(Either, [1, 2, 3], 4)
    Left(IndexError('list index out of range',))
    """
    return monad_cls.catch(lambda: collection[key])


def get(monad_cls, key, collection):
    """
    A partial friendly version of lookup

    >>> from fp.monads.maybe import Maybe
    >>> get(Maybe, 'foo', {'foo': 'bar'})
    Just('bar')

    >>> get(Maybe, 'foo', {})
    Nothing
    """
    return lookup(monad_cls, collection, key)


def get_nested(monad_cls, collection, *keys):
    """
    Get a value deep inside a nested data structure

    >>> from fp.monads.maybe import Maybe
    >>> data = {'foo': {'bar': {'baz': 'bing'}}}
    >>> get_nested(Maybe, data, 'foo', 'bar', 'baz')
    Just('bing')
    >>> get_nested(Maybe, data, 'foo', 'bing')
    Nothing
    >>> get_nested(Maybe, data, 'blegh', 'bar')
    Nothing
    >>> get_nested(Maybe, {'foo': [{'bar': 'baz'}]}, 'foo', 0, 'bar')
    Just('baz')
    >>> get_nested(Maybe, {'foo': [{'bar': 'baz'}]}, 'foo', 1, 'bar')
    Nothing
    >>> get_nested(Maybe, {})
    Just({})
    """
    return trampoline(__get_nested(
        monad_cls,
        monad_cls.ret(collection),
        keys,
    ))


def __get_nested(monad_cls, accM, keys):
    if len(keys) == 0:
        return accM
    else:
        key = keys[0]
        keys = keys[1:]
        return lambda: accM.bind(
            lambda c: __get_nested(
                monad_cls,
                lookup(monad_cls, c, key),
                keys
                )
            )
