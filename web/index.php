<?php
  echo '<?xml version="1.0" encoding="UTF-8"?>';
  include('config.php');
?>

<!-- -*- Mode: HTML; tab-width: 2; indent-tabs-mode:nil; -*- -->
<!-- vim: set ts=2 et sw=2 tw=80: !-->
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <title>MathJax Test</title>
    <!-- Copyright (c) 2011 Design Science, Inc.
         License: Apache License 2.0 -->
    <link rel="stylesheet" type="text/css" href="default.css"/>
  </head>

  <body>
    <div class="body">
      <h1>MathJax Test</h1>

      <h2>Test Suite </h2>

      <ul>
      <?php
         $directories = array("API", "Configuration", "Crashtests",
                              "LaTeXToMathML", "MathMLToDisplay", "Parsing",
                              "UI");
         for ($i = 0; $i < count($directories); $i++) {
           echo "<li><a href=\"";
           echo $DEFAULT_MATHJAX_TEST_PATH.$directories[$i];
           echo "/\">";
           echo $directories[$i]."/</a></li>";
         } 
       ?>
      </ul>

      <h2>Tools</h2>
      <ul>
        <li><a href="taskViewer.php">Task viewer</a></li>
        <li><a href="taskCreator.php">Task creator</a></li>
        <li><a href="results/">Reftest results</a></li>
        <li><a href="selectReftests.xhtml">Reftest selector</a></li>
        <li><a href="reftest-analyzer.xhtml">Reftest analyser</a></li>
      </ul>

      <h2>Documentation</h2>
      <ul>
        <li><a href="docs/html/index.html">MathJax-test</a></li>
        <li><a href="docs/doxygen/index.html">Doxygen</a></li>
        <li><a href="https://sites.google.com/site/mathjaxproject/design-documents/testing">Working document</a></li>
      </ul>
    </div>
  </body>
</html>