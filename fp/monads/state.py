from fp.monads.monad import Monad, noop


class State(Monad):
    """
    A State monad allows you to isolate state manipultaion within the context
    of a State monad.

    >>> get().bind(lambda x: State.ret(x+1)).run(0)
    (1, 0)

    >>> modify(lambda x: x+1).run(0)
    (noop, 1)

    >>> gets(lambda x: x+1).run(0)
    (1, 0)
    """

    def __init__(self, state_fun):
        self.__state_fun = state_fun

    def run(self, init):
        return self.__state_fun(init)

    def bind(self, f):
        def inner(s):
            v0, s0 = self.run(s)
            m = f(v0)
            return m.run(s0)
        return State(inner)

    @classmethod
    def ret(cls, value):
        return cls(lambda s: (value, s))


def get():
    return State(lambda s: (s, s))


def put(x):
    return State(lambda _: (noop, x))


def modify(f):
    return get().bind(
        lambda x: put(f(x)))


def gets(f):
    return get().bind(
        lambda x: State.ret(f(x)))
