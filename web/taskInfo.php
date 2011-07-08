<?php
  if (!isset($_GET['taskName'])) {
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
    <title>Task Info</title>
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
      <h1>Task Info</h1>

      <?php
             
          $file = fsockopen("localhost", 4445);
          if ($file) {
             fwrite($file, "TASKINFO ".$_GET['taskName']."\n");
             echo fgets($file);
             fclose($file);
          } else {
            echo '<p>Could not connect to the task handler.</p>';
          }

      ?>
    </div>
  </body>
</html>
