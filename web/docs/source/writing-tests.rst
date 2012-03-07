.. _writing-test:

##################
Writing Unit Tests
##################

This page describes how to write :ref:`unit-test` for the MathJax testsuite.
It is assumed that you have done the setup on your local machine as described
in :ref:`local-test-suite`.

.. _type-unit-tests:

Type of Unit Tests
==================

Before writing a test, you have to think about which kind of :ref:`unit-test`
is more appropriate for your purpose.

If you only want to test the stability of MathJax, a browser or a plugin, then
a load test is the simplest way to do that. You just have to write a Web page
that can cause a crash or a hang. Register it in a reftest manifest and do not
forget to  mark the test as ``skip`` or ``skip-if``, to prevent normal testing
instance to be interrupted because of a browser crash or hang.

If what you want to test can simply be exhibited by some Javascript code, then
a script test seems the best choice. You have to write one or more Javascript
functions executing some code to test features and returning true (PASS) or
false (FAIL). Then write a function ``getTestCases()`` which returns the list of
results as :ref:`described below <specificities>`.

To test the rendering engine, writing visual reftests is the way to go: you
compare your test page against a reference. One idea is to use an image as a
reference. However even in simple cases, the rendering of a page depends on too
many parameters such as operating system and browser, default text size,
type of fonts used, default zoom factor etc. A better approach borrowed from
Mozilla is to use a Web page for both the test and reference pages.

For example, suppose we want to check that ``<mstyle/>`` supports the
attributes of the ``<mfenced/>`` element. Then the test page

.. code-block:: html

   <mstyle open="[" close="]" separators=";">
      <mfenced>
         <mn>1</mn>
         <mn>2</mn>
      </mfenced>
   </mstyle>

should render the same as 

.. code-block:: html

   <mstyle>
      <mfenced open="[" close="]" separators=";">
         <mn>1</mn>
         <mn>2</mn>
      </mfenced>
   </mstyle>

The assumption here is that ``<mfenced/>`` already works correctly in order to
test ``<mstyle/>``. Similarly, one can think that HTML, CSS and maybe SVG are 
sufficiently stable and well supported browser features to use them for testing
the MathML rendering. In general, combining several == tests and != tests allows
to check carefully the implementation of any feature.

Another important feature of MathJax is its LaTeX to MathML converter. We could
use visual reftests to compare the rendering of the LaTeX source and of the
MathML expected to be generated. However, different sources may give the same
visual output (as we have just seen in the example above!) and thus the best is
to compare the XML trees directly. The concept of tree reftests has been
designed for that purpose. For example,

.. code-block:: latex

   \( \frac 1 2 \)

should generate the same XML tree as

.. code-block:: html

    <math>
      <mfrac>
        <mn>1</mn>
        <mn>2</mn>
      </mfrac>
    </math>

Note however that there is no canonical way to convert LaTeX to MathML. For
instance, attaching a ``linethickness="medium"`` to the ``mfrac`` in the
previous example is also acceptable. Thus, when we write a tree reftest, we
assume that we agree on the way a given LaTeX source is converted into MathML
by MathJax. The automated framework can then detect changes in the converter.
It is up to the developers to verify whether it is a regression or an
improvement. Note that tree reftests can also be used to compare more general
sets of DOM subtrees, not only a single ``<math>`` element. 

.. _test-page-template:

Test Page Template
==================

Here is the minimal structure for a test page. Most test pages should use the
HTML5 syntax and the UTF-8 encoding, except when you want to test specific
configurations such as XHTML. Also, the first comments lines define editing mode
and text indentation for emacs and vim. It is recommended to use a line length
limit of 80 characters and Unix-style carriage returns.

A page title should be given to your test page. All tests must include the
script ``header.js``, which ensures MathJax execution and communication with the
test launcher. The class "reftest-wait" should also be set on the root element.
In Mozilla framework, this attribute indicates reftest for which screenshot
capture should be delayed after some Javascript execution. In our testing
framework, we always wait after MathJax processing before reading the result.

.. code-block:: html

   <!-- -*- mode: HTML; tab-width: 2; indent-tabs-mode: nil; -*- -->
   <!-- vim: set tabstop=2 expandtab shiftwidth=2 textwidth=80:  -->
   <!DOCTYPE html>
   <html class="reftest-wait">
   <head>
     <title>__PAGE_TITLE__</title>
       <!-- Copyright (c) __YEAR__ Design Science, Inc.
            License: Apache License 2.0 -->
       <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
       <script type="text/javascript" src="__MATHJAX-TEST__/header.js"></script>
   </head>
   <body>
     <!-- Your test page -->
   </body>
   </html>

The file should also contain some free license and authoring information. If
the test is imported from another test suite, use the information of the source
and add a copy of the license to the `licenses/ </MathJax-test/licenses/>`_
directory if needed. Otherwise you may use the Copyright and License of the code
above. You can also add your author name if you want. Here are some models:

