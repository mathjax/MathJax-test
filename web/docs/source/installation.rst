.. _installation:

##############################################
Testing Framework Installation and Maintenance
##############################################

This section provides instructions to install and keep up-to-date the testing
framework. They should help to do a local installation as well as to maintain
the public machines used by the project.

.. _basic-install:

Basic Installation
==================

First, please have a look at the :ref:`framework overview <overview>` to
understand what you are going to do. The basic installation consists in
configuring the central machine that controls the framework. In this section,
we will only use the :ref:`test runner <test-runner>`. To avoid the installation
of a local Apache server, we will also rely on the public MathJax Web server.
Finally, the central machine will itself be used as a test machine. Hence, we
get the following structure:

.. image:: testing-framework-basic.svg

It is recommended to use an UNIX environment with standard programs installed.
On Windows, it is recommended to use
`Cygwin <http://www.cygwin.com/>`_ which emulates a UNIX-like environment and
to download software tools from its package manager and to execute the command
line commands below from the Cygwin environment.
After having installed all the programs you might need to use the
`Rebaseall <http://cygwin.wikia.com/wiki/Rebaseall>`_ command. On Mac OS, you
can download the programs from the `MacPorts <http://www.macports.org/>`_
repository. 

Start by installing git and get a copy of ``MathJax-test/`` with the command:

.. code-block:: bash

   git clone https://github.com/mathjax/MathJax-test

You can then move into ``MathJax-test/`` where the default configuration is
available in the file ``default.cfg``. Copy this file into a custom
configuration file ``custom.cfg``:

.. code-block:: bash

   cp -n default.cfg custom.cfg

Then install other standard programs: Python (2.6 or greater), Perl
(5.1 or greater), pip (to install Python libraries), sed (be sure to use the
GNU version, gsed on MacOS), wget (for automatic downloading), java (to run
Selenium servers), cron (for task scheduling). If necessary, update the
``[bin]`` section of ``custom.cfg`` accordingly and/or modify your ``PATH``
environment variable so that the testing framework will be able to find them.

Install Python libraries using the package manager of your system or Python's
pip. For example

.. code-block:: bash

  sudo pip install pil ply python-crontab selenium

will install
`Python Imaging Library <http://www.pythonware.com/products/pil/>`_,
`Python Lex-Yacc <http://www.dabeaz.com/ply/>`_ ,
`Python Crontab <http://pypi.python.org/pypi/python-crontab/>`_ and
`Selenium Python Driver <http://pypi.python.org/pypi/selenium/>`_. For the
Selenium Python Driver, installing from pil is the best option if you want to
get the latest version of the library and be able to upgrade it later with
``make updateSelenium``.

Once all the dependencies are satisfied, you should be able to configure the
framework with the command

.. code-block:: bash

   make config

We are now going to describe one of the simplest test machine configuration.
We assume that you have the latest version of Firefox installed. Download the
Selenium server with the command

.. code-block:: bash

  make downloadSeleniumServer

You should get a java executable ``MathJax-test/testRunner/seleniumServer.jar``.
Normally, you can start the Selenium server with the command

.. code-block:: bash

  make runSeleniumServer

However, on Windows it may be preferable to execute the server outside the
Cygwin environnement. Indeed, it appears that otherwise the server can not
communicate with the browsers. Assuming that you have java installed on your
Windows system, open a command line (``cmd`` in the start menu) and type

.. code-block:: bash

  java -jar /path/to/the/selenium/server/runSeleniumServer.jar

Once you have started the server via one of the method above, open a new
terminal and move into the ``MathJax-test/testRunner`` directory. Copy the
default configuration with

.. code-block:: bash

  cp config/default.cfg config/custom.cfg

and open this new file ``config/custom.cfg`` in a text editor. Modify ``host``
to be your local host (generally 127.0.0.1 or localhost), ``operatingSystem``
to match your system configuration (Windows, Mac or Linux), set ``browser`` to
Firefox, ``font`` to TeX and ``outputJax`` to SVG.

