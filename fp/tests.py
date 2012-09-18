from unittest import TestCase as BaseTestCase
from collections import Iterator
import fp

class TestCase(BaseTestCase):
    def assert_iterator(self, obj):
        self.assertIsInstance(obj, Iterator)


##
# Operator tests
##

class TestAdd(TestCase):

    def test(self):
        self.assertEqual(4,
                         fp.add(2, 2))


class TestSub(TestCase):

    def test(self):
        self.assertEqual(2, fp.sub(4, 2))


class TestMul(TestCase):

    def test(self):
        self.assertEqual(10, fp.mul(5, 2))


class TestDiv(TestCase):

    def test(self):
        self.assertEquals(1.5,
                          fp.div(3, 2))


class TestQuot(TestCase):

    def test(self):
        self.assertEquals(1,
                          fp.quot(3, 2))


class TestPow(TestCase):

    def test(self):
        self.assertEquals(256,
                          fp.pow(2, 8))


class TestMod(TestCase):

    def test(self):
        self.assertEquals(3,
                          fp.mod(18, 5))


class TestNeg(TestCase):

    def test(self):
        self.assertEquals(-1,
                          fp.neg(1))

        self.assertEquals(1,
                          fp.neg(-1))


class TestConcat(TestCase):

    def test(self):
        self.assertEqual([1, 2],
                         fp.concat([1], [2]))

        self.assertEqual("abcdef",
                         fp.concat("abc", "def"))


class TestAnd(TestCase):

    def test(self):
        self.assertEquals(1,
                          fp.and_(3, 1))

        self.assertIs(True,
                      fp.and_(True, True))

        self.assertIs(False,
                      fp.and_(True, False))


class TestXor(TestCase):

    def test(self):
        self.assertEquals(4,
                          fp.xor(12, 8))

        self.assertIs(True,
                      fp.xor(True, False))

        self.assertIs(False,
                      fp.xor(True, True))

        self.assertIs(False,
                      fp.xor(False, False))


class TestOr(TestCase):

    def test(self):
        self.assertEqual(15,
                         fp.or_(8, 7))

        self.assertEqual(True,
                         fp.or_(True, False))

        self.assertEqual(True,
                         fp.or_(True, True))

        self.assertEqual(False,
                         fp.or_(False, False))


class TestInvert(TestCase):

    def test(self):
        self.assertEqual(-1,
                         fp.invert(0))


class TestNot(TestCase):

    def test(self):
        self.assertEqual(False, fp.not_(True))
        self.assertEqual(True, fp.not_(False))


class TestLT(TestCase):

    def test(self):
        self.assertEqual(True, fp.lt(5, 10))
        self.assertEqual(False, fp.lt(10, 5))
        self.assertEqual(False, fp.lt(5, 5))


class TestLE(TestCase):

    def test(self):
        self.assertEqual(True, fp.le(5, 10))
        self.assertEqual(False, fp.le(10, 5))
        self.assertEqual(True, fp.le(5, 5))


class TestEq(TestCase):

    def test(self):
        self.assertEqual(True, fp.eq(5, 5))
        self.assertEqual(False, fp.eq(10, 5))


class TestGT(TestCase):

    def test(self):
        self.assertEqual(True, fp.gt(10, 5))
        self.assertEqual(False, fp.gt(5, 10))
        self.assertEqual(False, fp.gt(5, 5))


class TestGE(TestCase):

    def test(self):
        self.assertEqual(True, fp.ge(10, 5))
        self.assertEqual(False, fp.ge(5, 10))
        self.assertEqual(True, fp.ge(5, 5))


# mimics the signature of Python's in operator
class TestIn_(TestCase):

    def test(self):
        self.assertEquals(True,
                          fp.in_(1, [1, 2]))

        self.assertEquals(True,
                          fp.in_(2, {1, 2}))

        self.assertEquals(True,
                          fp.in_("one", {"one": 1}))


class TestCaseOp(TestCase):
    def test(self):
        import re
        from fp import p, ap, c, case, identity, concat

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


##
# Partials
##


class TestPartial(TestCase):

    def test(self):
        add_three = fp.p(fp.add, 3)

        self.assertEqual(6, add_three(3))


class TestPartialPrepend(TestCase):
    def test(self):
        def example(a, b, op=fp.sub):
            return op(a, b)

        sub_two = fp.ap(example, 2)

        self.assertEqual(4, sub_two(6))
        self.assertEqual(-2, sub_two(0))
        self.assertEqual(20, sub_two(10, op=fp.mul))


class TestCompose(TestCase):

    def test(self):
        c = fp.c
        p = fp.p
        mul = fp.mul
        add = fp.add

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
        t = fp.t
        p = fp.p
        mul = fp.mul
        add = fp.add

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
class TestIZip(TestCase):

    def test(self):
        result = fp.izip(
            ["a", "b", "c"],
            [1, 2]
        )
        self.assert_iterator(result)

        self.assertEqual(
            [("a", 1), ("b", 2), ],
            list(result)
        )


class TestIZipLongest(TestCase):
    def test(self):

        result = fp.izip_longest(
            ["a", "b", "c"],
            [1, 2]
        )

        self.assert_iterator(result)

        self.assertEqual(
            [
                ("a", 1),
                ("b", 2),
                ("c", None)
            ],
            list(result)
        )

    def test_fillvalue(self):

        result = fp.izip_longest(
            ["a", "b", "c"],
            [1, 2],
            fillvalue=0
        )

        self.assert_iterator(result)

        self.assertEqual(
            [
                ("a", 1),
                ("b", 2),
                ("c", 0)
            ],
            list(result)
        )


