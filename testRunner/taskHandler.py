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

import socket
import SocketServer
import subprocess
from signal import SIGINT, SIGCHLD
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

    def getTaskList(self):
        if (len(gServer.mTasks) == 0):
            return "TASK LIST EMPTY\n"

        taskList = "TASK LIST NONEMPTY\n"
        for k in gServer.mTasks.keys():
            taskList += k + " " + gServer.mTasks[k].serialize() + "\n"
        return taskList

    def addParameter(self, aTask):
        
        request = self.rfile.readline().strip()
        print request

        if (request == "TASKEDITOR ADD END"):
            return False

        items = request.split("=")
        parameterName = items[0]
        parameterValue = items[1]
    
        if (parameterName == "fullScreenMode" or
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

    def addTask(self, aTaskName, aOutputDirectory):
        global gServer

        if aTaskName in gServer.mTasks.keys():
            return "'" + aTaskName + "' is already in the task list!" + "'\n"

        t = task()
        t.mName = aTaskName
        t.mOutputDirectory = t.mOutputDirectory + aOutputDirectory + "/"

        # read the configuration parameters of the task
        while (self.addParameter(t)): None

        gServer.mTasks[aTaskName] = t
        return "'" + aTaskName + "' added to the task list.\n"

    def removeTask(self, aTaskName):
        global gServer

        if aTaskName not in gServer.mTasks.keys():
            return "'" + aTaskName + "' was not found in the task list!"

        t = gServer.mTasks[aTaskName]
        if (not t.isRunning()):
            del gServer.mTasks[aTaskName]
            return "'" + aTaskName + "' removed from the task list.\n"
        
        return "'" + aTaskName + "' is running and can not be removed!\n"

    def runTask(self, aTaskName, aRestart = False):
        global gServer

        if aTaskName not in gServer.mTasks.keys():
            return "'" + aTaskName + "' was not found in the task list!"

        t = gServer.mTasks[aTaskName]

        if (t.isRunning()):
            return "'" + aTaskName + "' is already running!\n"

        h = t.host()
        if (h in gServer.mMachines.keys()):
            return "'" + gServer.mMachines[h].mName + \
                "' is already running on this machine!\n"

        if (aRestart):
            t.mParameters["startID"] = ""

        t.generateConfigFile()
        t.mPopen = t.execute()
        gServer.mPID[str(t.mPopen.pid)] = t
        gServer.mMachines[t.host()] = t
        return "Run signal sent to '" + aTaskName + "'.\n"

    def stopTask(self, aTaskName):
        global gServer

        if aTaskName not in gServer.mTasks.keys():
            return "'" + aTaskName + "' was not found in the task list!"

        t = gServer.mTasks[aTaskName]

        if (t.isRunning()):
            t.mPopen.send_signal(SIGINT)
            return "Stop signal sent to '" + aTaskName + "'.\n"

        return "'" + aTaskName + "' is not running!\n"

    def getTaskInfo(self, aTaskName):

        global gServer

        if aTaskName not in gServer.mTasks.keys():
            return "<p>No task '" + aTaskName + "' in the task list.</p>"

        return gServer.mTasks[aTaskName].serializeHTML();

    def handle(self):
        global gServer

        if (self.client_address[0] == "127.0.0.1"):
            # Only accept request from localhost
            request = self.rfile.readline().strip()
            print request
            items = request.split()
            client = items[0]
            if (client == "TASKVIEWER"):
                self.wfile.write(self.getTaskList())
            elif (client == "TASK"):
                taskName = items[1]
                if taskName in gServer.mTasks.keys():
                    t = gServer.mTasks[taskName]
                    t.mStatus = items[2]
                    if (t.mStatus == "Interrupted"):
                        t.mParameters["startID"] = items[3]
                    else:
                        t.mProgress = items[3]
            elif (client == "TASKDEATH"):
                death = items[1]
                pid = str(items[2])
                if (pid in gServer.mPID.keys()):
                    t = gServer.mPID[pid]
                    del gServer.mPID[pid]
                    del gServer.mMachines[t.host()]
                    if (death == "UNEXPECTED"):
                        t.mStatus = "Killed"


            elif (client == "TASKEDITOR"):
                command = items[1]
                taskName = items[2]
                if command == "ADD":
                    outputDirectory = items[3]
                    self.wfile.write(self.addTask(taskName, outputDirectory))
                elif command == "REMOVE":
                    self.wfile.write(self.removeTask(taskName))
                elif command == "RUN":
                    self.wfile.write(self.runTask(taskName, False))
                elif command == "RESTART":
                    self.wfile.write(self.runTask(taskName, True))
                elif command == "STOP":
                    self.wfile.write(self.stopTask(taskName))
            elif (client == "TASKINFO"):
                taskName = items[1]
                self.wfile.write(self.getTaskInfo(taskName))
        else:
            print "Received request by unknown host " + self.client_address[0]

class task:

    def __init__(self):
        self.mName = "Unknown"
        self.mStatus = "Pending"
        self.mProgress = "-"
        self.mParameters = {}
        self.mParameters["host"] = "Unknown"
        self.mPopen = None
        self.mOutputDirectory = datetime.utcnow().strftime("%Y-%m-%d/")

    def isRunning(self):
        return (self.mPopen != None and self.mPopen.poll() == None)

    def host(self):
        return socket.gethostbyname(self.mParameters["host"])

    def serialize(self):
        s = ""
        s += self.mParameters["host"] + " "
        s += self.mStatus + " ";
        s += self.mProgress + " "
        if (self.mStatus == "Pending"):
            s += "-"
        else:
            s += self.mOutputDirectory

        return s

    def serializeHTML(self):
        s = ""
        s += "<p><table>"
        s += "<tr><th>Name</th><td>" + self.mName + "</td></tr>"

        for k in self.mParameters.keys():
            s += "<tr><th>" + k + "</th><td>" + \
                self.mParameters[k].__str__() + "</td></tr>"

        s += "</table></p>"

        return s

    def getConfigName(self):
        return "config/" + self.mName + ".cfg"

    def generateConfigFile(self):
        p = self.mParameters;

        fp = file(self.getConfigName(), "wb")

        fp.write("[framework]\n")        
        fp.write("taskName = " + self.mName + "\n")
        fp.write("host = " + p["host"] + "\n")
        fp.write("port = " + str(p["port"]) + "\n")
        fp.write("mathJaxPath = " + p["mathJaxPath"] + "\n")
        fp.write("mathJaxTestPath = " + p["mathJaxTestPath"] + "\n")
        fp.write("timeOut = " + str(p["timeOut"]) + "\n")
        fp.write("fullScreenMode = " + boolToString(p["fullScreenMode"]) + "\n")
        fp.write("formatOutput = " + boolToString(p["formatOutput"]) + "\n")
        fp.write("compressOutput = " + boolToString(p["compressOutput"]) + "\n")
        fp.write("\n")

        fp.write("[platform]\n")
        fp.write("operatingSystem = " + p["operatingSystem"] + "\n")
        fp.write("browser = " + p["browser"] + "\n")
        fp.write("browserMode = " + p["browserMode"] + "\n")
        fp.write("browserPath = " + p["browserPath"] + "\n")
        fp.write("font = " + p["font"] + "\n")
        fp.write("nativeMathML = " + boolToString(p["nativeMathML"]) + "\n")
        fp.write("\n")

        fp.write("[testsuite]\n")
        fp.write("runSlowTests = " + boolToString(p["runSlowTests"]) + "\n")
        fp.write("runSkipTests = " + boolToString(p["runSkipTests"]) + "\n")
        fp.write("listOfTests = " + p["listOfTests"] + "\n")
        fp.write("startID = " + p["startID"] + "\n")

        fp.close()

    def execute(self):
        return subprocess.Popen(['python', 'runTestsuite.py',
                                 '-c', self.getConfigName(),
                                 '-o', self.mOutputDirectory,
                                 '-t'])
   
class taskHandler:

    def __init__(self, aHost, aPort):
        self.mHost = aHost
        self.mPort = aPort
        self.mTasks = {}
        self.mMachines = {}
        self.mPID = {}

    def start(self):
        server = SocketServer.TCPServer((self.mHost, self.mPort),
                                        requestHandler)
        server.serve_forever()

gServer = taskHandler("localhost", 4445)
 
if __name__ == "__main__":
    gServer.start()
