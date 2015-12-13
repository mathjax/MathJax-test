/* ***** BEGIN LICENSE BLOCK *****
/* Version: Apache License 2.0
 *
 * Copyright (c) 2011-2015 MathJax Consortium, Inc.
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
 *  @file selectReftests.js
 *  @brief script for selectReftests.html
 *
 *  This file is used by selectReftests.html to provide a user interface to
 *  the test suite and allow to select some tests to execute.
 */

var gNumberOfTests;

/**
 * Fill aParent with XML nodes representing the hierarchy given by aList
 *
 * @tparam Array   aList   an array containing the list of reftests
 * @tparam Element aParent the element to fill
 *
 */
function writeReftestList(aList, aParent)
{
    // Create a checkbox
    var checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.checked = true;
    checkbox.addEventListener("click", checkboxClick, false);
    aParent.appendChild(checkbox);

	  if (aList.constructor == Array) { // directory
        // create a button to open/close the directory
        var button = document.createElement("input");
        button.type = "button";
        button.value = aList[0];
        button.setAttribute("class", "directory");
        button.addEventListener("click", directoryClick, false);
        aParent.appendChild(button);

        // create a sublist
        var ul = document.createElement("ul");
        ul.setAttribute("class", "closed");
        aParent.appendChild(ul);

        // and fill it recursively
        for (var i = 1; i < aList.length; i++) {
            var li = document.createElement("li");
            ul.appendChild(li);
            writeReftestList(aList[i], li)
        }
    } else { // test file
        // create a span with the name of the test
        var span = document.createElement("span");
        span.setAttribute("class", "directory");
        aParent.appendChild(span);
        var text = document.createTextNode(aList);
        span.appendChild(text);
        gNumberOfTests++;
    }
}

/**
 * Function called when a checkbox is checked/unchecked.
 *
 * If the user checks a checkbox, all the parent are also checked using
 * propagateUp. If the checkbox is the one of a directory, all the descendants
 * are also checked/unchecked.
 *
 * @tparam Event aEvent the checkbox click event
 *
 */
function checkboxClick(aEvent)
{
    var checkbox = aEvent.target;
    var ul = checkbox.parentNode.getElementsByTagName("ul")[0];
    if (ul) {
        var list = ul.getElementsByTagName("input");
        for (var i = 0; i < list.length; i++) {
            if (list[i].type == "checkbox") {
                list[i].checked = checkbox.checked;
            }
        }
    }

    if (checkbox.checked) {
        propagateUp(checkbox);
    }
}

/**
 * Check all the checkboxes from bottom to top, starting from aCheckBox and
 * ending to the one representing the testsuite/ root
 *
 * @tparam Element aCheckBox the starting checkbox
 *
 */
function propagateUp(aCheckBox)
{
    if (aCheckBox.parentNode.id != "root") {
        parent = aCheckBox.parentNode.parentNode.parentNode;
        checkbox = parent.getElementsByTagName("input")[0];
        checkbox.checked = true;
        propagateUp(checkbox);
    }
}

/**
 * Function called when the user clicks on a directory.
 *
 * The action is folding/unfolding the directory by removing/attaching a
 * "closed" class.
 *
 * @tparam Event aEvent the directory click event
 *
 */
function directoryClick(aEvent)
{
    var text = aEvent.target;
    var ul = text.parentNode.getElementsByTagName("ul")[0];
    if (ul.hasAttribute("class")) {
        ul.removeAttribute("class")
    } else {
        ul.setAttribute("class", "closed");
    }
}

/**
 * init selectReftests.html using @ref gTestSuite
 * 
 */
function init()
{
    gNumberOfTests = 0;
    
    // fill the root with the test suite hierarchy
    writeReftestList(gTestSuite, document.getElementById("root"));

    document.title += " (" + gNumberOfTests + " tests)";

    if (window.opener) {
        // The selectReftest was opened from taskEditor.php
        document.getElementById("listOfTests").value =
            window.opener.document.getElementById("listOfTests").value
        read();
    }
}

