from abc import ABCMeta, abstractmethod
from fp import atom, p, identity
from six import moves
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
    def sequence(cls, monad_list):
        """
        """
        ret = []
        for monad in monad_list:
            monad.bind(lambda x: ret.append(x))
        return ret

    @classmethod
    def sequence_(cls, monad_list):
        """
        """
        for monad in monad_list:
            monad.bind(lambda x: cls(noop))
        return cls(noop)

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
    def liftM(cls, f, *monads):
        """
        Lift a non-monadic function into the monad. 

        >>> from fp import even
        >>> from fp.monads.maybe import Maybe
        >>> Maybe.liftM(even, Maybe(1))
        Maybe(False)

        >>> Maybe.liftM(even, Maybe(2))
        Maybe(True)
        """
        pass
    
    def _liftM2(cls, f):
        def inner(m1, m2):
            return m1.bind(lambda x: 
                   m2.bind(lambda y:
                   f(x, y)))
        return inner

    @classmethod
    def _ap(cls, f):
        """
        """
        return p(cls.liftM2, identity)
    
    

    @classmethod
    def filterM(cls, predM, items):
        """
        >>> from fp.monads.maybe import Maybe
        >>> from fp import even, c
        >>> maybeInt = Maybe.error_to_nothing(int) # convert int to a Maybe arrow
        >>> maybeEven = Maybe.liftM(even) # lift even into Maybe
        >>> Maybe.filterM(c(maybeEven, maybeInt), ["x","1","2","3","4"])
        Maybe(['2', '4'])
        """
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
        >>> from fp.monads.maybe import Maybe
        >>> Maybe.guard(True)
        Maybe(noop)

        >>> Maybe.guard(False)
        Maybe(None)
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
