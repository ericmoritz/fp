from fp.monads.monad import Monad, MonadIter, MonadPlus


class Maybe(Monad, MonadIter, MonadPlus):
    """
    A Maybe monad.

    The Maybe monad is helpful when dealing with sequences of functions that could return None.

    For instance, when fetching a key from a dictionary that may not be there:

    >>> from fp.monads.maybe import *
    >>> data = {"foo": {"bar": {"baz": "bing"}}}
    >>> data['foo']['bong']['baz']
    Traceback (most recent call last):
        ...
    KeyError: 'bong'

    This is a very common problem when processing JSON. Often, with JSON, a missing key is the same as null
    but in Python a missing key raises an error. 

    `dict.get` is often the solution for missing keys but is
    still not enough:

    >>> data.get("foo").get("bong").get("baz")
    Traceback (most recent call last):
        ...
    AttributeError: 'NoneType' object has no attribute 'get'

    To final solution to this ends up being ugly:

    >>> data.get("foo", {}).get("bong", {}).get("baz") is None
    True

    It is even more complex when dealing with mixed types; for instance if "bong" ends up bing
    a string instead of a dict.

    The :class:`Maybe` monad lets us express errors such as these as
    either something or nothing.  This is much like :func:`dict.get`
    returning None, but we can chain Maybe actions so that they fail
    with :class:`Nothing`, if any of the functions in the chain
    returns :class:`Nothing`.

    Normally getitem will raise an error if the key or index is
    invalid, :func:`Maybe.error_to_nothing` causes :class:`Nothing` to
    be returned if any exception occurs.

    >>> from operator import getitem
    >>> lookup = Maybe.error_to_nothing(getitem)

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

    Other operations are:

    >>> Just(1).is_just
    True
    
    >>> Just(1).is_nothing
    False

    >>> Nothing.is_nothing
    True

    >>> Nothing.is_just
    False
    
    To chain the lookups, we simply need to partially apply the lookup function:

    >>> from fp import pp
    >>> lookup(data, "foo").bind(pp(lookup, "bar")).bind(pp(lookup, "baz"))
    Just('bing')

    >>> lookup(data, "foo").bind(pp(lookup, "bong")).bind(pp(lookup, "baz"))
    Nothing

    The Maybe monad also supports abuse of list comprehensions for expressing Maybe actions:
    >>> Maybe.from_iterable(
    ... baz
    ... for foo  in lookup(data, 'foo')
    ... for bong in lookup(foo, 'bong')
    ... for baz  in lookup(bong, 'baz')
    ... )
    Nothing

    >>> Maybe.from_iterable(
    ... baz
    ... for foo  in lookup(data, 'foo')
    ... for bar in lookup(foo, 'bar')
    ... for baz  in lookup(bar, 'baz')
    ... )
    Just('bing')


    More Examples:

    >>> from fp.monads.maybe import Just, Nothing, Maybe
    >>> Maybe.sequence([Just(1), Nothing, Just(2)])    
    Nothing

    >>> Maybe.sequence([Just(1), Just(2)])
    Just([1, 2])

    >>> Maybe.sequence_dict({"foo": Just(1), "bar": Just(2)})
    Just({'foo': 1, 'bar': 2})

    >>> maybe_int = Maybe.error_to_nothing(int)
    >>> Maybe.mapM(maybe_int, ["1", "2"])
    Just([1, 2])

    >>> Maybe.mapM(maybe_int, ["1", "a"])
    Nothing



    Left to Right arrow composition.  maybe cast the string as an int, then maybe add 1

    >>> string_to_plus1 = Maybe.arrow_cl(maybe_int, lambda x: Maybe(x+1))
    >>> string_to_plus1("1")
    Just(2)


    Right to Left arrow composition.  maybe cast the string as an int, then maybe add 1

    >>> string_to_plus1 = Maybe.arrow_cr(lambda x: Maybe(x+1), maybe_int)
    >>> string_to_plus1("1")
    Just(2)

    >>> Maybe.ap(lambda x: x+1, Just(1))
    Just(2)

    >>> Maybe.ap(lambda x: x+1, Nothing)
    Nothing
    
    >>> import operator
    >>> Maybe.ap(operator.add, Just(1), Just(2))
    Just(3)

    >>> Maybe.ap(operator.add, Nothing, Just(2))
    Nothing

    >>> Maybe.ap(operator.add, Just(1), Nothing)
    Nothing

    >>> from datetime import timedelta
    >>> Maybe.ap(timedelta, days=Just(1), seconds=Just(60))
    Just(datetime.timedelta(1, 60))

    >>> from fp.monads.maybe import Maybe
    >>> from fp import even, c, p
    >>> maybeInt = Maybe.error_to_nothing(int) # convert int to a Maybe arrow
    >>> maybeEven = p(Maybe.ap, even) # lift even into Maybe
    >>> Maybe.filterM(c(maybeEven, maybeInt), ["x","1","2","3","4"])
    Just(['2', '4'])

    >>> Maybe.msum([Maybe(1), Nothing, Maybe(2)])
    Just(1)

    >>> Maybe.msum([Nothing, Nothing, Maybe(2)])
    Just(2)

    >>> Maybe.msum([Nothing, Nothing, Nothing])
    Nothing

    >>> from fp.monads.maybe import Maybe
    >>> Maybe.guard(True)
    Just(noop)

    >>> Maybe.guard(False)
    Nothing

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

    @staticmethod
    def error_to_nothing(f):
        """
        Converts a function that raises an exception of any kind to
        Nothing.
        """
        def inner(*args, **kwargs):
            try:
                return Just(f(*args, **kwargs))
            except:
                return Nothing
        return inner
    
    ##=====================================================================
    ## Monad methods
    ##=====================================================================
    def bind(self, f):
        """
        The Maybe's bind function

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

    ##=====================================================================
    ## MonadIter methods
    ##=====================================================================
    def __iter__(self):
        """
        The MonadIter.__iter__ function to enable monadic exploitation
        of list generators:

        >>> list(Just(1))
        [1]

        >>> list(Nothing)
        []

        >>> def lookup(d, x):
        ...     return Maybe(d.get(x))
        >>> data = {"foo": {"bar": "baz"}}

        
        >>> Maybe.from_iterable(
        ...    val
        ...    for inner in lookup(data, "foo")
        ...    for val   in lookup(inner, "bar")
        ... )
        Just('baz')

        Failure on the first key:

        >>> Maybe.from_iterable(
        ...    val
        ...    for inner in lookup(data, "fud")
        ...    for val   in lookup(inner, "baz")
        ... )
        Nothing

        Failure on the second key:

        >>> Maybe.from_iterable(
        ...    val
        ...    for inner in lookup(data, "foo")
        ...    for val   in lookup(inner, "bong")
        ... )
        Nothing
        """
        if self.is_just:
            return iter([self.__value])
        else:
            return iter([])

    @classmethod
    def from_iterable(cls, iterable):
        for x in iterable:
            return Maybe(x)
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


if __name__ == '__main__':
    import pytest, sys
    sys.exit(pytest.main(["--doctest-modules", __file__]))
