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
 *  @file commandHandler.php
 *  @brief Sends editing command to the task handler
 *  
 */

if (!isset($_POST['command']) ||
    !(isset($_POST['taskName']) || isset($_POST['taskList']))) {
  header('Location: taskViewer.php');
  exit;
}
echo '<?xml version="1.0" encoding="UTF-8"?>';
include('config.php');

/**
 *  @brief convert a boolean value to a string
 *  @param aValue boolean value to convert
 *  @return 'true' or 'false'
 */
function boolToString($aValue)
{
  return $aValue ? 'true' : 'false';
}

/**
 *  @brief convert a string from a select form into a valid string
 *  @param aValue string value to convert
 *  @param aSelectValues possible values of the select form
 *  @return aValue if it is found in aSelectValues, or the first element of
 *          aSelectValues otherwise.
 *  
 */
function selectToString($aValue, $aSelectValues)
{
  if (!in_array($aValue, $aSelectValues)) {
    $aValue = $aSelectValues[0];
  }
  return $aValue;
}

/**
< * @fn selectToCronItem($aValue, $aSelectValues)
 * @brief convert a string from a select form into a cron item
 * @param aValue string value to convert
 * @param aSelectValues possible values of the select form (minus the first
          item, which is always "*")
 * @return a string representing the index of aValue in the select form, if it
           is found in aSelectValues, or "*" otherwise.
 */
function selectToCronItem($aValue, $aSelectValues)
{
  for ($i = 0; $i < count($aSelectValues); $i++) {
    if ($aSelectValues[$i] == $aValue) {
      return strval(1 + $i);
    }
  }
  return "*";
}

/**
 *  @fn truncateString($aValue, $aMaxLength)
 *  @brief truncate a string
 *  @param aValue the string to truncate
 *  @param aMaxLength maximum length of the result
 *  @return the longest prefix of the string with at most aMaxLength
 *          characters
 */
function truncateString($aValue, $aMaxLength)
{
  return substr($aValue, 0, $aMaxLength);
}

/**
 *  @fn createTask($aTaskName,
 *                 $aConfigFile,
 *                 $aOutputDirectory,
 *                 $aTaskSchedule,
 *                 $aUseGrid,
 *                 $aHost,
 *                 $aPort,
 *                 $aMathJaxPath,
 *                 $aMathJaxTestPath,
 *                 $aTimeOut,
 *                 $aUseWebDriver,
 *                 $aFullScreenMode,
 *                 $aAloneOnHost,
 *                 $aFormatOutput,
 *                 $aCompressOutput,
 *                 $aOperatingSystem,
 *                 $aBrowser,
 *                 $aBrowserVersion,
 *                 $aBrowserMode,
 *                 $aBrowserPath,
 *                 $aFont,
 *                 $aOutputJax,
 *                 $aRunSlowTests,
 *                 $aRunSkipTests,
 *                 $aListOfTests,
 *                 $aStartID)
 *
 *  @brief Send a request to the task handler to create a task and print the
 *         result.
 */
function createTask($aTaskName,
                    $aConfigFile,
                    $aOutputDirectory,
                    $aTaskSchedule,
                    $aUseGrid,
                    $aHost,
                    $aPort,
                    $aMathJaxPath,
                    $aMathJaxTestPath,
                    $aTimeOut,
                    $aUseWebDriver,
                    $aFullScreenMode,
                    $aAloneOnHost,
                    $aFormatOutput,
                    $aCompressOutput,
                    $aOperatingSystem,
                    $aBrowser,
                    $aBrowserVersion,
                    $aBrowserMode,
                    $aBrowserPath,
                    $aFont,
                    $aOutputJax,
                    $aRunSlowTests,
                    $aRunSkipTests,
                    $aListOfTests,
                    $aStartID)
{
  global $TASK_HANDLER_HOST, $TASK_HANDLER_PORT, $ERROR_CONNECTION_TASK_HANDLER;  
  $file = fsockopen($TASK_HANDLER_HOST, $TASK_HANDLER_PORT);
  if ($file) {
    fwrite($file, "TASKEDITOR EDIT ".$aTaskName." ".$aConfigFile." ".
                  $aOutputDirectory." ".$aTaskSchedule."\n".
                  "useGrid=".$aUseGrid."\n".
                  "host=".$aHost."\n".
                  "port=".strval($aPort)."\n".
                  "mathJaxPath=".$aMathJaxPath."\n".
                  "mathJaxTestPath=".$aMathJaxTestPath."\n".
                  "timeOut=".strval($aTimeOut)."\n".
                  "useWebDriver=".$aUseWebDriver."\n".
                  "fullScreenMode=".$aFullScreenMode."\n".
                  "aloneOnHost=".$aAloneOnHost."\n".
                  "formatOutput=".$aFormatOutput."\n".
                  "compressOutput=".$aCompressOutput."\n".
                  "operatingSystem=".$aOperatingSystem."\n".
                  "browser=".$aBrowser."\n".
                  "browserVersion=".$aBrowserVersion."\n".
                  "browserMode=".$aBrowserMode."\n".
                  "browserPath=".$aBrowserPath."\n".
                  "font=".$aFont."\n".
                  "outputJax=".$aOutputJax."\n".
                  "runSlowTests=".$aRunSlowTests."\n".
                  "runSkipTests=".$aRunSkipTests."\n".
                  "listOfTests=".$aListOfTests."\n".
                  "startID=".$aStartID."\n".
                  "TASKEDITOR EDIT END\n");
    echo '<p>'.trim(fgets($file)).'</p>';
    fclose($file);
  } else {
    echo '<p>'.$ERROR_CONNECTION_TASK_HANDLER.'</p>';
  }
}

