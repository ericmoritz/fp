"""
The module provides the base class for Monads in Python.

Monads
"""

from abc import ABCMeta, abstractmethod
from fp import atom
from six import moves
import six

# atoms
noop = atom("noop")


class Monad(object):
    __metaclass__ = ABCMeta

    @classmethod
    @abstractmethod
    def ret(cls, value):
        """
        The return function for the monad
        """

    @abstractmethod
    def bind(self, f):
        """
        Pass the value of this monad into the action f
        """

    @classmethod
    @abstractmethod
    def fail(cls, error):
        """
        Return the failure case of the monad.
        """

    def bind_(self, f):
        """
        Call the action f, throwing away the value of this monad
        """
        return self.bind(lambda _: f())

    @classmethod
    def sequence(cls, ms):
        """
        execute the monadic actions in ms, returning the result

        >>> from fp.monads.maybe import Just, Nothing, Maybe
        >>> Maybe.sequence([Just(1), Nothing, Just(2)])
        Nothing

        >>> Maybe.sequence([Just(1), Just(2)])
        Just([1, 2])
        """
        ret = cls.ret([])

        def append_and_return(xs, x):
            xs.append(x)
            return xs

        for m in ms:
            ret = ret.bind(
                lambda xs: m.bind(
                    lambda x: cls.ret(append_and_return(xs, x))))
        return ret

    @classmethod
    def sequence_(cls, ms):
        """
        Execute the

        >>> from fp.monads.iomonad import printLn, IO
        >>> actions = [printLn("Hello"), printLn("World")]
        >>> IO.sequence_(actions).run()
        Hello
        World
        """
        def reducer(acc, m):
            return acc.bind_(lambda: m)
        return moves.reduce(
            reducer,
            ms,
            cls.ret(noop)
        )

    @classmethod
    def sequence_dict(cls, d):
        """
        Perform all the actions inside a dictionary and return the result

        >>> from fp.monads.maybe import Maybe, Just
        >>> Maybe.sequence_dict({"foo": Just(1), "bar": Just(2)})  == \
               Just({'foo': 1, 'bar': 2})
        True
        """
        ret = cls.ret({})

        def store_and_return(d, k, v):
            d[k] = v
            return d

        for k, m in six.iteritems(d):
            ret = ret.bind(
                lambda d: m.bind(
                    lambda v: cls.ret(store_and_return(d, k, v))))
        return ret

    @classmethod
    def mapM(cls, arrow, items):
        """
        Map an arrow accross a list of values:

        >>> from fp import p
        >>> from fp.monads.maybe import Maybe
        >>> maybe_int = p(Maybe.catch, int)
        >>> Maybe.mapM(maybe_int, ["1", "2"])
        Just([1, 2])

        >>> Maybe.mapM(maybe_int, ["1", "a"])
        Nothing
        """
        return cls.sequence(moves.map(arrow, items))

    @classmethod
    def mapM_(cls, arrow, items):
        """
        >>> from fp.monads.iomonad import IO, printLn
        >>> action = IO.mapM_(printLn, ["Hello", "World"])
        >>> action.run()
        Hello
        World

        >>> action = IO.mapM_(printLn, ["Hello", "World"])
        >>> action.run()
        Hello
        World
        """
        return cls.sequence_(moves.map(arrow, items))

    @classmethod
    def arrow_cl(cls, arrow1, arrow2):
        """Left to Right arrow composition

        This expressions means: maybe cast the string as an int, then
        maybe add 1

        >>> from fp.monads.maybe import Maybe, Just
        >>> from fp import p
        >>> maybe_int = p(Maybe.catch, int)
        >>> string_to_plus = Maybe.arrow_cl(maybe_int, lambda x: Just(x+1))
        >>> string_to_plus("1")
        Just(2)

        >>> string_to_plus("a")
        Nothing
        """

        return lambda x: arrow1(x).bind(arrow2)

    @classmethod
    def arrow_cr(cls, arrow1, arrow2):
        """Right to Left arrow composition

        This expression means the same as: maybe cast the string as an
        int, then maybe add 1 but read right to left.

        >>> from fp.monads.maybe import Maybe
        >>> from fp import p
        >>> maybe_int = p(Maybe.catch, int)
        >>> string_to_plus = Maybe.arrow_cr(lambda x: Maybe(x+1), maybe_int)
        >>> string_to_plus("1")
        Just(2)
        """
        return cls.arrow_cl(arrow2, arrow1)

    @classmethod
    def ap(cls, f, *monads, **kwarg_monads):
        """
        Monad.ap(f, *args, **kwargs) allows you to call a pure
        function within a Monad.

        A normal function like `f(x): x + 1` can be made to take a
        Maybe and return a Maybe without any boilerplating:

        >>> from fp.monads.maybe import Maybe, Just, Nothing
        >>> Maybe.ap(lambda x: x+1, Just(1))
        Just(2)

        >>> Maybe.ap(lambda x: x+1, Nothing)
        Nothing

        Here's an example with an add function:

        >>> import operator
        >>> Maybe.ap(operator.add, Just(1), Just(2))
        Just(3)

        >>> Maybe.ap(operator.add, Nothing, Just(2))
        Nothing

        >>> Maybe.ap(operator.add, Just(1), Nothing)
        Nothing

        It even works with kwargs:

        >>> from datetime import timedelta
        >>> Maybe.ap(timedelta, days=Just(1), seconds=Just(60))
        Just(datetime.timedelta(1, 60))
        """

        argsM = cls.sequence(monads)
        kwargsM = cls.sequence_dict(kwarg_monads)

        return argsM.bind(
            lambda args: kwargsM.bind(
                lambda kwargs: cls.ret(f(*args, **kwargs))))

    @classmethod
    def filterM(cls, predM, items):
        """
        >>> from fp.monads.maybe import Maybe
        >>> from fp import even, c, p
        >>> maybeInt = p(Maybe.catch, int) # convert int to a Maybe arrow
        >>> maybeEven = p(Maybe.ap, even) # lift even into Maybe
        >>> Maybe.filterM(c(maybeEven, maybeInt), ["x","1","2","3","4"])
        Just(['2', '4'])
        """
        ret = []

        for x in items:
            def filterArrow(b):
                if b:
                    ret.append(x)
            boolM = predM(x)
            boolM.bind(filterArrow)
        return cls.ret(ret)

    def when(self, b):
        """
        Execute the action when True, return a noop otherwise

        >>> from fp.monads.iomonad import printLn
        >>> _ = printLn("Hello").when(True).run()
        Hello

        >>> _ = printLn("Hello").when(False).run()
        """
        cls = self.__class__
        noopM = cls.ret(noop)

        if b:
            return self.bind_(lambda: noopM)
        else:
            return noopM

    def unless(self, b):
        """
        Execute the action when False, return a noop otherwise

        >>> from fp.monads.iomonad import printLn
        >>> _ = printLn("Hello").unless(False).run()
        Hello

        >>> _ = printLn("Hello").unless(True).run()
        """
        return self.when(not b)

    @classmethod
    def catch(cls, f, *args, **kwargs):
        """
        Execute the function f(*args, **kwargs) and return the value inside the
        monad.

        Catch any errors and call the monad's fail method

        >>> from fp.monads.maybe import Maybe
        >>> from fp.monads.either import Either
        >>> from fp.monads.iomonad import IO

        >>> Maybe.catch(lambda: {'foo': 'bar'}['foo'])
        Just('bar')

        >>> Maybe.catch(lambda: {}['foo'])
        Nothing

        >>> Either.catch(lambda: {'foo': 'bar'}['foo'])
        Right('bar')

        >>> Either.catch(lambda: {}['foo'])
        Left(KeyError('foo',))

        >>> IO.catch(lambda: {'foo': 'bar'}['foo']).run()
        'bar'

        >>> IO.catch(lambda: {}['foo']).run()
        Traceback (most recent call last):
            ...
        KeyError: 'foo'
        """
        try:
            return cls.ret(f(*args, **kwargs))
        except Exception as e:
            return cls.fail(e)


