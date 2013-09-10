from fp.monads.monad import Monad, MonadIter


class Maybe(Monad, MonadIter):
    """
    A Maybe monad.
    """

    ##=====================================================================
    ## Maybe methods
    ##=====================================================================
    def __init__(self, value):
        self.__value = value

    def __eq__(self, other):
        return self.__value == other.__value

    def __repr__(self):
        return "Maybe({0!r})".format(self.__value)

    @property
    def is_just(self):
        """
        Tests if the Maybe is just a value

        >>> Maybe(1).is_just
        True

        >>> Maybe(None).is_just
        False
        """
        return self.__value is not None
    
    @property
    def is_nothing(self):
        """
        Tests if the Maybe is Nothing
        
        >>> Maybe(None).is_nothing
        True

        >>> Maybe(1).is_nothing
        False
        """
        return not self.is_just

    @property
    def from_just(self):
        """
        Extracts the just value from the Maybe; raises a ValueError
        if the value is None

        >>> Maybe(1).from_just
        1

        >>> Maybe(None).from_just
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

        >>> Maybe(1).default(-1)
        1

        >>> Maybe(None).default(-1)
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
        ...     Maybe(1), Maybe(None), Maybe(2)
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
        ...         return Maybe(x)
        ...     else:
        ...         return Maybe(None)
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
    def bind(self, f):
        """
        The Maybe's bind function

        >>> Maybe(1).bind(lambda x: Maybe(x)).from_just
        1
        
        >>> def crashy(x):
        ...     assert False, "bind will not call me"
        >>> Maybe(None).bind(crashy).is_nothing
        1
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

        >>> list(Maybe(1))
        [1]

        >>> list(Maybe(None))
        []

        >>> def lookup(d, x):
        ...     return Maybe(d.get(x))
        >>> data = {"foo": {"bar": "baz"}}

        
        >>> Maybe.from_iterable(
        ...    val
        ...    for inner in lookup(data, "foo")
        ...    for val   in lookup(inner, "bar")
        ... )
        Maybe('baz')


        Failure on the first key:

        >>> Maybe.from_iterable(
        ...    val
        ...    for inner in lookup(data, "fud")
        ...    for val   in lookup(inner, "baz")
        ... ) == Maybe(None)
        True


        Failure on the second key:

        >>> Maybe.from_iterable(
        ...    val
        ...    for inner in lookup(data, "foo")
        ...    for val   in lookup(inner, "bong")
        ... ) == Maybe(None)
        True
        """
        if self.is_just:
            return iter([self.__value])
        else:
            return iter([])

    @classmethod
    def from_iterable(cls, iterable):
        for x in iterable:
            return Maybe(x)
        return Maybe(None)

if __name__ == '__main__':
    import pytest, sys
    sys.exit(pytest.main(["--doctest-modules", __file__]))