/**
 *  @fn executeCommand($aCommand, $aTaskName)
 *  @brief execute a simple command
 */
function executeCommand($aCommand, $aTaskName)
{
  global $TASK_HANDLER_HOST, $TASK_HANDLER_PORT, $ERROR_CONNECTION_TASK_HANDLER;  
  $file = fsockopen($TASK_HANDLER_HOST, $TASK_HANDLER_PORT);
  if ($file) {
    fwrite($file, "TASKEDITOR ".$aCommand." ".$aTaskName."\n");
    echo '<p>'.trim(fgets($file)).'</p>';
    fclose($file);
  } else {
    echo '<p>'.$ERROR_CONNECTION_TASK_HANDLER.'</p>';
  }
}

/**
 *  @fn executeCommandWithParameter($aCommand, $aTaskName, $aParameter)
 *  @brief execute a simple command with parameter
 */
function executeCommandWithParameter($aCommand, $aTaskName, $aParameter)
{
  global $TASK_HANDLER_HOST, $TASK_HANDLER_PORT, $ERROR_CONNECTION_TASK_HANDLER;  
  $file = fsockopen($TASK_HANDLER_HOST, $TASK_HANDLER_PORT);
  if ($file) {
    fwrite($file, "TASKEDITOR ".$aCommand." ".$aTaskName." ".$aParameter."\n");
    echo '<p>'.trim(fgets($file)).'</p>';
    fclose($file);
  } else {
    echo '<p>'.$ERROR_CONNECTION_TASK_HANDLER.'</p>';
  }
}
?>

