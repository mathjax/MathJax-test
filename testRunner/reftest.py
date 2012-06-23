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

"""
@file reftest.py
The file for the @ref reftest module.

@var EXPECTED_PASS
The test is expected to pass.

@var EXPECTED_FAIL
The test is expected to fail.

@var EXPECTED_RANDOM
The test is expected to pass or fail randomly.

@var EXPECTED_DEATH
The test is marked skip and is expected to cause a crash, hang etc.

@var EXPECTED_FUZZY
The test is expected to have small pixel differences.

@var EXPECTED_IRRELEVANT
The test is marked with a require field which is not fullfilled by the current
configuration.

@package reftest
This module implements various types of reftests, controls the executions and
reports the results.
"""

from config import MATHJAX_TEST_PUBLIC_URI
MATHJAX_TESTSUITE_PATH = "../testsuite/"

from PIL import Image, ImageChops
import os, cgi
import conditionParser
import difflib
import seleniumMathJax
import socket
import string
import sys
import time
from selenium.common.exceptions import WebDriverException

EXPECTED_PASS = 0
EXPECTED_FAIL  = 1
EXPECTED_RANDOM = 2
EXPECTED_DEATH = 3
EXPECTED_FUZZY = 4
EXPECTED_IRRELEVANT = 5

def verifyPageExistence(aTestDir, aTestPage):
    """
    @fn verifyPageExistence(aTestDir, aTestPage)
    Verify that a page in the test suite exists and display a warning if it
    does not.
    """
    path = aTestPage
    i = path.find("?")
    if (i >= 0):
        path = path[:i]
    path = aTestDir + path
    if (not os.path.exists(MATHJAX_TESTSUITE_PATH + path)):
        print >> sys.stderr, "warning: " + path + " does not exist!"