.. code-block:: html

   <!-- Copyright (c) 2011 Design Science, Inc.
        License: Apache License 2.0
        Author: John Doe <john.doe@des@dessci.com>
        Source: My MathML Test Suite -->

.. code-block:: html

    <!-- Copyright (C) 2008 Karl Tomlinson
         License: MPL 1.1 or later
         Source: Mozilla MathML reftests -->

.. code-block:: html

  <!--
       Copyright (c) World Wide Web Consortium
       License: W3C Document License
       Author: Robert Miner and Jeff Schaefer, Geometry Technologies
       Source: W3C MathML Test Suite
               http://www.w3.org/Math/testsuite/build/main/
                              Presentation/GeneralLayout/mphantom/mphantomB1.mml
    -->

.. _test-files:

Test Files
==========

When it is possible, the naming convention for files is lowercase,
dash-separated words, and .html extension. Also, it is recommended to end the
file name by a 1 in case other similar tests 2, 3 etc are added later.

For unit test with a test and reference, the general naming convention is to
append "-ref" to the reference page. When several test pages share the same
reference, you can also enumerate them with lowercase letters. Following this
convention helps people to deduce the reference from the test page, without
having to look in the reftest manifest.

Here are some examples:

.. code-block:: none

   load-page-1.html
   test-page-1.html  test-page-1-ref.html
   test-page-2a.html test-page-2-ref.html
   test-page-2b.html test-page-2-ref.html

Once you have written the test pages for your unit tests, you may want to
include it in the automated test suite. You should add them to the
:ref:`testsuite file hierarchy <test-suite>` by referencing them in a
reftest manifest. If you have created a new directory to store your test files,
a reftest manifest should be added to that directory. This manifest should
in turn be referenced by a parent manifest using the ``include`` directive. The
conventional name for reftest manifests is ``reftest.list``.

.. _specificities:

Specificities of Unit Tests
===================================

In general, visual and load unit tests do not need any specific additional
configuration. Script and tree unit tests must include the corresponding
Javascript files in the header:

.. code-block:: html

 <script type="text/javascript" src="__MATHJAX-TEST__/treeReftests.js"></script>
 <script type="text/javascript" src="__MATHJAX-TEST__/scriptTests.js"></script>

Good practice for non-regression test is to add a comment with a
reference to the issue corresponding to the bug tested:

.. code-block:: html

  <!-- See issue __ISSUE-NUMBER__
       https://github.com/mathjax/MathJax/issues/__ISSUE-NUMBER__ -->

A script reftest must implement a ``getTestCases()`` returning an array of
reftest results. Such a reftest result can be built with the
``newScriptReftestResult`` function. This function takes two parameters, a
description of the test performed and a boolean pass/fail result.

.. code-block:: javascript

    function getTestCases()
    {
      return [
        newScriptReftestResult("A first test", executeFirstTest()),
        newScriptReftestResult("A successful test", true),
        newScriptReftestResult("A failing test", false),
        newScriptReftestResult("Yet another test",
                               document.getElementById("id").innerHTML == "OK")
      ];
    }    

There are two ways to write a tree reftests. The simplest one is to include
a ``"reftest-element"`` ``div``, containing a single ``<math>`` element
(hardcoded or generated by MathJax). For instance, here is an example of two
pages that are expected to generate the same MathML source code:

.. code-block:: html

  <body>
    <div id="reftest-element">
      \( x \)
    </div>
  </body>

  <body>
    <div id="reftest-element">
      <math><mi>x</mi></math>
    </div>
  </body>

A more general way is to define a function ``getReftestElements()`` on the test
and reference pages, which takes no arguments and returns the list of elements
to serialize. As an example, the page

.. code-block:: html

    ...
    <head>
    <script type="text/javascript">
      function getReftestElements()
      {
        return ["id1", "id2", "id3"];
      }
    
      function postMathJax()
      {
      MathJax.HTML.addText(document.getElementById("id1"), "text1");
      MathJax.HTML.addText(document.getElementById("id2"), "text2");
      MathJax.HTML.addText(document.getElementById("id3"), "text3");
      }
    </script>
    </head>
    ...
    <body>
      <div id="id1"></div>
      <div id="id2"></div>
      <div id="id3"></div>
    </body>
    ...

indicates that we should serialize the ``<div>``'s of "id1", "id2" and "id3".
The results are concatenated in one string. It should provide the same result as
this reference page:

.. code-block:: html

    ...
    <head>
    <script type="text/javascript">
      function getReftestElements()
      {
        return ["id1", "id2", "id3"];
      }
    </script>
    </head>
    ...
    <body>
      <div id="id1">text1</div>
      <div id="id2">text2</div>
      <div id="id3">text3</div>
    </body>
    ...

.. _useful-interfaces:

Useful Interfaces
=======================

You can write test depending on some parameters, provided in the query string.
This one is parsed at the beginning of the test and can be easily accessed by
the following function:

.. code-block:: javascript

   function getQueryString(aParamName)

Similar functions exist to get integer and boolean parameters. For the former
you have to specify a default value when the parameter is not present whereas
for the latter, it defaults to false.

