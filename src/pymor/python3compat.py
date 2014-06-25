import sys
import numbers
import numpy as np
if sys.version >= '3':
    xrange = range
    long = int

try:
    # python 2
    from itertools import izip
except ImportError:
    # python3
    izip = zip

Integer = (numbers.Integral, np.integer)
