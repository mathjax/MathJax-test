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
 *  @file taskCreator.js
 *  @brief script for taskCreator.php
 *
 *  This file is used by taskCreator.php
 */

function updateFieldVisibility(aCheckboxId, aFieldId, aCond)
{
    el = document.getElementById(aFieldId);
    if (document.getElementById(aCheckboxId).checked == aCond) {
        el.style.visibility = "visible";
    } else {
        el.style.visibility = "hidden";
    }
}

function updateFieldValue(aSelectId, aFieldId)
{
    document.getElementById(aFieldId).value =
        document.getElementById(aSelectId).value
}

function openReftestSelector()
{
    window.open("selectReftests.xhtml","","");
}

function init()
{
    updateFieldVisibility("taskSchedule", "crontabParameters", true);
    updateFieldVisibility("useWebDriver", "fullScreenMode", false);
    updateFieldValue("host_select", "host");
}
