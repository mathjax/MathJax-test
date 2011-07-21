.. _components:

############################
Testing Framework Components
############################

This section gives an overview of the different testing framework components.

Overview
========

.. image:: testing-framework.svg

The diagram above summarizes the components of the testing framework. There are
several :ref:`test machines <test-machine>` on which a browser is executing test
pages. These test pages are loaded from a :ref:`web servers <web-servers>`,
together with the relevant Javascript files.

In order to execute testing instances on the test machines, a
:ref:`test runner <test-runner>` python script is used. Although this program
can directly be called using the command line, there is a more general
:ref:`task controller <task-controller>` to handle several testing instances.

.. _web-servers:

Web Servers
===========

As previously seen, each :ref:`unit test <unit-test>` is made of one or two HTML
pages. All these pages can be stored on any Web server, indicated by the
**mathJaxTestPath** :ref:`configuration option <test-runner-config>`. The pages
use various
:ref:`Javascript headers <mathjax-test-headers>` located on the same Web server.

The test pages also need to use MathJax javascript files. It is also possible to
test a MathJax installation on any Web server, indicated by the **mathJaxPath**
:ref:`configuration option <test-runner-config>`.

.. _test-machine:

Test Machine
============

A test machine is a given operating system with a basic set up. Typically, we
want a graphical interface, browsers, fonts, plugins etc. A **Selenium server**
must also be running on this machine, to ensure communication between the test
runner and the browser. It is simply a 
`Java executable <http://code.google.com/p/selenium/downloads/detail?name=selenium-server-standalone-2.0.0.jar&can=2&q=>`_, which can be started using the
command

.. code-block:: sh

   java -jar name-of-the-selenium-server.jar

Note that because some unit tests need to take screenshots of test pages, one
should not do any actions on the test machines that could disturb the rendering
of the pages. In particular, it is neither possible to run several testing
instances on the same test machine simultaneously nor to use the operating
system graphical interface to do other work while the tests are running. If you
want to run tests on your local machine, a tip is to use virtual test machines.

.. _test-runner:

Test Runner
===========

The test runner is located in the ``MathJax-tests/testRunner/`` directory. It is
made of a set of several Python scripts as well as configuration files in the
``MathJax-tests/testRunner/config/`` directory.

Once you have correctly set up the :ref:`Web servers <web-servers>` and at least
one :ref:`test machine <test-machine>`, you can execute a testing instance with
the following command:

.. code-block:: sh

   python runTestsuite.py

In that case, the configuration default.cfg will be used. That may not really
correspond to your set up, so be sure that the options are set correctly. You
may specify a custom configuration file with the -c option. Actually, the
option value can even be a list of comma-separated configuration files to run
several testing instances sequentially. For example

.. code-block:: sh

   python runTestsuite.py -c windows.cfg,linux.cfg

By default, the :ref:`output files <test-results>` are created in a directory
whose name is of the form ``MathJax-test/web/results/YEAR-MONTH-DAY/TIME/``. It
is possible to use the -o option to specify an alternative subdirectory inside
``MathJax-test/web/results/``. For instance

.. code-block:: sh

   python runTestsuite.py -o next-release/MSIE/

to store all the output files in the
``MathJax-test/web/results/next-release/MSIE/`` directory.

The test runner may me configured with many options. Here is the exhaustive
list:

.. _test-runner-config:

- Framework configuration options

  - ``host``, ``port``: the host and port of a Selenium Server running on a test
    machine.
  
  - ``mathJaxPath``: the absolute uri to a ``MathJax/`` installation. This
    allows to test different versions of MathJax.
  
  - ``mathJaxTestPath``: the absolute uri to a ``MathJax-test/testsuite/``
    directory containing the test pages.
  
  - ``timeOut``: time in seconds before aborting the loading of a page.
  
  - ``fullScreenMode``: indicates whether the browsers should be opened in full
    screen mode when possible.
  
  - ``formatOutput`` : indicates whether the output should be formatted in HTML,
    using the Perl script
    `clean-reftest-output.pl <../doxygen/clean-reftest-output_8pl.html>`_.
  
  - ``compressOutput``: indicates whether the output should be gzipped
  
- Platform configuration options

  - ``operatingSystem``: Windows, Linux (Mac not tested yet)
  
  - ``browser``: Firefox, Safari, Chrome, Opera (not supported), MSIE, Konqueror
  
  - ``browserMode``: Internet Explorer mode among StandardMode, Quirks, IE7, IE8
    and IE9.
  
  - ``browserPath``: auto or path to the browser executable on the test machine.
    This option is ignored if several browsers are specified (see below).
  
  - ``font``: STIX, TeX or ImageTeX
  
  - ``nativeMathML``: for unit tests which do not specify the MathML engine,
    this option forces the use of the browser's native MathML.
  
- Test Suite configuration options

  - ``runSlowTests``: whether to run unit tests marked "slow".
  
  - ``runSkipTests``: whether to run unit tests marked "skip".

  - ``listOfTests``: the subset of the test suite to run. See the reftest
    selector (ADDREF) for a detailed description.

  - ``startID``: the ID of the test to start with. This is mainly used when a
    testing instance was interrupted. In that case, the text ouput contain a
    startID that we can use to recover the testing instance. 
  
``browser``, ``browserMode`` and ``font`` may be a list of elements separated by
white spaces. In that case, testing instances are executed for all the possible
combinations of browser, font and browserMode. Also note that browserMode are
ignored for other browsers that Internet Explorer.

The rationale for this feature, as well as the one for multiple configuration
files, is to provide a convenient way to run several instances on an operating
system in one go. This is mainly useful when you work in command line but you
may ignore them if you use the :ref:`task controller <task-controller>` instead.

.. _task-controller:

Task Controller
================

This is an additional component to centralize the control of the testing
instances and make it more convenient for QA engineers.

The **task handler** is a server that maintains a list of tasks. It
can receive instructions to add new tasks, run tasks etc It stores information
on each task, such that
:ref:`configuration options <test-runner-config>` to use. When the task handler
runs a task, it creates a new :ref:`test runner <test-runner>` process and
communicates with it to stay informed of the testing instance status and
progress, to know whether the process has been killed etc

A **QA User Interface** is available to verify the status of each task, the
information on the task, to edit, schedule and run tasks etc It directly sends
the instructions to the task handler. Actions can be made throughout the command
line with the help of the ``taskViewer.py`` and ``taskEditor.py`` Python
scripts. A web interface is also available. See the section
:ref:`QA tools <qa-tools>`. 

A **Task Scheduler** can memorize tasks to run regularly at a specified date and
time. It is based on the `cron <http://en.wikipedia.org/wiki/Cron>`_ tool and
thus accepts the same syntax. It sends run instructions to the task handler
when a task should be started. 
