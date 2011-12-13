.. _installation:

##############################################
Testing Framework Installation and Maintenance
##############################################

This section provides instructions to install and keep up-to-date the testing
framework. They should help to do a local installation as well as to maintain
the public machines used by the project.

Note: the main component is already installed on ``dessci.webfactional.com``.
It uses a custom Python environment which can be enable with ``workon testing``.
Use the ``screen`` tool to keep the server running when your ssh connection
is closed. Public test machines are not available yet, though.

.. _basic-install:

Basic installation
==================

You need to have a central machine on which you will install
the :ref:`Task controller <task-controller>` and the
:ref:`Web servers <web-servers>`. You must set up an
`Apache <http://www.apache.org/>`_ web server on this machine. The
``MathJax-test/`` directory mentioned below should be accessible from your
server's root directory (via a symbolic link for example).

A copy of ``MathJax-test/`` can be downloaded with the command

.. code-block:: bash

   git clone https://github.com/mathjax/MathJax-test

You can then move into ``MathJax-test/`` where you find an ``INSTALL`` file,
which contains basic instructions on how to configure the framework. The default
configuration is available in the file ``default.cfg``. Copy this file into
``custom.cfg``:

.. code-block:: bash

   cp -n default.cfg custom.cfg

and edit the following sections of the new file with your favorite text editor:

- [bin]
  
  This section contains various paths to dependencies. They are listed in the
  ``INSTALL`` file. Some programs such as python or perl are
  quite standard and may easily be installed on your system if they are not
  already.

  The same holds for Python libraries. It is however recommended to use
  the Python's ``pip`` utilitary to install them, so that you can regularly use
  the ``make updateSelenium`` command to upgrade the Selenium python driver
  library.

  The installation of custom doxygen filters may be slightly less convenient
  but you only need them if you wish to generate the code documentation.

- [qa]

  You should fill in this section with a user name and a password file, which
  will be used to provide secured access to the QA interface. Such an
  account can be created in the standard way with the ``htpasswd``
  program.

Then use

.. code-block:: bash

   make config

to generate the configuration files. You may also want to generate the
documentation with the command

.. code-block:: bash

   make doc

Finally start the task handler server with

.. code-block:: bash

   make runTaskHandler

Now, open the directory ``http://path-to-mathjax-test/MathJax-test/web/`` in
your browser to access the QA interface. You should now be able to view and
edit tasks. However, to run them you need to set up
:ref:`test machines <test-machines-install>`.

.. _advanced-install:

Advanced configuration and maintenance
======================================

Once the :ref:`basic installation <basic-install>` is made, you can stop
the server at any time with a SIGINT command, typically with CTRL+C. This will
allow to modify the testing framework safely, for example to do a ``git pull``
or configuration changes. Then you can run the server again with

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

