:mod:`fp` --- A collection of functional programming inspired utilities
=======================================================================

.. module:: fp
   :synopsis: A collection of functional programming inspired
              utilities
.. moduleauthor:: Eric Moritz <eric@themoritzfamily.com>
.. versionadded:: 0.1

the :mod:`fp` module provides a collection of functional programming
inspired utilities.

this module supplements the core :mod:`operator`, :mod:`functools`,
and :mod:`itertools` modules.

**Higher-Order Functions**

Included with :mod:`fp` are higher-order functions which supplement
those provided by :mod:`functools`.

.. py:function:: fp.p(func : callable[, *args][, **keywords])

   Alias of `functools.partial`

.. autofunction:: fp.pp

.. autofunction:: fp.c

.. autofunction:: fp.const

.. autofunction:: fp.callreturn

.. autofunction:: fp.kwfunc

.. autofunction:: fp.identity

**Iterators**

These provide a common set of iterators to supplement the built-in
:mod:`itertools` module.

.. autofunction:: fp.itake

.. autofunction:: fp.idrop

.. autofunction:: fp.isplitat

.. autofunction:: fp.izipwith

**Reducers**

.. autofunction:: fp.allmap

.. autofunction:: fp.anymap

**Predicates**

.. autofunction:: fp.even

.. autofunction:: fp.odd
