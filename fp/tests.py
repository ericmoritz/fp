from unittest import TestCase as BaseTestCase
from collections import Iterator
import fp
import operator as op


class TestCase(BaseTestCase):
    def assert_iterator(self, obj):
        self.assertIsInstance(obj, Iterator)


##
# Operator tests
##
class TestCaseOp(TestCase):
    def test(self):
        import re
        from fp import p, ap, c, case, identity
        from operator import concat

        add_domain = p(concat, "https://example.com/")
        make_secure = p(re.sub, r"^http://", r"https://")

        sanitize_url = case(
            (ap(str.startswith, "http://"), make_secure),

            (ap(str.startswith, "/"), c(add_domain, ap(str.lstrip, "/"))),

            (True, add_domain),
        )
        self.assertEqual(
            "https://example.com/",
            sanitize_url("http://example.com/"))

        self.assertEqual(
            "https://example.com/test.htm",
            sanitize_url("/test.htm")
        )
        self.assertEqual(
            "https://example.com/test.htm",
            sanitize_url("test.htm")
        )

        # describe a case function using a list of rules rather than
        # arguments
        rules = [
            (ap(str.startswith, "http://"),
             make_secure),
            (ap(str.startswith, "/"),
             c(add_domain, ap(str.lstrip, "/"))),
            (True,
             add_domain),
        ]
        sanitize_url2 = case(rules)

        self.assertEqual(
            "https://example.com/",
            sanitize_url2("http://example.com/"))

        self.assertEqual(
            "https://example.com/test.htm",
            sanitize_url2("/test.htm")
        )

        self.assertEqual(
            "https://example.com/test.htm",
            sanitize_url2("test.htm")
        )

    def test_unmatched(self):
        from fp import ap, case, const
        from operator import lt
        op = case([
            (ap(lt, 0), const(True))
        ])

        self.assertRaises(RuntimeError, op, 1)


class TestGetItem(TestCase):
    def test(self):
        x = {"foo": 1}

        self.assertEqual(
            1,
            fp.getitem(x, "foo")
        )

        self.assertEqual(
            None,
            fp.getitem(x, "bar")
        )

        self.assertEqual(
            0,
            fp.getitem(x, "bar", default=0)
        )


class TestSetItem(TestCase):
    def test(self):
        x = {}
        self.assertEqual(
            {"foo": 1},
            fp.setitem(x, "foo", 1)
        )


class TestDelItem(TestCase):
    def test(self):
        x = {"foo": 1}
        self.assertEqual(
            {},
            fp.delitem(x, "foo")
        )

        self.assertEqual(
            {},
            fp.delitem({}, "foo")
        )
##
# Partials
##


class TestPartial(TestCase):

    def test(self):
        add_three = fp.p(op.add, 3)

        self.assertEqual(6, add_three(3))


class TestPartialPrepend(TestCase):
    def test(self):
        def example(a, b, op=op.sub):
            return op(a, b)

        sub_two = fp.ap(example, 2)

        self.assertEqual(4, sub_two(6))
        self.assertEqual(-2, sub_two(0))
        self.assertEqual(20, sub_two(10, op=op.mul))


class TestCompose(TestCase):

    def test(self):
        from fp import c, p
        from operator import mul, add

        add_three_and_double1 = c(
            lambda x: x * 2,

            lambda x: x + 3)

        add_three_and_double2 = c(p(mul, 2),
                                  p(add, 3))

        self.assertEqual(10,
                         add_three_and_double1(2))

        self.assertEqual(10,
                         add_three_and_double2(2))


class TestThread(TestCase):

    def test(self):
        from fp import t, p
        from operator import mul, add

        add_three_and_double1 = t([
            lambda x: x + 3,
            lambda x: x * 2])

        add_three_and_double2 = t([p(add, 3),
                                   p(mul, 2)])

        self.assertEqual(10,
                         add_three_and_double1(2))

        self.assertEqual(10,
                         add_three_and_double2(2))


class TestConst(TestCase):

    def test(self):
        say_hi = fp.const("hi")

        self.assertEqual("hi",
                         say_hi(1, a=1))


class TestFlip(TestCase):

    def test(self):
        def f(x, y):
            return x, y

        self.assertEqual((2, 1),
                         fp.flip(f)(1, 2))


class TestIdentity(TestCase):

    def test(self):
        self.assertEqual(1,
                         fp.identity(1))


####
## Generator functions
####


class TestISlice(TestCase):

    def test_badarglen(self):
        self.assertRaises(TypeError, fp.islice)
        self.assertRaises(TypeError, fp.islice, 1, 2, 3, 4, 5)

    def test_start(self):
        result = fp.islice(
            1, xrange(5)
        )

        self.assert_iterator(result)
        self.assertEqual(
            [1, 2, 3, 4],
            list(result)
        )

    def test_start_stop(self):
        result = fp.islice(
            1, 3, xrange(5)
        )

        self.assert_iterator(result)
        self.assertEqual(
            [1, 2],
            list(result)
        )

    def test_start_stop_step(self):
        result = fp.islice(
            1, None, 2,
            xrange(10)
        )

        self.assert_iterator(result)


class TestITake(TestCase):

    def test(self):
        result = fp.itake(3, xrange(0, 10))

        self.assert_iterator(result)

        self.assertEqual(
            [0, 1, 2],
            list(result)
        )


class TestIDrop(TestCase):

    def test(self):
        self.assertEqual(
            [3, 4, 5],
            list(fp.idrop(3, range(6))))


class TestFirst(TestCase):
    def test(self):
        self.assertEqual(1,
                         fp.first(xrange(1, 10)))

    def test_empty(self):
        self.assertRaises(StopIteration, fp.first, [])


class TestIRest(TestCase):
    def test(self):
        rest = fp.irest(xrange(1, 10))

        self.assert_iterator(rest)

        self.assertEqual([2, 3, 4, 5, 6, 7, 8, 9],
                         list(rest))


class TestISplitAt(TestCase):
    def test(self):
        result = fp.isplitat(
            2,
            [0,1,2,3,4]
        )

        self.assert_iterator(result)

        consumed = [list(sub) for sub in result]

        self.assertEqual(
            [[0,1], [2,3,4]],
            consumed
        )


class TestZipWith(TestCase):

    def test(self):
        from operator import add

        result = fp.izipwith(
            add,
            [1, 2, 3],
            [2, 3, 4]
        )

        self.assert_iterator(result)
        self.assertEqual(
            [3, 5, 7],
            list(result)
        )


class TestIChain(TestCase):
    def test(self):
        result = fp.ichain([
            [1, 2],
            [3, 4]
        ])

        self.assert_iterator(result)

        self.assertEqual(
            [1, 2, 3, 4],
            list(result)
        )


class TestIChunk(TestCase):

    def test(self):
        result = fp.ichunk(
            3,
            xrange(1, 10)
        )

        self.assert_iterator(result)

        self.assertEqual(
            [
                (1, 2, 3),
                (4, 5, 6),
                (7, 8, 9),
            ],
            list(result)
        )

    def test_uneven(self):
       result = fp.ichunk(
           3,
           xrange(1, 11)
       )

       self.assert_iterator(result)

       self.assertEqual(
           [
               (1, 2, 3),
               (4, 5, 6),
               (7, 8, 9),
               (10, )
           ],
           list(result)
       )

    def test_fillvalue(self):
        self.assertEqual(
            [
                (1, 2, 3),
                (4, 5, 6),
                (7, 8, 9),
                (10, 0, 0)
            ],
            list(fp.ichunk(3, xrange(1, 11), fillvalue=0))
        )

    def test_fillvalue_even(self):
        self.assertEqual(
            [
                (1, 2, 3),
                (4, 5, 6),
                (7, 8, 9),
             ],
            list(fp.ichunk(3, xrange(1, 10), fillvalue=0))
        )

    def test_empty(self):
        self.assertEqual(
            [],
            list(fp.ichunk(2, []))
        )


##
# Reducers
##

class TestDictUpdate(TestCase):
    def test(self):
        start = {}
        result = fp.dictupdate(
            start,
            [
                ("key1", "val1"),
                ("key2", "val2"),
            ]
        )

        self.assertEqual(
            {"key1": "val1",
             "key2": "val2"},
            result)

        # mergedict updates in place, start is the same dict as result
        self.assertIs(start, result)

# bookmark


class TestAllMap(TestCase):

    def test(self):
        from fp import even, odd, allmap

        self.assertTrue(allmap(even, xrange(2, 10, 2)))
        self.assertFalse(allmap(odd, xrange(2, 10, 2)))


class TestAnyMap(TestCase):
    def test(self):
        from fp import even, odd, anymap

        self.assertTrue(anymap(even, [2,3,4]))
        self.assertFalse(anymap(odd, [2,4,6]))


class TestGetter(TestCase):

    def test(self):
        from fp import getitem, t, c

        get_city = fp.getter("addresses", 0, "city")

        self.assertEqual("Reston",
                         get_city({"addresses": [{"city": "Reston"}]}))

        self.assertEqual(None,
                         get_city({"addresses": []}))

        self.assertEqual(None,
                         get_city({"addresses": [{}]}))




class TestKWUnary(TestCase):
    def test_simple(self):
        from fp import kwfunc

        def func(a=None, b=None):
            return a + b

        mapper = kwfunc(func)

        self.assertEqual(
            5,
            mapper({"a": 2, "b": 3})
        )

    def test_restricted(self):
        from fp import kwfunc

        def func(a=None, b=None):
            return a + b

        mapper = kwfunc(func, "a", "b")

        # a naive call using func(**kwargs)
        # would raise an error but put a bound
        # on which keys to use
        self.assertEqual(
            5,
            mapper({"a": 2, "b": 3, "c": 4})
        )

####
## predicates
####
class TestEven(TestCase):
    def test(self):
        self.assertTrue(fp.even(2))
        self.assertFalse(fp.even(1))


class TestOdd(TestCase):
    def test(self):
        self.assertFalse(fp.odd(2))
        self.assertTrue(fp.odd(1))


class TestIsNone(TestCase):
    def test(self):
        self.assertTrue(fp.is_none(None))
        self.assertFalse(fp.is_none(False))


class TestNotNone(TestCase):
    def test(self):
        self.assertFalse(fp.not_none(None))
        self.assertTrue(fp.not_none(False))