By default, the results will be gzipped text and html files. You may want to
set ``formatOutput`` or ``compressOutput`` to change this behavior. Also, the
whole test suite will be executed. You can use the
`reftest selector <http://devel.mathjax.org/testing/web/selectReftests.xhtml>`_
to choose only a subset and get the corresponding ``listOfTests`` string.

Finally, run the tests with the command below. If you want to interrupt the
script properly, press CTRL+C in the terminal where you typed that command.

.. code-block:: bash

  python runTestsuite.py -c config/custom.cfg

At the end of the execution, you will be able to find in
``MathJax-test/web/results/`` the results of the testing instance.

.. _advanced-install:

Advanced Configuration
======================

As a general rule of thumb, you can do more advanced configuration by editing
the ``custom.cfg`` and updating the configuration with

.. code-block:: bash

   make config

We are now going to describe this configuration more precisely. Although we do
not repeat it keep in mind that you should always execute the ``make config``
command after having edited the configuration file if you want your changes to
be taken into account.

Task Handler
------------

After the :ref:`basic installation <basic-install>` is made, you can start the
task handler with the command

.. code-block:: bash

   make runTaskHandler

and stop it at any time with CTRL+C. When the task handler is running, you can
already use the command line :ref:`task viewer <command-task-viewer>` and
:ref:`task editor <command-task-viewer>` without additional configuration.

The task list is saved in ``testRunner/taskList.txt`` when the server is
stopped and should be restored when you start it again. However, if you see
error messages saying that a configuration file can not be found, you can try to
remove the erroneous line in  ``testRunner/taskList.txt`` or empty the task
list with the command:

.. code-block:: bash

   make clearTaskList

Test Machines
-------------

You can now install the different components of each
:ref:`test machine as indicated here<test-machine>`.

It is recommended to edit the HOST_LIST and HOST_LIST_OS options of
``custom.cfg`` to describe the testing machines available, so that the testing
framework can do helpful guesses or suggestions. For instance,

.. code-block:: bash

   HOST_LIST = localhost 192.168.0.11 192.168.0.12 VirtualBox.local
   HOST_LIST_OS = Linux Mac Windows Linux

describes a network of four machines. Two Linux machines with hostname
"localhost" and "VirtualBox.local" together with Mac and Windows machines of
respective IP adresses 192.168.0.11 and 192.168.0.12.

Before running any task on a test machine, be sure that the
:ref:`the Selenium server is running <executing-selenium-servers>` on that
test machine. Also, verify that the IP adresses or host names are correct. You
may also have to configure your firewall to accept requests from the central
machines.

Local Web Server
----------------

By default, the testing framework uses the public
:ref:`Web server <web-servers>` of the MathJax project for both the testsuite
and the MathJax scripts. However, it is sometimes useful to have a local copy
of these pages.

If you have cloned MathJax-test as described in the
:ref:`basic installation <basic-install>`, then the testsuite is directly
available in the ``testsuite/`` subdirectory.

You can modify the ``MATHJAX_GIT_USERS`` configuration option to enumerate the
list of developers from which you want to download the branches. Then you can
download all the development branches of the project in one go with the command

.. code-block:: bash

   make updateMathJaxBranches

These branches are stored in the ``mathjax/`` subdirectory.

Finally, you need to do a standard installation of Apache and PHP and map the
``MathJax-test/`` to some location. On Windows, the EasyPHP tool can help to do
that quickly.

Note that the testing framework uses ``.htaccess`` files, for example to
restrict access to some directories or serve the test results as gzipped files.
It is possible that you need to add some ``AllowOverride`` directives in your
Apache configuration in order to make the htaccess rules effective.

