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
 *  @brief TODO
 */

echo '<?xml version="1.0" encoding="UTF-8"?>';
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

        $file = fsockopen("localhost", 4445);
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
              $argument = explode(" ", $line, 5);
              if (count($argument) == 5) {
                $taskName = $argument[0];
                $host = $argument[1];
                $status = $argument[2];
                $progress = $argument[3];
                $results = $argument[4];
  
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
  
              if ($status == "Running") {
                  commandButton($taskName, "STOP");
                } else if($status == "Interrupted") {
                  commandButton($taskName, "RUN");
                  commandButton($taskName, "RESTART");
                  commandButton($taskName, "REMOVE");
                } else if ($status == "Complete" || $status == "Killed") {
                  commandButton($taskName, "RESTART");
                  commandButton($taskName, "REMOVE");
                } else if ($status == "Pending") {
                  commandButton($taskName, "RUN");
                  commandButton($taskName, "REMOVE");
                }
                echo '</td>';
  
                echo '<td>'.$progress.'</td>';
                echo '<td>';
                if ($status == "Pending") {
                  echo $results;
                } else {
                  echo '<a href="results/'.$results.'">'.$results.'</a>';
                }
                echo '</td>';
                echo '</tr>';
              }
            }
            echo '</table>';
            fclose($file);
          }
        } else {
          echo '<p>Could not connect to the task handler.</p>';
        }
      ?>

      <p><a href="taskCreator.xhtml">Create a new task</a></p>

    </div>
  </body>
</html>
