import itertools
import six

if six.PY3:
    ifilter = filter
else:
    ifilter = itertools.ifilter
