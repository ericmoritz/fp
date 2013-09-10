

class Monad(object):
    def bind(self, f):
        raise NotImplementedError()

    def bind_(self, f):
        return self.bind(lambda _: f())


class MonadIter(object):
    def __iter__(self):
        raise NotImplementedError()

    @classmethod
    def from_iterable(cls, iterable):
        raise NotImplementedError()
