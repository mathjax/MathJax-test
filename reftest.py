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
import conditionParser

EXPECTED_PASS = 0
EXPECTED_FAIL  = 1
EXPECTED_RANDOM = 2
EXPECTED_DEATH = 3
EXPECTED_IRRELEVANT = 4

class reftestSuite(unittest.TestSuite):

    def __init__(self, aRunSlowTests, aRunSkipTests, aListOfTests):
        unittest.TestSuite.__init__(self)
        self.mRunSlowTests = aRunSlowTests
        self.mRunSkipTests = aRunSkipTests
        self.mListOfTests = aListOfTests
        self.mPreviousURLRef = None
        self.mPreviousImageRef = None

    def getDirectoryFromManifestFile(self, aManifestFile):
        return aManifestFile[:(string.rfind(aManifestFile, "/") + 1)]

    def addReftests(self, aSelenium, aManifestFile, aIndex,
                    aInheritedStatus = EXPECTED_PASS):
        # This function parses a reftest manifest file.
        # http://mxr.mozilla.org
        #                /mozilla-central/source/layout/tools/reftest/README.txt

        testDirectory = self.getDirectoryFromManifestFile(aManifestFile)
        index = aIndex

        with open(aManifestFile) as f:

            for line in f:

                state = 0
                testClass = None
                testType = None
                testURL = None
                testURLRef = None         
                testExpectedStatus = 0
                testSlow = False

                for word in line.split():
                    
                    if word[0] == '#':
                        # the remaining of the line is a comment
                        break

                    if state == 0:
                        # 2. <failure-type>
                        if word == "fails":
                            testExpectedStatus = EXPECTED_FAIL
                            continue
                        elif word.startswith("fails-if"):
                            # 8 = len("fails-if")
                            if conditionParser.parse(aSelenium, word[8:]):
                                testExpectedStatus = EXPECTED_FAIL
                            continue
                        elif word == "random":
                            testExpectedStatus = EXPECTED_RANDOM
                            continue
                        elif word.startswith("random-if"):
                            # 9 = len("random-if")
                            if conditionParser.parse(aSelenium, word[9:]):
                                testExpectedStatus = EXPECTED_RANDOM
                            continue
                        elif word.startswith("require"):
                            # 7 = len("require")
                            if not conditionParser.parse(aSelenium, word[7:]):
                                testExpectedStatus = EXPECTED_IRRELEVANT
                            continue
                        elif word == "skip":
                            testExpectedStatus = EXPECTED_DEATH
                            continue
                        elif word.startswith("skip-if"):
                            # 7 = len("skip-if")
                            if conditionParser.parse(aSelenium, word[7:]):
                                testExpectedStatus = EXPECTED_DEATH
                            continue
                        elif word == "slow":
                            testSlow = True
                            continue
                        elif word.startswith("slow-if"):
                            # 7 = len("slow-if")
                            if conditionParser.parse(aSelenium, word[7:]):
                                testSlow = True
                            continue
                        else:
                            # The following failure types are not supported:
                            #   needs-focus
                            #   asserts
                            #   asserts
                            #   silentfail
                            #   silentfail-if
                            testExpectedStatus = max(testExpectedStatus,
                                                     aInheritedStatus)
                            state = 1

                    if state == 1 and word == "include":
                        # 1. include
                        state = 2
                        continue

                    if state == 2:
                        # 1. <relative_path>
                        reftestList = testDirectory + word
                        if aSelenium == None:
                            print ",[\"" + \
                                self.getDirectoryFromManifestFile(word) + "\"",
                            self.addReftests(aSelenium, reftestList, -1,
                                             testExpectedStatus)
                            print "]",
                        else:
                            if index == -1:
                                self.addReftests(aSelenium,
                                                 reftestList,
                                                 -1,
                                                 testExpectedStatus)
                            else:
                                if self.mListOfTests[index] == "2":
                                    # all the tests in the subdirectory
                                    self.addReftests(aSelenium,
                                                     reftestList,
                                                     -1,
                                                     testExpectedStatus)
                                    index = index + 1
                                elif self.mListOfTests[index] == "1":
                                    # tests indicated in listOfTests
                                    index = index + 1
                                    index = self.addReftests(aSelenium,
                                                             reftestList,
                                                             index,
                                                             testExpectedStatus)
                                elif self.mListOfTests[index] == "0":
                                    # none of the tests in the subdirectory
                                    index = index + 1
                                else:
                                    raise NameError("invalid listOfTests")
                        break

                    if state == 1:
                        # 2. [<http>]
                        state = 3
                        if word.startswith("HTTP"):
                            raise NameError("http syntax not supported")

                    if state == 3:
                        # 2. <type>
                        if word == "load":
                            testClass = loadReftest
                            state = 4
                            continue
                        elif word == "script":
                            testClass = scriptReftest
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
                        if testClass == loadReftest:
                            if (testExpectedStatus == EXPECTED_FAIL or
                                testExpectedStatus == EXPECTED_RANDOM):
                                raise NameError("loadtest can't be marked as \
fails/random")
                            state = 6
                        elif testClass == scriptReftest:
                            state = 6
                        else:
                            state = 5
                        continue

                    if state == 5:
                        # 2. <url_ref>
                        testURLRef = word
                        state = 6
                        continue

                    raise NameError("reftest syntax not supported")

                # end for word

                if state == 6:
                    if aSelenium == None:
                        print ",\"" + testURL + "\"",
                    else:
                        if (index == -1 or self.mListOfTests[index] == "1"):
                            self.addTest(testClass(self,
                                                   aSelenium,
                                                   testType,
                                                   testDirectory,
                                                   testURL,
                                                   testURLRef,
                                                   testExpectedStatus,
                                                   testSlow))
                        if (index == -1):
                            continue
                        elif (self.mListOfTests[index] == "0" or
                              self.mListOfTests[index] == "1"):
                            index = index + 1
                            continue
                        else:
                            raise NameError("invalid listOfTests")
            # end for line

        # end with open
        return index

    def takeReferenceScreenshot(self, aURLRef, aSelenium):
        if (aURLRef == self.mPreviousURLRef):
            return self.mPreviousImageRef

        aSelenium.open(aURLRef, aSelenium.mNativeMathML)
        # self.mPreviousURLRef is only set after the page is loaded, so that
        # the screenshot won't be used if the loading failed.
        self.mPreviousURLRef = aURLRef
        self.mPreviousImageRef = aSelenium.takeScreenshot()
        return self.mPreviousImageRef