/**
 * Generate the listOfTests string for a given directory/file
 *
 * @tparam Element aParent the XML element representing a directory/file
 *
 * @treturn Object An object with three properties all, none, str indicating
 * whether all/none of the tests of the directory should be run and the
 * listOfTests string for this directory.
 *
 */
function generateListOfTests(aParent)
{
    var checkbox = aParent.getElementsByTagName("input")[0];
    if (!checkbox.checked) {
        // it's not checked, return "none"
        return { all: false, none: true, str: "0"};
    }

    var ul = aParent.getElementsByTagName("ul")[0];
    if (!ul) {
        // it's a file and is selected, return "all"
        return { all: true, none: false, str: "1"};
    }

    var all = true;
    var none = true;
    var str = "";

    // now apply recursively to the subdirectories / files
    var list = ul.childNodes;
    for (var i = 0; i < list.length; i++) {
        var result = generateListOfTests(list[i]);
        if (!result.all) {
            all = false;
        }
        if (!result.none) {
            none = false;
        }
        str += result.str;
    }
    
    if (all) {
        str = "2";
    } else if(none) {
        str = "0";
    } else {
        str = "1" + str;
    }
    
    return {all: all, none: none, str: str};
}

/**
 *  generate a string listOfTests representing the selected tests
 */
function generate()
{
    var result = generateListOfTests(document.getElementById("root"));
    if (result.all) {
        // all tests
        document.getElementById("listOfTests").value = "default";
    } else if(result.none) {
        // no tests
        alert("You must select at least one test!");
        return;
    } else {
        // selection of tests
        // ignore the first character (representing the root testsuite/)
        document.getElementById("listOfTests").value = result.str.substr(1);
    }

    if (window.opener) {
        // The selectReftest was opened from taskEditor.php
        window.opener.document.getElementById("listOfTests").value =
            document.getElementById("listOfTests").value;
        window.close();
    }
}

/**
 * Check the checkboxes of aParent according to the string provided
 *
 * @tparam String  aList   the list of tests represented as a string
 * @tparam int     aIndex  the index in the string where aParent starts
 * @tparam Element aParent the XML element representing a directory/file
 *
 * @treturn int            new value for aIndex
 *
 * @exception "invalid listOfTests"
 *
 */
function readListOfTests(aList, aIndex, aParent)
{
    var index = aIndex;

    // check/uncheck the checkbox for this directory/file
    var checkbox = aParent.getElementsByTagName("input")[0];
    checkbox.checked = (aList[aIndex] != "0");
    index++;

    var ul = aParent.getElementsByTagName("ul")[0];
    if (ul) {
        // It's a directory, consider the subdirectories/files
        if (aList[aIndex] == "1") {
            // apply the actions recursively to this subdirectory
            var list = ul.childNodes;
            for (var i = 0; i < list.length; i++) {
                index = readListOfTests(aList, index, list[i]);
            }
        } else if (aList[aIndex] == "0" || aList[aIndex] == "2") {
            // check or uncheck all in this directory
            var checked = (aList[aIndex] == "2");
            var list = ul.getElementsByTagName("input");
            for (var i = 0; i < list.length; i++) {
                if (list[i].type == "checkbox") {
                    list[i].checked = checked;
                }
            }
        } else {
            throw "invalid listOfTests"
        }
    }
    return index;
}

/**
 *  read the string listOfTests and check/uncheck the checkboxes accordingly
 */
function read()
{
    var listOfTests = document.getElementById("listOfTests").value;
    var root = document.getElementById("root");

    if (listOfTests == "default") {
        // check all the checkboxes
        var list = root.getElementsByTagName("input");
        for (var i = 0; i < list.length; i++) {
            if (list[i].type == "checkbox") {
                list[i].checked = true;
            }
        }
        return;
    }

    // check the checkboxes according to what is in the listOfTests string
    // "1" is for the root root testsuite/
    readListOfTests("1" + listOfTests, 0, root);
}
