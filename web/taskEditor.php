<?php
/* -*- Mode: PHP; tab-width: 2; indent-tabs-mode:nil; -*- */
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
 *  @file taskEditor.php
 *  @brief This file contains a form to create a new task
 *  
 */

  echo '<?xml version="1.0" encoding="UTF-8"?>';
  include('config.php');
  include('branchList.php');

  if (isset($_GET['taskName'])) {
    $taskName = $_GET['taskName'];
  } else {
    $taskName = $DEFAULT_TASK_NAME;
  }

  /**
   *  @fn generateOptionList($aList)
   *  @brief write several a list of &lt;option&gt;...&lt;/option&gt; 
   *  @param aList list of options
   */
  function generateOptionList($aList)
  {
    for ($i = 0; $i < count($aList); $i++) {
      echo '<option>'.$aList[$i].'</option>';
    }
  }

  /**
   *  @fn generateCheckboxList($aList)
   *  @brief write several a list of checkboxes
   *  @param aList list of options
   */
  function generateCheckboxList($aList, $aName)
  {
    for ($i = 0; $i < count($aList); $i++) {
      echo '<li><input type="checkbox" name="'.$aName.strval($i).'" value="';
      echo $aList[$i].'" checked="checked"/>'.$aList[$i].'</li>';
    }
  }

?>

