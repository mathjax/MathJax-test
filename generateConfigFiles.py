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

import string
import subprocess
import sys
import ConfigParser

def parseStringArray(aValue):
    return [string.strip(obj) for ind,obj in enumerate(aValue.split())]

def declarePythonString(aStream, aName, aValue):
    print >>aStream, aName + " = '" + aValue + "'"

def declarePythonInteger(aStream, aName, aValue):
    print >>aStream, aName + " = " + str(aValue)

def declarePythonStringArray(aStream, aName, aValue):
    aStream.write(aName + " = [")
    if (len(aValue) > 0):
        aStream.write("'" + aValue[0] + "'")
        for i in range(1, len(aValue)):
            aStream.write(",'" + aValue[i] + "'")
    aStream.write("]\n")

def declarePythonIntegerArray(aStream, aName, aValue):
    aStream.write(aName + " = [")
    if (len(aValue) > 0):
        aStream.write(str(aValue[0]))
        for i in range(1, len(aValue)):
            aStream.write("," + str(aValue[i]))
    aStream.write("]\n")

def declarePhpString(aStream, aName, aValue):
    print >>aStream, "$" + aName + " = '" + aValue + "';"

def declarePhpInteger(aStream, aName, aValue):
    print >>aStream, "$" + aName + " = " + str(aValue) + ";"

def declarePhpStringArray(aStream, aName, aValue):
    aStream.write("$" + aName + " = array(")
    if (len(aValue) > 0):
        aStream.write("'" + aValue[0] + "'")
        for i in range(1, len(aValue)):
            aStream.write(",'" + aValue[i] + "'")
    aStream.write(");\n")

def declareJsString(aStream, aName, aValue):
    print >>aStream, "var " + aName + " = '" + aValue + "';"

def declareJsIntegerArray(aStream, aName, aValue):
    aStream.write("var " + aName + " = [")
    if (len(aValue) > 0):
        aStream.write(str(aValue[0]))
        for i in range(1, len(aValue)):
            aStream.write("," + str(aValue[i]))
    aStream.write("];\n")

def createLexExpression(aList):
    v = ""
    if (len(aList) > 0):
        v = v + aList[0]
        for i in range(1, len(aList)):
            v = v + "|" + aList[i]
    return v
    
# Parse the config file
configParser = ConfigParser.ConfigParser()
configParser.optionxform = str # to preserve the case of parameter name
configParser.readfp(open("custom.cfg.tmp"))
PYTHON = configParser.get("bin", "PYTHON")
PERL = configParser.get("bin", "PERL")
QA_USER_NAME = configParser.get("qa", "QA_USER_NAME")
QA_PASSWORD_FILE = configParser.get("qa", "QA_PASSWORD_FILE")
TASK_HANDLER_HOST = configParser.get("task_handler", "TASK_HANDLER_HOST")
TASK_HANDLER_PORT = configParser.getint("task_handler", "TASK_HANDLER_PORT")

DEFAULT_TASK_NAME = configParser.get("testing_instance", "DEFAULT_TASK_NAME")
HOST_LIST = parseStringArray(configParser.get("testing_instance",
                                              "HOST_LIST"))
HOST_LIST_OS_ = parseStringArray(configParser.get("testing_instance",
                                                 "HOST_LIST_OS"))
DEFAULT_SELENIUM_PORT = configParser.getint("testing_instance",
                                            "DEFAULT_SELENIUM_PORT")
DEFAULT_MATHJAX_PATH = configParser.get("testing_instance",
                                        "DEFAULT_MATHJAX_PATH")
DEFAULT_MATHJAX_TEST_PATH = configParser.get("testing_instance",
                                             "DEFAULT_MATHJAX_TEST_PATH")
DEFAULT_TIMEOUT = configParser.getint("testing_instance",
                                      "DEFAULT_TIMEOUT")

BROWSER_LIST = parseStringArray(configParser.get("testing_instance",
                                                 "BROWSER_LIST"))
OS_LIST = parseStringArray(configParser.get("testing_instance",
                                            "OS_LIST"))

BROWSER_VERSION_REGEXP = configParser.get("testing_instance",
                                             "BROWSER_VERSION_REGEXP")

BROWSER_MODE_LIST = parseStringArray(configParser.get("testing_instance",
                                                      "BROWSER_MODE_LIST"))
FONT_LIST = parseStringArray(configParser.get("testing_instance",
                                              "FONT_LIST"))
OUTPUT_JAX_LIST = parseStringArray(configParser.get("testing_instance",
                                                    "OUTPUT_JAX_LIST"))
CONDITION_PARSER = configParser.get("generated_files", "CONDITION_PARSER")
CONFIG_PY = configParser.get("generated_files", "CONFIG_PY")
CONFIG_PHP = configParser.get("generated_files", "CONFIG_PHP")
CONFIG_JS = configParser.get("generated_files", "CONFIG_JS")

WARNING_GENERATED_FILE = configParser.get("messages",
                                          "WARNING_GENERATED_FILE")
ERROR_CONNECTION_TASK_HANDLER = \
    configParser.get("messages", "ERROR_CONNECTION_TASK_HANDLER")

MATHJAX_TEST_URI = configParser.get("other", "MATHJAX_TEST_URI")
MONTH_LIST = parseStringArray(configParser.get("other", "MONTH_LIST"))
WEEKDAY_LIST = parseStringArray(configParser.get("other", "WEEKDAY_LIST"))
TESTSUITE_TOPDIR_LIST = \
    parseStringArray(configParser.get("other", "TESTSUITE_TOPDIR_LIST"))
