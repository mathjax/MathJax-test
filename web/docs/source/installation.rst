.. _installation:

##############################################
Testing Framework Installation and Maintenance
##############################################

This section provides instructions to install and keep up-to-date the testing
framework. They should help to do a local installation as well as to maintain
the public machines used by the project.

.. _basic-install:

Basic installation
==================

First, please have a look at the :ref:`framework overview <overview>` to
understand what you are going to do. The basic installation consists in
configuring the central machine that controls the framework. In this section,
we will only use the :ref:`test runner <test-runner>`. To avoid the installation
of a local Apache server, we also rely on the public MathJax Web server.
Finally, the central machine will itself be used as a test machine.

It is recommended to use an UNIX environment with the standard programs. On
Windows, you might want to use
`Cygwin <http://www.cygwin.com/>`_ which emulates a UNIX-like environment and
download software tools from that system. In that case, after having installed all
the programs you might need to use the
`Rebaseall <http://cygwin.wikia.com/wiki/Rebaseall>`_ command. On Mac OS, you can
download the programs from the `MacPorts <http://www.macports.org/>`_ repository. 

Start by installing git and get a copy of ``MathJax-test/`` with the command:

.. code-block:: bash

   git clone https://github.com/mathjax/MathJax-test

You can then move into ``MathJax-test/`` where the default configuration is
available in the file ``default.cfg``. Copy this file into a custom
configuration file ``custom.cfg``:

.. code-block:: bash

   cp -n default.cfg custom.cfg

Then install various other standard programs: python (2.6 or greater), perl
(5.1 or greater), pip, sed (use the GNU version gsed on MacOS), wget and java.
If necessary, update the [bin] section accordingly and/or modify your PATH
variable so that the testing framework will be able to find them.

Install various libraries using the package manager of your system or
Python's pip. For example

.. code-block:: bash

  sudo pip install pil ply python-crontab selenium

will install `Python Imaging Library <http://www.pythonware.com/products/pil/>`_,
`Python Lex-Yacc <http://www.dabeaz.com/ply/>`_ and 
`Python Crontab <http://pypi.python.org/pypi/python-crontab/>`_ and
`Selenium Python Driver <http://pypi.python.org/pypi/selenium/>`_. For the
Selenium Python Driver, installing from pil is the best option if you want to
get the latest version of the library and be able to to upgrade it later with the
``make updateSelenium``.