class TestIMap(TestCase):
    def test(self):
        result = fp.imap(
            fp.p(fp.add, 1),
            xrange(3)
        )

        self.assert_iterator(result)
        self.assertEqual(
            [1, 2, 3],
            list(result)
        )


class TestIFilter(TestCase):

    def test(self):
        result = fp.ifilter(
            fp.even,
            xrange(3)
        )
        self.assert_iterator(result)
        self.assertEqual(
            [0,2],
            list(result)
        )


class TestICycle(TestCase):

    def test(self):
        result = fp.icycle(
            "ABC"
        )

        self.assert_iterator(result)

        self.assertEquals(
            ["A", "B", "C", "A","B", "C", "A"],
            list(fp.itake(7, result))
        )


class TestIRepeat(TestCase):

    def test(self):
        result = fp.irepeat(
            "Hi"
        )

        self.assert_iterator(result)

        self.assertEquals(
            ["Hi", "Hi", "Hi"],
            list(
                fp.itake(
                    3,
                    result
                )
            )
        )


class TestDropWhile(TestCase):

    def test(self):
        predicate = fp.ap(fp.lt, 5)
        result = fp.idropwhile(
            predicate,
            [1, 4, 5, 1, 3]
        )
        self.assert_iterator(result)

        self.assertEqual(
            [5, 1, 3],
            list(result)
        )


class TestTakeWhile(TestCase):

    def test(self):
        predicate = fp.ap(fp.lt, 4)
        result = fp.itakewhile(
            predicate,
            [1, 3, 4, 2, 1]
        )
        self.assert_iterator(result)
        self.assertEqual(
            [1, 3],
            list(result)
        )


class TestICompress(TestCase):
    def test(self):
        result = fp.icompress(
            "ABCDEF",
            [1, 0, 1, 0, 1, 1]
        )
        self.assert_iterator(result)
        self.assertEqual(["A", "C", "E", "F"],
                         list(result))


class TestISlice(TestCase):

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
        result = fp.izipwith(
            fp.add,
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


class TestIGroupBy(TestCase):
    def test(self):
        from fp import (
            imap,
            igroupby,
            odd)

        items = [1, 3, 5, 2, 4, 6]  # items must be sorted
        grouped = igroupby(odd, items)

        resolved = [(k, list(iterable))
                    for k, iterable in grouped]

        self.assertEqual([
            (True, [1, 3, 5]),
            (False, [2, 4, 6]),
        ], resolved)


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

# bookmark


class TestIAND(TestCase):
    def test(self):
        def crashing_gen():
            yield True
            yield False
            raise Exception("crap")
            yield True

        self.assertFalse(fp.iand(crashing_gen()))
        self.assertTrue(fp.iand([True, True, True]))


class TestIAll(TestCase):

    def test(self):
        iall = fp.iall
        even = fp.even
        odd = fp.odd

        self.assertTrue(iall(even, xrange(2, 10, 2)))
        self.assertFalse(iall(odd, xrange(2, 10, 2)))

        # ensure that iall is lazy
        def crashing_gen():
            yield 2
            yield 3
            raise Exception("crap")
            yield 4

        # if this returns false, that means we never get to the
        # exception in the generator
        self.assertFalse(iall(even, crashing_gen()))


class TestIOR(TestCase):

    def test(self):
        self.assertTrue(fp.ior([True, False, True]))
        self.assertFalse(fp.ior([False, False, False]))

        def crashing_gen():
            yield False
            yield True
            raise Exception("crap")
            yield False

        self.assertTrue(fp.ior(crashing_gen()))


class TestIAny(TestCase):

    def test(self):
        iany = fp.iany
        even = fp.even
        odd = fp.odd

        self.assertTrue(iany(even, xrange(1, 10)))
        self.assertFalse(iany(odd, xrange(2, 10, 2)))

        # ensure that iall is lazy
        def crashing_gen():
            yield 2
            raise Exception("crap")
            yield 3
            yield 4

        # if this returns false, that means we never get to the
        # exception in the generator
        self.assertTrue(iany(even, crashing_gen()))


class TestIAdd(TestCase):
    def test(self):
        iadd = fp.iadd

        self.assertEqual("eric",
                         iadd(["er", "ic"]))

        self.assertEqual([1, 2, 3, 4],
                         iadd([[1, 2], [3, 4]]))








class TestGet(TestCase):

    def test_missing(self):
        self.assertEqual(None,
                         fp.get("test", None))

        self.assertEqual(None,
                         fp.get("test", {})),

        self.assertEqual(None,
                         fp.get("test", [])),

        self.assertEqual(None,
                         fp.get(0, [])),

        self.assertEqual(None,
                         fp.get("a", set())),

    def test_exists(self):
        self.assertEqual("val",
                         fp.get("test", {"test": "val"})),

        self.assertEqual("test",
                         fp.get(0, ["test"])),

        self.assertEqual("a",
                         fp.get("a", set("a"))),


class TestGetter(TestCase):

    def test(self):
        get = fp.get
        t = fp.t
        p = fp.p
        c = fp.c

        get_city1 = t([
            p(get, "addresses"),
            p(get, 0),
            p(get, "city")])

        get_city2 = fp.getter("addresses", 0, "city")

        self.assertEqual("Reston",
                         get_city1({"addresses": [{"city": "Reston"}]}))

        self.assertEqual("Reston",
                         get_city2({"addresses": [{"city": "Reston"}]}))

        get_address = fp.getter("name")

        self.assertEqual("Eric",
                         get_address({"name": "Eric"}))

        self.assertEqual(None,
                         get_city2({"addresses": []}))

        self.assertEqual(None,
                         get_city2({"addresses": [{}]}))




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
