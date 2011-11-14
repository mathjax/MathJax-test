.. _manual-testing:

**************
Manual Testing
**************

It is expected that the tests in the suite are run automatically. However, it
is sometimes convenient to do some manual testing for example to verify a test
failure or to write new tests. For that reason, the testing framework is
designed to allow manual testing of files in the test suite, with a minimal
setup.

.. _public-test-suite:

Public Test Suite
=================

A public server with the :ref:`MathJax testsuite <test-suite>` is available.
This testsuite uses the development version of
`MathJax <https://github.com/mathjax/MathJax>`_ and
`MathJax-test <https://github.com/mathjax/MathJax-test>`_. You can browse
the file hierarchy made with test pages and manifest files and directly
:ref:`open the test pages <loading-unit-test>`. This allows one to test MathJax
on his own environment without having to do any setup. However if you want to
do more advanced testing, for example to
:ref:`write your own unit tests <writing-test>`, you should consider
doing a :ref:`local installation <local-test-suite>`.

.. _local-test-suite:

Local Test Suite Installation
=============================

It is assumed that you already have the browsers, fonts and plugins you want to
test with on your operating system. Also, you should have access to a MathJax
installation, for example a local copy or the CDN.

Next, you should download the Web pages used for the unit test you want to test.
Recall that it is either a single page or a pair test/reference. These Web pages
may also point to external resources so be sure to download these files too. In
particular, the following Javascript files are important:

.. _mathjax-test-headers:

- `header.js </MathJax-test/testsuite/header.js>`_: this script is supposed to be used in
  all the unit tests. Among other things, it loads MathJax, executes pre and
  post actions and communicates with the test launcher.

- `treeReftests.js </MathJax-test/testsuite/treeReftests.js>`_: this script is needed for
  tree reftests to serialize DOM trees.

- `scriptTests.js </MathJax-test/testsuite/scriptTests.js>`_: this script is needed for
  script tests to determine whether all the Javascript tests passed.

The best thing to do is to create a ``testsuite/`` directory where you put
the scripts above as well as the Web pages and resources of the test suite,
respecting its file hierarchy. One way to do that is to download the
`MathJax-test GitHub repository <https://github.com/mathjax/MathJax-test/>`_.
If you plan to run automated tests on your machine, you can do a
:ref:`complete installation of MathJax-test <installation>`. Otherwise,
you simply have to do this:

- keep only the ``testsuite/`` directory
- In ``header-tpl.js``, set ``gMathJaxPath`` to the location of a MathJax
  installation.
- rename this template file ``header.js``

.. _loading-unit-test:

Loading a Unit Test
===================

To load a unit test, you just have to open the test pages in the browser you
want to test. It is also possible to provide some
:ref:`configuration options <test-runner-config>` in the query string of the
URI:

- **mathJaxPath**. By default, the test page use the MathJax installation
  specified in the ``gMathJaxPath`` variable of ``header.js``. This query
  parameter allows to specify your own MathJax installation.

- **font**. One of the value ``STIX``, ``TeX``, ``ImageTeX`` indicating the
  font used by MathJax to render the mathematics. Default is ``STIX``.

- **outputJax**. One of the value ``HTML-CSS``, ``SVG``, ``NativeMML``
  indicating which output jax should be used to render mathematics. Note that
  tree reftests force the use of MathML output, so this parameter is
  ignored in that case. In the other cases, the default value is ``HTML-CSS``.

- **errorHandler**. A boolean that indicates whether javascript errors should
  be caught by an handler. Default is ``false``. This parameter is used during
  the execution of tests and can be ignored when doing manual testing.

Some examples:

- ``mytest.html?mathJaxPath=http://cdn.mathjax.org/mathjax/latest/``, to
  test with the latest CDN version of MathJax.

- ``mytest.html?mathJaxPath=/path-to-mathjax/MathJax/unpacked/`` to use the
  unpacked version of MathJax, which is useful for debugging.

- ``mytest.html?outputJax=NativeMML`` to test the MathML support of your browser
  instead of MathJax's one.

- ``mytest.html?mathJaxPath=/mypath/&font=TeX`` for using a custom MathJax
  installation and TeX fonts.

.. _determining-success-manually:

Determining Success
===================

Once you have opened the test pages in your browser, you can determine the
success in the following ways:

- For visual reftests, one only has to compare the visual rendering of the
  reference and test pages. One way to do that is to have two tabs with the
  reference and test pages and to switch between the two. Be aware that
  some differences may be hard to detect with the naked eye.

- For tree reftests, a textarea containing the result of the serialization is
  available. One has to compare these sources. You can copy and paste the
  content of the textareas in two text files and use a
  `diff tool <http://en.wikipedia.org/wiki/Diff>`_.

- For load tests, you only have to see if the Web page is loaded without
  problem. Check the Javascript console to be sure that no errors happen.

- For script reftests, a textarea containing the list of Javascript tests and
  their results is available. The final result can be found at the end of the
  textarea and is also repeated in the page title.