class reftestSuite():
    """
    @class reftest::reftestSuite
    @brief A class implementing a test suite.
    """

    def __init__(self,
                 aTaskHandler = None,
                 aRunSlowTests = True,
                 aRunSkipTests = True,
                 aListOfTests = None,
                 aStartID = ""):
        """
        @fn __init__(self,
                     aTaskHandler = None,
                     aRunSlowTests = True,
                     aRunSkipTests = True,
                     aListOfTests = None,
                     aStartID = "")
    
        @param aTaskHandler  Value to assign to @ref mTaskHandler
        @param aRunSlowTests Value to assign to @ref mRunSlowTests
        @param aRunSkipTests Value to assign to @ref mRunSkipTests
        @param aListOfTests  Value to assign to @ref mListOfTests
        @param aStartID      Initial value of @ref mRunningTestID.

        @property mTaskHandler
        This variable describes the task handler to which the test runner will
        send the status and progress of the testing instance.
        It is made of three elements: the task handler host, task handler port
        and name of the task running. If this table is set to None, then the
        testing framework will not send any information.

        @property mRunSlowTests
        Indicate whether the suite should run tests marked slow.
        
        @property mRunSkipTests
        Indicate whether the suite should run tests marked skip.

        @property mListOfTests
        A string made representing the list of tests to run, as generated
        by selectReftests.xhtml.

        @property mRunningTestID
        Initially, the ID of the first test to run or an empty string. It is
        updated later to reflect the current running test.

        @property mStarted
        Whether the testing instance has started. Set to True if aStartID is
        empty. Otherwise it remains False until we meet aStartID. This is used
        to recover testing instance.

        @property mPreviousURIRef
        The previous URI of a reference page called in a visual reftest.

        @property mPreviousImageRef
        The previous screenshot taken, the one of the page at mPreviousURIRef.

        @property mTestsExecuted
        Number of tests in the suite that have been executed in the testing
        instance.

        @property mNumberOfTests
        Total number of tests in the suite.

        @property mTests
        The list of tests.
        """
        self.mTaskHandler = aTaskHandler
        self.mRunSlowTests = aRunSlowTests
        self.mRunSkipTests = aRunSkipTests
        self.mListOfTests = aListOfTests
        self.mRunningTestID = aStartID
        self.mStarted = (aStartID == "")
        self.mPreviousURIRef = None
        self.mPreviousImageRef = None
        self.mTestsExecuted = 0
        self.mNumberOfTests = 0
        self.mTests = []

    def printInfo(self, aString):
        """
        @fn printInfo(self, aString)
        @brief print a reftest info to the standard output
        
        @param aString the message to print

        @details Each line of the message is prefixed by "REFTEST INFO | ", so
        that it will be kept by the output formater.
        """
        prefix = "REFTEST INFO | "
        print prefix + aString.replace("\n", "\n" + prefix)

    def getDirectoryFromManifestFile(self, aManifestFile):
        """
        @fn getDirectoryFromManifestFile(self, aManifestFile)
        @brief return a directory of a manifest file.

        @param aManifestFile the URI of the manifest file
        @return the directory containing the manifest file
        """
        return aManifestFile[:(string.rfind(aManifestFile, "/") + 1)]

    def addReftests(self, aSelenium, aRoot, aManifestFile, aIndex,
                    aInheritedStatus = EXPECTED_PASS):
        """
        @fn addReftests(self, aSelenium, aRoot, aManifestFile, aIndex,
                        aInheritedStatus = EXPECTED_PASS)
        @brief This function parses a reftest manifest file and adds the tests
        to the test suite.
        @see   http://mxr.mozilla.org/mozilla-central/source/layout/tools/reftest/README.txt

        @param aSelenium @ref seleniumMathJax object that will be used for
        the test suite, or a string "printReftestList"/"printNotes".
        @param aRoot root of the MathJax-test directory
        @param aManifestFile manifest file to parse
        @param aIndex index of the manifest file inside the @ref mListOfTests
        string. -1 means run all tests.
        @param aInheritedStatus expected status inherited from ancestor manifest
        files. @ref EXPECTED_PASS, @ref EXPECTED_FAIL etc
        @return the new index inside @ref mListOfTests

        @exception "invalid listOfTests" The @ref mListOfTests does not match
        the file hierarchy given by the manifest file.
        @exception "http syntax not supported" This Mozilla's syntax is used
        in the manifest but it is not supported in this testing framework.
        @exception "loadtest can't be marked as fails/random" A loadtest is
        marked fails or random in the manifest.        
        @exception "reftest syntax not supported" Other syntax errors in the
        manifest.
        """
        testDirectory = self.getDirectoryFromManifestFile(aManifestFile)
        index = aIndex

        with open(aRoot + aManifestFile) as f:

            state2 = 0
            annotationPrefix = testDirectory.replace('/', '_')

            for line in f:

                state = 0
                testClass = None
                testType = None
                testURI = None
                testURIRef = None         
                testExpectedStatus = 0
                testSlow = False
                testAnnotation = None

                errorMsg = ("invalid line in " + aRoot + aManifestFile +
                            ": " + line + "\n")

                if aSelenium == "printNotes":
                    if state2 == 1:
                        if line.startswith("#") and not line.startswith("# @"):
                            words = line.split()
                            if len(words) > 1:
                                print line[1:].rstrip().lstrip()
                            continue
                        else:
                            print '</div>'
                            state2 = 0

                    if state2 == 0:
                        if line.startswith("# @"):
                            annotationID = line.split()[1][1:]
                            print '<div id="' + \
                                annotationPrefix + \
                                annotationID + '">'
                            print '<h2><a href="' + MATHJAX_TEST_PUBLIC_URI + \
                                'testsuite/' + aManifestFile + '">' + \
                                aManifestFile + ' [' + \
                                annotationID + ']</a></h2>'
                            state2 = 1
                            continue

                for word in line.split():
                    
                    if word[0] == '#':
                        # the remaining of the line is a comment
                        break

                    if state == 0:
                        try:
                            # link to an annotation
                            if word.startswith("annotate"):
                                # 8 = len(annotate)
                                testAnnotation = word[8:]
                                continue

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
                            elif word == "fuzzy":
                                testExpectedStatus = EXPECTED_FUZZY
                                continue
                            elif word.startswith("fuzzy-if"):
                                # 8 = len("fuzzy-if")
                                if conditionParser.parse(aSelenium, word[8:]):
                                    testExpectedStatus = EXPECTED_FUZZY
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
                        except Exception as data:
                            raise Exception(errorMsg + str(repr(data)))

                    if state == 1 and word == "include":
                        # 1. include
                        state = 2
                        continue

                    if state == 2:
                        # 1. <relative_path>
                        reftestList = testDirectory + word
                        if type(aSelenium) == str:
                          if aSelenium == "printList":
                            print ",[\"" + \
                                self.getDirectoryFromManifestFile(word) + "\"",
                            self.addReftests(aSelenium, aRoot, reftestList, -1,
                                             testExpectedStatus)
                            print "]",
                          elif aSelenium == "printNotes":
                              self.addReftests(aSelenium, aRoot, reftestList,
                                               -1, testExpectedStatus)
                        else:
                            if index == -1:
                                self.addReftests(aSelenium,
                                                 aRoot,
                                                 reftestList,
                                                 -1,
                                                 testExpectedStatus)
                            else:
                                if self.mListOfTests[index] == "2":
                                    # all the tests in the subdirectory
                                    self.addReftests(aSelenium,
                                                     aRoot,
                                                     reftestList,
                                                     -1,
                                                     testExpectedStatus)
                                    index = index + 1
                                elif self.mListOfTests[index] == "1":
                                    # tests indicated in listOfTests
                                    index = index + 1
                                    index = self.addReftests(aSelenium,
                                                             aRoot,
                                                             reftestList,
                                                             index,
                                                             testExpectedStatus)
                                elif self.mListOfTests[index] == "0":
                                    # none of the tests in the subdirectory
                                    index = index + 1
                                else:
                                    raise Exception(errorMsg +
                                                    "invalid listOfTests")
                        break

                    if state == 1:
                        # 2. [<http>]
                        state = 3
                        if word.startswith("HTTP"):
                            raise Exception(errorMsg +
                                            "http syntax not supported")

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
                        testURI = word
                        if testClass == loadReftest:
                            if (testExpectedStatus == EXPECTED_FAIL or
                                testExpectedStatus == EXPECTED_RANDOM):
                                raise Exception(errorMsg +
                                                "loadtest can't be marked as \
fails/random")
                            state = 6
                        elif testClass == scriptReftest:
                            state = 6
                        elif testClass == visualReftest:
                            if (type(aSelenium) != str and
                                aSelenium.mBrowser == "HTMLUnit"):
                                testExpectedStatus = EXPECTED_IRRELEVANT
                            state = 5
                        else:
                            state = 5
                        continue

                    if state == 5:
                        # 2. <url_ref>
                        testURIRef = word
                        state = 6
                        continue

                    raise Exception(errorMsg + "reftest syntax not supported");

                # end for word

                if state == 6:
                    if type(aSelenium) == str:
                        if aSelenium == "printList":
                            print ",\"" + testURI + "\"",
                            verifyPageExistence(testDirectory,
                                                testURI)
                            if testURIRef:
                                verifyPageExistence(testDirectory,
                                                    testURIRef)
                    else:
                        if (index == -1 or self.mListOfTests[index] == "1"):
                            self.mTests.append(testClass(self,
                                                         aSelenium,
                                                         testType,
                                                         testDirectory,
                                                         testURI,
                                                         testURIRef,
                                                         testExpectedStatus,
                                                         testSlow,
                                                         testAnnotation))
                            self.mNumberOfTests = self.mNumberOfTests + 1

                        if (index == -1):
                            continue
                        elif (self.mListOfTests[index] == "0" or
                              self.mListOfTests[index] == "1"):
                            index = index + 1
                            continue
                        else:
                            raise Exception("invalid listOfTests")
            # end for line

        # end with open
        return index

    def takeReferenceScreenshot(self, aURIRef, aSelenium):
        """
        @fn takeReferenceScreenshot(self, aURIRef, aSelenium)
        @brief take a screenshot of a reference page for a visual test. If
        the URI is the same as @ref mPreviousURIRef, then we return
        @ref mPreviousImageRef immediatly. This is a cache system to speed up
        the execution of tests sharing the same reference page.
        
        @param aURIRef   the URI of the reference page to capture
        @param aSelenium @ref seleniumMathJax object in which the tests are
        executed.
        """
        if (aURIRef == self.mPreviousURIRef):
            return self.mPreviousImageRef

        aSelenium.open(aURIRef, aIsReference=True)
        # self.mPreviousURIRef is only set after the page is loaded, so that
        # the screenshot won't be used if the loading failed.
        self.mPreviousURIRef = aURIRef
        self.mPreviousImageRef = aSelenium.takeScreenshot()
        return self.mPreviousImageRef

    def sendRequest(self, aStatus, aProgress = None):
        """
        @fn sendRequest(self, aStatus, aProgress = None):
        @brief Send status information to the task handler
        
        @details If @ref mTaskHandler is None, this function does nothing.
        Otherwise, it connects to the task handler using the specified host and
        port and send the request "TASK UPDATE pid aStatus Progress", where
        Progress is either the specified aProgress or the string
        @ref mTestsExecuted / @ref mNumberOfTests if aProgress is None.
        """

        if self.mTaskHandler == None:
            return

        if aProgress == None:
           aProgress = \
               str(self.mTestsExecuted) + "/" + str(self.mNumberOfTests)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.mTaskHandler[0], self.mTaskHandler[1]))
        sock.send("TASK UPDATE " +
                  self.mTaskHandler[2] + " " +
                  aStatus + " " +
                  aProgress + "\n")

    def run(self):
        """
        @fn run(self)
        @brief run the test suite
        @return True if the testsuite completed. False if a fatal error occured.
        """
        for test in self.mTests:
            self.sendRequest("Running")

            # execute the test
            test.runTest()

            # flush the output buffer (so that the test information will really
            # be written in the output file)
            sys.stdout.flush()

            self.mTestsExecuted = self.mTestsExecuted + 1

        return True
            
