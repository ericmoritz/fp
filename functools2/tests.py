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


class TestQuot(TestCase):

    def test(self):
        self.assertEquals(1,
                          functools2.quot(3, 2))


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


class TestPartial(TestCase):

    def test(self):
        add_three = functools2.p(functools2.add, 3)

        self.assertEqual(6, add_three(3))


class TestCompose(TestCase):

    def test(self):
        c = functools2.c
        p = functools2.p
        mul = functools2.mul
        add = functools2.add

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
        t = functools2.t
        p = functools2.p
        mul = functools2.mul
        add = functools2.add

        add_three_and_double1 = t([
            lambda x: x + 3,
            lambda x: x * 2])

        add_three_and_double2 = t([p(add, 3),
                                   p(mul, 2)])

        self.assertEqual(10,
                         add_three_and_double1(2))

        self.assertEqual(10,
                         add_three_and_double2(2))


class TestIAND(TestCase):
    def test(self):
        def crashing_gen():
            yield True
            yield False
            raise Exception("crap")
            yield True

        self.assertFalse(functools2.iand(crashing_gen()))
        self.assertTrue(functools2.iand([True, True, True]))


class TestIAll(TestCase):

    def test(self):
        iall = functools2.iall
        even = functools2.even
        odd = functools2.odd

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
        self.assertTrue(functools2.ior([True, False, True]))
        self.assertFalse(functools2.ior([False, False, False]))

        def crashing_gen():
            yield False
            yield True
            raise Exception("crap")
            yield False

        self.assertTrue(functools2.ior(crashing_gen()))


class TestIAny(TestCase):

    def test(self):
        iany = functools2.iany
        even = functools2.even
        odd = functools2.odd

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
        iadd = functools2.iadd

        self.assertEqual("eric",
                         iadd(["er", "ic"]))

        self.assertEqual([1, 2, 3, 4],
                         iadd([[1, 2], [3, 4]]))


class TestIConcatMap(TestCase):

    def test(self):
        iconcat_map = functools2.iconcat_map

        self.assertEqual(
            "1234",
            iconcat_map(str, [1,2, 3,4]))


class TestConst(TestCase):

    def test(self):
        one = functools2.const(1)

        self.assertEqual(1, one())


class TestDrop(TestCase):

    def test(self):
        self.assertEqual(
            [3,4,5],
            list(functools2.idrop(3, range(6))))


class TestDropWhile(TestCase):

    def test(self):
        lt = functools2.lt
        p = functools2.p
        idrop_while = functools2.idropwhile

        self.assertEqual(
            [5, 6, 7, 8, 9, 10],
            list(idrop_while(
                lambda x: x < 5,
                xrange(0, 11))))

class TestTake(TestCase):

    def test(self):
        itake = functools2.itake

        self.assertEqual(
            [1,2,3],
            list(
                itake(3, xrange(1, 10))))


class TestTakeWhile(TestCase):

    def test(self):
        itakewhile = functools2.itakewhile

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
        izip = functools2.izip

        self.assertEqual(
            [(1, 'a'),
             (2, 'b'),
             (3, 'c')],
            list(izip([1, 2, 3], 'abc')))


class TestZipWith(TestCase):

    def test(self):
        izip_with = functools2.izip_with
        add = functools2.add

        self.assertEqual(
            [7, 9, 11, 13, 15],
            list(izip_with(add,
                           xrange(1, 6),
                           xrange(6, 11))))


class TestGet(TestCase):

    def test_missing(self):
        self.assertEqual(None,
                         functools2.get("test", None))

        self.assertEqual(None,
                         functools2.get("test", {})),

        self.assertEqual(None,
                         functools2.get("test", [])),

        self.assertEqual(None,
                         functools2.get(0, [])),

        self.assertEqual(None,
                         functools2.get("a", set())),


    def test_exists(self):
        self.assertEqual("val",
                         functools2.get("test", {"test": "val"})),

        self.assertEqual("test",
                         functools2.get(0, ["test"])),

        self.assertEqual("a",
                         functools2.get("a", set("a"))),


class TestGetter(TestCase):

    def test(self):
        get = functools2.get
        t   = functools2.t
        p   = functools2.p

        get_address = functools2.getter("name")
        self.assertEqual("Eric",
                         get_address({"name": "Eric"}))

        get_city1 = t([
            p(get, "addresss"),
            p(get, 0),
            p(get, "city")])


        get_city2 = functools2.getter("addresses", 0, "city")

        self.assertEqual("Reston",
                         get_city1({"addresses": [{"city": "Reston"}]}))


        self.assertEqual("Reston",
                         get_city2({"addresses": [{"city": "Reston"}]}))

        self.assertEqual(None,
                         get_city2({"addresses": []}))

        self.assertEqual(None,
                         get_city2({"addresses": [{}]}))


class TestIChain(TestCase):
    def test(self):
        self.assertEqual([1, 2, 3, 4],
                         list(
                             functools2.ichain(
                                 [
                                     xrange(1, 3),
                                     xrange(3, 5)
                                 ])))


class TestICompress(TestCase):
    def test(self):
        self.assertEqual(["A","C","E","F"],
                         list(
                             functools2.icompress("ABCDEF",
                                                  [1, 0, 1, 0, 1, 1])))


class TestIGroupBy(TestCase):
    def test(self):
        imap     = functools2.imap
        igroupby = functools2.igroupby
        binfunc  = functools2.binfunc
        odd      = functools2.odd
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
