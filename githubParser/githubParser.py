# -*- Mode: Python; tab-width: 2; indent-tabs-mode:nil; -*-
# vim: set ts=2 et sw=2 tw=80:
# ***** BEGIN LICENSE BLOCK *****
# Version: Apache License 2.0
#
# Copyright (c) 2012 Design Science, Inc.
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

"""
@file githubParser.py
The file for the @ref githubParser module.

@package githubParser
This module implements allow to parse github comments
"""

from lxml import etree
from urllib import urlretrieve
from copy import deepcopy

GITHUB_URI='https://github.com/mathjax/MathJax/'
GITHUB_ISSUE_LIST="issues?labels=Accepted&state=open"
TMP_FILE = "tmp.html"

def downloadPage(aURL, aFile):
    print "Downloading " + aURL + "..."
    urlretrieve(aURL, aFile)
    print "done"

def isInTestSuite(aNode):

    for child in aNode:
        if child.text == "QA - In Testsuite":
            return True

    return False

def appendElements(aList, aNode):
    for child in aNode:
        if isInTestSuite(child):
            # remove the sharp prefix and convert to a number
            issueId = int(child.get("id")[1:])
            aList.append(issueId)

if __name__ == "__main__":
    HTMLparser = etree.HTMLParser()
    issueListXSLT = etree.XSLT(etree.parse("githubIssueList.xsl"))
    issuePageXSLT = etree.XSLT(etree.parse("githubIssuePage.xsl"))

    downloadPage(GITHUB_URI + GITHUB_ISSUE_LIST + "&page=1", TMP_FILE)
    root = issueListXSLT(etree.parse(TMP_FILE, HTMLparser)).getroot()
    numberOfPages = int(root[0].get("numberOfPages"))

    issueList = []
    appendElements(issueList, root[1])

    for i in range(2,numberOfPages+1):
        downloadPage(GITHUB_URI + GITHUB_ISSUE_LIST + "&page=" + str(i),
                     TMP_FILE)
        root = \
            issueListXSLT(etree.parse(TMP_FILE, HTMLparser)).getroot()
        appendElements(issueList, root[1])

    issueList.sort()

    for issueId in issueList:
        downloadPage(GITHUB_URI + "issues/" + str(issueId),
                     TMP_FILE)
        root = issuePageXSLT(etree.parse(TMP_FILE, HTMLparser)).getroot()
        print etree.tostring(root)
