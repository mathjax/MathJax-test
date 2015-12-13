# -*- Mode: Python; tab-width: 2; indent-tabs-mode:nil; -*-
# vim: set ts=2 et sw=2 tw=80:
# ***** BEGIN LICENSE BLOCK *****
# Version: Apache License 2.0
#
# Copyright (c) 2011-2015 MathJax Consortium, Inc.
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
@file taskEditor.py
@brief Script to send editing commands to the task handler.

This script can be called to send TASKEDITOR request to the task handler.
Currently, the following commands are accepted: EDIT, REMOVE, RUN, RESTART and
STOP. It returns 1 if the command failed and 0 otherwise.
"""

from config import TASK_HANDLER_HOST, TASK_HANDLER_PORT

gRequest = ""

import SocketServer
import os
import socket
import sys

# TODO: CLONE, RENAME

def usage():
    """
    @fn usage()
    @brief Display command line usage for this script
    """
    print
    print("Usage:")
    print
    print("python taskEditor.py command taskName")
    print
    print("where command is REMOVE, RUN, RESTART, STOP or FORMAT and taskName")
    print("corresponds to an element in the task list, or")
    print
    print("python taskEditor.py EDIT taskName configFile [outputDirectory\
 [taskSchedule]]")
    print
    exit(1)

if __name__ == "__main__":

    l = len(sys.argv)
    
    if (l < 2):
        usage()
    
    command = sys.argv[1]

    if (command not in ["EDIT", "REMOVE", "RUN", "RESTART", "STOP", "FORMAT"]):
        usage()

    if ((command != "EDIT" and l != 3) or
        (command == "EDIT" and l < 4 and l > 6)):
        usage()

    taskName = sys.argv[2]

    if (command == "EDIT"):
        configFile = sys.argv[3]
        if (not os.path.exists(configFile)):
            print("File '" + configFile + "' not found.")
            exit(1)
        if l >= 5:
            outputDirectory = sys.argv[4]
        else:
            outputDirectory = "None"
        if l >= 6:
            taskSchedule = sys.argv[5]
        else:
            taskSchedule = "None"

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((TASK_HANDLER_HOST, TASK_HANDLER_PORT))
    
    gRequest = "TASKEDITOR " + command + " " + taskName
    if (command == "EDIT"):
        gRequest += " " + configFile + " " + outputDirectory
        gRequest += " " + taskSchedule
        gRequest += "\nTASKEDITOR EDIT END" 
    gRequest += "\n"

    print(gRequest)
    sock.send(gRequest)

    response = sock.recv(128).strip()
    print(response)
    
    if ((command == "EDIT" and
         response == ("'" + taskName + "' edited.")) or
        (command == "REMOVE" and
         response == ("'" + taskName + "' removed from the task list.")) or
        ((command == "RUN" or command == "RESTART") and
         response == ("Run signal sent to '" + taskName + "'.")) or
        (command == "STOP" and
         response == ("Stop signal sent to '" + taskName + "'.")) or
        (command == "FORMAT" and
         response == ("Output of '" + taskName + "' formatted!"))):
        exitCode = 0
    else:
        exitCode = 1
    
    exit(exitCode)
