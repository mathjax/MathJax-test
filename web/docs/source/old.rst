.. _old:

#################
Old Documentation
#################

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

.. _launcher-config:

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

.. _reftest-manifest:

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


Test results
======================================

Results are located in ``MathJax-test/results/``. By default, the output files
are stored in ``YEAR-MONTH-DAY/TIME/``. One can specify a custom sub directory
using the -o option. The name of this directory can only contain alphanumeric
characters and its length must not exceed ten characters. For example

.. code-block:: sh

   python runTestsuite.py -o issue87

will store all the results in ``YEAR-MONTH-DAY/issue87/``. This is useful to
group several outputs of different testing instance in a same directory.

The name of the output files is determined according to the configuration
options of the Test Launcher. For example ``Windows_MSIE_StandardMode_STIX``.
A testing instance generates an output file in text format. According to the
values of ``formatOutput`` and ``compressOutput``, this output can be
formatted in HTML or gzipped. Note that if the program receives SIGINT signal,
only the text format is generated, so that one can concatenate partial outputs
and format/compress them afterwards.
