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

import SocketServer
import subprocess
from signal import SIGINT
from datetime import datetime, timedelta

def boolToString(aBoolean):
    """
    @fn boolToString(aBoolean)
    @brief A simple function to convert a boolean to a string

    @return the string "true" or "false"
    """
    if aBoolean:
        return "true"
    return "false"

class requestHandler(SocketServer.StreamRequestHandler):

    def addParameter(self, aTask):
        
        request = self.rfile.readline().strip()
        print request

        if (request == "TASKEDITOR ADD END"):
            return False

        items = request.split("=")
        parameterName = items[0]
        parameterValue = items[1]
    
        if (parameterName == "transmitToTaskHandler" or
            parameterName == "fullScreenMode" or
            parameterName == "formatOutput" or
            parameterName == "compressOutput" or
            parameterName == "nativeMathML" or
            parameterName == "runSlowTests" or
            parameterName == "runSkipTests"):
            aTask.mParameters[parameterName] = (parameterValue == "true")
        elif (parameterName == "port" or
              parameterName == "timeOut"):
            aTask.mParameters[parameterName] = int(parameterValue)
        elif (parameterName == "host" or
              parameterName == "mathJaxPath" or
              parameterName == "mathJaxTestPath" or
              parameterName == "mathJaxTestPath" or
              parameterName == "operatingSystem" or
              parameterName == "browser" or
              parameterName == "browserMode" or
              parameterName == "browserPath" or
              parameterName == "font" or
              parameterName == "listOfTests" or
              parameterName == "startID"):
            aTask.mParameters[parameterName] = parameterValue
        else:
            print "Unknown parameter " + parameterName

        return True

    def addTask(self, aTaskName):
        global gServer

        if aTaskName not in gServer.mTasks.keys():
            t = task()
            t.mName = aTaskName
            t.mOutputDirectory = t.mOutputDirectory + aTaskName + "/"
            while (self.addParameter(t)):
                None
            gServer.mTasks[aTaskName] = t
            t.createConfigFile()
            t.mPopen = t.execute()
            return "Task '" + aTaskName + "' added\n"

        return "Failed to add task '" + aTaskName + "'\n"

    def removeTask(self, aTaskName):
        global gServer

        if aTaskName in gServer.mTasks.keys():
            t = gServer.mTasks[aTaskName]
            if (t.mPopen == None or
                t.mPopen.poll() != None):
                del gServer.mTasks[aTaskName]
                return "Task '" + aTaskName + "' removed\n"
            elif t.mPopen.poll() == None:
                t.mPopen.send_signal(SIGINT)
                return "SIGINT sent to '" + aTaskName + "'\n"

        return "Failed to add remove '" + aTaskName + "'\n"
        
    def handle(self):
        global gServer

        if (self.client_address[0] == "127.0.0.1"):
            # Only accept request from localhost
            request = self.rfile.readline().strip()
            print request
            items = request.split()
            client = items[0]
            if (client == "TASKVIEWER"):
                for k in gServer.mTasks.keys():
                    self.wfile.write(k + " " +
                                     gServer.mTasks[k].serialize() + "\n")
            elif (client == "TASK"):
                taskName = items[1]
                if taskName in gServer.mTasks.keys():
                    gServer.mTasks[taskName].mStatus = items[2]
                    gServer.mTasks[taskName].mProgress = items[3]
            elif (client == "TASKEDITOR"):
                command = items[1]
                taskName = items[2]
                if command == "ADD":
                    self.wfile.write(self.addTask(taskName))
                elif command == "REMOVE":
                    self.wfile.write(self.removeTask(taskName))
        else:
            print "Received request by unknown host " + self.client_address[0]

class task:

    def __init__(self):
        self.mName = "Unknown"
        self.mStatus = "Unknown"
        self.mProgress = "Unknown"
        self.mParameters = {}
        self.mParameters["host"] = "Unknown"
        self.mPopen = None
        self.mOutputDirectory = datetime.utcnow().strftime("%Y-%m-%d/")

    def host(self):
        return self.mParameters["host"]

    def serialize(self):
        return self.host() + " " + self.mStatus + " " + self.mProgress + " " + \
            self.mOutputDirectory

    def getConfigName(self):
        return "config/" + self.mName + ".cfg"

    def createConfigFile(self):
        fp = file(self.getConfigName(), "wb")

        fp.write("[framework]\n")        
        fp.write("taskName = " + self.mName + "\n")
        fp.write("transmitToTaskHandler = " +
                 boolToString(self.mParameters["transmitToTaskHandler"]) + "\n")
        fp.write("host = " +
                 self.mParameters["host"] + "\n")
        fp.write("port = " +
                 str(self.mParameters["port"]) + "\n")
        fp.write("mathJaxPath = " +
                 self.mParameters["mathJaxPath"] + "\n")
        fp.write("mathJaxTestPath = " +
                 self.mParameters["mathJaxTestPath"] + "\n")
        fp.write("timeOut = " +
                 str(self.mParameters["timeOut"]) + "\n")
        fp.write("fullScreenMode = " +
                 boolToString(self.mParameters["fullScreenMode"]) + "\n")
        fp.write("formatOutput = " +
                 boolToString(self.mParameters["formatOutput"]) + "\n")
        fp.write("compressOutput = " +
                 boolToString(self.mParameters["compressOutput"]) + "\n")
        fp.write("\n")

        fp.write("[platform]\n")
        fp.write("operatingSystem = " +
                 self.mParameters["operatingSystem"] + "\n")
        fp.write("browser = " +
                 self.mParameters["browser"] + "\n")
        fp.write("browserMode = " +
                 self.mParameters["browserMode"] + "\n")
        fp.write("browserPath = " +
                 self.mParameters["browserPath"] + "\n")
        fp.write("font = " +
                 self.mParameters["font"] + "\n")
        fp.write("nativeMathML = " +
                 boolToString(self.mParameters["nativeMathML"]) + "\n")
        fp.write("\n")

        fp.write("[testsuite]\n")
        fp.write("runSlowTests = " +
                 boolToString(self.mParameters["runSlowTests"]) + "\n")
        fp.write("runSkipTests = " +
                 boolToString(self.mParameters["runSkipTests"]) + "\n")
        fp.write("listOfTests = " +
                 self.mParameters["listOfTests"] + "\n")
        fp.write("startID = " +
                 self.mParameters["startID"] + "\n")

        fp.close()

    def execute(self):
        return subprocess.Popen(['python', 'runTestsuite.py',
                                 '-c', self.getConfigName(),
                                 '-o', self.mOutputDirectory])
   
class taskHandler:

    def __init__(self, aHost, aPort):
        self.mHost = aHost
        self.mPort = aPort
        self.mTasks = {}

    def start(self):
        server = SocketServer.TCPServer((self.mHost, self.mPort),
                                        requestHandler)
        server.serve_forever()

gServer = taskHandler("localhost", 4445)
 
if __name__ == "__main__":
    gServer.start()
