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
 *  @file taskViewer.js
 *  @brief script for taskViewer.php
 *
 *  This file is used by taskViewer.php
 */

/**
 * Concatenate the names of all the selected tasks in one comma separated list
 */
function computeTaskNameList()
{
    var multipleTasksList = document.getElementById("multipleTasksList");
    var taskList = document.getElementById("taskList");
    var checkboxes = taskList.getElementsByClassName("taskCheckbox");
    multipleTasksList.value = "";
    for (var i = 0; i < checkboxes.length; i++) {
        if (checkboxes[i].checked) {
            if (multipleTasksList.value != "") {
                multipleTasksList.value += ",";
            }
            multipleTasksList.value += checkboxes[i].name.
                substr(String("checkbox-").length);
        }
    }
}

/**
 * Set all the task checkboxes to aChecked
 * @param aChecked Whether the checkboxes should be checked
 */
function taskCheckboxes(aChecked)
{
    var taskList = document.getElementById("taskList");
    var checkboxes = taskList.getElementsByClassName("taskCheckbox");
    for (var i = 0; i < checkboxes.length; i++) {
        checkboxes[i].checked = aChecked;
    }
}

/**
 *  Send a request to remove selected tasks
 */
function removeMultipleTasks()
{
    // XXXfred Warn user about impossible removal before submitting?
    document.getElementById("multipleTasksCommand").value = "MULTIPLE_REMOVE";
    computeTaskNameList();
    document.forms['multipleTasks'].submit();
}

/**
 * Send a request to run selected tasks
 */
function runMultipleTasks()
{
    // XXXfred Warn user about impossible run before submitting?
    document.getElementById("multipleTasksCommand").value = "MULTIPLE_RUN";
    computeTaskNameList();
    document.forms['multipleTasks'].submit();
}

/**
 * Send a request to restart selected tasks
 */
function restartMultipleTasks()
{
    // XXXfred Warn user about impossible restart before submitting?
    document.getElementById("multipleTasksCommand").value = "MULTIPLE_RESTART";
    computeTaskNameList();
    document.forms['multipleTasks'].submit();
}

/**
 * Send a request to stop selected tasks
 */
function stopMultipleTasks()
{
    // XXXfred Warn user about impossible stop before submitting?
    document.getElementById("multipleTasksCommand").value = "MULTIPLE_STOP";
    computeTaskNameList();
    document.forms['multipleTasks'].submit();
}
