#!/usr/bin/env python
# -*- Mode: Python; tab-width: 2; indent-tabs-mode:nil; -*-
# vim: set ts=2 et sw=2 tw=80:
#
# Copyright (c) 2013-2015 MathJax Consortium, Inc.
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
@package LiPlusText
This modules implements LiPlus's testcase interface for text documents, where
tokens are lines or characters.
"""

from collections import deque
from lxml import etree
from sys import maxsize
from shutil import copy as copyFile
from os import remove as removeFile

class LiPlusText:

    def __init__(self,
                 aFileName,
                 aDelimiters = None,
                 aWorkOnCharacters = False):

        self.mDelimiters = aDelimiters
        if self.mDelimiters is not None:
            self.mDelimiters = self.mDelimiters.split(",")
            if len(self.mDelimiters) < 2:
                self.mDelimiters = ["DDBEGIN", "DDEND"]

        self.mFileName = aFileName
        self.mTmpFileName = self.mFileName + "-"
        copyFile(self.mFileName, self.mTmpFileName)

        self.mWorkOnCharacters = aWorkOnCharacters

        self.mRemovedBlocks = deque()
        self.mRemovedBlocks.append(None) # add a "None" element to mark the end
        self.clearChunkBoundaries()

    def __del__(self):
        removeFile(self.mTmpFileName)

    def clearChunkBoundaries(self):
        self.mMinIndex = maxsize
        self.mMaxIndex = -1

    def isChunkCleared(self):
        return self.mMaxIndex == -1

    def getIterable(self):
        iterable = deque()
        inputFile = open(self.mFileName, "r")

        if self.mWorkOnCharacters:
            i = 1
            while True:
                c = inputFile.read(1)
                if c == "":
                    break
                iterable.appendleft(i)
                i += 1
        else:
            i = 1
            if self.mDelimiters is None:
                for line in inputFile:
                    iterable.appendleft(i)
                    i += 1
            else:
                i = 1
                while True:
                    line = inputFile.readline()
                    if line == "":
                        break
                    i += 1
                    if line.find(self.mDelimiters[0]) >= 0:
                        break
                while True:
                    line = inputFile.readline()
                    if line == "":
                        break
                    if line.find(self.mDelimiters[1]) >= 0:
                        break
                    iterable.appendleft(i)
                    i += 1

        inputFile.close()
        return iterable

    def mark(self, aIndex):
        # update the chunk boundaries.
        self.mMinIndex = min(self.mMinIndex, aIndex)
        self.mMaxIndex = max(self.mMaxIndex, aIndex)

    def unmark(self, aElement):
        if not self.isChunkCleared():
            self.clearChunkBoundaries()

    def remove(self, aElement):
        if self.isChunkCleared():
            return

        firstBlock = self.mRemovedBlocks[-1]
        if firstBlock is None or self.mMaxIndex < firstBlock[0] - 1:
            # put the chunk at the beginning
            self.mRemovedBlocks.append([self.mMinIndex, self.mMaxIndex])
            self.clearChunkBoundaries()
            return            

        # Insert the chunk into the list of removed blocks...
        while True:
            block = self.mRemovedBlocks.pop()

            if self.mMaxIndex == block[0] - 1:
                # We are just before the current block: merge the block
                # with the chunk.
                block[0] = self.mMinIndex
                self.mRemovedBlocks.appendleft(block)
                break

            nextBlock = self.mRemovedBlocks[-1]

            if block[1] + 1 == self.mMinIndex:
                # We are just after the current block...
                if (nextBlock is not None and
                    nextBlock[1] + 1 == self.mMinIndex):
                    # ... and just before the next block: merge the three
                    # blocks.
                    nextBlock = self.mRemovedBlocks.pop()
                    block[1] = nextBlock[1]
                    self.mRemovedBlocks.appendleft(block)
                    break
                # ... merge it with the chunk
                block[1] = self.mMaxIndex
                self.mRemovedBlocks.appendleft(block)
                break

            # put back the current block into self.mRemovedBlocks
            self.mRemovedBlocks.appendleft(block)

            if nextBlock is None or self.mMaxIndex < nextBlock[0] - 1:
                # We arrived at the end or are not just before the next block
                # insert the chunk here.
                self.mRemovedBlocks.appendleft([self.mMinIndex, self.mMaxIndex])
                break

        # Now rotate self.mRemovedBlocks to put in order again:
        while True:
            block = self.mRemovedBlocks.pop()
            self.mRemovedBlocks.appendleft(block)
            if block is None:
                break

        self.clearChunkBoundaries()

    def readToken(self, aFile):
        if self.mWorkOnCharacters:
            return aFile.read(1)
        else:
            return aFile.readline()

    def outputFile(self):

        inputFile = open(self.mTmpFileName, "r")
        outputFile = open(self.mFileName, "w")

        i = 1
        while True:
            block = self.mRemovedBlocks.pop()

            if block is None:
                self.mRemovedBlocks.appendleft(block)
                break

            # copy the tokens before the current removed block...
            while i < block[0]:
                t = self.readToken(inputFile)
                if not (self.mMinIndex <= i and i <= self.mMaxIndex):
                    # ... if they are not inside the marked chunk
                    outputFile.write(t)
                i += 1

            # ignore the tokens inside the current removed block
            while i <= block[1]:
                t = self.readToken(inputFile)
                i += 1

            self.mRemovedBlocks.appendleft(block)

        # copy the tokens at the end, if they are not inside the marked chunk
        while True:
            t = self.readToken(inputFile)
            if t == "":
                break
            if not (self.mMinIndex <= i and i <= self.mMaxIndex):
                outputFile.write(t)
            i += 1

        outputFile.close()
        inputFile.close()
