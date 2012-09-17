This project aims to build a standard collection of functional
programming inspired tools to Python.

# Goals

 * Provide the tools to decoratively compose functions using
   `partial`, `compose` and `thread` seen often in FP.
 * Provide a collection of useful predicates and operator functions to
   use with higher-order functions
 * Provide a collection of common higher-order functions usually
   bundled with functional languages
 * Provide a common interface to existing tools that makes using
   partials with higher-order functions more natural

## Partial, Compose, and Thread

### Partial

`functools` provides the `p(f, *args, **kwargs)` function which
will create a partial application of the function `f`.

The `p` function is implemented using the built-in functools.partial
function bundled with Python and is simply a shorten alias to that
function.

Partials enable you to construct functions with constant arguments.

    >>> from functools2 import mul, p
    >>> times_two = p(mul, 2) # multiply x by two
    >>> times_two(5)
    10

Partial allows you to construct predicates which are self documenting

   >>> from functool2 import ifilter, p, eq
   >>> is_eric = p(eq, "Eric Moritz")
   >>> only_eric = ifilter(is_eric, ["Eric Moritz", "John Doe"])
   >>> list(only_eric)
   ["Eric Moritz"]

`ifilter` is a generator which only yields values which the predicate
passes; list() is needed to resolve the generator to a list.

Partial allows you to map function which normally takes more than one
argument:

    from functools2 import imap, p
    from datetime import date
    import calendar
    
    
    def days_in_month(year, month):
         _, days_in_month = calendar.monthrange(year, month)
         return imap(
              p(date, year, month),
              xrange(1, days_in_month+1)
         )


### Compose 

Another function that is found in functional programming is a compose
function.  This enables the creation of a function which is the
composition of multiple unary functions.

Here's how you would express (x + 3) * 2:

     from functools2 import mul, add, p, c
     
     add_three_and_double = c(p(mul, 2), p(add, 3))
     assert add_three_and_double(2) == 10)


c() is right associative so p(add, 3) is applied first and then
p(mul, 2) is applied.


This is obviously a terrible example of what is essentially
`lambda x: (x + 3) * 2` but becomes powerful with more complex
compositions which would look like:


     # buggy way
     def dosomething(x):
        x1 = do1(x)
        x2 = do2(x1)
        return do3(x2)

     # ugly way
     def dosomething(x):
         return do3(do2(do1(x)))
        
     # simple way
     dosomething = c(do2, c(do2, do1))

Doing work-flows with compose is confusing because it is right
associative.  For that there is the thread function

### Thread

The final function composition is the thread function.  It does a
similar job as c() but is left associative.

    dosomething = t([do1, do2, do3])
    

## Operators

Every operator in Python will be mirrored in `functools2`.  In most
cases these operators are simply mirrors of the function in the
`operator` module.

## Lazily loading generators

Functional languages provide powerful primitives for consuming
sequences of data.  Languages like Clojure and Haskell provide a way
to lazily compose these primitives so that iteration is occurs N-times
rather than N*M-times where M is the number of things happening to
those sequences.

Here is an example in Python:

    x_times_two = [x*2 for x in xrange(10)]
    x_plus_one  = [x+1 for x in x_times_two]
    
The code above iterates does 20 iterations, 10 to produce x_times_two
10 to produce x_plus_one.  

Python provides generators to lazily consume iterables.  Here is the
same result which only does 10 iterations:

    x_times_two = (x*2 for x in xrange(10))
    x_plus_one  = [x+1 for x in x_times_two]
    
Now, `x_times_two` is only a temporary variable, so we could rewrite
this algorithm using t():

    # create our thread of generators
    itimestwo_plus_one  = t([
         lambda iterable: (x*2 for x in iterable),
         lambda iterable: (x+1 for x in iterable) 
    ])
    
    # apply our algorithm over xrange(10) 
    x_times_two_plus_one = list(
        itimestwo_plus_one(
            xrange(10)
        )
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

All generators defined in `functools2` start with an "i" to tell you
than it lazily operates over an iterable.  These generators all take
an iterator as there final argument to enable the use of p() to
produce partials in functional compositions.
