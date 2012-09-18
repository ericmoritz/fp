from unittest import TestCase
import fp


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


class TestContains(TestCase):

    def test(self):
        self.assertEquals(True,
                          fp.contains([1, 2], 1))

        self.assertEquals(True,
                          fp.contains({1, 2}, 2))

        self.assertEquals(True,
                          fp.contains({"one": 1}, "one"))


# mimics the signature of Python's in operator
class TestIn_(TestCase):

    def test(self):
        self.assertEquals(True,
                          fp.in_(1, [1, 2]))

        self.assertEquals(True,
                          fp.in_(2, {1, 2}))

        self.assertEquals(True,
                          fp.in_("one", {"one": 1}))


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


class TestCaseOp(TestCase):
    def test(self):
        import re
        from fp import p, pp, c, case, identity, concat

        add_domain = p(concat, "https://example.com/")
        make_secure = p(re.sub, r"^http://", r"https://")

        sanitize_url = case(
            (pp(str.startswith, "http://"), make_secure),

            (pp(str.startswith, "/"), c(add_domain, pp(str.lstrip, "/"))),

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
            (pp(str.startswith, "http://"),
             make_secure),
            (pp(str.startswith, "/"),
             c(add_domain, pp(str.lstrip, "/"))),
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
            return op(a,b)

        sub_two = fp.pp(example, 2)

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


####
## Generators
####
class TestIChunk(TestCase):
    def test_fillvalue(self):
        self.assertEqual(
            [
                (1,2,3),
                (4,5,6),
                (7,8,9),
                (10, )
            ],
            list(fp.ichunk(3, xrange(1, 11)))
        )


    def test_fillvalue(self):
        self.assertEqual(
            [
                (1,2,3),
                (4,5,6),
                (7,8,9),
                (10,0,0)
            ],
            list(fp.ichunk(3, xrange(1, 11), fillvalue=0))
        )

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


class TestConst(TestCase):

    def test(self):
        one = fp.const(1)

        self.assertEqual(1, one())


class TestDrop(TestCase):

    def test(self):
        self.assertEqual(
            [3,4,5],
            list(fp.idrop(3, range(6))))


class TestDropWhile(TestCase):

    def test(self):
        lt = fp.lt
        p = fp.p
        idrop_while = fp.idropwhile

        self.assertEqual(
            [5, 6, 7, 8, 9, 10],
            list(idrop_while(
                lambda x: x < 5,
                xrange(0, 11))))

class TestTake(TestCase):

    def test(self):
        itake = fp.itake

        self.assertEqual(
            [1,2,3],
            list(
                itake(3, xrange(1, 10))))


class TestTakeWhile(TestCase):

    def test(self):
        itakewhile = fp.itakewhile

        def crashing_gen():
            yield 1
            yield 2
            yield 3
            yield 4
            raise Exception("crap")
            yield 5

        self.assertEqual(
            [1,2,3],
            list(itakewhile(
                lambda x: x < 4,
                crashing_gen())))


class TestIZip(TestCase):

    def test(self):
        izip = fp.izip

        self.assertEqual(
            [(1, 'a'),
             (2, 'b'),
             (3, 'c')],
            list(izip([1, 2, 3], 'abc')))


class TestZipWith(TestCase):

    def test(self):
        izip_with = fp.izip_with
        add = fp.add

        self.assertEqual(
            [7, 9, 11, 13, 15],
            list(izip_with(add,
                           xrange(1, 6),
                           xrange(6, 11))))


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
        t   = fp.t
        p   = fp.p
        c   = fp.c

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


class TestIChain(TestCase):
    def test(self):
        self.assertEqual([1, 2, 3, 4],
                         list(
                             fp.ichain(
                                 [
                                     xrange(1, 3),
                                     xrange(3, 5)
                                 ])))


class TestICompress(TestCase):
    def test(self):
        self.assertEqual(["A","C","E","F"],
                         list(
                             fp.icompress("ABCDEF",
                                                  [1, 0, 1, 0, 1, 1])))


class TestIGroupBy(TestCase):
    def test(self):
        imap     = fp.imap
        igroupby = fp.igroupby
        binfunc  = fp.binfunc
        odd      = fp.odd
        items    = [1,3,5,2,4,6] # items must be sorted
        grouped  = igroupby(odd, items)


        resolved = list(imap(
            binfunc(
                lambda k, g: (k, list(g))),
            grouped))

        self.assertEqual([
            (True, [1, 3, 5]),
            (False, [2, 4, 6]),
        ], resolved)

class TestKWUnary(TestCase):
    def test_simple(self):
        from fp import kwunary

        def func(a=None, b=None):
            return a + b

        mapper = kwunary(func)

        self.assertEqual(
            5,
            mapper({"a": 2, "b": 3})
        )

    def test_restricted(self):
        from fp import kwunary

        def func(a=None, b=None):
            return a + b

        mapper = kwunary(func, "a", "b")

        # a naive call using func(**kwargs)
        # would raise an error but put a bound
        # on which keys to use
        self.assertEqual(
            5,
            mapper({"a": 2, "b": 3, "c": 4})
        )
