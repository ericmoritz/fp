from fp.monads.monad import Monad, MonadPlus


class Maybe(Monad, MonadPlus):
    """
    A Maybe monad.

    The Maybe monad is helpful when dealing with sequences of
    functions that could return None.

    For instance, when fetching a key from a dictionary that may not
    be there:

    >>> from fp.monads.maybe import Maybe, Just, Nothing
    >>> data = {"foo": {"bar": {"baz": "bing"}}}
    >>> data['foo']['bong']['baz']
    Traceback (most recent call last):
        ...
    KeyError: 'bong'

    This is a very common problem when processing JSON. Often, with
    JSON, a missing key is the same as null but in Python a missing
    key raises an error.

    `dict.get` is often the solution for missing keys but is
    still not enough:

    >>> data.get("foo").get("bong").get("baz")
    Traceback (most recent call last):
        ...
    AttributeError: 'NoneType' object has no attribute 'get'

    To final solution to this ends up being ugly:

    >>> data.get("foo", {}).get("bong", {}).get("baz") is None
    True

    It is even more complex when dealing with mixed types; for
    instance if "bong" ends up being a list instead of a dict.

    The :class:`Maybe` monad lets us express errors such as these as
    either something or nothing.  This is much like :func:`dict.get`
    returning None, but we can chain Maybe actions so that they fail
    with :class:`Nothing`, if any of the functions in the chain
    returns :class:`Nothing`.

    Normally getitem will raise an error if the key or index is
    invalid, :func:`Maybe.catch` causes :class:`Nothing` to
    be returned if any exception occurs.

    >>> from operator import getitem
    >>> from fp import p
    >>> lookup = p(Maybe.catch, getitem)

    >>> lookup({"foo": "bar"}, "foo")
    Just('bar')

    >>> lookup({"foo": "bar"}, "bong")
    Nothing

    Now lookup returns :class:`Just(x)` if the key is found or
    :class:`Nothing` if the key is not found.

    To extract the value out of the :class:`Just()` class, we can call
    :class:`Maybe.default()`:

    >>> lookup({'foo': 'bar'}, 'foo').default('')
    'bar'

    >>> lookup({'foo': 'bar'}, 'bong').default('')
    ''

    To chain the lookups, we simply need to partially apply the lookup
    function:

    >>> from fp import pp
    >>> lookup(data, "foo").bind(pp(lookup, "bar")).bind(pp(lookup, "baz"))
    Just('bing')

    >>> lookup(data, "foo").bind(pp(lookup, "bong")).bind(pp(lookup, "baz"))
    Nothing

    This is still not as pretty as it could be so we provide a
    `get_nested` function in the `fp.collections` module:

    >>> from fp.collections import get_nested
    >>> get_nested(Maybe, data, "foo", "bar", "baz")
    Just('bing')

    >>> get_nested(Maybe, data, "foo", "bong", "baz")
    Nothing

    In addition, functions that return None become Nothing automatically:

    >>> Maybe.ret(None)
    Nothing

    >>> Maybe.ret({}.get('foo'))
    Nothing

    This feature allows you to easily integrate the Maybe monad with
    existing functions that return None.
    """

    ##=====================================================================
    ## Maybe methods
    ##=====================================================================
    def __init__(self, value):
        self.__value = value

    def __eq__(self, other):
        return self.__value == other.__value

    def __repr__(self):
        if self.is_just:
            return "Just({0!r})".format(self.__value)
        else:
            return "Nothing"

    @property
    def is_just(self):
        """
        Tests if the Maybe is just a value

        >>> Just(1).is_just
        True

        >>> Nothing.is_just
        False
        """
        return self.__value is not None

    @property
    def is_nothing(self):
        """
        Tests if the Maybe is Nothing

        >>> Nothing.is_nothing
        True

        >>> Just(1).is_nothing
        False
        """
        return not self.is_just

    @property
    def from_just(self):
        """
        Extracts the just value from the Maybe; raises a ValueError
        if the value is None

        >>> Just(1).from_just
        1

        >>> Nothing.from_just
        Traceback (most recent call last):
            ...
        ValueError: Maybe.from_just called on Nothing
        """
        if self.is_just:
            return self.__value
        else:
            raise ValueError("Maybe.from_just called on Nothing")

    def default(self, default_value):
        """
        Returns the just value or the default value if Nothing

        >>> Just(1).default(-1)
        1

        >>> Nothing.default(-1)
        -1
        """
        if self.is_just:
            return self.__value
        else:
            return default_value

    @classmethod
    def cat_maybes(cls, maybes):
        """
        Returns an iterator of the Just values

        >>> list(Maybe.cat_maybes([
        ...     Just(1), Nothing, Just(2)
        ... ]))
        [1, 2]
        """
        for maybe in maybes:
            if maybe.is_just:
                yield maybe.__value

    @classmethod
    def map_maybes(cls, f, xs):
        """
        maps a list over a Maybe arrow

        >>> def maybe_even(x):
        ...     if x % 2 == 0:
        ...         return Just(x)
        ...     else:
        ...         return Nothing
        >>> list(Maybe.map_maybes(maybe_even, [1,2,3,4]))
        [2, 4]
        """
        for x in xs:
            maybe = f(x)
            if maybe.is_just:
                yield maybe.__value

    ##=====================================================================
    ## Monad methods
    ##=====================================================================
    @classmethod
    def ret(cls, value):
        return cls(value)

    def bind(self, f):
        """
        The Maybe's bind function.  `f` is called only if `self` is a Just.

        >>> Just(1).bind(lambda x: Maybe(x))
        Just(1)

        >>> def crashy(x):
        ...     assert False, "bind will not call me"
        >>> Nothing.bind(crashy)
        Nothing
        """
        if self.is_just:
            return f(self.__value)
        else:
            return self

    @classmethod
    def fail(cls, err):
        """
        >>> Maybe.fail("some error")
        Nothing
        """
        return Nothing

    ##=====================================================================
    ## MonadPlus methods
    ##=====================================================================
    def mplus(self, y):
        """
        An associative operation.

        >>> Just(1).mplus(Maybe.mzero)
        Just(1)

        >>> Nothing.mplus(Maybe(2))
        Just(2)

        >>> Just(1).mplus(Just(2))
        Just(1)

        """
        if self.is_just:
            return self
        else:
            return y

Just = Maybe
Nothing = Maybe(None)

Maybe.mzero = Nothing