(TODO: verify other dependencies on Python and Perl's libraries)

Once all the dependencies are satisfied, you should be able to configure the
framework with the command

.. code-block:: bash

   make config

We are now going to describe one of the simplest test machine configuration.
We assume that you have the latest version of Firefox installed. Download the
Selenium server with the command

.. code-block:: bash

  make downloadSeleniumServer

and then execute it with

.. code-block:: bash

  make runSeleniumServer

Now open a new terminal and move into the ``MathJax-test/testRunner`` directory.
Copy ``testRunner/default.cfg`` with

.. code-block:: bash

  cp config/default.cfg config/custom.cfg

and open this new file ``config/custom.cfg`` in a text editor. Modify ``host``
to be your local host (generally 127.0.0.1 or localhost), ``operatingSystem``
to match your system configuration (Windows, Mac or Linux), ``browser`` to
Firefox, ``font`` to TeX and ``outputJax`` to SVG. Finally, run the test with

.. code-block:: bash

  python runTestsuite.py -c config/custom.cfg

If you want to interrupt the script properly, press Ctrl + C in the terminal
where you typed the command above.

You will now be able to find in ``MathJax-test/web/results/`` the results of
the testing instance.

TODO: rewrite sections below

.. _advanced-install:

Advanced configuration and maintenance
======================================

Once the :ref:`basic installation <basic-install>` is made, you can stop
the server at any time with a SIGINT command, typically with CTRL+C. This will
allow you to modify the testing framework safely, for example to do a
``git pull`` or configuration changes. Then you can run the server again with

.. code-block:: bash

   make runTaskHandler

The task list is saved when the server is closed and should be restored when you
start it again. However, if you see error messages saying that a configuration
file can not be found, you can empty the task list with the command:

.. code-block:: bash

   make clearTaskList

To upgrade the Selenium python driver library, use

.. code-block:: bash

   make updateSelenium

The basic installation does not come with any MathJax installation. You can
download and update all the development branches of the project in one go with:

.. code-block:: bash

   make updateMathJaxBranches

The MathJax installations will then be available in
``http://path-to-mathjax-test/MathJax-test/mathjax/`` and can be used when
running testing instances. If you run ``make config`` again, the branches will
be listed in the known branches of the task editor.

You may also want to look at ``mathjax/getMathJaxBranches.sh`` or 
``web/docs/Makefile`` to get more specific commands to maintain the MathJax
branches and documentation.

You can do more advanced configuration by editing the [testing_instance] and
[other] sections of the ``custom.cfg`` and generating it again with:

.. code-block:: bash

   make config

Note that this command should be run again each time you add or remove tests in
the testsuite.

Test results are stored in
``http://path-to-mathjax-test/MathJax-test/web/results/``. You can freely
organize this directory to fit your needs. In particular, you may want
to regularly remove obsolete test outputs and keep a copy of important ones in 
dedicated directories.

.. _test-machines-install:

Installation and maintenance of test machines
=============================================

A test machine is a given operating system which contains a selenium a browser
and other related programs to make the whole thing work. See the section about
:ref:`test machine <test-machine>` for more details.

A test machine can be the local machine on which the testing framework is
installed, virtual machines on the same host or even other remote hosts. The
important point is that they can communicate using their respective IP adresses
or host names. You may have to configure your firewall to accept requests from
the central machines.

Once you have your network of machines ready, you can use the task editor in
the QA interface to run testing instance. Be careful to enter the correct
``host`` and ``operatingSystem`` fields. It may become a pain to do this each
time you create a new task. Hence, it is recommended to edit the HOST_LIST and
HOST_LIST_OS options in the [testing_instance] sections to describe the
testing machine availables. Do not forget to execute ``make config`` and run
the server again after your changes.

For example:

.. code-block:: bash

   HOST_LIST = localhost 192.168.0.11 192.168.0.12 VirtualBox.local
   HOST_LIST_OS = Linux Mac Windows Linux

describes a network of four machines. Two Linux machines with hostname
"localhost" and "VirtualBox.local" together with Mac and Windows machines of
respective IP adresses 192.168.0.11 and 192.168.0.12.

After that, you can directly choose a host among a list of known hosts.
Conversely, if you choose a template in fast configuration, the testing
framework will try to find a host corresponding to the requested operating
system.

The test machines should be kept up-to-date, essentially by upgrading the latest
versions of software components (browsers, fonts, plugins, selenium server etc).
Also, to test MathJax updates one often has to clear cache and cookies.
Unfortunately, no interface is available yet to perform all these tasks. One
has to do it manually.

.. _grid

Executing Selenium servers
==========================

The traditionnal configuration is to execute a selenium server on each
:ref:`test machine <test-machine>`, with a command like:

.. code-block:: bash

  java -jar name-of-the-selenium-server.jar

If you have the code for the testing framework installed on the test machine, the
following command will do the same:

.. code-block:: bash

  make runSeleniumServer

Except that you can also modify the server properties in your config file:

.. code-block:: bash

  SELENIUM_SERVER_HOST
  SELENIUM_SERVER_PORT

An alternative approach is Selenium 2's new
`Grid feature <http://code.google.com/p/selenium/wiki/Grid2>`_. Please read
the Selenium documentation for details. You can execute the servers with

.. code-block:: bash

  make runSeleniumHub # command to execute on the task controller
  make runSeleniumNode # command to execute on the test machines

Where the first command is for the Hub on :ref:`task controller <task-controller>`
and the second command is for the :ref:`test machine <test-machine>`. The
configuration options to consider are:

.. code-block:: bash

  SELENIUM_SERVER_HUB_HOST
  SELENIUM_SERVER_HUB_PORT
  SELENIUM_SERVER_NODE_OPTIONS
  SELENIUM_SERVER_NODE_TIMEOUT
