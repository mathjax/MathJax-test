##########################
MathJax-test Documentation
##########################

.. toctree::
   :maxdepth: 2

The Test Suite File Hierarchy
======================================

The root of the test suite is ``MathJax-test/``, which contains various Python 
scripts, configuration files and text documents. The page ``blank.html`` is used
by the test launcher to configure the testing instance. Some Javascript files
provide utilitary functions and may be used in unit test pages:

- ``header.js``: this script is supposed to be used in all the unit tests. Among
  other things, it loads MathJax, executes pre and post actions and communicates
  with the test launcher.

- ``treeReftests.js``: this script is needed for tree reftests to serialize the
  ``<math>`` element.

- ``scriptTests.js``: this script is needed for script tests to determine the
  whether all the Javascript tests passed.

As you may guess the directory ``MathJax-test/results/`` contains results of tests.

The remainer is a recursive set of directories each one containing a file
``reftest.list`` which lists the unit tests and the children directories. The
format is the similar to Mozilla's 
`ReftestManifest
<http://mxr.mozilla.org/mozilla-central/source/layout/tools/reftest/README.txt>`_.
See the section The Reftest Manifest below. The topmost directories are the
following and should have straightforward
meanings:

- ``API/``
- ``Configuration/``
- ``Crashtests/``
- ``LaTeXToMathML/``
- ``MathMLToDisplay/``
- ``Parsing/``

Unit Tests
======================================

The test suite contains a set of unit tests, each one testing a particular
feature of MathJax. A unit test is made of one or two Web pages which are loaded
in the browsers during the execution of the test suite. There are six kinds of unit
tests, each one determining the success in a different way:

- == reftest: two pages are loaded and their visual outputs compared. The
  result is Pass if these outputs are equal.

- != reftest: same as == reftest, but the result is Pass if the renderings of
  the pages are different.

- ==tree reftest: two pages are loaded, the ``<math>`` element of each of them
  is serialized and the XML source should be the same in order to get the Pass
  result.

- !=tree reftest: same as == reftest, but the result is Pass if the XML sources
  of the pages are different.

- load test: the unit test is made of a single Web page. The test passes if
  no crash, hang etc happens. These tests are also called crashtests.

- script test: the unit test is made of a single Web page, in which a
  sequence of Javascript test is executed. The unit test passes if each
  individual Javascript test passes.

For reftests, the two pages compared are called the `test page` and the
`reference page`.

The Test Machines and Test Launcher
======================================

A Test Machine is a standard system with browsers, fonts, etc. It also has a
Selenium server which is simply a running java file selenium-server.jar. This
server is controled by the machine where the Test Launcher is running and
transmits the intructions to the browsers. Note that because some unit tests
need to take screenshots of test pages, one should note do any actions on the
test machines that could disturb the rendering of the pages.

The Test Launcher is made of a set of Python scripts and configuration files.
It can be run by the following command:

.. code-block:: sh

   python runTestsuite.py

In that case, the configuration default.cfg will be used. You can also
specified a list of comma-separated configuration files with the -c option.
For example

.. code-block:: sh

   python runTestsuite.py -c windows.cfg,linux.cfg

The Test Launcher Configurations
======================================

The options of the configuration file are:

- ``host``, ``port``: the host and port of a Selenium Server running on a test
  machine. 

- ``mathJaxPath``: the absolute uri to a ``MathJax/`` installation. This
  allows to test different versions of MathJax.

- ``mathJaxTestPath``: the absolute uri to a ``MathJax-test/`` directory
  containing the test pages.

- ``timeOut``: time in ms before aborting the loading of a page.

- ``fullScreenMode``: indicates whether the browsers should be opened in full
  screen mode when possible.

- ``formatOutput`̀ : indicates whether the output should be formatted in HTML,
  using the Perl script ``MathJax-test/clean-reftest-output.pl``.

- ``compressOutput``: indicates whether the output should be gzipped

- ``operatingSystem``: Windows, Linux (Mac not tested yet)

- ``browser``: Firefox, Safari, Chrome, Opera (not supported), MSIE, Konqueror

- ``browserMode``: Internet Explorer mode among StandardMode, Quirks, IE7, IE8
  and IE9.

- ``browserPath``: auto or path to the browser executable on the test machine.

- ``font``: STIX, TeX or ImageTeX

- ``nativeMathML``: for unit tests which do not impose the MathML engine, this
  option forces the use of the browser's native MathML.

- ``runSlowTests``: whether to run unit tests marked as slow.

``browser``, ``browserVersion``, ``font`` and ``browserMode`` may be a list of
elements separated by white spaces. In that case, the test instance is
executed for each element of the cartesian product of these lists.

The Reftest Manifest
======================================

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

Checking Unit Test Manually
======================================

It is possible to directly open the Web pages of unit tests to check their
results manually. This is useful when writing test or analysing a test failure.
The result can be determined in the following ways:

- For (visual) reftests, one only has to compare the visual rendering of the
  reference and test pages.

- For tree reftests, a textarea containing the serialization of the ``<math>``
  element is available. One has to compare these sources.

- For load test, you only have to see if the Web page is loaded without problem.
  Check the Javascript console to be sure that no error happens.

- For script reftest, a textarea containing the list of Javascript tests and
  their results is available.

It is also possible to provide the counterparts of some configuration options
of the Test Launcher in the query string of the URI.

- ``mathJaxPath``. For example, the query string ``mathJaxPath=/MathJax/unpacked/``
  allows to use the unpacked version of MathJax and hence helps debugging.
- ``font``
- ``nativeMathML`` ("true" or "false")
  
Test results
======================================

Results are located in ``MathJax-test/results/``. By default, the output files are
stored in ``YEAR-MONTH-DAY/TIME/``. One can specify a custom sub directory using
the -o option. The name of this directory can only contain alphanumeric characters
and its length must not exceed ten characters. For example

.. code-block:: sh

   python runTestsuite.py -o issue87

will store all the results in ``YEAR-MONTH-DAY/issue87/``. This is useful to group
several outputs of different testing instance in a same directory.

The name of the output files is determined according to the configuration options
of the Test Launcher. For example ``Windows_MSIE_StandardMode_STIX``. A testing
instance generates an output file in text format. According to the values of
`formatOutput`̀  and ``compressOutput``, this output can be formatted in HTML or
gzipped. Note that if the program receives SIGINT signal, only the text format
is generated, so that one can concatenate partial outputs and format/compress
them afterwards.

A testing instance output starts by information on the start time and configuration options.
It finishes by the end time and time spent. 

A formatted output contains a summary of results, with the success and what is expected
from the content of the Reftest Manifest:

- PASS: the test passed.
- UNEXPECTED-FAIL: the test failed.
- UNEXPECTED-PASS: the test passed but was announced to fail in the manifest.
- KNOWN-FAIL: the test failed as announced in the manifest.
- PASS(EXPECTED-RANDOM): the test passed but a random result was announced.
- KNOWN-FAIL(EXPECTED-RANDOM): the test failed but a random result was announced.

The number of tests and the proportion of these categories are represented by a diagram.
It is also possible to quickly browse the errors (UNEXPECTED-FAIL or UNEXPECTED-PASS)
with the Previous and Next error buttons.

Each test result in the formatted output is marked with a specific color according to which
category it belongs. A link to the test page is provided. For failing tree/visual reftests,
a link to the content (source or screenshot) is also given as well as a link to a diff. This
helps to analyse the failures. For visual reftest, the diff uses
``MathJax-test/reftest-analyzer.xhtml``.

Writing refests
======================================

