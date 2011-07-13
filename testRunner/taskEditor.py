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

"""
@file taskEditor.py
@brief Script to send editing commands to the task handler.

This script can be called to send TASKEDITOR request to the task handler.
Currently, the following commands are accepted: REMOVE, RUN, RESTART and STOP.
It returns 1 if the command failed and 0 otherwise.

@var TASK_HANDLER_HOST
Host address of the task handler

@var TASK_HANDLER_PORT
Port of the task handler
"""

TASK_HANDLER_HOST = "localhost"
TASK_HANDLER_PORT = 4445

gRequest = ""

import ConfigParser
import SocketServer
import socket
import sys

def usage():
    """
    @fn usage()
    @brief Display command line usage for this script
    """
    print "Usage: python taskEditor.py command taskName [configFile\
[outputDirectory]]"
    print "where command is ADD, REMOVE, RUN, RESTART or STOP and taskName\
corresponds to an element in the task list. The optional parameters should only\
be specified with the ADD command and in that case configFile is mandatory."
    exit(1)

def sendConfigParameter(aParameter, aValue):
    global gRequest
    gRequest += (aParameter + "=" + aValue + "\n")

def sendConfigParameters(aConfigFile):
    configParser = ConfigParser.ConfigParser()
    configParser.optionxform = str # to preserve the case of parameter name
    configParser.readfp(open(aConfigFile))

    for section in ["framework", "platform", "testsuite"]:
        for item in configParser.items(section):
            sendConfigParameter(item[0], item[1])

if __name__ == "__main__":

    l = len(sys.argv)
    
    if (l < 2):
        usage()
    
    command = sys.argv[1]

    if (command not in ["ADD", "REMOVE", "RUN", "RESTART", "STOP"]):
        usage()

    if ((command != "ADD" and l != 3) or
        (command == "ADD" and (l <= 3 or l >= 6))):
        usage()

    taskName = sys.argv[2]

    if (command == "ADD"):
        configFile = sys.argv[3]

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((TASK_HANDLER_HOST, TASK_HANDLER_PORT))
    
    gRequest = "TASKEDITOR " + command + " " + taskName
    if (command == "ADD" and l == 5):
        gRequest += " " + sys.argv[4]
    gRequest += "\n"

    if (command == "ADD"):
        sendConfigParameters(configFile)
        gRequest += "TASKEDITOR ADD END\n"

    print gRequest
    sock.send(gRequest)

    response = sock.recv(128).strip()
    print response
    
    if ((command == "REMOVE" and
         response == ("'" + taskName + "' removed from the task list.")) or
        ((command == "RUN" or command == "RESTART") and
         response == ("Run signal sent to '" + taskName + "'.")) or
        (command == "STOP" and
         response == ("Stop signal sent to '" + taskName + "'."))):
        exitCode = 0
    else:
        exitCode = 1
    
    exit(exitCode)
