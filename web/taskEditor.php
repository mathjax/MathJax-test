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
 *  @brief Sends editing command to the task handler
 *  
 */

if (!isset($_POST['command']) || !isset($_POST['taskName'])) {
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
 * @fn selectToCronItem($aValue, $aSelectValues)
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
        $taskName = truncateString($_POST['taskName'], 50);

        if ($_POST['command'] == 'ADD') {

          if (isset($_POST['host'])) {
            $host = truncateString($_POST['host'], 255);
          } else {
            $host = "localhost";
          }

          if (isset($_POST['port'])) {
            $port = intval($_POST['port']);
          } else {
            $port = $DEFAULT_SELENIUM_PORT;
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
  
          $fullScreenMode = boolToString(isset($_POST['fullScreenMode']));
          $formatOutput = boolToString(isset($_POST['formatOutput']));
          $compressOutput = boolToString(isset($_POST['compressOutput']));
  
          $operatingSystem = selectToString($_POST['operatingSystem'],
                                            $OS_LIST);
  
          $browser = selectToString($_POST['browser'], $BROWSER_LIST);
  
          if ($browser == "MSIE") {
            $browserMode = selectToString($_POST['browser'],
                                          $BROWSER_MODE_LIST);
          } else {
            $browserMode = "StandardMode";
          }
  
          $browserPath = "auto"; // $_POST['auto']
   
          $font = selectToString($_POST['font'], $FONT_LIST);
   
          $nativeMathML = boolToString(isset($_POST['nativeMathML']));
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
            $taskSchedule .= truncateString($_POST['crontabM'], 2).",";
            $taskSchedule .= truncateString($_POST['crontabH'], 2).",";
            $taskSchedule .= truncateString($_POST['crontabDom'], 2).",";
            $taskSchedule .= selectToCronItem($_POST['crontabMon'],
                                              $MONTH_LIST).",";
            $taskSchedule .= selectToCronItem($_POST['crontabDow'],
                                              $WEEKDAY_LIST);
          } else {
            $taskSchedule = "None";
          }

          $file = fsockopen($TASK_HANDLER_HOST, $TASK_HANDLER_PORT);
          if ($file) {
             fwrite($file, "TASKEDITOR ADD ".$taskName." None ".
                           $outputDirectory." ".$taskSchedule."\n".
                           "host=".$host."\n".
                           "port=".strval($port)."\n".
                           "mathJaxPath=".$mathJaxPath."\n".
                           "mathJaxTestPath=".$mathJaxTestPath."\n".
                           "mathJaxTestPath=".$mathJaxTestPath."\n".
                           "timeOut=".strval($timeOut)."\n".
                           "fullScreenMode=".$fullScreenMode."\n".
                           "formatOutput=".$formatOutput."\n".
                           "compressOutput=".$compressOutput."\n".
                           "operatingSystem=".$operatingSystem."\n".
                           "browser=".$browser."\n".
                           "browserMode=".$browserMode."\n".
                           "browserPath=".$browserPath."\n".
                           "font=".$font."\n".
                           "nativeMathML=".$nativeMathML."\n".
                           "runSlowTests=".$runSlowTests."\n".
                           "runSkipTests=".$runSkipTests."\n".
                           "listOfTests=".$listOfTests."\n".
                           "startID=".$startID."\n".
                           "TASKEDITOR ADD END\n");
             echo trim(fgets($file));
             fclose($file);
          } else {
            echo '<p>'.$ERROR_CONNECTION_TASK_HANDLER.'</p>';
          }
        } else if ($_POST['command'] == 'REMOVE' ||
                   $_POST['command'] == 'RUN' ||
                   $_POST['command'] == 'RESTART' ||
                   $_POST['command'] == 'STOP') {
          $file = fsockopen($TASK_HANDLER_HOST, $TASK_HANDLER_PORT);
          if ($file) {
             fwrite($file, "TASKEDITOR ".$_POST['command']." ".$taskName."\n");
             echo trim(fgets($file));
             fclose($file);
          } else {
            echo '<p>'.$ERROR_CONNECTION_TASK_HANDLER.'</p>';
          }
        }
        ?>

        <p>You will be redirected to the task viewer page.</p>
    </div>
  </body>
</html>
