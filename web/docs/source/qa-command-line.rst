.. _qa-command-line:

#########################
QA Command line interface
#########################

This section describes a command line interface to the task controller.
Although the :ref:`Web interface <qa-web-interface>` is more convenient and may
have more features, the command line interface can sometimes be useful in
some situations. For example it is used for task scheduling: cron executes the
python scripts to send request to the task handler.

Note: the tools described on this page are available in the
``MathJax-tests/testRunner/`` directory.

.. _command-test-runner:

The Test Runner
===============

Once you have correctly set up the :ref:`Web servers <web-servers>` and at least
one :ref:`test machine <test-machine>`, you can execute a testing instance with
the following command:

.. code-block:: sh

   python runTestsuite.py

In that case, the configuration ``config/default.cfg`` will be used. That may
not really correspond to your set up, so be sure that the options are set
correctly. You may specify a custom configuration file with the -c option.
Actually, the option value can even be a list of comma-separated configuration
files to run several testing instances sequentially. For example

.. code-block:: sh

   python runTestsuite.py -c windows.cfg,linux.cfg

In the ``config/`` directory, you will also find a directory ``template/``
containing the template configuration files as well as a directory ``taskList/``
containing the configuration files of the task in the task handler.

By default, the :ref:`output files <test-results>` are created in a directory
whose name is of the form ``MathJax-test/web/results/YEAR-MONTH-DAY/TIME/``. It
is possible to use the -o option to specify an alternative subdirectory inside
``MathJax-test/web/results/``. For instance

.. code-block:: sh

   python runTestsuite.py -o next-release/MSIE/

to store all the output files in the
``MathJax-test/web/results/next-release/MSIE/`` directory.

.. _command-output-formatter:

Output formatter
================

This is the perl script ``clean-reftest-output.pl`` which is used to format the
text outputs. The basic usage is:

.. code-block:: sh

   clean-reftest-output.pl output.txt > output.html

which converts the file output.txt into a formatted file output.html. Some
options testsuiteURI and webURI are available:

.. code-block:: sh

   clean-reftest-output.pl output.txt [[testsuiteURI] webURI] > output.html

They are used to insert links to :ref:`test pages <test-suite>` (testsuiteURI)
and to :ref:`reftest analyser <reftest-analyser>` (webURI) inside the HTML
report.

.. _command-task-viewer:

Task Viewer
===========

The python script ``taskViewer.py`` takes no parameter. It displays the task
list in the same way as its :ref:`graphical counterpart <task-viewer>`:

.. code-block:: sh

   python taskViewer.py 
   TASK LIST NONEMPTY
   experimentalTask-opera-linux fred-VirtualBox.local Killed - 2011-11-15/experimentalTask/ None None
   experimentalTask-firefox-linux fred-VirtualBox.local Running 17/1258 2011-11-15/experimentalTask/ Linux_Firefox_default_STIX-1 None
   experimentalTask-msie-ie7 192.168.0.13 Killed Init 2011-11-15/experimentalTask/ Windows_MSIE_IE7_STIX None
   experimentalTask-htmlunit-linux fred-VirtualBox.local Pending - 2011-11-15/experimentalTask/ None None
   experimentalTask-chrome-linux fred-VirtualBox.local Pending - 2011-11-15/experimentalTask/ None None
   experimentalTask-firefox-windows 192.168.0.13 Killed - 2011-11-15/experimentalTask/ None None

Note that this output is saved in a file ``taskList.txt`` when the server is
stopped.

To get more precise description or perform actions, you can use
the :ref:`host info <command-host-info>` and
:ref:`task editor <command-task-editor>` python scripts. There is no task info
script, you can simply read the corresponding config file in
``config/taskList/``.

.. _command-host-info:

Host Info
=========

This is a simple python script ``hostInfo.py`` which takes an host name or
address as a parameter. It prints the list of running and pending tasks in the
same way as its :ref:`graphical counterpart <host-info>`:

.. code-block:: sh

   python hostInfo.py fred-VirtualBox.local

   HOST fred-VirtualBox.local (192.168.0.12)
   RUNNING_TASKS
   experimentalTask-firefox-linux 
   RUNNING_TASKS END
   PENDING_TASKS
   experimentalTask-htmlunit-linux 
   experimentalTask-chrome-linux 
   PENDING_TASKS END

.. _command-task-editor:

Task Editor
===========

This is a python to send commands to the task handler. Basic commands are
available:

.. code-block:: sh

   python taskEditor.py RUN taskName # run a task
   python taskEditor.py RESTART taskName # restart a task
   python taskEditor.py STOP taskName # stop a task
   python taskEditor.py REMOVE taskName # remove a task
   python taskEditor.py FORMAT taskName # format the text output of a task
   
where ``taskName`` is the name of an item in the task list. To create or edit a
task, one has to use the following syntax:

.. code-block:: sh

   python taskEditor.py EDIT taskName configFile [outputDirectory [taskSchedule]] # create or edit taskName

where ``configFile`` is the path to a configuration file. The optional
parameters ``outputDirectory`` and ``taskSchedule`` correspond to the those
available in  :ref:`the graphical version <task-editor>`, which are respectively
the directory where output files are stored and the date when the task is
scheduled.

The date uses the `cron <http://en.wikipedia.org/wiki/Cron>`_ scheduling
definitions, except that spaces are replaced by commas.
