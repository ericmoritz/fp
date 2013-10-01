import fp
from fp.monads.monad import Monad
from abc import ABCMeta, abstractmethod


class Either(Monad):
    """
    The Either monad is helpful when dealing with sequences of
    functions that can fail.  These functions return `Right(value)` on
    success and `Left(error)` on failure.

    When chained together, these functions will short circuit the chain when a
    failure occurs.

    For instance an example of `lookup(dict, key)` could be:

    >>> def lookup(d, k):
    ...     try:
    ...         return Right(d[k])
    ...     except Exception as err:
    ...         return Left(err)

    >>> lookup({'foo': 'bar'}, 'foo')
    Right('bar')
    >>> lookup({}, 'foo')
    Left(KeyError('foo',))

    The benefit of Either's over Exceptions is that you're forced to
    handle the error eventually.  You can't let the Exception bubble
    to the surface and crash your program. Nothing escapes the monad!

    The Either method lets you handle the error in your own way.

    >>> lookup({}, 'foo').either(
    ...     lambda err: err,
    ...     lambda val: val
    ... )
    KeyError('foo',)

    >>> lookup({'foo': 'bar'}, 'foo').either(
    ...     lambda err: err,
    ...     lambda val: val
    ... )
    'bar'

    The default method lets you completely ignore the error:

    >>> lookup({'foo': 'bar'}, 'foo').default('bing')
    'bar'

    >>> lookup({}, 'foo').default('bing')
    'bing'

    Just like any other monad, functions can be chained together using
    bind(f):

    >>> lookup({'foo': {'bar': 'baz'}}, 'foo').bind(
    ... lambda foo: lookup(foo, 'bar'))
    Right('baz')

    >>> lookup({'foo': {}}, 'foo').bind(
    ... lambda foo: lookup(foo, 'bar'))
    Left(KeyError('bar',))

    >>> lookup({}, 'foo').bind(
    ... lambda foo: lookup(foo, 'bar'))
    Left(KeyError('foo',))

    """
    __metaclass__ = ABCMeta

    @classmethod
    def ret(cls, value):
        return Right(value)

    @classmethod
    def fail(cls, exception):
        return Left(exception)

    @abstractmethod
    def either(self, left_fun, right_fun):
        """
        Execute the left_fun(err) on Left, right_fun(value) on Right
        """

    @abstractmethod
    def default(self, default):
        """
        Returns the value if right, default value if left.
        """

    @abstractmethod
    def is_left(self):
        """
        True if the Either is left
        """

    def is_right(self):
        """
        True if the Either is right
        """
        return not self.is_left()

    @classmethod
    def lefts(cls, eithers):
        """
        Extract the lefts from the list

        >>> list(Either.lefts([Left(1), Right(2), Left(3)]))
        [Left(1), Left(3)]
        """
        return fp.ifilter(lambda m: m.is_left(), eithers)

    @classmethod
    def rights(cls, eithers):
        """
        Extract the rights from the list

        >>> list(Either.rights([Left(1), Right(2), Left(3)]))
        [Right(2)]
        """
        return fp.ifilter(lambda m: m.is_right(), eithers)


class Left(Either):
    def __init__(self, error):
        self.__error = error

    def bind(self, _):
        return self

    def either(self, left_fun, _):
        return left_fun(self.__error)

    def default(self, default):
        return default

    def __repr__(self):
        return "Left({0!r})".format(self.__error)

    def is_left(self):
        """
        True if Either is Left

        >>> Left(1).is_left()
        True

        >>> Left(1).is_right()
        False
        """
        return True


class Right(Either):
    def __init__(self, value):
        self.__value = value

    def bind(self, f):
        return f(self.__value)

    def either(self, _, right_fun):
        return right_fun(self.__value)

    def default(self, _):
        return self.__value

    def __repr__(self):
        return "Right({0!r})".format(self.__value)

    def is_left(self):
        """
        True if Either is Left

        >>> Right(1).is_left()
        False

        >>> Right(1).is_right()
        True
        """
        return False
