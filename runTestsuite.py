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
# Contributor(s):
#   Frederic Wang <fred.wang@free.fr> (original author)
#
# ***** END LICENSE BLOCK *****

from datetime import datetime
import ConfigParser
import HTMLTestRunner
import platform
import reftest
import seleniumMathJax
import time
import unittest

def getOperatingSystem(aOperatingSystem):

    if aOperatingSystem != "auto":
        return aOperatingSystem

    return platform.system()

def getBrowserStartCommand(aBrowserPath, aOS, aBrowser):

    if aBrowser == "Firefox":
        startCommand = "*firefox"
    elif (aOS == "Windows" or aOS == "Mac") and aBrowser == "Safari":
        startCommand = "*safariproxy"
    elif aBrowser == "Chrome":
        startCommand = "*googlechrome"
    elif aBrowser == "Opera":
        startCommand = "*opera"
    elif aOS == "Windows" and aBrowser == "MSIE":
        startCommand = "*iexploreproxy"
    elif aOS == "Linux" and aBrowser == "Konqueror":
        startCommand = "*konqueror"
    else:
        startCommand = "*custom"
    
    if aBrowserPath == "auto":
        if aOS == "Linux" and aBrowser == "Konqueror":
           startCommand = startCommand + " /usr/bin/konqueror" 
    else:
        startCommand = startCommand + " " + aBrowserPath
    
    return startCommand

def getOutputFileName(aOutput, aSelenium):

    if aOutput != "auto":
        return aOutput

    utcdate = datetime.now().isoformat("_")
    return "results/" + \
        aSelenium.mOperatingSystem + "_" + \
        aSelenium.mBrowser + "_" + \
        aSelenium.mBrowserVersion + "_" + \
        aSelenium.mFonts + "_" + \
        utcdate + ".html"

if __name__ == "__main__":

    # Load configuration file
    config = ConfigParser.ConfigParser()
    config.readfp(open("default.cfg"))
    sectionFramework = "framework"
    sectionPlatform = "platform"
    sectionTestsuite = "testsuite"

    browser = config.get(sectionPlatform, "browser")

    operatingSystem = getOperatingSystem(
        config.get(sectionPlatform, "operatingSystem"))

    browserStartCommand = getBrowserStartCommand(
        config.get(sectionPlatform, ("browserPath")), operatingSystem, browser)

    # Create a Selenium instance
    selenium = seleniumMathJax.seleniumMathJax(
        config.get(sectionFramework, "host"),
        config.getint(sectionFramework, "port"),
        config.get(sectionFramework, "mathJaxPath"),
        config.get(sectionFramework, "mathJaxTestPath"),
        operatingSystem,
        browser,
        config.get(sectionPlatform, "browserVersion"),
        browserStartCommand,
        config.get(sectionPlatform, "fonts"),
        config.getboolean(sectionPlatform, "nativeMathML"),
        config.getint(sectionFramework, "timeOut"),
        config.getboolean(sectionFramework, "fullScreenMode"))

    # Create the test suite
    suite = reftest.reftestSuite(
        config.getboolean(sectionTestsuite, "runSlowTests"))
    suite.addReftests(selenium, "reftest.list")

    # Create the output file
    output = getOutputFileName(config.get("testsuite", "outputFile"), selenium)

    # Run the test suite
    selenium.start()

    fp = file(output, "wb")
    HTMLTestRunner.HTMLTestRunner(stream=fp, verbosity=2).run(suite)
    fp.close()

    selenium.stop()
    time.sleep(2)
