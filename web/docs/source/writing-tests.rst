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
Mozilla is to use a Web page for both the test and reference page.

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
improvement.

.. _test-page-template:

Test Page Template
==================

Here is the minimal structure for a test page. Most test pages should use the
HTML5 syntax and the UTF-8 encoding, except when you want to test specific
configurations such as XHTML. Also, the first comments lines define editing mode
and text indentation for emacs and vim. It is recommended to use a line length
limit of 80 characters and Unix-style carriage returns.

A page title should be given to your test page. All tests must include the
script ``header.js`` and set a class "reftest-wait" to the root element.

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

The test pages of tree reftests must include a ``"reftest-element"`` ``div``,
containing a single ``<math>`` element (hardcoded or generated by MathJax). For
instance:

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

Finally, good practice for non-regression test is to add a comment with a
reference to the issue corresponding to the bug tested:

.. code-block:: html

  <!-- See issue __ISSUE-NUMBER__
       https://github.com/mathjax/MathJax/issues/__ISSUE-NUMBER__ -->

.. _useful-interfaces:

Useful Interfaces
=======================

You can write test depending on some parameters, provided in the query string.
This one is parsed at the beginning of the test and can be easily accessed by
the following function:

.. code-block:: javascript

   function getQueryString(aParamName)

Test pages first use the default MathJax configuration. It is merged with a
custom configuration object at startup, created according to the testing
instance configuration. You can access this config object and modify it before
MathJax starts, via the function

.. code-block:: javascript

   function getConfigObject()

Finally, you can add actions before/after MathJax starts by defining the
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
     config = getConfigObject()
     config["HTML-CSS"].minScaleAdjust = getQueryString("minScaleAdjust");
     config.NativeMML = {scale: 200};
   }

   function postMathJax()
   {
     document.getElementById("id").style.background = getQueryString("color");
   }

