:mod:`fp` --- A collection of functional programming inspired utilities
=======================================================================

.. module:: fp
   :synopsis: A collection of functional programming inspired
              utilities
.. moduleauthor:: Eric Moritz <eric@themoritzfamily.com>
.. versionadded:: 0.1

the :mod:`fp` module provides a collection of functional programming
inspired utilities which makes working with `iterators` easier. 

this module supplements the core :mod:`operator`, :mod:`functools`,
and :mod:`itertools` modules.

**Higher-Order Functions**

Included with :mod:`fp` are higher-order functions which supplement
those provided by :mod:`functools`.

.. py:function:: fp.p(func : callable[, *args][, **keywords])

   Alias of `functools.partial`

.. autofunction:: fp.pp

.. autofunction:: fp.c

.. autofunction:: fp.constantly

.. autofunction:: fp.callreturn

.. autofunction:: fp.kwfunc

.. autofunction:: fp.getter

**Operators**

Included with :mod:`fp` are operators which work with higher order
functions. These are supplemental functions or replacements for those
found in :mod:`operator`.

`getitem`, `setitem` and `delitem` are slightly different from the
versions in the :mod:`operator` module.

They exists to provide a common interface for
:class:`collections.MutableSequence` and
:class:`collections.MutableMapping` type objects.


.. autofunction:: fp.getitem

.. autofunction:: fp.setitem

.. autofunction:: fp.delitem

.. autofunction:: fp.identity

**Iterators**

These provide a common set of iterators to supplement the built-in
:mod:`itertools` module.

.. autofunction:: fp.itake

.. autofunction:: fp.idrop

.. autofunction:: fp.isplitat