class MonadPlus(object):
    """
    MonadPlus allows a Monad to define what a zero result is and a
    method for adding two MonadPlus instances together.
    """

    __metaclass__ = ABCMeta

    mzero = NotImplemented  # MonadPlus sub-classes need to define mzero

    @abstractmethod
    def mplus(self, y):
        """
        An associative operation
        """

    @classmethod
    def msum(cls, xs):
        """
        Reduces a list of MonadPlus instances using its mplus method:

        >>> from fp.monads.maybe import Just, Nothing, Maybe
        >>> Maybe.msum([Just(1), Nothing, Just(2)])
        Just(1)

        >>> Maybe.msum([Nothing, Nothing, Just(2)])
        Just(2)

        >>> Maybe.msum([Nothing, Nothing, Nothing])
        Nothing

        """
        return moves.reduce(
            cls.mplus,
            xs,
            cls.mzero)

    def mfilter(self, pred):
        """
        Returns Monad.mzero if the pred is False.

        >>> from fp.monads.maybe import Just
        >>> from fp import even
        >>> Just(4).mfilter(even)
        Just(4)

        >>> Just(3).mfilter(even)
        Nothing
        """

        cls = self.__class__

        def inner(x):
            if pred(x):
                return cls.ret(x)
            else:
                return cls.mzero

        return self.bind(inner)

    @classmethod
    def guard(cls, b):
        """
        >>> from fp.monads.maybe import Maybe
        >>> Maybe.guard(True).bind_(lambda: Maybe.ret("Hello"))
        Just('Hello')

        >>> Maybe.guard(False).bind_(lambda: Maybe.ret("Hello"))
        Nothing
        """
        if b:
            return cls.ret(noop)
        else:
            return cls.mzero
