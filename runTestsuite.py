# -*- Mode: Python; tab-width: 2; indent-tabs-mode:nil; -*-
# vim: set ts=2 et sw=2 tw=80:
# ***** BEGIN LICENSE BLOCK *****
# Version: Apache License 2.0
#
# Copyright (c) 2011 Design Science, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# ***** END LICENSE BLOCK *****

import time
from datetime import datetime
import unittest
import HTMLTestRunner
import seleniumMathJax
import reftest
import ConfigParser

def addReftests(aSuite, aSelenium, aReftestClass, aReftestDirectory):
    manifestFile = aReftestDirectory + "reftest.list"

    with open(manifestFile) as f:
        for line in f:
            if (not line.isspace()) and len(line) > 0 and line[0] != '#':
                t = line.split()
                if len(t) == 3:
                    aSuite.addTest(aReftestClass(aSelenium, t[0],
                                                aReftestDirectory,
                                                t[1], t[2]))

def getBrowserStartCommandFromBrowser(aBrowser):

    if aBrowser == "Firefox":
        return "*firefox"

    if aBrowser == "Safari":
        return "*safariproxy"

    if aBrowser == "Chrome":
        return "*googlechrome"

    if aBrowser == "Opera":
        return "*opera"

    if aBrowser == "MSIE":
        return "*iexploreproxy"

    if aBrowser == "Konqueror":
        return "*konqueror /usr/bin/konqueror"

    return "unknown"

def getOutputFileName(aBrowser):
    utcdate = datetime.now().isoformat("_")
    return "results/" + aBrowser + "_" + utcdate + ".html"

if __name__ == "__main__":
    config = ConfigParser.ConfigParser()
    config.readfp(open("options.cfg"))
    section = "seleniumMathJax"

    browser = config.get(section, "browser")
    browserStartCommand = config.get(section, "browserStartCommand")
    if browserStartCommand == "auto":
        browserStartCommand = getBrowserStartCommandFromBrowser(browser)

    selenium = seleniumMathJax.seleniumMathJax(
        config.get(section, "host"),
        config.getint(section, "port"),
        browserStartCommand,
        config.get(section, "browserURL"),
        config.get(section, "mathJaxPath"),
        browser,
        config.getboolean(section, "useNativeMathML"),
        config.getint(section, "timeOut"),
        config.getboolean(section, "fullScreenMode"))
    selenium.start()
    
    output = config.get("testsuite", "outputFile")
    if output == "auto":
        output = getOutputFileName(selenium.mBrowser)

    fp = file(output, "wb")

    suite = unittest.TestSuite()
    addReftests(suite, selenium, reftest.treeReftest, "LaTeXToMathML/")
    addReftests(suite, selenium, reftest.visualReftest, "MathMLToDisplay/")
    HTMLTestRunner.HTMLTestRunner(stream=fp, verbosity=2).run(suite)

    fp.close()

    selenium.stop()
    time.sleep(2)
