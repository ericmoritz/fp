from unittest import TestCase
import functools2


class TestAdd(TestCase):

    def test(self):
        self.assertEqual(4,
                         functools2.add(2, 2))


class TestConcat(TestCase):

    def test(self):
        self.assertEqual([1, 2],
                         functools2.concat([1], [2]))


class TestContains(TestCase):

    def test(self):
        self.assertEquals(True,
                          functools2.contains([1, 2], 1))

        self.assertEquals(True,
                          functools2.contains({1, 2}, 2))

        self.assertEquals(True,
                          functools2.contains({"one": 1}, "one"))


# mimics the signature of Python's in operator
class TestIn_(TestCase):

    def test(self):
        self.assertEquals(True,
                          functools2.in_(1, [1, 2]))

        self.assertEquals(True,
                          functools2.in_(2, {1, 2}))

        self.assertEquals(True,
                          functools2.in_("one", {"one": 1}))


class TestDiv(TestCase):

    def test(self):
        self.assertEquals(1.5,
                          functools2.div(3, 2))


class TestFloorDiv(TestCase):

    def test(self):
        self.assertEquals(1,
                          functools2.floordiv(3, 2))


class TestAnd(TestCase):

    def test(self):
        self.assertEquals(1,
                          functools2.and_(3, 1))

        self.assertIs(True,
                      functools2.and_(True, True))

        self.assertIs(False,
                      functools2.and_(True, False))


class TestXor(TestCase):

    def test(self):
        self.assertEquals(4,
                          functools2.xor(12, 8))

        self.assertIs(True,
                      functools2.xor(True, False))

        self.assertIs(False,
                      functools2.xor(True, True))

        self.assertIs(False,
                      functools2.xor(False, False))