class reftest(unittest.TestCase):

    def __init__(self,
                 aTestSuite,
                 aSelenium, aType, aReftestDirectory, aURL, aURLRef,
                 aExpectedStatus, aSlow):
        unittest.TestCase.__init__(self)
        self.mTestSuite = aTestSuite
        self.mSelenium = aSelenium
        self.mType = aType
        self.mURL = aReftestDirectory + aURL

        if aURLRef == None:
            self.mURLRef = None
        else:
            self.mURLRef = aReftestDirectory + aURLRef

        self.mID = self.mURL
        self.mExpectedStatus = aExpectedStatus
        self.mSlow = aSlow

    def id(self):
       return self.mID

    def shouldSkipTest(self):
        if self.mExpectedStatus == EXPECTED_IRRELEVANT:
            msg = "REFTEST INFO | " + self.mID
            msg += " is irrelevant for this configuration\n"
            # self.skipTest(msg)
            print msg
            return True

        if ((not self.mTestSuite.mRunSkipTests) and
            self.mExpectedStatus == EXPECTED_DEATH):
            msg = "\nREFTEST TEST-KNOWN-FAIL | " + self.mID + " | (SKIP)\n"
            # self.skipTest(msg)
            print msg
            return True

        if  ((not self.mTestSuite.mRunSlowTests) and self.mSlow):
            msg = "\nREFTEST TEST-KNOWN-SLOW | " + self.mID + " | (SLOW)\n"
            # self.skipTest(msg)
            print msg
            return True

        return False

    def determineSuccess(self, aType, aResult):

        success = ((aType == None and aResult) or
                   (aType == "==" and aResult) or
                   (aType == "!=" and (not aResult)))

        if self.mExpectedStatus == EXPECTED_FAIL:
            if success:
                msg = "TEST-UNEXPECTED-PASS"
                success = False
            else:
                msg = "TEST-KNOWN-FAIL"
        elif self.mExpectedStatus == EXPECTED_RANDOM:
            if success:
                msg = "TEST-PASS(EXPECTED RANDOM)"
            else:
                msg = "TEST-KNOWN-FAIL(EXPECTED RANDOM)"
        else:
            if success:
                msg = "TEST-PASS"
            else:
                msg = "TEST-UNEXPECTED-FAIL"

        msg = "\nREFTEST " + msg + " | " + self.mID + " | "

        return success, msg

