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
 *  @file hostInfo.php
 *  @brief Displays information on a host.
 *  
 *  If no host parameter is present in the query string, this PHP script
 *  redirects to @ref taskViewer.php. Otherwise, it tries to connect to a task
 *  handler It displays an error message if it fails and the result of 
 *  a "HOSTINFO host" request if it succeeds.
 */

  if (!isset($_GET['host'])) {
    header('Location: taskViewer.php');
    exit;
  }
  echo '<?xml version="1.0" encoding="UTF-8"?>';
  include('config.php');

  function printTasks($aList)
  {
    $list = explode(" ", $aList);
    for ($i = 0; $i < count($list); $i++) {
      echo ' <a href="taskInfo.php?taskName='.$list[$i].'">';
      echo $list[$i].'</a> ';
    }
  }
?>

<!-- -*- Mode: HTML; tab-width: 2; indent-tabs-mode:nil; -*- -->
<!-- vim: set ts=2 et sw=2 tw=80: !-->
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <title>Host Info</title>
    <!-- Copyright (c) 2011 Design Science, Inc.
         License: Apache License 2.0 -->
    <link rel="stylesheet" type="text/css" href="default.css"/>
  </head>

  <body>
    <div class="related">
      <h3>Navigation</h3>
      <ul>
        <li><a href="./taskViewer.php">Back to Task Viewer</a></li> 
      </ul>
    </div>  

    <div class="body">
      <h1>Host Info</h1>

      <?php
          $file = fsockopen($TASK_HANDLER_HOST, $TASK_HANDLER_PORT);
          if ($file) {
             fwrite($file, "HOSTINFO ".$_GET['host']."\n");
 
             $l = trim(fgets($file));
             if ($l == "UNKNOWN_HOST") {
               echo '<p>Unknown host.</p>';
             } else {
               echo "<h2>Running Tasks</h2>";
               $l = trim(fgets($file)); // RUNNING_TASKS
               $l = trim(fgets($file));
               if ($l == "RUNNING_TASKS END") {
                 echo '<p>No running tasks</p>';
               } else {
                  echo '<p>';
                  printTasks($l);
                  echo '</p>';
                  $l = trim(fgets($file)); // RUNNING_TASKS END
               }
               echo "<h2>Pending Tasks</h2>";
               $l = trim(fgets($file)); // PENDING_TASKS
               $l = trim(fgets($file));
               if ($l == "PENDING_TASKS END") {
                 echo '<p>No pending tasks</p>';
               } else {
                 echo '<ol>';
                 while (!feof($file) && $l != "PENDING_TASKS END") {
                  echo '<li>';
                  printTasks($l);
                  echo '</li>';
                  $l = trim(fgets($file));
                 }
                 echo '</ol>';
               }
             }
             while (!feof($file)) {
               fgets($file);
             }
             fclose($file);
          } else {
            echo '<p>'.$ERROR_CONNECTION_TASK_HANDLER.'</p>';
          }
      ?>
    </div>
  </body>
</html>
