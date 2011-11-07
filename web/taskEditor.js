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
 *  @file taskEditor.js
 *  @brief script for taskEditor.php
 *
 *  This file is used by taskEditor.php
 */

/**
 * Open a new window with the reftest selector.
 */
function openReftestSelector()
{
    window.open("selectReftests.xhtml","","");
}

/**
 * update the visibility of a field according to the value of another one.
 *
 * This function consider a checkbox, input text or input select field
 * aFieldId1. If its value is the same as aValue, then aFieldId2 is made visible
 * otherwise it is made hidden.
 *
 * @param aFieldId1 id of the field whose value is read.
 * @param aFieldId2 id of the field whose visibility should be changed.
 * @param aValue value to consider.
 * 
 */
function updateFieldVisibility(aFieldId1, aFieldId2, aValue)
{
    var f1 = document.getElementById(aFieldId1);
    var f2 = document.getElementById(aFieldId2);
    var tag = f1.tagName.toLowerCase();
    if ((tag == "input" &&
         f1.type == "checkbox" && f1.checked == aValue) ||
        (tag == "select" && f1.value == aValue)) {
        f2.style.visibility = "visible";
        f2.style.position = "relative";
    } else {
        f2.style.visibility = "hidden";
        f2.style.position = "absolute";
    }
}

/**
 * Update a field value according to the value of a select field:
 * value of aField := value of aSelect
 *
 * @param aSelectId id of the select field
 * @param aFieldId field to update
 * 
 */
function updateFieldValueFrom(aSelectId, aFieldId)
{
    document.getElementById(aFieldId).value =
        document.getElementById(aSelectId).value
}

/**
 * Update the index of a select field according to the selected index of another
 * select field, using an array.
 * selected index of Select2 := Array[selected index of Select1]
 * 
 * @param aSelectId1 Field to take as a reference.
 * @param aSelectId2 Field to update.
 * @param aArray     Array used.
 *
 */
function updateSelectIndex(aSelectId1, aSelectId2, aArray)
{
    document.getElementById(aSelectId2).selectedIndex =
        aArray[document.getElementById(aSelectId1).selectedIndex];
}

/**
 * Update the submit button of the form, according to whether a task exists:
 * The submit says whether we update or create a task.
 * 
 * @param aTaskName name of the task considered
 * @param aExists   whether the task exists
 */
function updateTaskExists(aTaskName, aExists)
{
    document.getElementById("submit").value = aExists ?
        ("Update parameters of task '" + aTaskName + "'") :
        ("Create a new task '" + aTaskName + "'");
}

/**
 * Update a field value.
 *
 * This function update the field value corresponding to a given parameter,
 * according to the value we want to assign to it.
 *
 * @param aParamName  name of the parameter
 * @param aParamValue value to assign
 *
 */
function updateField(aParamName, aParamValue)
{
    var field = document.getElementById(aParamName);
    var tag = field.tagName.toLowerCase();
    
    if (tag == "input") {
        if (field.type == "checkbox") {
            field.checked = (aParamValue.toLowerCase() == "true");
        } else {
            field.value = aParamValue;
        }
    } else if (tag == "select") {
        field.selectedIndex = 0;
        for (var i = 0; i < field.length; i++) {
            if (field.options[i].value == aParamValue) {
                field.selectedIndex = i;
                break;
            }
        }
    }
}

/**
 * Update the all the fields of the page to reflect the configuration of an
 * element of the task list. The name of the task is the one given in the
 * taskName field.
 *
 */
function updateFieldsFromTaskName()
{
    var request = new XMLHttpRequest();
    var taskName = document.getElementById("taskName").value;
    request.open('GET', 'taskInfo.php?taskName=' + taskName, true);

    request.onreadystatechange = function (aEvent) {
        updateTaskExists(taskName, false);
        if (request.readyState == 4) {
            if (request.status == 200) {
                var tree = request.responseXML;
                if (tree) {
                    var tables = tree.getElementsByTagName("table");
                    if (tables.length > 0) {
                        updateTaskExists(taskName, true);

                        // First table is special. We only take schedule and
                        // output directory into account and need particular
                        // treatment.

                        var scheduled =
                            (tree.getElementById("taskSchedule") != null);

                        if (scheduled) {
                            // Update the field 'taskSchedule'
                            updateField("taskSchedule", "true");

                            // Update the cron parameters
                            cronParams = ["crontabDow", "crontabDom",
                                          "crontabMon", "crontabH", "crontabM"];
                            for (var i = 0; i < cronParams.length; i++) {
                                var paramName = cronParams[i];
                                var paramValue = tree.
                                    getElementById(paramName).innerHTML;
                                updateField(paramName, paramValue);
                            }
                        }

                        // Update the field 'outputDirectory'
                        var paramName = "outputDirectory";
                        var paramValue = tree.
                            getElementById(paramName).innerHTML;
                        paramValue = paramValue.substring(
                            (scheduled ? 0 : paramValue.indexOf("/") + 1),
                            paramValue.length - 1);
                        updateField(paramName, paramValue);

                        // Update the field from the information of the tables
                        for (var i = 1; i < tables.length; i++) {
                            var trs = tables[i].getElementsByTagName("tr");
                            for (var j = 0; j < trs.length; j++) {
                                var tr = trs[j];
                                var paramName = tr.
                                    getElementsByTagName("th")[0].innerHTML;
                                var paramValue = tr.
                                    getElementsByTagName("td")[0].innerHTML;
                                updateField(paramName, paramValue);
                            }
                        }
                    }
                }
            }
            updateAllFieldVisibilities();
        }
    }

    request.send(null);
}

