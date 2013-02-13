# -*- Mode: Python; tab-width: 2; indent-tabs-mode:nil; -*-
# vim: set ts=2 et sw=2 tw=80:
#
# Copyright (c) 2013 Design Science, Inc.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import sys
sys.path.append('../testRunner/')

import seleniumMathJax
from config import SELENIUM_SERVER_PORT, DEFAULT_MATHJAX_PATH
from config import DEFAULT_TIMEOUT, MATHJAX_TEST_LOCAL_URI
from config import OS_LIST, BROWSER_LIST, FONT_LIST, OUTPUT_JAX_LIST

from os import remove as removeFile
from lxml import etree

NS_XHTML = "http://www.w3.org/1999/xhtml"
NS_SVG = "http://www.w3.org/2000/svg"
NS_MATHML = "http://www.w3.org/1998/Math/MathML"

def init(args):
    global gSelenium
    global gOutputFile
    global gTestsuiteHeaderXSLT
    global gErrorFragment
    global gXHTMLContainerXSLT

    testFile = args[-1]
    mode = args[-2]
    if mode == "XML":
        gOutputFile = "Li+.xhtml"
        doc = etree.parse(testFile)
        ns = etree.QName(doc.getroot()).namespace
        if ns == NS_MATHML or ns == NS_SVG:
            gXHTMLContainerXSLT = etree.XSLT(etree.parse("xhtmlContainer.xsl"))
        elif ns == NS_XHTML:
            gXHTMLContainerXSLT = None
        else:
            raise BaseException("Unknown namespace")
    elif mode == "HTML":
        # LiPlusXML has converted the document into XHTML
        gOutputFile = "Li+.xhtml"
        gXHTMLContainerXSLT = None
    else:
        raise BaseException("Unknown document format")

    gErrorFragment = args[-3]
    l = len(args) - 3 

    if l > 0:
        mathjaxPath = args[0]
    else:
        mathjaxPath = DEFAULT_MATHJAX_PATH

    operatingSystem = OS_LIST[0]
    if l > 1:
        browser = args[1]
    else:
        browser = BROWSER_LIST[0]
    if l > 2:
        font = args[2]
    else:
        font = FONT_LIST[0]
    if l > 3:
        outputJax = args[3]
    else:
        outputJax = OUTPUT_JAX_LIST[0]
    if l > 4:
        timeOut = args[4]
    else:
        timeOut = DEFAULT_TIMEOUT * 1000

    gSelenium = seleniumMathJax.seleniumMathJax(True,
                                                False,
                                                "localhost",
                                                SELENIUM_SERVER_PORT,
                                                mathjaxPath,
                                                MATHJAX_TEST_LOCAL_URI +
                                                "testsuite/",
                                                operatingSystem,
                                                browser,
                                                "default",
                                                "default",
                                                "default",
                                                font,
                                                outputJax,
                                                timeOut,
                                                False)
    gSelenium.start()
    gSelenium.pre()
    gTestsuiteHeaderXSLT = etree.XSLT(etree.parse("testsuiteHeader.xsl"))

def interesting(args, tempPrefix):
    global gSelenium
    global gOutputFile
    global gTestsuiteHeaderXSLT
    global gXHTMLContainerXSLT
    global gErrorFragment

    testFile = args[-1]

    doc = etree.parse(testFile)
    if gXHTMLContainerXSLT is not None:
        doc = gXHTMLContainerXSLT(doc)

    doc = gTestsuiteHeaderXSLT(doc)

    outputFile = open(("../testsuite/%s" % gOutputFile), "w")
    outputFile.write(etree.tostring(doc,
                                    method="xml",
                                    xml_declaration = True,
                                    pretty_print = True,
                                    encoding = "UTF-8"))
    outputFile.close()

    try:
        # execute the test
        gSelenium.open(gOutputFile)
        return False
    except seleniumMathJax.ReftestError as data:
        errorMessage = str(data)
        print "seleniumMathJax: %s" % errorMessage
        if errorMessage.find(gErrorFragment) >= 0:
            return True
        return False

def finalize(args):
    global gSelenium

    gSelenium.post()
    gSelenium.stop()
    # removeFile(("../testsuite/%s" % gOutputFile))