<!-- -*- Mode: HTML; tab-width: 2; indent-tabs-mode:nil; -*- -->
<!-- vim: set ts=2 et sw=2 tw=80: !-->
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <title>Task Editor</title>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <!-- Copyright (c) 2011 Design Science, Inc.
         License: Apache License 2.0 -->
    <link rel="stylesheet" type="text/css" href="default.css"/>
    <script type="text/javascript" src="config.js"></script>
    <script type="text/javascript" src="taskEditor.js"></script>
  </head>

  <body onload="init()">
    <div class="related">
      <h3>Navigation</h3>
      <ul>
        <li><a href="./">Back to home</a></li> 
        <li><a href="./taskViewer.php">Task Viewer</a></li> 
      </ul>
    </div>  

    <div class="body">
      <h1>Task Editor</h1>
      
      <form action="commandHandler.php" method="post" id="commandHandlerForm">

        <fieldset>
          <legend>Task</legend>
          <p>
            <label>task name:
              <input id="taskName" name="taskName" type="text"
                     required="required"
                     pattern="([a-z]|[A-Z]|[0-9]|\-){1,40}"
                     value="<?php echo $taskName;?>"
                     onchange="taskNameChange();"
                     maxlength="40"/></label> (alphanumeric)
          </p>
          <p>
            <label>outputDirectory:
            <input id="outputDirectory" name="outputDirectory" type="text"
                   pattern="([a-z]|[A-Z]|[0-9]|\-){1,40}" maxlength="40"
                   value=""/>
            </label>
          </p>
          <p>
            <label>schedule task:
              <input id="taskSchedule" name="taskSchedule" type="checkbox"
                     onchange="updateFieldVisibility('taskSchedule',
                                                     'crontabParameters',
                                                     true)"/>
            </label>
            <span id="crontabParameters" style="visibility: hidden;">
            <span>day: 
            <select id="crontabDow" name="crontabDow">
              <option>*</option>
              <?php generateOptionList($WEEKDAY_LIST); ?>
            </select>
            <select id="crontabDom" name="crontabDom">
              <option>*</option>
              <?php
                for ($i = 1; $i <= 31; $i++) {
                  echo '<option>'.$i.'</option>';
                }
              ?>
            </select>
            <select id="crontabMon" name="crontabMon">
              <option>*</option>
              <?php generateOptionList($MONTH_LIST); ?>
            </select>
            </span>
            <span>time:
              <select id="crontabH" name="crontabH">
                <option>*</option>
                <?php
                  for ($i = 0; $i < 24; $i++) {
                    $v = ($i < 10 ? '0' : '').$i;
                    echo '<option>'.$v.'</option>';
                  }
                ?>
              </select> :
              <select id="crontabM" name="crontabM">
                <option>*</option>
                <?php
                  for ($i = 0; $i < 60; $i++) {
                    $v = ($i < 10 ? '0' : '').$i;
                    echo '<option>'.$v.'</option>';
                  }
                ?>
              </select>
            </span>

            (<a href="http://en.wikipedia.org/wiki/Cron">cron syntax</a>)
            </span>
          </p>
          <p>Fast configuration:
             <ul style="list-style: none;">
               <li><input type="radio" name="taskSingleMultiple"
                          value="single"
                          onchange="updateFieldsFromTaskSingleMultiple()"/>
                Create a single task:
                <select id="fast_config"
                    onchange="fastConfiguration()">
                  <option>Select template...</option>
                  <?php generateOptionList($TEMPLATE_CONFIG_LIST); ?>
                </select>
               </li>
               <li><input type="radio" name="taskSingleMultiple" 
                          value="multiple"
                          onchange="updateFieldsFromTaskSingleMultiple()" />
               Create multiple tasks:
               <ul id="taskMultipleList" style="list-style: none;">
               <?php generateCheckboxList($TEMPLATE_CONFIG_LIST,
                                          "taskTemplate"); ?></li>
               </ul>
             </ul>
          </p>
        </fieldset>

        <fieldset>
          <legend>Framework:</legend>
          <p>
            <label>use Grid:
              <input id="useGrid" name="useGrid" type="checkbox"
                     onchange="updateFieldVisibility('useGrid',
                                                     'seleniumServer',
                                                      false)"></input>
            </label>
          </p>
          <p id="seleniumServer">
            <label>host:
              <input id="host" name="host" type="text" required="required"
                     pattern="([a-z]|[A-Z]|[0-9]|-|\.)+"
                     value=""
                     maxlength="255"/>
            </label> (or choose among known hosts:
            <select id="host_select"
                    onchange="updateFieldValueFrom('host_select', 'host');
                              updateSelectIndex('host_select',
                                                'operatingSystem',
                                                HOST_LIST_OS)">
              <?php generateOptionList($HOST_LIST); ?>
            </select>)

            ; 
            <label>port:
              <input id="port" name="port" type="text"
                     value="<?php echo $SELENIUM_SERVER_PORT;?>"/>
            </label>
          </p>
          <p>
            <label>mathJaxPath:
              <input id="mathJaxPath" name="mathJaxPath" type="text" size="50"
                     pattern="(.)+\/" onchange="updateUnpackedBoxFromMathJaxPath()"
                     value="<?php echo $DEFAULT_MATHJAX_PATH;?>"/>
            </label>
            unpacked:
            <input id="unpacked" type="checkbox" onchange="updateMathJaxPathFromUnpackedBox()"/>
            (or choose among known branches:
            <select id="branchSelect" onchange="updateMathJaxPathFromBranch()">
              <?php generateOptionList($BRANCH_LIST); ?>
            </select>)
          </p>
          <p>
            <label>mathJaxTestPath:
              <input id="mathJaxTestPath" name="mathJaxTestPath" type="text" size="50"
                     pattern="(.)+\/"
                     value="<?php echo $MATHJAX_TEST_LOCAL_URI;?>testsuite/"/>
            </label>
          </p>
          <p>
            <label>timeOut:
              <input id="timeOut" name="timeOut" type="number" min="1" max="120"
                     value="<?php echo $DEFAULT_TIMEOUT?>"/> (seconds)
            </label>
          </p>
          <p>
            <label>use WebDriver:
              <input id="useWebDriver" name="useWebDriver" type="checkbox"
                     onchange="updateFieldVisibility('useWebDriver',
                                                     'fullScreenMode_', false);
                               updateFieldVisibility('useWebDriver',
                                                     'browserPath_', false);
                               updateFieldVisibility('useWebDriver',
                                                     'browserVersion_', true);"/>
            </label>
          <span id="fullScreenMode_">
            <label>fullScreenMode:
              <input id="fullScreenMode" name="fullScreenMode" type="checkbox" checked="checked"/>
            </label>
          </span>
	  </p>
          <p>
            <label>priority:</label>
	    <input id="priority" name="priority" type="text"
                     value="0"/>
          <p>
          <p>
            <label>formatOutput:
              <input id="formatOutput" name="formatOutput" type="checkbox" checked="checked"/>
            </label>
          </p>
          <p>
            <label>compressOutput:
              <input id="compressOutput" name="compressOutput" type="checkbox" checked="checked"/>
            </label>
          </p>
        </fieldset>

        <fieldset>
          <legend>Platform:</legend>
          <p>
            <label>operatingSystem:
              <select id="operatingSystem" name="operatingSystem">
                <?php generateOptionList($OS_LIST); ?>
              </select>
            </label>
          </p>
          <p>
            <label>browser:
              <select id="browser" name="browser"
                      onchange="updateFieldVisibility('browser',
                                                      'browserMode_', 'MSIE')">
              <?php generateOptionList($BROWSER_LIST); ?>
              </select>
            </label>
          <span id="browserMode_">
            <label>browserMode:
              <select id="browserMode" name="browserMode">
              <?php generateOptionList($BROWSER_MODE_LIST); ?>
              </select>
            </label>
          </span></p>
          <p id="browserVersion_">
            <label>browserVersion:
              <input id="browserVersion" name="browserVersion" type="text"
                     value="default"
                     readonly="readonly"/>
            </label>
          </p>
          <p id="browserPath_">
            <label>browserPath:
              <input id="browserPath" name="browserPath" type="text"
                     value="default"
                     readonly="readonly"/>
            </label>
          </p>
          <p>
            <label>font:
              <select id="font" name="font">
              <?php generateOptionList($FONT_LIST); ?>
              </select>
            </label>
          </p>
          <p>
            <label>outputJax:
              <select id="outputJax" name="outputJax">
              <?php generateOptionList($OUTPUT_JAX_LIST); ?>
              </select>
            </label>
          </p>
        </fieldset>

        <fieldset>
          <legend>Testsuite:</legend>
          <p>
            <label>runSlowTests:
              <input id="runSlowTests" name="runSlowTests" type="checkbox"/>
            </label>
          </p>
          <p>
            <label>runSkipTests:
              <input id="runSkipTests" name="runSkipTests" type="checkbox"/>
            </label>
          </p>
          <p>
            <label>listOfTests:
              <input style="visibility: hidden; position: absolute;" id="listOfTests"
                     name="listOfTests" type="text" value="default"
                     pattern="(default|([0-2]+))"/>
            </label>
            <a href="javascript:openReftestSelector();">Reftest Selector</a>
          </p>
          <p>
            <label>startID:
              <input id="startID" name="startID" type="text" value="default"
                     size="50" pattern="(default|([a-z]|[A-Z]|[0-9]|=|?|&|_|-|\.|/)+)" />
            </label> (used for test recovery)
          </p>
        </fieldset>

        <p style="visibility: hidden; height: 0;">
            <input id="command" name="command" type="text"
                   value="EDIT" readonly="readonly"/>
        </p>

        <p style="text-align: right;">
          <input id="submit" type="submit" value="Create new task"/>
        </p>

      </form>

    </div>
  </body>
</html>
