:mod:`fp.monads` --- A collection of monads
================================================================================

.. module:: fp.monads
   :synopsis: A collection of monads
.. moduleauthor:: Eric Moritz <eric@themoritzfamily.com>
.. versionadded:: 0.1

the :mod:`fp.monads` module provides a collection of monads to use with
your Python code.  

*fp.monads.maybe**

:mod:`fp.monads` provides an implementation of the :class:`Maybe` monad.


.. autoclass:: fp.monads.maybe.Maybe
    :members:

*fp.monads.maybe**

:mod:`fp.monads` provides an implementation of the :class:`Either` monad.


.. autoclass:: fp.monads.either.Either
    :members:


*fp.monads.iomonad**

:mod:`fp.monads` provides an implementation of the :class:`IO` monad. 

.. autoclass:: fp.monads.iomonad.IO
    :members:


**fp.monads.monad**

Provides the base classes for implementeding Monads with :mod:`fp`.

.. autoclass:: fp.monads.monad.Monad
    :members:

.. autoclass:: fp.monads.monad.MonadPlus
    :members:

    .. property:: mzero

       Zero results

.. autoclass:: fp.monads.monad.MonadIter
    :members:

