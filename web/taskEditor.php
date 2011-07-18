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
 *  
 */

  if (!isset($_POST['command']) || !isset($_POST['taskName'])) {
    header('Location: taskViewer.php');
    exit;
  }
  echo '<?xml version="1.0" encoding="UTF-8"?>';
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
        function boolToString($aPostValue)
        {
          return $aPostValue ? 'true' : 'false';
        }

        function selectToString($aPostValue, $aSelectValues)
        {
          if (!in_array($aPostValue, $aSelectValues)) {
            $aPostValue = $aSelectValues[0];
          }
          return $aPostValue;
        }

        function truncateString($aString, $aMaxLength)
        {
          return substr($aString, 0, $aMaxLength);
        }

        $taskName = truncateString($_POST['taskName'], 50);

        if ($_POST['command'] == 'ADD') {

          if (isset($_POST['host'])) {
            $host = truncateString($_POST['host'], 255);
          } else {
            $host = "localhost";
          }

          $port = 4444; // $_POST['host']
          $mathJaxPath = 'http://localhost/MathJax/';
          $mathJaxTestPath = 'http://localhost/MathJax-test/';
  
  
          $timeOut = intval($_POST['timeOut']);
          if ($timeOut < 0) {
            $timeOut = 0;
          } else if ($timeOut > 120) {
            $timeOut = 120;
          }
          $timeOut *= 1000;
  
          $fullScreenMode = boolToString(isset($_POST['fullScreenMode']));
          $formatOutput = boolToString(isset($_POST['formatOutput']));
          $compressOutput = boolToString(isset($_POST['compressOutput']));
  
          $operatingSystem = selectToString($_POST['operatingSystem'],
                                            array('auto',
                                                  'Linux',
                                                  'Windows',
                                                  'Mac'));
  
          $browser = selectToString($_POST['browser'],
                                    array('Firefox',
                                          'Safari',
                                          'Chrome',
                                          'Opera',
                                          'MSIE',
                                          'Konqueror'));
  
          if ($browser == "MSIE") {
            $browserMode = selectToString($_POST['browser'],
                                          array('StandardMode',
                                            'Quirks',
                                            'IE7',
                                            'IE8',
                                            'IE9'));
          } else {
            $browserMode = "StandardMode";
          }
  
          $browserPath = "auto"; // $_POST['auto']
   
          $font = selectToString($_POST['font'],
                                 array('STIX',
                                       'TeX',
                                       'ImageTeX'));
   
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
   
          $file = fsockopen("localhost", 4445);
          if ($file) {
             fwrite($file, "TASKEDITOR ADD ".$taskName." None ".$outputDirectory."\n".
                           "host=".$host."\n".
                           "port=".$port."\n".
                           "mathJaxPath=".$mathJaxPath."\n".
                           "mathJaxTestPath=".$mathJaxTestPath."\n".
                           "mathJaxTestPath=".$mathJaxTestPath."\n".
                           "timeOut=".$timeOut."\n".
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
            echo '<p>Could not connect to the task handler.</p>';
          }
        } else if ($_POST['command'] == 'REMOVE' ||
                   $_POST['command'] == 'RUN' ||
                   $_POST['command'] == 'RESTART' ||
                   $_POST['command'] == 'STOP') {
          $file = fsockopen("localhost", 4445);
          if ($file) {
             fwrite($file, "TASKEDITOR ".$_POST['command']." ".$taskName."\n");
             echo trim(fgets($file));
             fclose($file);
          } else {
            echo '<p>Could not connect to the task handler.</p>';
          }
        } else {
          echo '<p>Unknown command "'.$_POST['command'].'"</p>';
        }
        ?>

        <p>You will be redirected to the task viewer page.</p>
    </div>
  </body>
</html>