class reftest():

    """
    @class reftest::reftest
    @brief A class implementing a test case.
    """

    def __init__(self,
                 aTestSuite,
                 aSelenium, aType, aReftestDirectory, aURI, aURIRef,
                 aExpectedStatus, aSlow, aTestAnnotation):
        """
        @fn __init__(self,
                     aTestSuite,
                     aSelenium, aType, aReftestDirectory, aURI, aURIRef,
                     aExpectedStatus, aSlow, aTestAnnotation)
        @param aTestSuite Value to assign to @ref mTestSuite
        @param aSelenium Value to assign to @ref mSelenium
        @param aType Value to assigne to @ref mType
        @param aReftestDirectory the directory of the test page
        @param aURI the name of the test page
        @param aURIRef the name of the reference page. It may be None if the
        test is not a comparison.
        @param aExpectedStatus Value to assign to @ref mExpectedStatus
        @param aSlow Value to assign to @ref mSlow
        @param aTestAnnotation Value to assign to @ref mTestAnnotation

        @property mTestSuite
        The @ref reftestSuite running the tests
        @property mSelenium
        The @ref seleniumMathJax object in which the tests are run
        @property mType
        the type of reftest, either "==", "!=" or None if there is no
        comparison involved.
        @property mURI
        the URI of the page, given by aReftestDirectory + aURI
        @property mURIRef
        If aURIRef is given, it is aReftestDirectory + aURIRef. Otherwise it
        is None.
        @property mID
        An ID for the test. Initialized with the name of the test page.
        @property mExpectedStatus
        expected status for this test. @ref EXPECTED_PASS, @ref EXPECTED_FAIL
        etc
        @property mSlow
        whether this test is marked slow
        @property mTestAnnotation
        A string containing references of the form id to point to the
        testsuite note page.
        """
        self.mTestSuite = aTestSuite
        self.mSelenium = aSelenium
        self.mType = aType
        self.mURI = aReftestDirectory + aURI

        if aURIRef == None:
            self.mURIRef = None
        else:
            self.mURIRef = aReftestDirectory + aURIRef

        self.mID = self.mURI
        self.mExpectedStatus = aExpectedStatus
        self.mSlow = aSlow
        self.mTestAnnotation = aTestAnnotation

    def id(self):
        """
        @fn id(self)
        @return the test id @ref mID
        """
        return self.mID

    def shouldSkipTest(self):
        """
        @fn shouldSkipTest(self)
        Check whether the test is irrelevant, expected to die or slow and what
        is indicated in the configuration of @ref mTestSuite, in order to
        determine if we should skip this test.

        @return whether the test should be skipped
        """

        if (not self.mTestSuite.mStarted):
            if (self.mTestSuite.mRunningTestID == self.mID):
                self.mTestSuite.mStarted = True
            else:
                return True

        self.mTestSuite.mRunningTestID = self.mID

        if self.mExpectedStatus == EXPECTED_IRRELEVANT:
            msg = "REFTEST INFO | " + self.mID
            msg += " is irrelevant for this configuration\n"
            print msg
            return True

        if ((not self.mTestSuite.mRunSkipTests) and
            self.mExpectedStatus == EXPECTED_DEATH):
            msg = "\nREFTEST TEST-KNOWN-FAIL | " + self.mID + " | (SKIP)"
            if (self.mTestAnnotation):
                msg += " " + self.mTestAnnotation
            msg += "\n"
            print msg
            return True

        if  ((not self.mTestSuite.mRunSlowTests) and self.mSlow):
            msg = "\nREFTEST INFO | " + self.mID + " | (SLOW)"
            if (self.mTestAnnotation):
                msg += " " + self.mTestAnnotation
            msg += "\n"
            print msg
            return True

        return False

    def determineSuccess(self, aType, aResult):
        """
        @fn determineSuccess(self, aType, aResult):
        @brief determine the success of the unit test

        @param aType the type of the test "==", "!=" or None
        @param aResult For comparison test, whether the test and reference are
        equal. Otherwise, whether the test was successful.
        @return a pair (success, msg)

        @details The success takes into account the result given but also
        whether it matches the expected status. For example if the test passed
        but was expected to fail, the success is False. msg is a
        string used in the test report, "REFTEST TEST-PASS | id | " for example.
        """

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

        if (self.mTestAnnotation):
            msg += self.mTestAnnotation + " "

        return success, msg

    def escapeExceptionMessage(self, aExceptionMessage):
        # escape '&', '<' and '> for inclusion in test results
        msg = cgi.escape(aExceptionMessage);
        # also escape '@', so that it won't be considered an annotation
        msg = msg.replace("@", "&#64;");
        return msg;

    def runTest(self):

        if self.shouldSkipTest():
            # skip the test
            return

        try:
            # execute the test
            self.runTest_()
        except seleniumMathJax.ReftestError as data:
            (success, msg) = self.determineSuccess(None, False)
            msg += self.escapeExceptionMessage(str(data))
            print msg
        except WebDriverException as data:
            # exception raised by WebDriver
            (success, msg) = self.determineSuccess(None, False)
            msg += self.escapeExceptionMessage(data.msg)
            print msg
            # XXXfred: are WebDriverExceptions all fatal exceptions?
            # Otherwise, we should not propagate them
            raise
        except Exception as data:
            # other exception.
            (success, msg) = self.determineSuccess(None, False)
            msg += self.escapeExceptionMessage(repr(data))
            print msg
            raise
        
    def runTest_(self):
        None

