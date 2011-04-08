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

function finalizeScriptReftests()
{
    var success = true;
    var textarea = document.createElement("textarea");
    textarea.cols = 80;
    textarea.rows = 20;
    textarea.id = "results";

    textarea.value = "Results of the Script reftest:\n\n"

    var testcases = getTestCases();
    for (var i = 0; i < testcases.length; i++) {
        test = testcases[i];
        testPassed = test.testPassed();
        success = success && testPassed;
        textarea.value += "Test " + (i + 1) + ": " + test.testDescription();
        textarea.value += "... " + (testPassed ? "passed" : "failed") + "\n";
    }

    textarea.value += "\nScript reftest: " +  (success ? "passed" : "failed\n");
    document.body.appendChild(textarea);

    if (success) {
        document.documentElement.className = "reftest-success";
        document.title += " (success)";
    } else {
        document.documentElement.className = "reftest-failure";
        document.title += " (failure)";
    }
}