/**
 * Parse a config file.
 * 
 * This function is used to update the fields of the page according to a given
 * config file.
 */
function parseConfigFile(aContent)
{
    var lines = aContent.split("\n");
    for (var i = 0; i < lines.length; i++) {
        var line = lines[i];
        if (line.length == 0 || line[0] == '[') {
            continue;
        }
        var items = line.split("=");
        if (items.length == 2) {
            var paramName = items[0].trim();
            var paramValue = items[1].trim();
            if (paramValue != "-1" && paramValue != "default") {
                updateField(paramName, paramValue);
            }
        }
    }

    // Choose a host for the given OS
    document.getElementById("host_select").selectedIndex =
        HOST_LIST_OS.indexOf(document.getElementById("operatingSystem").
                             selectedIndex);
    updateFieldValueFrom("host_select", "host");

    // Update field visibilities
    updateAllFieldVisibilities();
}

/**
 * Do a fast configuration for a given platform
 *
 * This function reads the config file whose name is given by the select field
 * value. Non default values are then used in the corresponding fields of the
 * page. 
 */
function fastConfiguration()
{
    var select = document.getElementById("fast_config");
    if (select.selectedIndex == 0) {
        return;
    }

    var configFile = "../testRunner/config/templates/" + select.value + ".cfg";
    var request = new XMLHttpRequest();
    request.open('GET', configFile, true);
    request.onreadystatechange = function (aEvent) {
        if (request.readyState == 4) {
            if (request.status == 200) {
                parseConfigFile(request.responseText);
            }
        }
    }
    request.send(null);
}

/**
 * Update the visibility of all fields, according to the options selected.
 */
function updateAllFieldVisibilities()
{
    updateFieldVisibility("taskSchedule", "crontabParameters", true);
    updateFieldVisibility("useWebDriver", "fullScreenMode_", false);
    updateFieldVisibility("useWebDriver", "aloneOnHost_", true);
    updateFieldVisibility("browser", "browserMode_", "MSIE")
}

/**
 * Update fields from single task / multiple tasks.
 *
 * This function checks whether the user chooses single task / multiple task.
 * In the former case, it calls @ref updateFieldsFromTaskName and hide the task
 * multiple checkboxes. In the latter case, it shows these checkboxes and
 * update the submit button.
 **/
function updateFieldsFromTaskSingleMultiple()
{
    var taskSingleMultiple =
        document.getElementById("commandHandlerForm").taskSingleMultiple;
    var taskMultipleList = document.getElementById("taskMultipleList");

    if (taskSingleMultiple[0].checked) {
        updateFieldsFromTaskName();
        taskMultipleList.style.visibility = "hidden";
        taskMultipleList.style.position = "absolute";
    } else {
        document.getElementById("submit").value =
            "Create or Update multiple tasks '" +
            document.getElementById("taskName").value + "-*'";
        taskMultipleList.style.visibility = "visible";
        taskMultipleList.style.position = "relative";
    }
}

/**
 * Update the unpacked box according to the mathjax path
 */
function updateUnpackedBoxFromMathJaxPath()
{
    var mathJaxPath = document.getElementById("mathJaxPath");
    document.getElementById("unpacked").checked =
        mathJaxPath.value.match(/^(.)*\/unpacked\/$/);
}

/**
 * Add/Remove the "unpacked/" suffix
 */
function updateMathJaxPathFromUnpackedBox()
{
    var mathJaxPath = document.getElementById("mathJaxPath");
    var unpacked = document.getElementById("unpacked").checked;
    if (unpacked) {
        if (!mathJaxPath.value.match(/^(.)*\/unpacked\/$/)) {
            mathJaxPath.value += "unpacked/";
        }
    } else {
        if (mathJaxPath.value.match(/^(.)*\/unpacked\/$/)) {
            var l = String("unpacked/").length;
            mathJaxPath.value = mathJaxPath.value.substr(mathJaxPath.value,
                                                         mathJaxPath.value.
                                                         length - l);
        }
    }
}

/**
 * Initialize the field visibilities and values.
 */
function init()
{
    var taskSingleMultiple =
        document.getElementById("commandHandlerForm").taskSingleMultiple
    taskSingleMultiple[0].checked = true;
    taskSingleMultiple[1].checked = false;
    document.getElementById("fast_config").selectedIndex = 0;
    updateAllFieldVisibilities();
    updateFieldValueFrom("host_select", "host");
    updateFieldValueFrom("taskName", "outputDirectory");
    updateSelectIndex("host_select", "operatingSystem", HOST_LIST_OS);
    updateFieldsFromTaskSingleMultiple();
    updateUnpackedBoxFromMathJaxPath();
}