class loadReftest(reftest):

    """
    @class reftest::loadReftest
    @brief A class for load reftest
    @details A load test simply loads the test page. If an exception happens
    (crash, hang etc) the test fails.
    """

    def runTest_(self):
        """
        @fn runTest_(self)
        @brief run the loadReftest
        """

        self.mSelenium.open(self.mURI)

        (success, msg) = self.determineSuccess(self.mType, True)
        msg += "(LOAD ONLY)\n"
        print msg

class scriptReftest(reftest):

    """
    @class reftest::scriptReftest
    @brief A class for script reftest
    @details A script test executes several Javascript tests on a page and
    returns the success.
    """

    def runTest_(self):

        """
        @fn runTest_(self)
        @brief run the scriptReftest
        """

        self.mSelenium.open(self.mURI)

        (success1, msg1) = self.mSelenium.getScriptReftestResult()
        (success, msg) = self.determineSuccess(self.mType, success1)
        msg += "(SCRIPT REFTEST)"
        if success:
            print msg
            self.mTestSuite.printInfo(msg1)
        else:
            print msg
            self.mTestSuite.printInfo(msg1)
       
class treeReftest(reftest):

    """
    @class reftest::treeReftest
    @brief A class for tree reftest
    @details A tree reftest compares the MathML source of two pages.
    """

    def runTest_(self):

        """
        @fn runTest_(self)
        @brief run the treeReftest
        """

        self.mSelenium.open(self.mURI)
        source = self.mSelenium.getMathJaxSourceMathML()
        self.mSelenium.open(self.mURIRef, aIsReference=True)
        sourceRef = self.mSelenium.getMathJaxSourceMathML()

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

def isSmallPixelValue(aPixelValue):
    if aPixelValue <= 15:
        return 0
    else:
        return 1

class visualReftest(reftest):

    """
    @class reftest::visualReftest
    @brief A class for visual reftest
    @details A visual reftest compare the visual rendering of two pages.
    """

    def runTest_(self):

        """
        @fn runTest_(self)
        @brief run the visualReftest
        """

        # take the screenshot of the test
        self.mSelenium.open(self.mURI)
        image = self.mSelenium.takeScreenshot()
        
        # take the screenshot of the reftest using the one in memory if it
        # has been used just before.
        imageRef = self.mTestSuite.takeReferenceScreenshot(self.mURIRef,
                                                           self.mSelenium)

        # Compare image and imageRef
        diff = ImageChops.difference(image, imageRef)
        if self.mExpectedStatus == EXPECTED_FUZZY:
            diff = Image.eval(diff, isSmallPixelValue)
        box = diff.getbbox()
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
