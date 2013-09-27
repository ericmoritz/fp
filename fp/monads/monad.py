"""
The module provides the base class for Monads in Python.

Monads
"""

from abc import ABCMeta, abstractmethod
from fp import atom, p, identity
from six import moves
import six
from collections import namedtuple

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
        return cls.sequence(moves.map(arrow, items))

    @classmethod
    def mapM_(cls, arrow, items):
        return cls.sequence_(moves.map(arrow, items))

    @classmethod
    def arrow_cl(cls, arrow1, arrow2):
        """Left to Right arrow composition"""
        return lambda x: arrow1(x).bind(arrow2)

    @classmethod
    def arrow_cr(cls, arrow1, arrow2):
        """Right to Left arrow composition"""
        return cls.arrow_cl(arrow2, arrow1)

    @classmethod
    def ap(cls, f, *monads, **kwarg_monads):
        """
        apply a non-monadic function to the monads provided as arguments
        """
        argsM = cls.sequence(monads)
        kwargsM = cls.sequence_dict(kwarg_monads)
        
        return argsM.bind(
            lambda args: kwargsM.bind(
            lambda kwargs: cls.ret(f(*args, **kwargs))))
            

    @classmethod
    def filterM(cls, predM, items):
        ret = []
            
        for x in items:
            def filterArrow(b):
                if b:
                    ret.append(x)
            boolM = predM(x)
            boolM.bind(filterArrow)
        return cls.ret(ret)


    def when(self, b):
        cls = self.__class__
        noopM = cls.ret(noop)

        if b:
            return self.bind_(lambda: noopM)
        else:
            return noopM

    def unless(self, b):
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

        >>> getter = {"foo": "bar"}.__getitem__
        >>> Maybe.catch(getter, "foo")
        Just('bar')

        >>> Maybe.catch(getter, "baz")
        Nothing

        >>> Either.catch(getter, "foo")
        Right('bar')

        >>> Either.catch(getter, "baz")
        Left(KeyError('baz',))

        >>> IO.catch(getter, "foo").run()
        'bar'
        
        >>> IO.catch(getter, "baz")
        Traceback (most recent call last):
            ...
        KeyError: 'baz'
        """
        try:
            return cls.ret(f(*args, **kwargs))
        except Exception, e:
            return cls.fail(e)


class MonadPlus(object):
    """
    MonadPlus allows a Monad to define what a zero result is and a method for adding two MonadPlus
    instances together.
    """


    __metaclass__ = ABCMeta

    mzero = NotImplemented # MonadPlus sub-classes need to define mzero

    @abstractmethod
    def mplus(self, y):
        """
        An associative operation
        """

    @classmethod
    def msum(cls, xs):
        return moves.reduce(
            cls.mplus,
            xs,
            cls.mzero)

    def mfilter(self, pred):
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
        """
        if b:
            return cls.ret(noop)
        else:
            return cls.mzero

class MonadIter(object):
    """
    Provides the functionality to abuse list comprehensions
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def __iter__(self):
        """
        Exposes the contained value as an iterable object
        """

    @classmethod
    @abstractmethod
    def from_iterable(cls, iterable):
        """
        Converts an iterable into a Monad
        """

    @classmethod
    def do(cls, iterable):
        """
        An alias for from_iterable
        """
        return cls.from_iterable(iterable)
