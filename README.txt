********** Software Requirement **********

It is assumed that you have a local MathJax/ distribution on your computer.

Python and Java are quite popular software tools and are probably already
installed on your machine. If not, you can download them freely. You also need
the Python Imaging Library (PIL).

  http://www.python.org/
  http://www.pythonware.com/products/pil/
  http://www.java.com/en/download/

Also, the automated tests are run directly in browsers, so be sure to have on
your system those you are interested in:

  - Firefox
  - Safari (fullscreen mode not supported yet)
  - Chrome
  - Opera (not supported yet)
  - MSIE (possibly with the MathPlayer plugin to test its MathML support)
  - Konqueror

Finally, you need to download the Selenium server:

  http://selenium.googlecode.com/files/selenium-server-standalone-2.0b1.jar

********** Installing a local server **********

There are many inconsitencies across browsers & operating systems regarding the
URIs of local files. Although it is not mandatory, it is recommended to
have your MathJax distribution available from a server running on your local
machine.

For example, you can install an Apache server and use an alias or a symbolic
link to make the URI

  http://localhost/MathJax/

point to your local MathJax/ files.

********** Running MathJax testsuite **********

Start the Selenium server with the command

  java -jar /path/to/your/selenium-server.jar

Use the file options.cfg to configure the way the test is run. When all is ready
launch a new instance with the command

  python runTestsuite.py

and wait until the testsuite is complete.

Warning: because some unit tests need to take screenshots of test pages and
compare them, the browser is put in fullscreen mode and you should avoid any
action that could disturb what is rendered on the screen. Tip: use a separate
(virtual) machine to run your tests if you want to use your computer at the
same time.

********** Analysing the results **********

Once the testsuite run, a html page should appear in the results/ directory or
to the location you may have specified. Open the report in your browser to see
statistics on the tests.

Some failed tests provide an AssertionError with base64 screenshots of the test
pages. You can visualize them with Mozilla's reftest-analyzer.xhtml by coying
and pasting the "REFTEST TEST-UNEXPECTED-FAIL ..." AssertionError string.
