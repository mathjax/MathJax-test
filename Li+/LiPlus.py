#!/usr/bin/env python
# -*- Mode: Python; tab-width: 2; indent-tabs-mode:nil; -*-
# vim: set ts=2 et sw=2 tw=80:
#
# Copyright (c) 2013 Design Science, Inc.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
@package LiPlus
<p>This module implements Lithium's algorithm where testcase are represented as
abstract class. The testcase class passed to LiPlus should implement the
following member functions:</p>

<ul>
<li>getIterable(): returns an iterable for the testcase elements. The elements
from this iterable must not be None.</li>
<li>mark(aElement): mark the element for removal.</li>
<li>unmark(aElement): unmark the element for removal.</li>
<li>remove(aElement): permanently remove the element from the testcase.</li>
</ul>

<p>See also <a href="http://www.squarefree.com/2007/09/15/introducing-lithium-a-testcase-reduction-tool/">Jesse's Lithium program</a>. For a detailed
description of the query complexity of Lithium, see also
<a href="http://www.maths-informatique-jeux.com/blog/frederic/?post/2013/01/22/Analysis-of-Lithium-s-algorithm">this blog post</a>.
</p>
"""

from collections import deque
from lxml import etree

class LiPlusException(Exception):
    """
    @class LiPlus:LiPlusException
    @brief A class used for LiPlus exception
    """
    def __init__(self, aValue):
        self.mValue = aValue
    def __str__(self):
        return repr(self.mValue)

class LiPlus:
    """
    @class LiPlus:LiPlus
    @brief The main LiPlus class
    """

    def __init__(self, aTestcase):
        self.initialize(aTestcase)

    def initialize(self, aTestcase):

        self.mTestcase = aTestcase

        # Get the testcase as a deque
        self.mElements = deque(self.mTestcase.getIterable())

        # Compute the initial chunk size: the largest power of two less than N
        self.mTestcaseSize = len(self.mElements)
        if self.mTestcaseSize == 0:
            raise LiPlusException("Testcase can not be empty!")

        self.mChunkSize = 2
        while self.mChunkSize <= self.mTestcaseSize:
            self.mChunkSize *= 2
        self.mChunkSize /= 2
        self.mFinalAttempts = (self.mChunkSize == 1)

        # Add a "None" element to mark the end.
        self.mElements.appendleft(None)

    def verifyInitalization(self):
        if self.mTestcase is None:
            raise LiPlusException("Operation not permitted.")

    def markCurrentChunk(self):

        self.mLastChunkSize = 0

        while (self.mElements[-1] is not None and
               self.mLastChunkSize < self.mChunkSize):
            el = self.mElements.pop()
            self.mTestcase.mark(el)
            self.mElements.appendleft(el)
            self.mLastChunkSize += 1

    def removePreviousChunk(self):

        self.mTestcaseSize -= self.mLastChunkSize

        while self.mLastChunkSize > 0:
            el = self.mElements.popleft()
            self.mTestcase.remove(el)
            self.mLastChunkSize -= 1

    def unmarkPreviousChunk(self):

        i = 0
        while i < self.mLastChunkSize:
            el = self.mElements.popleft()
            self.mTestcase.unmark(el)
            self.mElements.append(el)
            i += 1
        self.mElements.rotate(self.mLastChunkSize)

    def reduceChunkSize(self):
        self.mChunkSize /= 2
        while self.mChunkSize > 1 and self.mTestcaseSize <= self.mChunkSize:
            self.mChunkSize /= 2

        if self.mChunkSize == 1:
            self.mFinalAttempts = True

    def provideResult(self, aIsInteresting):
        self.verifyInitalization()

        if aIsInteresting:
            # The testcase is still interesting, hence we permanently
            # remove the previous chunk and try another one.
            self.removePreviousChunk()
            if self.mElements[-1] is None:
                self.mElements.rotate()

            if self.mChunkSize == 1:
                self.mFinalAttempts = False
                if self.mTestcaseSize <= 1:
                    # It remains only one token in the testcase. We are
                    # done: this is a 1-minimal testcase!
                    self.mTestcase = None
                    return True
            else:
                if self.mTestcaseSize <= self.mChunkSize:
                    # It remains only one chunk in the testcase. Try with
                    # the smaller chunk size.
                    self.reduceChunkSize()
        else:
            # Removing the previous chunk did not provide an interesting
            # testcase. Let this chunk survive and try another one.
            self.unmarkPreviousChunk()

            if self.mElements[-1] is None:

                # We have browsed all the elements, skip the "None" sentinel
                self.mElements.rotate()

                if self.mFinalAttempts:
                    # We already tried to remove each single
                    # element of the testcase without success. Hence
                    # we are done: this is a 1-minimal testcase!
                    self.mTestcase = None
                    return True

                if self.mChunkSize > 1:
                    # We already tried to remove each chunk without
                    # success: try with a smaller chunk size.
                    self.reduceChunkSize()

            if self.mChunkSize == 1:
                self.mFinalAttempts = True

        return False

    def tryToReduce(self):
        self.verifyInitalization()
        self.markCurrentChunk()
