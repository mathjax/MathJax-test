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
        <li><a href="./taskEditor.xhtml">Task Editor</a></li> 
      </ul>
      </ul>
    </div>  

    <div class="body">
      <h1>Task Viewer</h1>

      <?php
        $file = fsockopen("localhost", 4445);
        if ($file) {
          echo '<table id="taskList">';
          echo '<tr>';
          echo '<th>Task Name</th>';
          echo '<th>Machine</th>';
          echo '<th>Status</th>';
          echo '<th>Progress</th>';
          echo '<th>Config</th>';
          echo '<th>Results</th>';
          echo '</tr>';
          fwrite($file, "TASKVIEWER\n");
          while(!feof($file)) {
            $line = fgets($file);
            $argument = explode(" ", $line, 5);
            if (count($argument) == 5) {
              echo '<tr>';
              echo '<td>'.$argument[0].'</td>';
              echo '<td>'.$argument[1].'</td>';
              echo '<td>'.$argument[2];
              echo '<form action="taskEditor.php" method="post">';
              echo '<input name="command" type="text" readonly="readonly"';
              echo       ' value="REMOVE" class="hiddenField"/>';
              echo '<input name="taskName" type="text" readonly="readonly"';
              echo       ' value="'.$argument[0].'" class="hiddenField"/>';
              echo '<input type="submit" value="" class="submitField"/>';
              echo '</form>';
              echo '</td>';
              echo '<td>'.$argument[3].'</td>';
              echo '<td><a href="../testRunner/config/'.$argument[0].'.cfg">';
              echo $argument[0].'.cfg</a></td>';
              echo '<td><a href="results/'.$argument[4].'">'.$argument[4].'</td>';
              echo '</tr>';
            }
          }
          echo '</table>';
          fclose($file);
        } else {
          echo '<p>Could not connect to the task handler.</p>';
        }
      ?>

    </div>
  </body>
</html>
