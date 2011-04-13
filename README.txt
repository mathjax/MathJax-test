********** Software Requirement **********

It is assumed that you have local MathJax/ and MathJax-test/ distributions on
your computer. You can pull them from GitHub:

  https://github.com/mathjax/MathJax
  https://github.com/mathjax/MathJax-test

Python and Java are quite popular software tools and are probably already
installed on your machine. If not, you can download them freely. You also need
the Python Imaging Library (PIL).

  http://www.python.org/
  http://www.pythonware.com/products/pil/
  http://www.java.com/en/download/

The automated tests are run directly in browsers, so be sure to have on your
system those you are interested in:

  - Firefox
  - Safari
  - Chrome
  - Opera (not supported yet)
  - MSIE (possibly with the MathPlayer plugin to test its MathML support)
  - Konqueror

Please also install the following fonts on your machine
(see http://www.mathjax.org/help/fonts/):

  - STIX (http://www.stixfonts.org/)
  - TeX  (in the fonts/HTML-CSS/TeX/otf/ directory)

Finally, you need to download the Selenium server:

  http://selenium.googlecode.com/files/selenium-server-standalone-2.0b1.jar

********** Installing a local server **********

There are many inconsitencies across browsers & operating systems regarding the
URIs of local files. Although it is not mandatory, it is recommended to
have your MathJax distribution available from a server running on your local
machine.

For example, you can install an Apache server and use an alias or a symbolic
link to make the URIs

  http://localhost/MathJax/
  http://localhost/MathJax-test/

point to your local MathJax/  MathJax-test/ files.

********** Running MathJax testsuite **********

Start the Selenium server with the command

  java -jar /path/to/your/selenium-server.jar

Use the file default.cfg to configure the way the test is run. When all is ready
launch a new instance with the command

  python runTestsuite.py

and wait until the testsuite is complete. You can also specified a custom
configuration file with the -c option. For example

  python runTestsuite.py -c windows.cfg

Warning: because some unit tests need to take screenshots of test pages and
compare them, you should avoid any action that could disturb what is rendered
on the screen. Tip: use a separate (virtual) machine to run your tests if you
want to use your computer or run other instances at the same time.

********** Analysing the results **********

Once the testsuite run, a html page should appear in the results/ directory or
to the location you may have specified. Open the report in your browser to see
statistics on the tests.

Some failed tests provide an AssertionError with base64 screenshots of the test
pages. To visualize them, open tools/reftest-analyzer.xhtml and paste the
the "REFTEST TEST-..." AssertionError string. You can also use the "Browse" 
button to load the html page and see all the results at once.