If you want, you can also set ``MATHJAX_TEST_URI`` to your local
installation (e.g. ``http://localhost/MathJax-test/``).

QA Web Interface
----------------

Although you can in theory control the whole testing framework from the command
line, it is generally more convenient to use the
:ref:`QA Web Interface <qa-web-interface>`. You need to follow the instructions
above about how to setup local web server. Note that even if you do not intend
to use the local MathJax installations, the ``updateMathJaxBranches`` command
is useful to initialize the list of MathJax developement branches in the
dropdown menu of the :ref:`task editor <task-editor>`.

Once the local web server installed, you can now open
``http://path-to-your-local-MathJax-test/web/`` in your Web browser to
access the QA Web Interface. Some pages in the documentation may not be
available until you follow the instructions of the next section.

To use the :ref:`task viewer <task-viewer>`, be sure that the task handler is
running.

If you install the interface on a public Web server, you certainly want to
restrict access to the task editor. To do that you just have to fill in the
``[qa]`` section of the configuration file.

Documentation
-------------

To generate the documentation, you need to install additional programs:
`sphinx-build <http://sphinx.pocoo.org/>`_,
`Graphviz <http://graphviz.org/>`_ (for the dot program) and
`Doxygen <http://www.doxygen.org/>`_.
For the doxygen documentation, you need some
filters for `Python <http://pypi.python.org/pypi/doxypy/>`_,
`Perl <http://www.bigsister.ch/doxygenfilter/>`_,
`Javascript <http://svn.berlios.de/wsvn/jsunit/trunk/jsunit/util/js2doxy.pl>`_.
If needed, modify the ``[bin]`` section to point to the programs and filters.

Finally, generate the documentation with the command:

.. code-block:: bash

  make doc

.. _test-machines-install:

Maintenance of Machines
=======================

Task Controller
---------------

The central machine should be updated regularly to keep the latest version of
the testing framework. We have already seen a couple of handy commands for that
purpose:

.. code-block:: bash

  git pull                    # update the testing framework
  make config                 # update the configuration
  make doc                    # update the documentation
  make updateSeleniumDriver   # update the selenium driver
  make updateMathJaxBranches  # update the MathJax branches

Note that the ``make config`` command is important. For example it should be run
again each time you add or remove tests in the testsuite, or do a ``git pull``
command.

Test results are stored in
``http://path-to-mathjax-test/MathJax-test/web/results/``. You can freely
organize this directory to fit your needs. In particular, you may want
to regularly remove obsolete test outputs and keep a copy of important ones in 
dedicated directories.

Test Machines
-------------

The test machines should be kept up-to-date, essentially by upgrading the latest
versions of software components (browsers, fonts, plugins, selenium server etc).
Also, to test MathJax updates one often has to clear cache and cookies.
Unfortunately, no interface is available yet to perform all these tasks. One
has to do it manually.

.. _executing-selenium-servers:

Executing Selenium Servers on Test Machines
===========================================

In the traditionnal configuration you execute a selenium server on each
:ref:`test machine <test-machine>`, with a command like:

.. code-block:: bash

  java -jar name-of-the-selenium-server.jar

If you have the code for the testing framework installed on the test machine,
the following command will do the same:

.. code-block:: bash

  make runSeleniumServer

Except that you can also modify the server properties in your config file:

.. code-block:: bash

  SELENIUM_SERVER_HOST
  SELENIUM_SERVER_PORT

An alternative approach is Selenium 2's new
`Grid feature <http://code.google.com/p/selenium/wiki/Grid2>`_. This feature is
still experimental in MathJax-test so we do not give the details here. If you
have the code for the testing framework installed on the test machine, you can
execute the servers with

.. code-block:: bash

  make runSeleniumHub # command to execute on the task controller
  make runSeleniumNode # command to execute on the test machines

Where the first command is for the Hub on
:ref:`task controller <task-controller>`
and the second command is for the :ref:`test machine <test-machine>`. The
configuration options to consider are:

.. code-block:: bash

  SELENIUM_SERVER_HUB_HOST
  SELENIUM_SERVER_HUB_PORT
  SELENIUM_SERVER_NODE_OPTIONS
  SELENIUM_SERVER_NODE_TIMEOUT
