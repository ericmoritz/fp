"""
This module implements an IO monad.  Its usefulness in Python can be argued against (and
won easily) but it is implement for completeness.

>>> @io
... def printLn(x):
...     print(x)

The IO action is returned when calling printLn but nothing
is printed

>>> action = printLn("hi")
>>> isinstance(action, IO)
True

>>> action.run()
hi

Using bind:

>>> printLn("Hello").bind_(
... lambda: printLn("World")
... ).run()
Hello
World

>>> actions = [printLn("Hello"), printLn("World")]
>>> IO.sequence_(actions).run()
Hello
World

>>> action = IO.mapM_(printLn, ["Hello", "World"])
>>> action.run()
Hello
World

>>> _ = printLn("Hello").when(True).run()
Hello

>>> _ = printLn("Hello").when(False).run()

>>> _ = printLn("Hello").unless(False).run()
Hello

>>> _ = printLn("Hello").unless(True).run()

"""

from fp.monads.monad import Monad, MonadIter
from functools import wraps


def io(f):
    """
    The IO decorator that types a function as an IO arrow

    """
    @wraps(f)
    def inner(*args, **kwargs):
        return IO(lambda: f(*args, **kwargs))
    return inner


class IO(Monad):
    """
    This is the IO monad.  Useful in composing IO code

    """
    def __init__(self, action):
        self.__action = action

    @classmethod
    def ret(cls, value):
        return IO(lambda: value)

    def bind(self, f):
        def new_action():
            x = self.run()
            ioM = f(x)
            return ioM.run()
        return IO(new_action)


    @classmethod
    def fail(cls, exception):
        """
        The failure of an IO monad is an exception

        >>> IO.fail(KeyError("key"))
        Traceback (most recent call last):
            ...
        KeyError: 'key'
        """
        raise exception

    def run(self):
        return self.__action()
