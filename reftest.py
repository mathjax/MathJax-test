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
# Contributor(s):
#   Frederic Wang <fred.wang@free.fr> (original author)
#
# ***** END LICENSE BLOCK *****

import time
import unittest
import seleniumMathJax
import string
from PIL import Image, ImageChops
import difflib

class reftestSuite(unittest.TestSuite):

    def __init__(self, aRunSlowTests):
        unittest.TestSuite.__init__(self)
        self.mRunSlowTests = aRunSlowTests

    def addReftests(self, aSelenium, aManifestFile):
        # This function parses a reftest manifest file.
        # http://mxr.mozilla.org
        #                /mozilla-central/source/layout/tools/reftest/README.txt

        i = string.rfind(aManifestFile, "/")
        testDirectory = aManifestFile[:(i+1)]

        with open(aManifestFile) as f:

            for line in f:

                state = 0
                testClass = None
                testType = None
                testURL = None
                testURLRef = None         
                testFails = False
                testRandom = False
                testSkip = False
                testSlow = False

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

                    if state == 0 or state == 2:
                        # 2. <failure-type>
                        if word == "fails":
                            testFails = True
                            state = 2
                            continue
                        elif word.startswith("fails-if"):
                            # 8 = len("fails-if")
                            testFails = self.parseCondition(aSelenium, word[8:])
                            state = 2
                            continue
                        elif word == "random":
                            testRandom = True
                            state = 2
                            continue
                        elif word.startswith("random-if"):
                            # 9 = len("random-if")
                            testRandom = self.parseCondition(aSelenium,
                                                             word[9:])
                            state = 2
                            continue
                        elif word == "skip":
                            testSkip = True
                            state = 2
                            continue
                        elif word.startswith("skip-if"):
                            # 7 = len("skip-if")
                            testSkip = self.parseCondition(aSelenium, word[7:])
                            state = 2
                            continue
                        elif word == "slow":
                            testSlow = True
                            state = 2
                            continue
                        elif word.startswith("slow-if"):
                            # 7 = len("slow-if")
                            testSlow = self.parseCondition(aSelenium, word[7:])
                            state = 2
                            continue
                        else:
                            # The following failure types are not supported:
                            #   needs-focus
                            #   asserts
                            #   asserts
                            #   silentfail
                            #   silentfail-if
                            state = 3

                    if state == 3:
                        # 2. [<http>]
                        state = 4
                        if word.startswith("HTTP"):
                            raise "http syntax not supported"

                    if state == 4:
                        # 2. <type>
                        if word == "load":
                            testClass = loadReftest
                            state = 5
                            continue
                        elif word == "tree==":
                            testClass = treeReftest
                            testType = "=="
                            state = 5
                            continue
                        elif word == "tree!=":
                            testClass = treeReftest
                            testType = "!="
                            state = 5
                            continue
                        elif word == "==":
                            testClass = visualReftest
                            testType = "=="
                            state = 5
                            continue
                        elif word == "!=":
                            testClass = visualReftest
                            testType = "!="
                            state = 5
                            continue

                    if state == 5:
                        # 2. <url>
                        testURL = word
                        if testClass == "load":
                            state = 7
                        else:
                            state = 6
                        continue

                    if state == 6:
                        # 2. <url_ref>
                        testURLRef = word
                        state = 7
                        continue

                    raise "reftest syntax not supported"

                # end for word

                if state == 7:
                    self.addTest(testClass(self,
                                           aSelenium,
                                           testType,
                                           testDirectory,
                                           testURL,
                                           testURLRef,
                                           testFails,
                                           testRandom,
                                           testSkip,
                                           testSlow))

            # end for line

        # end with open

    def parseCondition(self, aSelenium, aCondition):
        # A parser for reftest manifest condition.
        # Note that it is not claimed to be complete, but should work in most
        # cases, when the expression is not too complex.

        # a limited set of pre-defined variables
        if (aCondition == aSelenium.mOperatingSystem or
            aCondition == aSelenium.mBrowser or
            aCondition == aSelenium.mBrowserVersion or
            aCondition == aSelenium.mFonts):
            return True

        if (aCondition == "nativeMathML"):
            return aSelenium.mNativeMathML

        l = len(aCondition)
        
        # not
        if (l >= 1 and aCondition[0] == "!"):
            return (not self.parseCondition(aSelenium, aCondition[1:]))
            
        if l >= 2:
            # parenthesis
            if (aCondition[0] == "(" and aCondition[l-1] == ")"):
                return self.parseCondition(aSelenium, aCondition[1:l-1])

            # or
            orlist = aCondition.split("||")
            if (len(orlist) >= 2):
                for c in orlist:
                    if self.parseCondition(aSelenium, c):
                        return True
                return False
        
            # and
            andlist = aCondition.split("&&")
            if (len(andlist) >= 2):
                for c in andlist:
                    if (not self.parseCondition(aSelenium, c)):
                        return False
                return True

        assert "syntax not supported"