TEMPLATE_CONFIG_LIST = \
    parseStringArray(configParser.get("other", "TEMPLATE_CONFIG_LIST"))

# convert HOST_LIST_OS_ to a list of indices
HOST_LIST_OS = []
for v in HOST_LIST_OS_:
    HOST_LIST_OS.append(OS_LIST.index(v))

# Create testRunner/conditionParser.py
f_in = open(CONDITION_PARSER + "-tpl", "r")
f_out = open(CONDITION_PARSER, "w")
print >>f_out, "# " + WARNING_GENERATED_FILE
content = f_in.read()
content = content.replace("OS_LIST", createLexExpression(OS_LIST))
content = content.replace("BROWSER_LIST", createLexExpression(BROWSER_LIST))
content = content.replace("BROWSER_VERSION_REGEXP", BROWSER_VERSION_REGEXP)
content = content.replace("BROWSER_MODE_LIST",
                          createLexExpression(BROWSER_MODE_LIST))
content = content.replace("FONT_LIST", createLexExpression(FONT_LIST))
content = content.replace("OUTPUT_JAX_LIST", createLexExpression(OUTPUT_JAX_LIST))
f_out.write(content)
f_out.close()
f_in.close()

# Create testRunner/config.py
f_out = open(CONFIG_PY, "w")
print >>f_out, "# " + WARNING_GENERATED_FILE

declarePythonString(f_out, "PYTHON", PYTHON)
declarePythonString(f_out, "PERL", PERL)
declarePythonString(f_out, "TASK_HANDLER_HOST", TASK_HANDLER_HOST)
declarePythonInteger(f_out, "TASK_HANDLER_PORT", TASK_HANDLER_PORT)

declarePythonStringArray(f_out, "HOST_LIST", HOST_LIST)
declarePythonStringArray(f_out, "OS_LIST", OS_LIST)
declarePythonIntegerArray(f_out, "HOST_LIST_OS", HOST_LIST_OS)
declarePythonInteger(f_out, "DEFAULT_SELENIUM_PORT", DEFAULT_SELENIUM_PORT)
declarePythonString(f_out, "DEFAULT_MATHJAX_PATH", DEFAULT_MATHJAX_PATH)
declarePythonString(f_out, "DEFAULT_MATHJAX_TEST_PATH",
                    DEFAULT_MATHJAX_TEST_PATH)
declarePythonInteger(f_out, "DEFAULT_TIMEOUT", DEFAULT_TIMEOUT)

declarePythonString(f_out, "MATHJAX_TEST_URI", MATHJAX_TEST_URI)
declarePythonStringArray(f_out, "MONTH_LIST", MONTH_LIST)
declarePythonStringArray(f_out, "WEEKDAY_LIST", WEEKDAY_LIST)
declarePythonStringArray(f_out, "OUTPUT_JAX_LIST", OUTPUT_JAX_LIST)

f_out.close()

# Create web/config.php
f_out = open(CONFIG_PHP, "w")
print >>f_out, "<?php"
print >>f_out, "/* " + WARNING_GENERATED_FILE + " */"

declarePhpString(f_out, "TASK_HANDLER_HOST", TASK_HANDLER_HOST)
declarePhpInteger(f_out, "TASK_HANDLER_PORT", TASK_HANDLER_PORT)

declarePhpString(f_out, "DEFAULT_TASK_NAME", DEFAULT_TASK_NAME)
declarePhpStringArray(f_out, "HOST_LIST", HOST_LIST)
declarePhpInteger(f_out, "DEFAULT_SELENIUM_PORT", DEFAULT_SELENIUM_PORT)
declarePhpString(f_out, "DEFAULT_MATHJAX_PATH", DEFAULT_MATHJAX_PATH)
declarePhpString(f_out, "DEFAULT_MATHJAX_TEST_PATH",
                 DEFAULT_MATHJAX_TEST_PATH)
declarePhpInteger(f_out, "DEFAULT_TIMEOUT", DEFAULT_TIMEOUT)

declarePhpStringArray(f_out, "BROWSER_LIST", BROWSER_LIST)
declarePhpStringArray(f_out, "OS_LIST", OS_LIST)
declarePhpStringArray(f_out, "BROWSER_MODE_LIST", BROWSER_MODE_LIST)
declarePhpStringArray(f_out, "FONT_LIST", FONT_LIST)
declarePhpStringArray(f_out, "OUTPUT_JAX_LIST", OUTPUT_JAX_LIST)

declarePhpString(f_out, "ERROR_CONNECTION_TASK_HANDLER",
                 ERROR_CONNECTION_TASK_HANDLER)

declarePhpStringArray(f_out, "MONTH_LIST", MONTH_LIST)
declarePhpStringArray(f_out, "WEEKDAY_LIST", WEEKDAY_LIST)
declarePhpStringArray(f_out, "TESTSUITE_TOPDIR_LIST", TESTSUITE_TOPDIR_LIST)
declarePhpStringArray(f_out, "TEMPLATE_CONFIG_LIST", TEMPLATE_CONFIG_LIST)

print >>f_out, "?>"
f_out.close()

# Create web/config.js
f_out = open(CONFIG_JS, "w")
print >>f_out, "/* " + WARNING_GENERATED_FILE + " */"
declareJsString(f_out, "MATHJAX_TEST_URI", MATHJAX_TEST_URI)
declareJsIntegerArray(f_out, "HOST_LIST_OS", HOST_LIST_OS)
f_out.close()
