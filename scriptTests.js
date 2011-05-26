/* -*- Mode: Javascript; tab-width: 2; indent-tabs-mode:nil; -*- */
/* vim: set ts=2 et sw=2 tw=80: */
/* ***** BEGIN LICENSE BLOCK *****
/* Version: Apache License 2.0
 *
 * Copyright (c) 2011 Design Science, Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * Contributor(s):
 *   Frederic Wang <fred.wang@free.fr> (original author)
 *
 * ***** END LICENSE BLOCK ***** */

/**
 *  @file
 *  This file is for test pages of type @ref reftest::scriptReftest
 */

/**
 * Return a test result, endowed with the methods given in Mozilla's description
 * of script reftests:
 *
 * - testPassed() returns true if the test result object passed,
 *                otherwise it returns false.
 * - testDescription() returns a string describing the test
 *                     result.
 *
 * @tparam String  aTestDescription the description o the test
 * @tparam Boolean aTestPassed      whether the test is passed
 * 
 * @treturn Object          the test result object
 *
 */
function newScriptReftestResult(aTestDescription, aTestPassed)
{
    var result = new Object(); 

    result["mTestPassed"] = aTestPassed;
    result["mTestDescription"] = aTestDescription;
    // These functions are only useful to follow Mozilla's description of
    // script reftests. finalizeScriptReftests use them, so that it would also
    // be possible to load tests from other testing systems.
    result["testPassed"] = function() { return this.mTestPassed; }
    result["testDescription"] = function() { return this.mTestDescription; }

    return result;
}

/**
 * finalize the script reftests
 *
 * A textarea is inserted in the document, describing the result for each test
 * as well as the final result. This one is also set in the class and title
 * of the document.
 *
 */
function finalizeScriptReftests()
{
    // create a textarea to store the list of results
    var textarea = document.createElement("textarea");
    textarea.cols = 80;
    textarea.rows = 20;
    textarea.id = "results";

    textarea.value = "Results of the Script reftest:\n\n"
    document.body.appendChild(textarea);

    // fill the textarea with the results of each test
    var testcases = getTestCases();
    var success = true;
    for (var i = 0; i < testcases.length; i++) {
        test = testcases[i];
        testPassed = test.testPassed();
        success = success && testPassed;
        textarea.value += "Test " + (i + 1) + ": " + test.testDescription();
        textarea.value += "... " + (testPassed ? "passed" : "failed") + "\n";
    }

    // print the global success in the textarea
    textarea.value += "\nScript reftest: " +  (success ? "passed" : "failed\n");

    // set the global success in the title and class name of the document
    if (success) {
        document.documentElement.className = "reftest-success";
        document.title += " (success)";
    } else {
        document.documentElement.className = "reftest-failure";
        document.title += " (failure)";
    }
}
