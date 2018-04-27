#
# I/O helper classes for Pints
#
# This file is part of PINTS.
#  Copyright (c) 2017-2018, University of Oxford.
#  For licensing information, see the LICENSE file distributed with the PINTS
#  software package.
#
from __future__ import absolute_import, division
from __future__ import print_function, unicode_literals
import os
import numpy as np

import pints


def load_samples(filename, n=None):
    """
    Loads samples from the given ``filename`` and returns a 2d numpy array
    containing them.

    If the optional argument ``n`` is given, the method assumes there are ``n``
    files, with names based on ``filename`` such that e.g. ``test.csv`` would
    become ``test_0.csv``, ``test_1.csv``, ..., ``test_n.csv``. In this case
    a list of 2d numpy arrays is returned.

    Assumes the first line in each file is a header.

    See also :meth:`save_samples()`.
    """
    # Define data loading method
    def load(filename):
        with open(filename, 'r') as f:
            lines = iter(f)
            next(lines)  # Skip header
            return np.asarray(
                [[float(x) for x in line.split(',')] for line in lines])

    # Load from filename directly
    if n is None:
        return load(filename)

    # Load from systematically named files
    n = int(n)
    if n < 1:
        raise ValueError(
            'Argument `n` must be `None` or an integer greater than zero.')
    parts = os.path.splitext(filename)
    filenames = [parts[0] + '_' + str(i) + parts[1] for i in range(n)]

    # Check if files exist before loading (saves times)
    for filename in filenames:
        if not os.path.isfile(filename):
            try:
                # Python 3
                raise FileNotFoundError('File not found: ' + filename)
            except NameError:
                # Python 2
                raise IOError('File not found: ' + filename)

    # Load and return
    return [load(filename) for filename in filenames]


def save_samples(filename, *sample_lists):
    """
    Stores one or multiple lists of samples at the path given by ``filename``.

    If one list of samples is given, the filename is used as is. If multiple
    lists are given, the filenames are updated to include ``_0``, ``_1``,
    ``_2``, etc.

    For example, ``save_samples('test.csv', samples)`` will store information
    from ``samples`` in ``test.csv``. Using
    ``save_samples('test.csv', samples_0, samples_1)`` will store the samples
    from ``samples_0`` to ``test_0.csv`` and ``samples_1`` to ``test_1.csv``.

    See also: :meth:`load_samples()`.
    """
    # Get filenames
    k = len(sample_lists)
    if k < 1:
        raise ValueError('At least one set of samples must be given.')
    elif k == 1:
        filenames = [filename]
    else:
        parts = os.path.splitext(filename)
        filenames = [parts[0] + '_' + str(i) + parts[1] for i in range(k)]

    # Check shapes
    i = iter(sample_lists)
    shape = np.asarray(next(i)).shape
    if len(shape) != 2:
        raise ValueError(
            'Samples must be given as 2d arrays (e.g. lists of lists).')
    for samples in i:
        if np.asarray(samples).shape != shape:
            raise ValueError('All sample lists must have same shape.')

    # Store
    filename = iter(filenames)
    header = ','.join(['"p' + str(j) + '"' for j in range(shape[1])])
    for samples in sample_lists:
        with open(next(filename), 'w') as f:
            f.write(header + '\n')
            for sample in samples:
                f.write(','.join([pints.strfloat(x) for x in sample]) + '\n')