class reftest(unittest.TestCase):

    def __init__(self,
                 aTestSuite,
                 aSelenium, aType, aReftestDirectory, aURL, aURLRef,
                 aFails, aRandom, aSkip, aSlow):
        unittest.TestCase.__init__(self)
        self.mTestSuite = aTestSuite
        self.mSelenium = aSelenium
        self.mType = aType
        self.mURL = aReftestDirectory + aURL

        if aURLRef == None:
            self.mURLRef = None
        else:
            self.mURLRef = aReftestDirectory + aURLRef

        self.mID = aURL.split('.')[0]
        self.mFails = aFails
        self.mRandom = aRandom
        self.mSkip = aSkip
        self.mSlow = aSlow

    def id(self):
       return self.mID

    def shouldSkipTest(self):
        if self.mSkip:
            msg = "REFTEST TEST-KNOWN-FAIL | " + self.mID + " | (SKIP)\n"
            # self.skipTest(msg)
            print msg
            return True

        if  ((not self.mTestSuite.mRunSlowTests) and self.mSlow):
            msg = "REFTEST TEST-KNOWN-SLOW | " + self.mID + " | (SLOW)\n"
            # self.skipTest(msg)
            print msg
            return True

        return False

    def determineSuccess(self, aIsEqual):

        success = ((self.mType == '==' and aIsEqual) or
                   (self.mType == '!=' and (not aIsEqual)))

        if self.mFails:
            if success:
                msg = "TEST-UNEXPECTED-PASS"
                success = False
            else:
                msg = "TEST-KNOWN-FAIL"
        elif self.mRandom:
            if success:
                msg = "TEST-PASS(EXPECTED RANDOM)"
            else:
                msg = "TEST-KNOWN-FAIL(EXPECTED RANDOM)"
        else:
            if success:
                msg = "TEST-PASS"
            else:
                msg = "TEST-UNEXPECTED-FAIL"

        msg = "REFTEST " + msg + " | " + self.mID + " | "
        return success, msg

class loadReftest(reftest):

    def runTest(self):

        if self.shouldSkipTest():
            return
        self.mSelenium.open(self.mURL, self.mSelenium.mNativeMathML)
        msg = "REFTEST TEST-PASS | " + self.mID + " | (LOAD ONLY)\n"
        print msg
        
class treeReftest(reftest):

    def runTest(self):

        if self.shouldSkipTest():
            return
        self.mSelenium.open(self.mURL, True)
        source = self.mSelenium.getMathJaxSourceMathML()
        self.mSelenium.open(self.mURLRef, True)
        sourceRef = self.mSelenium.getMathJaxSourceMathML()

        # Compare source == sourceRef
        isEqual = (source == sourceRef);
        (success, msg) = self.determineSuccess(isEqual)
        
        if success:
            print msg
        else:
            # Return failure together with a diff of the sources
            msg += "source comparison ("+ self.mType +") \n"

            if not isEqual:
                msg += "REFTEST   SOURCE 1 (TEST): " + \
                    source + "\n"
                msg += "REFTEST   SOURCE 2 (REFERENCE): " + \
                    sourceRef + "\n"

                msg += "REFTEST   DIFF:\n"
                generator = difflib.unified_diff(source.splitlines(1),
                                                 sourceRef.splitlines(1))
                for line in generator:
                    msg += line
            elif isEqual:
                msg += "REFTEST   SOURCE: " + \
                    source + "\n"
 
            self.fail(msg)

class visualReftest(reftest):

    def runTest(self):

        if self.shouldSkipTest():
            return
        self.mSelenium.open(self.mURL, self.mSelenium.mNativeMathML)
        image = self.mSelenium.takeScreenshot()
        self.mSelenium.open(self.mURLRef, self.mSelenium.mNativeMathML)
        imageRef = self.mSelenium.takeScreenshot()

        # Compare image and imageRef
        box = ImageChops.difference(image, imageRef).getbbox()
        isEqual = (box == None or (box[0] == box[2] and box[1] == box[3]))
        (success, msg) = self.determineSuccess(isEqual)

        if success:
            print msg
        else:
            # Return failure together with base64 images of the reftest
            msg += "image comparison ("+ self.mType +") \n"
            if not isEqual:
                msg += "REFTEST   IMAGE 1 (TEST): " + \
                    self.mSelenium.encodeImageToBase64(image) + "\n"
                msg += "REFTEST   IMAGE 2 (REFERENCE): " + \
                    self.mSelenium.encodeImageToBase64(imageRef) + "\n"
            elif isEqual:
                msg += "REFTEST   IMAGE: " + \
                    self.mSelenium.encodeImageToBase64(image) + "\n"

            self.fail(msg)
