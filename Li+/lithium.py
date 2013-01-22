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

from LiPlus import LiPlus
from LiPlusXML import LiPlusXML

import argparse
import legacy

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Li^+ is an implementation of Lithium's algorithm (an automated testcase reduction tool by Jesse Ruderman) for abstract data structures.")
    parser.add_argument('condition', help='Condition script')
    parser.add_argument("input", help="Input file to reduce")
    args = parser.parse_args()

    conditionScript = legacy.importRelativeOrAbsolute(args.condition)

    testcase = LiPlusXML(args.input, True)
    lithium = LiPlus(testcase)

    isMinimal = (len(lithium.mElements) <= 1)
    
    while not isMinimal:

        print ("size of Testcase: %d ; Chunck size: %d" %
               (len(lithium.mElements), lithium.mChunkSize))

        print "Trying to reduce..."
        lithium.tryToReduce()
        testcase.outputFile()

        isMinimal = lithium.provideResult(conditionScript.interesting())

    testcase.outputFile()
    print "Minimal testcase obtained"