class loadReftest(reftest):

    def runTest(self):

        if self.shouldSkipTest():
            return

        try:
            self.mSelenium.open(self.mURL, self.mSelenium.mNativeMathML)
        except Exception, data:
            (success, msg) = self.determineSuccess(None, False)
            msg += repr(data)
            print msg
            self.fail()

        (success, msg) = self.determineSuccess(self.mType, True)
        msg += "(LOAD ONLY)\n"
        print msg

class scriptReftest(reftest):

    def runTest(self):

        if self.shouldSkipTest():
            return

        try:
            self.mSelenium.open(self.mURL, self.mSelenium.mNativeMathML)
        except Exception, data:
            (success, msg) = self.determineSuccess(None, False)
            msg += repr(data)
            print msg
            self.fail()

        (success1, msg1) = self.mSelenium.getScriptReftestResult()
        (success, msg) = self.determineSuccess(self.mType, success1)
        msg += "(SCRIPT REFTEST)"
        if success:
            print msg
        else:
            msg += "\n" + msg1
            print msg
            self.fail()
       
class treeReftest(reftest):

    def runTest(self):

        if self.shouldSkipTest():
            return

        try:
            self.mSelenium.open(self.mURL, True)
            source = self.mSelenium.getMathJaxSourceMathML()
            self.mSelenium.open(self.mURLRef, True)
            sourceRef = self.mSelenium.getMathJaxSourceMathML()
        except Exception as data:
            (success, msg) = self.determineSuccess(None, False)
            msg += repr(data)
            print msg
            self.fail()

        # Compare source == sourceRef
        isEqual = (source == sourceRef)
        (success, msg) = self.determineSuccess(self.mType, isEqual)

        if success:
            print msg
        else:
            # Return failure together with a diff of the sources
            msg += "source comparison ("+ self.mType +") \n"

            if not isEqual:
                msg += "REFTEST   SOURCE 1 (TEST): " + \
                    self.mSelenium.encodeSourceToBase64(source) + "\n"
                msg += "REFTEST   SOURCE 2 (REFERENCE): " + \
                    self.mSelenium.encodeSourceToBase64(sourceRef) + "\n"

                msg += "REFTEST   DIFF: "
                diff = ""
                generator = difflib.unified_diff(source.splitlines(1),
                                                 sourceRef.splitlines(1))
                for line in generator:
                    diff += line

                msg += self.mSelenium.encodeSourceToBase64(diff)
            elif isEqual:
                msg += "REFTEST   SOURCE: " + \
                    self.mSelenium.encodeSourceToBase64(source)

            print msg
            self.fail()

class visualReftest(reftest):

    def runTest(self):

        if self.shouldSkipTest():
            return

        try:
            # take the screenshot of the test
            self.mSelenium.open(self.mURL, self.mSelenium.mNativeMathML)
            image = self.mSelenium.takeScreenshot()

            # take the screenshot of the reftest using the one in memory if it
            # has been used just before.
            imageRef = self.mTestSuite.takeReferenceScreenshot(self.mURLRef,
                                                               self.mSelenium)
        except Exception, data:
            (success, msg) = self.determineSuccess(None, False)
            msg += repr(data)
            print msg
            self.fail()

        # Compare image and imageRef
        box = ImageChops.difference(image, imageRef).getbbox()
        isEqual = (box == None or (box[0] == box[2] and box[1] == box[3]))
        (success, msg) = self.determineSuccess(self.mType, isEqual)

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
                    self.mSelenium.encodeImageToBase64(image)
            print msg
            self.fail()
