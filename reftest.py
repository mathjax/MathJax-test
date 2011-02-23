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
from PIL import Image

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

class visualReftest(reftest):

    def runTest(self):
        self.mSelenium.open(self.mURL, self.mSelenium.mUseNativeMathML)
        image1 = self.mSelenium.takeScreenshot()
        self.mSelenium.open(self.mURLRef, self.mSelenium.mUseNativeMathML)
        image2 = self.mSelenium.takeScreenshot()
        result = self.mSelenium.visualReftest(self.mID, self.mType,
                                              image1, image2)
        self.assertTrue(result[0], result[1])

class treeReftest(reftest):

    def runTest(self):
        self.mSelenium.open(self.mURL, True)
        source1 = self.mSelenium.serializeReftest()
        self.mSelenium.open(self.mURLRef, True)
        source2 = self.mSelenium.serializeReftest()
        result = self.mSelenium.treeReftest(self.mID, self.mType,
                                            source1, source2)
        self.assertTrue(result[0], result[1])

class loadReftest(reftest):

    def runTest(self):
        self.mSelenium.open(self.mURL, self.mSelenium.mUseNativeMathML)
