import fp
from fp.monads.monad import Monad
from abc import ABCMeta, abstractmethod


class Either(Monad):
    __metaclass__ = ABCMeta

    @classmethod
    def ret(cls, value):
        return Right(value)

    @classmethod
    def fail(cls, exception):
        return Left(exception)

    @classmethod
    def lefts(cls, eithers):
        """
        Filter on the lefts

        >>> Either.lefts([Left(1), Right(2), Left(3)])
        [Left(1), Left(3)]
        """

    @classmethod
    def rights(cls, eithers):
        """
        Filter on the rights
        
        >>> Either.lefts([Left(1), Right(2), Left(3)])
        [Right(2)]
        """

    @abstractmethod
    def either(self, left_fun, right_fun):
        """
        Execute the left_fun(err) on Left, right_fun(value) on Right
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
