#!/usr/bin/env python
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

import legacy
from LiPlus import LiPlus
from LiPlusXML import LiPlusXML
from LiPlusText import LiPlusText

from argparse import ArgumentParser, RawDescriptionHelpFormatter

if __name__ == "__main__":

    parser = ArgumentParser(

        formatter_class = RawDescriptionHelpFormatter,

        description = "\
Li+ is an implementation of Lithium's algorithm, an automated testcase\n\
reduction tool by Jesse Ruderman. Rather than just reducing a file by\n\
removing characters or lines, this version can handle document at an\n\
abstract level and remove data structure like XML nodes or grammar tokens.\n\
\n\
Example: \n\
\n\
./lithium.py crashes 120 ~/tracemonkey/js/src/debug/js -j a.js\n\
     Lithium will reduce a.js subject to the condition that the following\n\
     crashes in 120 seconds:\n\
     ~/tracemonkey/js/src/debug/js -j a.js",

        epilog="\
Condition scripts\n\
\n\
  interactive\n\
    Let the user determine whether the testcase is interesting\n\
  mathjax [MathjaxURI [browser [font [outputjax [timeout]]]]] errorFragment\n\
    Open the testcase using MathJax test framework. The testcase is\n\
    interesting if a Javascript error containing errorFragment is found.\n\
    \n\
\n\
Text mode\n\
\n\
This mode is used to reduce general text documents, viewed as a sequence of\n\
lines. There is one --init option possible:\n\
\n\
  char: Don't treat lines as atomic units; treat the file as a sequence\n\
        of characters rather than a sequence of lines.\n\
\n\
In line mode, the --subset option can be a list of two delimiters of the\n\
portion to reduce e.g. --subset DDBEGIN,DDEND. You can also just use\n\
--subset= as a shorthand for --subset DDBEGIN,DDEND. Then Lithium will reduce\n\
the portion starting from the first line containing the begin delimiter and\n\
ending to the next line containing the end delimiter.\n\
\n\
XML and HTML modes\n\
\n\
These modes are used to reduce XML or HTML documents, by relying on their DOM\n\
structures. Use --subset=[id] or --subset=[tagName] to restrict the reduction\n\
an element. The --init options are the following:\n\
\n\
  depthBrowing: browse the tree in depth rather than in breadth.\n\
  elOnly: only remove elements, not attributes.\n\
  attrOnly: only remove attributes, not elements.")

    parser.add_argument("--subset", help="This allows to identify a subset of \
the document to which the reduction algorithm should be restricted.",
                        default=None)

    parser.add_argument("--init", action="append", default=[],
                        help="Indicate how the set of tokens is initialized.")

    parser.add_argument("--mode", help="Mode used to reduce the file. \
The following modes are available: XML, HTML, text. If this option is not \
specified then it will be determined from the extension of the input file. If \
the extension is not recognized, the text mode is used as a default.",
                        default=None)

    parser.add_argument("condition", help="Condition script in Python, used to \
determine whether the file is still interesting. See a list of some predefined \
scripts below.")

    parser.add_argument('conditionArgs', nargs="*", help="Arguments of the \
condition script.")

    parser.add_argument("input", help="Input file to reduce.")

    args = parser.parse_args()

    if args.mode is None:
        # Try to guess the mode from the file extension
        ext = args.input[args.input.rfind(".")+1:]
        if ext in ["xml", "mml", "svg", "xhtml"]:
            args.mode = "XML"
        elif ext == "html":
            args.mode = "HTML"
        else:
            args.mode = "text"

    args.conditionArgs.append(args.mode)
    args.conditionArgs.append(args.input)

    # Load the condition script module and its arguments
    conditionScript = legacy.importRelativeOrAbsolute(args.condition)
    if hasattr(conditionScript, "init"):
        conditionScript.init(args.conditionArgs)

    # Create the testcase according to the selected mode
    if args.mode == "XML" or args.mode == "HTML":
        testcase = LiPlusXML(args.input,
                             args.mode == "XML",
                             args.subset,
                             "depthBrowing" in args.init,
                             "elOnly" in args.init,
                             "attrOnly" in args.init)
    else: # args.mode == "text"
        testcase = LiPlusText(args.input, args.subset, "char" in args.init)

    # Finally create a Lithium instance to work on that testcase and apply the
    # algorithm!
    lithium = LiPlus(testcase)
    isMinimal = (len(lithium.mElements) <= 1)               

    # the parsing/serializing of the initial testcase may change it a bit, so
    # output it now.
    testcase.outputFile() 
    if not conditionScript.interesting(args.conditionArgs, None):
        print "The initial testcase is not interesting!"
        if hasattr(conditionScript, "finalize"):
            conditionScript.finalize(args.conditionArgs)
        exit(0)

    while not isMinimal:

        print ("size of Testcase: %d ; Chunck size: %d" %
               (len(lithium.mElements), lithium.mChunkSize))

        print "Trying to reduce..."
        lithium.tryToReduce()
        testcase.outputFile()

        isMinimal = lithium.\
            provideResult(conditionScript.\
                              interesting(args.conditionArgs, None))

    if hasattr(conditionScript, "finalize"):
        conditionScript.finalize(args.conditionArgs)

    testcase.outputFile()
    print "Minimal testcase obtained"
