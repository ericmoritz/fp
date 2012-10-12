This project aims to build a standard collection of functional
programming inspired tools to Python.

[![Build Status](https://secure.travis-ci.org/ericmoritz/fp.png)](http://travis-ci.org/ericmoritz/fp)

# Goals

 * Provide the functions to make compositions of functions using
   `partial`, `compose` and `thrush` seen often in FP.
 * Provide a collection of useful predicates and operator functions to
   use with higher-order functions
 * Provide a collection of common higher-order functions usually
   bundled with functional languages
 * Provide a common interface to existing tools that makes using
   partials with higher-order functions more natural

## Partial, Compose, and Thrush

### Partial

`fp` provides the `p(f, *args, **kwargs)` function which
will create a partial application of the function `f`.

The `p` function is implemented using the built-in `functools.partial`
function bundled with Python and is simply a shorten alias to that
function.

Partials enable you to construct functions with constant arguments.

    from fp import mul, p
    times_two = p(mul, 2) # multiply x by two
    assert times_two(5) == 10

Partial allows you to construct predicates which are self documenting

    from fp import p
    from itertools import ifilter
    from operator import eq

    is_eric = p(eq, "Eric Moritz")
    only_eric = ifilter(is_eric, ["Eric Moritz", "John Doe"])
    assert list(only_eric) == ["Eric Moritz"]

`ifilter` is a generator for which only yields values which the
predicate passes; list() is needed to resolve the generator to a list.

Partial allows you to map a functions which normally takes more than
one argument:

    from fp import p
    from itertools import imap
    from datetime import date
    import calendar
    

    def days_in_month(year, month):
         _, days_in_month = calendar.monthrange(year, month)
         return imap(
              p(date, year, month),
              xrange(1, days_in_month+1)
         )

A complement to `p` is  `ap` which is an appended
partial.  Constant arguments in an appended partial are appended to
the argument list when calling the partial:

    ap(date, 1)(2010, 10) == date(2010, 10, 1)
    
This enables you to fetch a list of values from a dictionary for
instance:

    get_name = ap(dict.get, "name")
    ["eric", "mark"] == map(get_name, [{"name": "eric"}, {"name": "mark"}])
    
    
### Compose 

Another function that is found in functional programming is a compose
function.  This enables the creation of a function which is the
composition of multiple unary functions.

Here's how you would express `(x + 3) * 2`:

     from fp import p, c
     from operator import mul, add
     
     add_three_and_double = c(p(mul, 2), p(add, 3))
     assert add_three_and_double(2) == 10


`c` is right associative so `p(add, 3)` is applied first and then
`p(mul, 2)` is applied.


This is obviously a terrible example of what is essentially
`lambda x: (x + 3) * 2` but its power is shown when used with more complex
compositions:


     # buggy way
     def dosomething(x):
        x1 = do1(x)
        x2 = do2(x1)
        return do3(x2)

     # ugly way
     def dosomething(x):
         return do3(do2(do1(x)))
        
     # the fp way
     dosomething = c(do3, c(do2, do1))

However doing workflows with compose is not as natural is it could
be. This is where the functional thread comes into play.

### Thrush

A Thrush composes a single function from sequence of functions.  It
does a similar job as `c` but is left associative.


    dosomething = t([do1, do2, do3])
    
    # both expressions have the same result
    assert do3(do2(do1(value))) == dosomething()


## Lazily loading generators

Functional languages provide powerful primitives for consuming
sequences of data.  Languages like Clojure and Haskell provide a way
to lazily compose these primitives so that iteration is occurs N-times
rather than N*M-times where M is the number of things happening to
those sequences.

Here is an example of the wrong way in Python:

    x_times_two = [x*2 for x in xrange(10)]
    x_plus_one  = [x+1 for x in x_times_two]
    
The code above iterates does 20 iterations, 10 to produce x_times_two
10 to produce x_plus_one.  

Python provides generators to lazily consume iterables.  Here is the
same result which only does 10 iterations:

    x_times_two = (x*2 for x in xrange(10))
    x_plus_one  = [x+1 for x in x_times_two]
    
Now, `x_times_two` is only a temporary variable and temporary
variables are error prone. We could rewrite this algorithm using t():

    # create our thread of generators
    itimestwo_plus_one  = t([
         lambda iterable: (x*2 for x in iterable),
         lambda iterable: (x+1 for x in iterable) 
    ])
    
    # apply our algorithm over xrange(10) 
    x_times_two_plus_one = list(
        itimestwo_plus_one(xrange(10))
    )
    
This functional thread can be implemented using a partial application
of imap:

    itimestwo_plus_one = t([
        p(imap, p(mul, 2)), # multiply all items by 2
        p(imap, p(add, 1))  # add 1 to each item
    ])

They all do the same thing, yet this final generator implementation is
going to be less error prone because you're simply describing
operations over a list rather than programming the operations over the
list.

All generators defined in `fp` start with an "i" to tell you
than it lazily operates over an iterable.  These generators all take
an iterator as there final argument to enable the use of p() to
produce partials to be used in functional compositions.
