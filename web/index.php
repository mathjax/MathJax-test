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
 *  @file index.php
 *  @brief Home page of the testing framework
 */
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

      <h2>Test Suite</h2>

      <ul>
      <?php
         for ($i = 0; $i < count($TESTSUITE_TOPDIR_LIST); $i++) {
           echo "<li><a href=\"";
           echo $DEFAULT_MATHJAX_TEST_PATH.$TESTSUITE_TOPDIR_LIST[$i];
           echo "/\">";
           echo $TESTSUITE_TOPDIR_LIST[$i]."/</a></li>";
         } 
       ?>
      </ul>

      <h2>Tools</h2>
      <ul>
        <li><a href="taskViewer.php">Task viewer</a></li>
        <li><a href="taskEditor.php">Task editor</a></li>
        <li><a href="results/">Reftest results</a></li>
        <li><a href="testsuiteNotes.xhtml">Testsuite notes</a></li>
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
