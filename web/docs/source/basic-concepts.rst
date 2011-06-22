.. _basic-concepts:

**************
Basic Concepts
**************

This page describes the essential concepts you should get familiar with before
doing some testing of MathJax.

.. _issue-tracker:

Issue Tracker
=============

The `GitHub issue tracker <https://github.com/mathjax/MathJax/issues>`_ is the
place where a list of issues for MathJax are managed. In parallel with the
development workflow management, some Quality Assurance actions are performed.
These actions are described in this section.

When an issue is reported, it is important to know how to reproduce the bug.
Scenarios, code snippets or Web pages demonstrating the issue are very useful
for that purpose. We call this a **testcase**.

However, the testcase may be quite complicated at the beginning. Hence it is
more helpful to reduce it to a minimal Web page exhibiting the issue. Such a
page is called a **reduced testcase**.

To verify that the issue is fixed and detect it if it appears again, we want
to integrate the testcase in the :ref:`test-suite`. Some additional work is
necessary to convert the testcase into the :ref:`unit-test` format used in our
automated testing framework.

In order to manage the QA workflow, three tags are available in the tracker:

1) **QA - Testcase Wanted**: a reduced testcase for the issue is expected.
2) **QA - UnitTest Wanted**: a reduced testcase is available but we want to
   convert it into an automated test.
3) **QA - In Testsuite**: an automated test is written and integrated in the
   testsuite.

Ideally, all issues should reach the third status. However, it may not always be
possible to write a unit test.

.. _unit-test:

Unit Test
=========

A **unit test** verifies a particular feature of MathJax. The testing framework
have four kinds of unit test, each one determining the success in a different
way:

- **visual reftest**: two pages are loaded and their visual outputs compared.

- **tree reftest**: two pages are loaded, DOM subtrees are serialized and the
  corresponding output strings compared.

- **load test**: the unit test is made of a single Web page. The test is passed
  if no crashes, hangs etc happen. Such a test is also often called
  **crashtest**.

- **script test**: the unit test is made of a single Web page, in which a
  sequence of Javascript tests is executed. The unit test is passed if each
  individual Javascript test is successful.

The name reftest comes from the fact that we perform a comparison between a
**test page** and a **reference page**. By abuse of language, all the unit tests
are commonly called reftests in the MathJax testing framework, even when no
comparisons are involved.

It may not necessarily be obvious why we use two Web pages for Visual/tree
reftests instead of, for example, a Web page for the test and a screenshot for
the reference. The rationale for this choice
:ref:`is explained later <type-unit-tests>` in the writing tests section.
These kinds of test also have two subcategories: **equal equal reftest** (==)
and **not equal reftest** (!=) reftests. The difference between the two lies
in the way the success is determined: for the former the test and reference
should be equal whereas they should be different for the latter.

When a bug is found and a unit test is written to verify it, the unit test is
also called a **non-regression test**.

.. _test-suite:

Test Suite
==========

The **test suite** is a set of unit tests organized in a file hierarchy. The
topmost directories are the following:

- `API/ </MathJax-test/API/>`_: Tests for MathJax's Application Programming
  Interface.
- `Configuration/ </MathJax-test/Configuration/>`_: Tests for MathJax's
  configuration options.
- `Crashtests/ </MathJax-test/Crashtests/>`_: Tests for browser or Mathjax's
  crashes and hangs.
- `LaTeXToMathML/ </MathJax-test/LaTeXToMathML/>`_: Tests for the conversion
  from LaTeX to MathML.
- `MathMLToDisplay/ </MathJax-test/MathMLToDisplay/>`_: Tests for the rendering
  of MathML.
- `Parsing/ </MathJax-test/Parsing/>`_: Tests for the source code parsing.
- `UI/ </MathJax-test/UI/>`_: Tests for MathJax's User Interface.

A **reftest manifest** is available at the topmost level, as well as inside
each subdirectories containing unit tests. Such a manifest describes the test
suite structure, the type of :ref:`unit-test`, what are the test and reference
pages as well as information on the unit test's success or failure.

Below is an example of a ``reftest.list`` manifest. It provides reference to
manifest files in two subdirectories ``dir1/`` and ``dir2/dir3/``. It enumerates
three unit tests: a != visual reftest, a load test and an == tree reftest. It
also indicates that the second should be skipped with Internet Explorer and
that the third fails on Linux.

.. code-block:: none

   include dir1/reftest.list
   include dir2/dir3/reftest.list

   != page.html page-ref.html
   skip-if(MSIE) load crashtest.html
   fails-if(Linux) tree== tree.html tree-ref.html

For a detailed description of the manifest syntax, see :ref:`reftest-manifest`

.. _testing-instance:

Testing Instance
================

Even if it is possible to
:ref:`determine the test success manually<determining-success-manually>`,
the test suite is supposed to run in an automated way. A **testing instance**
is such an execution of the testsuite. Such a testing instance is controlled by
a machine called the **test launcher** and the test pages are loaded on a
**test machine**. These machines may be the same.

A testing instance corresponds to a given configuration: an operating system, a
browser, a MathJax installation, a subset of tests to run, etc See
:ref:`launcher-config` for a list of options avalaible. At the end, the testing
instance generates output in text and HTML formats, which are the
:ref:`test-results`.

A testing instance may be interrupted at any time by sending a SIGINT signal to
the program on the test launcher. In that case, the testing instance tries to
stop the browser and to keep the partial results.

.. _test-results:

Test Results
============

The **test results** are text or HTML files, possibly compressed with the gzip
tool. They are located in the `results/ </MathJax-test/results/>`_ directory.
The name of the output files is determined according to the configuration
options of the Test Launcher. For example ``Linux_Chrome_StandardMode_STIX``
means a testing instance run on Chrome for Linux, using the STIX fonts.

A testing instance output contains various information, such as the start/end
time, the time spent and the configuration options. The remainder is a status
for each test, based on the actual test success and the one expected from the
status given in the reftest manifest:

- **PASS**: the test passed.
- **UNEXPECTED-FAIL**: the test failed.
- **UNEXPECTED-PASS**: the test passed but was announced to fail in the
  manifest.
- **KNOWN-FAIL**: the test failed as announced in the manifest.
- **PASS(EXPECTED-RANDOM**): the test passed but a random result was announced.
- **KNOWN-FAIL(EXPECTED-RANDOM)**: the test failed but a random result was
  announced.

UNEXPECTED-FAIL and UNEXPECTED-PASS are worth considering, as they may indicate
bugs or fixes.

In addition, the formatted HTML output provides the number of tests run. The
proportion of tests in each of the above categories are represented by a
diagram. It is also possible to quickly browse the errors (UNEXPECTED-FAIL or
UNEXPECTED-PASS) with the Previous and Next error buttons.

Each test result in the formatted output is marked with a specific color
according to which category it belongs. A link to the test page is provided.
For failing tree/visual reftests, a link to the content (source or screenshot)
is also given as well as a link to a diff. Visual reftest's diff are analysed
using `Mozilla's reftest analyser <MathJax-test/reftest-analyzer.xhtml>`_.
Detailed results are also provided for script reftest.
