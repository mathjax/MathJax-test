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

from datetime import datetime
import ConfigParser
import HTMLTestRunner
import platform
import reftest
import seleniumMathJax
import time
import unittest

def getOperatingSystem():

    return platform.system()

def getBrowserStartCommand(aOS, aBrowser):

    if aBrowser == "Firefox":
        return "*firefox"

    if (aOS == "Windows" or aOS == "Mac") and aBrowser == "Safari":
        return "*safariproxy"

    if aBrowser == "Chrome":
        return "*googlechrome"

    if aBrowser == "Opera":
        return "*opera"

    if aOS == "Windows" and aBrowser == "MSIE":
        return "*iexploreproxy"

    if aOS == "Linux" and aBrowser == "Konqueror":
        return "*konqueror /usr/bin/konqueror"

    return "unknown"

def getOutputFileName(aOperatingSystem, aBrowser):
    utcdate = datetime.now().isoformat("_")
    return "results/" + \
        aOperatingSystem + "_" + aBrowser + "_" +  utcdate + ".html"

if __name__ == "__main__":

    # Load configuration file
    config = ConfigParser.ConfigParser()
    config.readfp(open("default.cfg"))
    section = "seleniumMathJax"

    browser = config.get(section, "browser")

    operatingSystem = config.get(section, "operatingSystem")
    if operatingSystem == "auto":
        operatingSystem = getOperatingSystem()

    browserStartCommand = config.get(section, "browserStartCommand")
    if browserStartCommand == "auto":
        browserStartCommand = getBrowserStartCommand(operatingSystem, browser)

    # Create a Selenium instance
    selenium = seleniumMathJax.seleniumMathJax(
        config.get(section, "host"),
        config.getint(section, "port"),
        browserStartCommand,
        config.get(section, "browserURL"),
        config.get(section, "mathJaxPath"),
        browser,
        operatingSystem,
        config.getboolean(section, "useNativeMathML"),
        config.getint(section, "timeOut"),
        config.getboolean(section, "fullScreenMode"))

    # Create the test suite
    suite = reftest.reftestSuite()
    suite.addReftests(selenium, "reftest.list")

    # Create the output file
    output = config.get("testsuite", "outputFile")
    if output == "auto":
        output = getOutputFileName(selenium.mOperatingSystem,
                                   selenium.mBrowser)

    # Run the test suite
    selenium.start()

    fp = file(output, "wb")
    HTMLTestRunner.HTMLTestRunner(stream=fp, verbosity=2).run(suite)
    fp.close()

    selenium.stop()
    time.sleep(2)