.. code-block:: javascript

   function getQueryInteger(aParamName, aDefaultValue)
   function getQueryBoolean(aParamName)

Test pages first use the default MathJax configuration. It is merged with a
custom configuration object ``gConfigObject`` at startup, created according to
the testing instance configuration. You can access this config object and modify
it before MathJax starts. Other global objects may help writing test, such as
``gMathJaxPath`` and ``gMathJaxQueryString`` which describes the URI of the
MathJax.js script.

You can also add actions before/after MathJax starts by defining the
following functions in your test page:

.. code-block:: javascript

   function preMathJax()
   function postMathJax()

For example, the following code modify the MathJax configuration in the
``preMathJax()`` function and change the background color of an object in the
``postMathJax()`` function. Some values are determined from parameters of the
query string.

.. code-block:: javascript

   function preMathJax()
   {
     gConfigObject["HTML-CSS"].minScaleAdjust = getQueryString("minScaleAdjust");
     gConfigObject.NativeMML = {scale: 200};
   }

   function postMathJax()
   {
     document.getElementById("id").style.background = getQueryString("color");
   }

Note that ``preMathJax()`` is executed before inserting the MathJax script to
the page, so you can not use the ``MathJax`` object in this function, which is
not created yet at this time. However, it is possible to declare another
function executed at an intermediate level of the MathJax startup sequence:

.. code-block:: javascript

   function xMathJaxConfig()

A call to this function will be inserted in a ``text/x-mathjax-config`` script,
after the call to ``MathJax.Hub.Config`` and before one to
``MathJax.Hub.Startup.onload``. For example, to register a signal hook:

.. code-block:: javascript

   function xMathJaxConfig()
   {
     MathJax.Hub.Register.StartupHook("End Styles", myCallback);
   }

For each test, finalize functions are pushed into ``MathJax.Hub.queue`` after
``postMathJax()`` is executed. These functions add serialization, script results
etc and alert the test launcher that the test is complete. In general you do not
need to call them, but it may sometimes be useful to know them for advanced
synchronisation tests:

.. code-block:: javascript

   function finalizeTreeReftests()   // finalizer for tree reftests
   function finalizeScriptReftests() // finalizer for script tests
   function finalizeReftests()       // default finalizer


.. _reftest-manifest:

The Reftest Manifest
======================================

A reftest manifest is a file describing the tests in a directory. A basic
example can be found in the :ref:`test-suite` section. This section gives
the syntax for reftest manifest, in a more formal way.

The test manifest format is a plain text file.  A line starting with a
"#" is a comment.  Lines may be commented using whitespace followed by
a "#" and the comment.  Each non-blank line (after removal of comments)
must be one of the following:

1. Inclusion of another manifest

    <failure-type>* include <relative_path>
 
    <failure-type> is the same as listed below for a test item.  As for 
    test items, multiple failure types listed on the same line are 
    combined by using the last matching failure type listed.  However, 
    the failure type on a manifest is combined with the failure type on 
    the test (or on a nested manifest) with the rule that the last in the
    following list wins:  fails, random, skip.  (In other words, skip 
    always wins, and random beats fails.)

2. A test item

   <failure-type>* <type> <url> <url_ref>

   where

   a. <failure-type> (optional) is one of the following:

      fails  The test passes if the test result DOES NOT
             meet the conditions specified in the <type>.

      fails-if(condition) If the condition is met, the test passes if the 
                          test result DOES NOT meet the 
                          conditions of <type>. If the condition is not met,
                          the test passes if the conditions of <type> are met.

      random  The results of the test are random and therefore not to be
              considered in the output.

      random-if(condition) The results of the test are random if a given
                           condition is met.

      skip  This test should not be run. This is useful when a test fails in a
            catastrophic way, such as crashing or hanging the browser. Using
            'skip' is preferred to simply commenting out the test because we
            want to report the test failure at the end of the test run.

      skip-if(condition) If the condition is met, the test is not run. This is
                         useful if, for example, the test crashes only on a
                         particular platform (i.e. it allows us to get test
                         coverage on the other platforms).

      slow  The test may take a long time to run, so run it if slow tests are
            either enabled or not disabled.

      slow-if(condition) If the condition is met, the test is treated as if
                         'slow' had been specified. 

      require(condition) The test is run only if the condition is met. This is
      useful for tests written for a particular configuration and irrelevant
      otherwise. Contrary to skip, the test is not considered as a failure and
      is even not taken into account for the statistical outputs.

      Conditions are boolean expressions with literals given by the
      configuration options ``operatingSystem, browser, browserVersion,
      browserMode, font, nativeMathML``. For example ``(STIX&&Windows||!Linux)``

   b. <type> is one of the following:

      - ==     (== reftest)
      - !=     (!= reftest)
      - ==tree (==tree reftest)
      - !=tree (!=tree reftest)
      - load   (load test)
      - script (script test)

   c. <url> is either a relative file path or an absolute URL for the
      test page

   d. <url_ref> is either a relative file path or an absolute URL for
      the reference page
