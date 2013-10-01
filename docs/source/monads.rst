:mod:`fp.monads` --- A collection of monads
================================================================================

.. module:: fp.monads
   :synopsis: A collection of monads
.. moduleauthor:: Eric Moritz <eric@themoritzfamily.com>
.. versionadded:: 0.1

the :mod:`fp.monads` module provides a collection of monads to use with
your Python code.  

**Maybe**

:mod:`fp.monads` provides an implementation of the :class:`Maybe` monad.


.. autoclass:: fp.monads.maybe.Maybe
    :members:

**Either**

:mod:`fp.monads` provides an implementation of the :class:`Either` monad.


.. autoclass:: fp.monads.either.Either
    :members:


**IO**

:mod:`fp.monads` provides an implementation of the :class:`IO` monad. 

.. autoclass:: fp.monads.iomonad.IO
    :members:


**Base Monad classes**

Use the following classes for defining your own monads.

.. autoclass:: fp.monads.monad.Monad
    :members:

.. autoclass:: fp.monads.monad.MonadPlus
    :members:

    .. property:: mzero

       Zero results

