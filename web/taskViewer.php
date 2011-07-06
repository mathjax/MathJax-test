<?echo '<?xml version="1.0" encoding="UTF-8"?>'?>
<!-- -*- Mode: HTML; tab-width: 2; indent-tabs-mode:nil; -*- -->
<!-- vim: set ts=2 et sw=2 tw=80: !-->
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1 plus MathML 2.0 plus SVG 1.1//EN"
          "http://www.w3.org/2002/04/xhtml-math-svg/xhtml-math-svg.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <title>MathJax Automated Tests</title>
    <!-- Copyright (c) 2011 Design Science, Inc.
         License: Apache License 2.0 -->
    <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
    <link type="text/css" rel="stylesheet" href="taskViewer.css"/>
  </head>

  <body>
    <h1>MathJax Automated Tests</h1>

    <?
      $file = fsockopen("localhost", 5557);
      if ($file) {
        echo '<table id="taskList">';
        echo '<tr><th>Task Name</th><th>Machine</th><th>Status</th><th>Progress</th></tr>';
        fwrite($file, "TASKVIEWER\n");
        while(!feof($file)) {
          $line = fgets($file);
          $argument = explode(" ", $line, 4);
          if (count($argument) == 4) {
            echo "<tr>";
            for ($i = 0;  $i < 4; $i++) {
              echo "<td>".$argument[$i]."</td>";
            }
            echo "</tr>";
          }
        }
        echo '</table>';
        fclose($file);
      } else {
        echo "<p>Could not connect to the task handler.</p>";
      }
    ?>

  </body>
</html>
