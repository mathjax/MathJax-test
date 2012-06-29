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
from config import TESTSUITE_TOPDIR_LIST
import re

GITHUB_URI='https://github.com/mathjax/MathJax/'
GITHUB_ISSUE_LIST="issues?&state=open"
TMP_FILE = "tmp.html"
REGEXP_TEST_LIST = ""

class issueClass:
    def __init__(self, aId):
        self.mId = aId
        self.mLabels = []
        self.mTests = []

    def addLabel(self, aLabel):
        self.mLabels.append(aLabel)

    def hasLabel(self, aLabel):
        return self.mLabels.count(aLabel) > 0

def downloadPage(aURL, aFile):
    print "Downloading " + aURL + "..."
    urlretrieve(aURL, aFile)
    print "done"

def appendIssues(aList, aNode):
    for issueNode in aNode:
        # remove the sharp prefix and convert to a number
        issue = issueClass(int(issueNode.get("id")[1:]))
        for labelNode in issueNode:
            issue.addLabel(labelNode.text)
        aList.append(issue)

def getTestListsFromComment(aList, aComment):
    words = re.findall(r"\S+", aComment)
    for w in words:
        if re.match(REGEXP_TEST_LIST, w):
            aList.append(w)

if __name__ == "__main__":
    # Load XSL stylesheets
    HTMLparser = etree.HTMLParser()
    issueListXSLT = etree.XSLT(etree.parse("githubIssueList.xsl"))
    issuePageXSLT = etree.XSLT(etree.parse("githubIssuePage.xsl"))

    # Download the first page of issue list and determine the number of pages
    downloadPage(GITHUB_URI + GITHUB_ISSUE_LIST + "&page=1", TMP_FILE)
    root = issueListXSLT(etree.parse(TMP_FILE, HTMLparser)).getroot()
    numberOfPages = root[0].get("numberOfPages")
    if (numberOfPages):
        numberOfPages = int(numberOfPages)
    else:
        numberOfPages = 1

    # Fill-in the issue list with the issue marked "In Testsuite"
    issueList = []
    appendIssues(issueList, root.find('issueList'))
    for i in range(2,numberOfPages+1):
        downloadPage(GITHUB_URI + GITHUB_ISSUE_LIST + "&page=" + str(i),
                     TMP_FILE)
        root = \
            issueListXSLT(etree.parse(TMP_FILE, HTMLparser)).getroot()
        appendIssues(issueList, root.find('issueList'))
    issueList.sort()

    # Initialize regexp to match "TESTSUITE_TOPDIR_LIST/*.html" that does not
    # end by "-ref.html".
    topdir = ""
    for i in range(len(TESTSUITE_TOPDIR_LIST)):
        if i > 0:
            topdir += "|"
        topdir += TESTSUITE_TOPDIR_LIST[i]
    REGEXP_TEST_LIST = re.compile("(?:" + topdir + ")/.*(?<!-ref)\.html")

    # Download each issue page and 
    for i in range(len(issueList)):
        issue = issueList[i]
        if (issue.hasLabel("Accepted") and
            issue.hasLabel("Ready for Release")):
            if (issue.hasLabel("QA - In Testsuite")):
                downloadPage(GITHUB_URI + "issues/" + str(issue.mId),
                             TMP_FILE)
                root = issuePageXSLT(etree.parse(TMP_FILE, HTMLparser)).\
                    getroot()
                for paragraph in root.iter("paragraph"):
                    getTestListsFromComment(issue.mTests, paragraph.text)

    # Generate the list of issues ready for release
    f1 = open("IssueList.txt", "w")
    f2 = open("AutomatedTestList.txt", "w")
    for i in range(len(issueList)):
        issue = issueList[i]
        if (issue.hasLabel("Accepted") and
            issue.hasLabel("Ready for Release")):
            print >>f1, "Issue " + str(issue.mId)
            print >>f1, "https://github.com/mathjax/MathJax/issues/" + \
                str(issue.mId) + "\n"
            if (issue.hasLabel("QA - Do Not Write Automated Test")):
                print "No Automated Test. To verify manually."
            elif (issue.hasLabel("QA - In Testsuite")):
                for test in issue.mTests:
                    print >>f1, test
                    print >>f2, test
            else:
                print >>f1, "Is it ready for Release?"
            print >>f1
    f2.close()
    f1.close()
