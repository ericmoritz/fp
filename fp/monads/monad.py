from abc import ABCMeta, abstractmethod
from fp import atom, p, identity
from six import moves
import six
from collections import namedtuple

# atoms
noop = atom("noop")

class Monad(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def bind(self, f):
        """
        Pass the value of this monad into the action f
        """

    def bind_(self, f):
        """
        Call the action f, throwing away the value of this monad
        """
        return self.bind(lambda _: f())

    @classmethod
    def reduce_sequence(cls, f, items, initial):
        """
        folds a list of monads over f starting with an initial monad
        """
        def reducer(ms, m):
            return m.bind(lambda x: ms.bind(
                          lambda xs: cls(f(xs, x))))
        return reduce(
            reducer,
            items,
            initial)
        
        
    @classmethod
    def sequence(cls, ms):
        """
        execute the monadic actions in ms, returning the result
        """
        ret = cls([])
        def append_and_return(xs, x):
            xs.append(x)
            return xs

        for m in ms:
            ret = ret.bind(
                lambda xs: m.bind(
                lambda x: cls(append_and_return(xs, x))))
        return ret

    @classmethod
    def sequence_(cls, ms):
        return reduce(cls.bind_, ms, cls(noop))
        
    @classmethod
    def sequence_dict(cls, d):
        """
        Perform all the actions inside a dictionary and return the result
        """
        ret = cls({})
        def store_and_return(d, k, v):
            d[k] = v
            return d

        for k, m in six.iteritems(d):
            ret = ret.bind(
                lambda d: m.bind(
                lambda v: cls(store_and_return(d, k, v))))
        return ret

    def sequence_dict_(cls, d):
        return cls.sequence_(six.itervalues(d))

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
            lambda kwargs: cls(f(*args, **kwargs))))
            

    @classmethod
    def filterM(cls, predM, items):
        ret = []
            
        for x in items:
            def filterArrow(b):
                if b:
                    ret.append(x)
            boolM = predM(x)
            boolM.bind(filterArrow)
        return cls(ret)

    
class MonadPlus(object):
    __metaclass__ = ABCMeta

    mzero = NotImplemented # MonadPlus sub-classes need to define mzero

    @abstractmethod
    def mplus(self, y):
        """
        An associative operation
        """

    @classmethod
    def msum(cls, xs):
        return reduce(
            cls.mplus,
            xs,
            cls.mzero)

    def mfilter(self, pred):
        cls = self.__class__
        def inner(x):
            if pred(x):
                return cls(x)
            else:
                return cls.mzero

        return self.bind(inner)

    @classmethod
    def guard(cls, b):
        """
        """
        if b:
            return cls(noop)
        else:
            return cls.mzero

    def when(self, b):
        cls = self.__class__
        noopM = cls(noop)

        if b:
            self.bind_(lambda: noopM)
        else:
            return noopM

    def unless(self, b):
        return self.when(not b)

class MonadIter(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __iter__(self):
        """
        """

    @classmethod
    @abstractmethod
    def from_iterable(cls, iterable):
        """
        """

if __name__ == '__main__':
    import pytest, sys
    sys.exit(pytest.main(["--doctest-modules", __file__]))
