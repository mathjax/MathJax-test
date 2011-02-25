# -*- Mode: Python; tab-width: 2; indent-tabs-mode:nil; -*-
# vim: set ts=2 et sw=2 tw=80:
# ***** BEGIN LICENSE BLOCK *****
# Version: Apache License 2.0
#
# Copyright (c) 2011 Design Science, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# ***** END LICENSE BLOCK *****

import time
import unittest
import seleniumMathJax
import string
from PIL import Image

class reftestSuite(unittest.TestSuite):

    def addReftests(self, aSelenium, aManifestFile):

        i = string.rfind(aManifestFile, "/")
        testDirectory = aManifestFile[0:(i+1)]

        with open(aManifestFile) as f:

            for line in f:

                state = 0
                testClass = None
                testType = None
                testURL = None
                testURLRef = None         

                for word in line.split():
                    
                    if word[0] == '#':
                        # the remaining of the line is a comment
                        break

                    if state == 0 and word == "include":
                        # 1. include
                        state = 1
                        continue

                    if state == 1:
                        # 1. <relative_path>
                        self.addReftests(aSelenium, testDirectory + word)
                        break

                    if state == 0:
                        # 2. <failure-type>*
                        if (word == "fails" or
                            word.startswith("fails-if") or
                            word == "needs-focus" or
                            word == "random" or
                            word.startswith("random-if") or
                            word == "silentfail" or
                            word.startswith("silentfail-if") or
                            word == "skip" or
                            word.startswith("skip-if") or
                            word == "slow" or
                            word.startswith("slow-if") or
                            word.startswith("asserts") or
                            word.startswith("asserts-if")):
                            print "failure-type not supported"
                            continue
                        else:
                            state = 2

                    if state == 2:
                        # 2. [<http>]
                        state = 3
                        if word.startswith("HTTP"):
                            print "http syntax not implemented"
                            continue

                    if state == 3:
                        # 2. <type>
                        if word == "load":
                            testClass = loadReftest
                            state = 4
                            continue
                        elif word == "tree==":
                            testClass = treeReftest
                            testType = "=="
                            state = 4
                            continue
                        elif word == "tree!=":
                            testClass = treeReftest
                            testType = "!="
                            state = 4
                            continue
                        elif word == "==":
                            testClass = visualReftest
                            testType = "=="
                            state = 4
                            continue
                        elif word == "!=":
                            testClass = visualReftest
                            testType = "!="
                            state = 4
                            continue

                    if state == 4:
                        # 2. <url>
                        testURL = word
                        if testClass == "load":
                            state = 6
                        else:
                            state = 5
                        continue

                    if state == 5:
                        # 2. <url_ref>
                        testURLRef = word
                        state = 6
                        continue

                    print "reftest syntax not supported"
                    break

                # end for word

                if state == 6:
                    self.addTest(testClass(aSelenium, testType,
                                           testDirectory,
                                           testURL, testURLRef))

            # end for line

        # end with open

class reftest(unittest.TestCase):

    def __init__(self, aSelenium, aType, aReftestDirectory, aURL, aURLRef):
        unittest.TestCase.__init__(self)
        self.mSelenium = aSelenium
        self.mType = aType
        self.mURL = aReftestDirectory + aURL

        if aURLRef == None:
            self.mURLRef = None
        else:
            self.mURLRef = aReftestDirectory + aURLRef

        self.mID = aURL.split('.')[0]

    def id(self):
       return self.mID

class loadReftest(reftest):

    def runTest(self):
        self.mSelenium.open(self.mURL, self.mSelenium.mUseNativeMathML)

class treeReftest(reftest):

    def runTest(self):
        self.mSelenium.open(self.mURL, True)
        source1 = self.mSelenium.serializeReftest()
        self.mSelenium.open(self.mURLRef, True)
        source2 = self.mSelenium.serializeReftest()
        result = self.mSelenium.treeReftest(self.mID, self.mType,
                                            source1, source2)
        self.assertTrue(result[0], result[1])

class visualReftest(reftest):

    def runTest(self):
        self.mSelenium.open(self.mURL, self.mSelenium.mUseNativeMathML)
        image1 = self.mSelenium.takeScreenshot()
        self.mSelenium.open(self.mURLRef, self.mSelenium.mUseNativeMathML)
        image2 = self.mSelenium.takeScreenshot()
        result = self.mSelenium.visualReftest(self.mID, self.mType,
                                              image1, image2)
        self.assertTrue(result[0], result[1])
