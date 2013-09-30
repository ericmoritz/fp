from fp import trampoline


def lookup(monad_cls, collection, key):
    """
    >>> from fp.monads.maybe import Maybe
    >>> lookup(Maybe, {'foo': 'bar'}, 'foo')
    Just('bar')

    >>> lookup(Maybe, {}, 'foo')
    Nothing
    """
    return monad_cls.catch(lambda: collection[key])


def get_nested(monad_cls, collection, *keys):
    """
    >>> from fp.monads.maybe import Maybe
    >>> from fp.monads.either import Either
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