<!-- -*- Mode: HTML; tab-width: 2; indent-tabs-mode:nil; -*- -->
<!-- vim: set ts=2 et sw=2 tw=80: !-->
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <title>Task Editor</title>
    <!-- Copyright (c) 2011 Design Science, Inc.
         License: Apache License 2.0 -->
    <link rel="stylesheet" type="text/css" href="default.css"/>
    <meta http-equiv="refresh" content="1; url=./taskViewer.php">
  </head>

  <body>
    <div class="related">
      <h3>Navigation</h3>
      <ul>
        <li><a href="./">Back to home</a></li> 
      </ul>
    </div>  

    <div class="body">
      <h1>Task Editor</h1>

     <?php
        if (isset($_POST['taskName'])) {
          $taskName = truncateString($_POST['taskName'], 50);
        }

        if ($_POST['command'] == 'EDIT') {

          $useGrid = boolToString(isset($_POST['useGrid']));

          if ($_POST['taskSingleMultiple'] == 'single' &&
            isset($_POST['host'])) {
            $host = truncateString($_POST['host'], 255);
          } else {
            $host = "default";
          }

          if (isset($_POST['port'])) {
            $port = intval($_POST['port']);
          } else {
            $port = $SELENIUM_SERVER_PORT;
          }

          if (isset($_POST['mathJaxPath'])) {
            $mathJaxPath = truncateString($_POST['mathJaxPath'], 255);
          } else {
            $mathJaxPath = $DEFAULT_MATHJAX_PATH;
          }

          if (isset($_POST['mathJaxTestPath'])) {
            $mathJaxTestPath = truncateString($_POST['mathJaxTestPath'], 255);
          } else {
            $mathJaxTestPath = $DEFAULT_MATHJAX_TEST_PATH;
          }
    
          $timeOut = intval($_POST['timeOut']);
          if ($timeOut < 0) {
            $timeOut = 0;
          } else if ($timeOut > 120) {
            $timeOut = 120;
          }
  
          $useWebDriver = boolToString(isset($_POST['useWebDriver']));
          if ($useWebDriver == 'true') {
            $aloneOnHost = boolToString(isset($_POST['aloneOnHost']));
            $fullScreenMode = boolToString(False);
          } else {
            $aloneOnHost = boolToString(True);
            $fullScreenMode = boolToString(isset($_POST['fullScreenMode']));
          }

          $formatOutput = boolToString(isset($_POST['formatOutput']));
          $compressOutput = boolToString(isset($_POST['compressOutput']));
  
          $operatingSystem = selectToString($_POST['operatingSystem'],
                                            $OS_LIST);
  
          $browser = selectToString($_POST['browser'], $BROWSER_LIST);

          if ($browser == "MSIE") {
            $browserMode = selectToString($_POST['browserMode'],
                                          $BROWSER_MODE_LIST);
          } else {
            $browserMode = "default";
          }

          if ($useWebDriver == 'true') {
            $browserVersion = truncateString($_POST['browserVersion'], 20);
            $browserPath = "default";
          } else {
            $browserVersion = "default";
            $browserPath = truncateString($_POST['browserPath'], 100);
          }
   
          $font = selectToString($_POST['font'], $FONT_LIST);
   
          $aOutputJax = selectToString($_POST['outputJax'], $OUTPUT_JAX_LIST);
          $runSlowTests = boolToString(isset($_POST['runSlowTests']));
          $runSkipTests = boolToString(isset($_POST['runSkipTests']));
          $listOfTests = $_POST['listOfTests'];
          $startID = $_POST['startID'];

          if (isset($_POST['outputDirectory']) &&
              $_POST['outputDirectory'] != "") {
            $outputDirectory = truncateString($_POST['outputDirectory'], 20);
          } else {
            $outputDirectory = "None";
          }
   
          if (isset($_POST['taskSchedule'])) {
            $taskSchedule = "";
            $v = $_POST['crontabM']; if ($v != "*") $v = intval($v);
            $taskSchedule .= $v.",";
            $v = $_POST['crontabH']; if ($v != "*") $v = intval($v);
            $taskSchedule .= $v.",";
            $taskSchedule .= truncateString($_POST['crontabDom'], 2).",";
            $taskSchedule .= selectToCronItem($_POST['crontabMon'],
                                              $MONTH_LIST).",";
            $taskSchedule .= selectToCronItem($_POST['crontabDow'],
                                              $WEEKDAY_LIST);
          } else {
            $taskSchedule = "None";
          }

          if ($_POST['taskSingleMultiple'] == 'single') {
              createTask($taskName,
                         "None",
                         $outputDirectory,
                         $taskSchedule,
                         $useGrid,
                         $host,
                         $port,
                         $mathJaxPath,
                         $mathJaxTestPath,
                         $timeOut,
                         $useWebDriver,
                         $fullScreenMode,
                         $aloneOnHost,
                         $formatOutput,
                         $compressOutput,
                         $operatingSystem,
                         $browser,
                         $browserVersion,
                         $browserMode,
                         $browserPath,
                         $font,
                         $aOutputJax,
                         $runSlowTests,
                         $runSkipTests,
                         $listOfTests,
                         $startID);
            } else {
              for ($i = 0; $i < count($TEMPLATE_CONFIG_LIST); $i++) {
                if (isset($_POST['taskTemplate'.strval($i)])) {
                  createTask($taskName.'-'.$TEMPLATE_CONFIG_LIST[$i],
                             "config/templates/".$TEMPLATE_CONFIG_LIST[$i].".cfg",
                             $outputDirectory,
                             $taskSchedule,
                             $useGrid,
                             $host,
                             $port,
                             $mathJaxPath,
                             $mathJaxTestPath,
                             $timeOut,
                             $useWebDriver,
                             $fullScreenMode,
                             $aloneOnHost,
                             $formatOutput,
                             $compressOutput,
                             $operatingSystem,
                             $browser,
                             $browserVersion,
                             $browserMode,
                             $browserPath,
                             $font,
                             $aOutputJax,
                             $runSlowTests,
                             $runSkipTests,
                             $listOfTests,
                             $startID);
                }
              }
            }
        } else if ($_POST['command'] == 'REMOVE' ||
                   $_POST['command'] == 'RUN' ||
                   $_POST['command'] == 'RESTART' ||
                   $_POST['command'] == 'STOP' ||
                   $_POST['command'] == 'FORMAT') {
          executeCommand($_POST['command'], $taskName);
        } else if ($_POST['command'] == "MULTIPLE_REMOVE" ||
                   $_POST['command'] == "MULTIPLE_RUN" ||
                   $_POST['command'] == "MULTIPLE_RESTART" ||
                   $_POST['command'] == "MULTIPLE_STOP") {
          $command = substr($_POST['command'], strlen("MULTIPLE_"));
          $taskList = explode(",", $_POST['taskList']);
          for ($i = 0; $i < count($taskList); $i++) {
            executeCommand($command, $taskList[$i]);
          }
        } else if ($_POST['command'] == 'CLONE' ||
                   $_POST['command'] == 'RENAME') {
          if (isset($_POST['newName'])) {
            executeCommandWithParameter($_POST['command'],
                                        $taskName, $_POST['newName']);
          }
        } else {
              echo '<p>Invalid request.</p>';
        }
        ?>

        <p>You will be redirected to the task viewer page.</p>
    </div>
  </body>
</html>
