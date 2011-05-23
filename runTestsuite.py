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

from datetime import datetime, timedelta
import ConfigParser
import argparse
import errno
import gzip
import math
import os
import platform
import re
import reftest
import seleniumMathJax
import string
import subprocess
import sys
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
        if startCommand == "*custom":
            print >> sys.stderr, "Unknown browser"
            return "unknown"

        if aOS == "Linux" and aBrowser == "Konqueror":
           startCommand = startCommand + " /usr/bin/konqueror" 
    else:
        startCommand = startCommand + " " + aBrowserPath
    
    return startCommand

def getOutputFileName(aDirectory, aSelenium):

    return \
        aDirectory + \
        aSelenium.mOperatingSystem + "_" + \
        aSelenium.mBrowser + "_" + \
        aSelenium.mBrowserMode + "_" + \
        aSelenium.mFont

def printInfo(aString):
  print "REFTEST INFO | " + aString

def boolToString(aBoolean):
    if aBoolean:
        return "true"
    return "false"

def gzipFile(aFile):
    f_in = open(aFile, "rb")
    f_out = gzip.open(aFile + ".gz", "wb")
    f_out.writelines(f_in)
    f_out.close()
    f_in.close()
    os.remove(aFile)

if __name__ == "__main__":

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="A Python script to run MathJax automated tests.")
    parser.add_argument("-c", "--config", nargs="?", default="default.cfg",
                        help="A comma separated list of files describing the \
parameters of the automated test instance to run. The default configuration \
file is default.cfg.")
    parser.add_argument("-o", "--output", nargs="?", default=None,
                        help="By default, the output files are stored in \
default results/YEAR-MONTH-DAY/TIME/. This option allows to specify a \
custom sub directory instead of TIME/. The name of this directory can only \
contain alphanumeric characters and its length must not exceed ten characters.")
    args = parser.parse_args()

    # create the date directory
    now = datetime.utcnow();
    directory = "results/" + now.strftime("%Y-%m-%d") + "/"
    if not os.path.exists(directory):
        os.makedirs(directory)

    # create the subdirectory
    if args.output and re.match("^([0-9]|[a-z]|[A-Z]){1,10}$", args.output):
        directory += args.output + "/"
    else:
        directory += now.strftime("%H-%M-%S/")

    if not os.path.exists(directory):
        os.makedirs(directory)

    # execute testing instances for all the config files
    configFileList = args.config.split(",")

    for configFile in configFileList:

        if (not os.path.isfile(configFile)):
            print >> sys.stderr,\
                "Warning: config file " + configFile + " not found!"
            continue

        # Load configuration file
        config = ConfigParser.ConfigParser()
        config.readfp(open(configFile))

        # framework section
        section = "framework"
        host = config.get(section, "host")
        port = config.getint(section, "port")
        mathJaxPath = config.get(section, "mathJaxPath")
        mathJaxTestPath = config.get(section, "mathJaxTestPath")
        timeOut = config.getint(section, "timeOut")
        fullScreenMode = config.getboolean(section, "fullScreenMode")
        formatOutput = config.getboolean(section, "formatOutput")
        compressOutput = config.getboolean(section, "compressOutput")
    
        # platform section
        section = "platform"
        operatingSystem = getOperatingSystem(config.get(section,
                                                        "operatingSystem"))
        browserList = config.get(section, "browser").split()
        browserModeList = config.get(section, "browserMode").split()
        browserPath = config.get(section, "browserPath")
        fontList = config.get(section, "font").split()
        nativeMathML = config.getboolean(section, "nativeMathML")
    
        # testsuite section
        section = "testsuite"
        runSlowTests = config.getboolean(section, "runSlowTests")
        runSkipTests = config.getboolean(section, "runSkipTests")
        listOfTests = config.get(section, "listOfTests")
       
        if ((len(browserList) > 1 or len(browserModeList) or len(fontList) > 1)
            and browserPath != "auto"):
            print >> sys.stderr, "Warning: browserPath ignored"
            browserPath = "auto"

        for browser in browserList:
            for font in fontList:
                for browserMode in browserModeList:

                    # Browser mode is only relevant for MSIE
                    if not(browser == "MSIE"):
                        browserMode = "StandardMode"

                    browserStartCommand = getBrowserStartCommand(
                        browserPath,
                        operatingSystem,
                        browser)

                    if browserStartCommand != "unknown":

                        # Create a Selenium instance
                        selenium = seleniumMathJax.seleniumMathJax(
                            host, port, mathJaxPath, mathJaxTestPath,
                            operatingSystem,
                            browser,
                            browserMode,
                            browserStartCommand, 
                            font,
                            nativeMathML,
                            timeOut,
                            fullScreenMode)
                        
                        # Create the test suite
                        suite = reftest.reftestSuite(runSlowTests,
                                                     runSkipTests,
                                                     listOfTests)
                        if listOfTests == "all":
                            index = -1 # all tests
                        else:
                            index = 0 # tests indicated in listOfTests

                        suite.addReftests(selenium, "reftest.list", index)
                        
                        # Create the output file
                        output = getOutputFileName(directory, selenium)
                        outputTxt = output + ".txt"
                        outputHTML= output + ".html"
                        fp = file(outputTxt, "wb")
                        stdout = sys.stdout
                        sys.stdout = fp
                        
                        # Run the test suite
                        startTime = datetime.utcnow()
                        printInfo("Starting Testing Instance ; " +
                                  startTime.isoformat())
                        interrupted = False
                        try:
                            selenium.start()
                            printInfo("host=" + str(host))
                            printInfo("port=" + str(port))
                            printInfo("mathJaxPath = " + mathJaxPath)
                            printInfo("mathJaxTestPath = " + mathJaxTestPath)
                            printInfo("operatingSystem = " + operatingSystem)
                            printInfo("browser = " + browser)
                            printInfo("browserMode = " + browserMode)
                            printInfo("font = " + font)
                            printInfo("nativeMathML = " +
                                      boolToString(nativeMathML))
                            printInfo("runSlowTests = " +
                                      boolToString(runSlowTests))
                            unittest.TextTestRunner(sys.stderr,
                                                    verbosity=2).run(suite)
                            selenium.stop()
                            time.sleep(4)
                        except KeyboardInterrupt:
                            selenium.stop()
                            interrupted = True
                            
                        endTime = datetime.utcnow()
                        deltaTime = endTime - startTime
                        if not interrupted:
                            printInfo("Testing Instance Finished ; " +
                                      endTime.isoformat())
                        else:
                            printInfo("Testing Instance Interrupted ; " +
                                      endTime.isoformat())

                        printInfo("Testing Instance took " +
                                  str(math.trunc( \
                                    deltaTime.total_seconds() / 60)) +
                                  " minute(s) and " +
                                  str(deltaTime.seconds % 60) + " second(s)")
                        sys.stdout = stdout
                        fp.close()

                        if not interrupted:
                            if formatOutput:
                                # Execute the Perl script to format the output
                                print "Formatting the text ouput..."
                                pipe = subprocess.Popen(
                                    ["perl", "clean-reftest-output.pl",
                                     outputTxt],
                                    stdout=subprocess.PIPE)
                                fp = file(outputHTML, "wb")
                                print >> fp, pipe.stdout.read()
                                fp.close()

                            if compressOutput:
                                # gzip the outputs
                                print "Compressing the output files..."
                                gzipFile(outputTxt)
                                if formatOutput:
                                    gzipFile(outputHTML)
                        else:
                            print
                            print "Test Launcher received SIGINT!"
                            print "Testing Instance Interrupted."

                    # end if browserStartCommand
                # end browserMode
            # end for font
        # end browser

    exit(0)
