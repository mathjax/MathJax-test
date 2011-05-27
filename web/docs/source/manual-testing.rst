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

XXXfred: this server is not available yet!

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

- `header.js </MathJax-test/header.js>`_: this script is supposed to be used in
  all the unit tests. Among other things, it loads MathJax, executes pre and
  post actions and communicates with the test launcher.

- `treeReftests.js </MathJax-test/treeReftests.js>`_: this script is needed for
  tree reftests to serialize the ``<math>`` element.

- `scriptTests.js </MathJax-test/scriptTests.js>`_: this script is needed for
  script tests to determine whether all the Javascript tests passed.

The best thing to do is to create a ``MathJax-test/`` directory where you put
the scripts above as well as the Web pages and resources of the test suite,
respecting its file hierarchy. One way to do that is to download the
`MathJax-test GitHub repository <https://github.com/mathjax/MathJax-test/>`_.

.. _loading-unit-test:

Loading a Unit Test
===================

To load a unit test, you just have to open the test pages in the browser you
want to test. It is also possible to provide the some configuration options in
the query string of the URI:

- **mathJaxPath**. By default, the test page looks for an ancestor directory
  called ``MathJax-test/``. Then it uses a ``MathJax/`` directory at the same
  level. This query parameter allows to specify your own MathJax installation.

- **font**. One of the value ``STIX``, ``TeX``, ``ImageTeX`` indicating the
  font used by MathJax to render the mathematics. Default is ``STIX``.

- **nativeMathML**. This indicates whether the browser's renderer should be used
  to display mathematics. This is either "false" or "true". It is not relevant
  for tree reftests since the MathML output is always used to serialize the
  math elements. In the other cases, the default value is "false".  

Some examples:

- ``mytest.html?mathJaxPath=http://cdn.mathjax.org/mathjax/latest/``, to
  test with the latest CDN version of MathJax.

- ``mytest.html?mathJaxPath=/path-to-mathjax/MathJax/unpacked/`` to use the
  unpacked version of MathJax, which is useful for debugging.

- ``mytest.html?nativeMathML=false`` to test the MathML support of your browser
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

- For tree reftests, a textarea containing the serialization of the ``<math>``
  element is available. One has to compare these sources. You can copy and paste
  the content of the textareas in two text files and use a
  `diff tool <http://en.wikipedia.org/wiki/Diff>`_.

- For load tests, you only have to see if the Web page is loaded without
  problem. Check the Javascript console to be sure that no errors happen.

- For script reftests, a textarea containing the list of Javascript tests and
  their results is available. The final result can be found at the end of the
  textarea and is also repeated in the page title.
