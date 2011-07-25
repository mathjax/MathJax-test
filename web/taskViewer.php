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
 *  @file taskViewer.php
 *  @brief Gives a preview of all the tasks in the task lists.
 *
 *  This PHP script tries to connect to a task handler. It displays an error
 *  message if it fails. Otherwise, it gets the answer of the server:
 *  - If it is "TASK LIST EMPTY" it displays a message providing that information.
 *  - If it is "TASK LIST NONEMPTY", it displays a HTML table. It reads the
 *    socket line by line until the end and convert each line into a row giving
 *    information on a task. The table contains also various useful links to
 *    task information, test outputs and command of @ref taskEditor.php.
 */

  echo '<?xml version="1.0" encoding="UTF-8"?>';
  include('config.php');

  /**
   *  @brief print HTML code to generate a command button.
   *  @param aTaskName name of the task to control
   *  @param aCommand name of the command to execute
   */
  function commandButton($aTaskName, $aCommand)
  {
  $c = strtolower($aCommand);

  echo '<form action="taskEditor.php" method="post">';
  echo '<input name="command" type="text" readonly="readonly"';
  echo       ' value="'.$aCommand.'" class="hiddenField"/>';
  echo '<input name="taskName" type="text" readonly="readonly"';
  echo       ' value="'.$aTaskName.'" class="hiddenField"/>';
  echo '<input type="submit" value="" class="submitField"';
  echo       ' style="background-image: url(icons/'.$c.'.png)" ';
  echo       ' title="'.$c.' task" />';
  echo '</form>';
  }
?>

<!-- -*- Mode: HTML; tab-width: 2; indent-tabs-mode:nil; -*- -->
<!-- vim: set ts=2 et sw=2 tw=80: !-->
<!DOCTYPE html>
<html>
  <head>
    <title>Task Viewer</title>
    <!-- Copyright (c) 2011 Design Science, Inc.
         License: Apache License 2.0 -->
    <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
    <link rel="stylesheet" type="text/css" href="default.css"/>
    <link type="text/css" rel="stylesheet" href="taskViewer.css"/>
  </head>

  <body>
    <div class="related">
      <h3>Navigation</h3>
      <ul>
      <ul>
        <li><a href="./">Back to home</a></li> 
      </ul>
      </ul>
    </div>  

    <div class="body">
      <h1>Task Viewer
        <a href="javascript:location.reload();">
          <img src="icons/reload.png" width="24" height="24" alt="reload page"/>
        </a>
      </h1>

      <?php
        $file = fsockopen($TASK_HANDLER_HOST, $TASK_HANDLER_PORT);
        if ($file) {
          fwrite($file, "TASKVIEWER\n");
          $line = trim(fgets($file));
          if ($line == "TASK LIST EMPTY") {
            echo "<p>The task list is empty.</p>";
          } else {
            echo '<table id="taskList">';
            echo '<tr>';
            echo '<th>Task Name</th>';
            echo '<th>Host</th>';
            echo '<th>Status</th>';
            echo '<th>Progress</th>';
            echo '<th>Result directory</th>';
            echo '</tr>';
            while(!feof($file)) {
              $line = trim(fgets($file));
              $argument = explode(" ", $line, 6);
              if (count($argument) == 6) {
                $taskName = $argument[0];
                $host = $argument[1];
                $status = $argument[2];
                $progress = $argument[3];
                $results = $argument[4];
                $schedule = $argument[5];

                echo '<tr>';
                echo '<td><a href="taskInfo.php?taskName='.$taskName.'">';
                echo $taskName.'</a></td>';
                echo '<td>'.$host.'</td>';
                echo '<td>';
                if ($status == "Killed") {
                  echo '<a href="taskInfo.php?taskName='.$taskName;
                  echo '#exceptionError">'.$status.'</a>';
		            } else {
                  echo $status;
		            }

                $isScheduled = ($schedule != "None");
                if ($isScheduled) {
                  echo " (scheduled)";
                }

                if ($status == "Running" || $status == "Pending") {
                  commandButton($taskName, "STOP");
                } else if($status == "Interrupted") {
                  if (!$isScheduled) {
                    commandButton($taskName, "RUN");
                    commandButton($taskName, "RESTART");
                  }
                  commandButton($taskName, "REMOVE");
                } else if ($status == "Complete" || $status == "Killed") {
                  if (!$isScheduled) {
                    commandButton($taskName, "RESTART");
                  }
                  commandButton($taskName, "REMOVE");
                } else if ($status == "Inactive") {
                  if (!$isScheduled) {
                    commandButton($taskName, "RUN");
                  }
                  commandButton($taskName, "REMOVE");
                }

                echo '</td>';
  
                echo '<td>'.$progress.'</td>';
                echo '<td>';
                if (file_exists("results/".$results)) {
                  echo '<a href="results/'.$results.'">'.$results.'</a>';
                } else {
                  echo $results;
                }
                echo '</td>';
                echo '</tr>';
              }
            }
            echo '</table>';
            fclose($file);
          }
        } else {
            echo '<p>'.$ERROR_CONNECTION_TASK_HANDLER.'</p>';
        }
      ?>

      <p><a href="taskCreator.php">Create a new task</a></p>

    </div>
  </body>
</html>
