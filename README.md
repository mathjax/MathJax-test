# MathJax-test

## A testing framework for the MathJax project

MathJax-test is a project to provide a testing framework for
[MathJax](http://www.mathjax.org/), based on
[Selenium testing system](<http://seleniumhq.org/>). MathJax-test has three main
components:

- Test Suite: a set of Web pages intended to cover all the features of MathJax
and ensure non regression.

- Test Runner: a set of scripts to automatically run the Test Suite in all the
platforms supported.

- Quality Assurance Framework: interface and tools to control the framework and
analyse the results.

![Testing Framework Infrastructure](https://raw.github.com/mathjax/MathJax-test/master/web/docs/source/testing-framework.svg)

The files for these components are respectively in the directories testsuite/,
testRunner/ and web/. MathJax-test is distributed under the Apache License but
also relies on files with a different free software license. You may find a
copy of these licenses in the licenses/ directory.

## Installation and Usage

The MathJax-test installation and usage documentation is available in the
web/docs/html/ directory of the MathJax-test distribution. People willing to
work on the development of this framework may also be interested in the
doxygen documentation in the web/docs/doxygen/ directory. The documents are
also available on the MathJax-test web site on line at
<https://github.com/mathjax/MathJax-test/tree/master/web/docs/source>

## Community

The main MathJax website is <http://www.mathjax.org>, and it includes
announcements and other important information. The testing project is maintained
and distributed on GitHub at <http://github.com/mathjax/MathJax-test>. If you
are interested in contributing to this project, a developer forum is available
at Google:

MathJax-Developers Group: <http://groups.google.com/group/mathjax-dev>
