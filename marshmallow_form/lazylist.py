#############################################################################
#
# Copyright (c) 2006 Zope Corporation. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Visible Source
# License, Version 1.0 (ZVSL).  A copy of the ZVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Lazy List 
"""

import itertools

unspecified = object()


class LazyList(object):
    def __init__(self, iterable, length=unspecified):
        self.length = length
        self.iterator = iter(iterable)
        try:
            self.len = iterable.__len__
        except AttributeError:
            self.len = unspecified
        self.data = []

    def __add__(self, other):
        return LazyList(itertools.chain(self, other))

    def __radd__(self, other):
        return LazyList(itertools.chain(self, other))

    def __getslice__(self, i1, i2):
        result = []
        for i in range(i1, i2):
            try:
                result.append(self[i])
            except IndexError:
                break

        return result

    def __nonzero__(self):
        try:
            self[0]
        except IndexError:
            return False

        return True

    def __repr__(self):
        return '<' + self.__class__.__name__ + ' ' + repr(list(self)) + '>'

    def __getitem__(self, index):
        i = index
        # handle negative indices
        if i < 0:
            i += len(self)
        if i < 0:
            raise IndexError(index)

        # move through the input sequence mapping values until we get to the
        # requested index
        if len(self.data) <= i:
            for x in range(len(self.data), i + 1):
                try:
                    self.data.append(next(self.iterator))
                except StopIteration:
                    raise IndexError(index)

        return self.data[i]

    def __len__(self):
        if self.length is unspecified:
            if self.len is not unspecified:
                self.length = self.len()
            else:
                # This may be expensive, but we don't have a choice, I hope we
                # weren't given an infinite iterable.
                i = -1
                for i, x in enumerate(self):
                    pass
                self.length = i + 1

        if self.length is None:
            raise RuntimeError('Calling len() on this object is not allowed.')

        return self.length
