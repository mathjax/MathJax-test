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
@file taskHandler.py
The file for the @ref taskHandler module.

@package taskHandler
This module implements a server handling a task list. It can communicate
with external programs such that Web server to receive instructions or provides
the current status of each task. It also runs and communicates task programs
(which are testing instance executing the runTestsuite.py script) so that it
knows the status and progress of each running task.

@var gServer
The server handling the task list.

@var TASK_HANDLER_HOST
Host address of the task handler

@var TASK_HANDLER_PORT
Port of the task handler
"""

TASK_HANDLER_HOST = "localhost"
TASK_HANDLER_PORT = 4445

import socket
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
    """
    @class taskHandler::requestHandler
    @brief A class inheriting from SocketServer.StreamRequestHandler and dealing
    with the requests received by the task handler.
    """

    def getTaskList(self):
        """
        @fn getTaskList(self)
        @brief return a string representing a task list

        If the task list is empty, one line

        "TASK LIST EMPTY"

        is returned. Otherwise, the returned string starts with the line

        "TASK LIST NONEMPTY"

        and continue with one line per task, each one of the form

        "Task Name	Host Status Progress outputDirectory"
        """
        if (len(gServer.mTasks) == 0):
            return "TASK LIST EMPTY\n"

        taskList = "TASK LIST NONEMPTY\n"
        for k in gServer.mTasks.keys():
            taskList += k + " " + gServer.mTasks[k].serialize() + "\n"
        return taskList

    def getTaskInfo(self, aTaskName):
        """
        @fn getTaskInfo(self, aTaskName)
        @brief Get an HTML representation of properties of a given task.
        @param aTaskName Name of the task from which to retrieve information.
        
        If the task is not in the list, this function returns a message
        indicating so. Otherwise, it calls the task::serializeHTML function.
        """

        global gServer

        if aTaskName not in gServer.mTasks.keys():
            return "<p>No task '" + aTaskName + "' in the task list.</p>"

        return gServer.mTasks[aTaskName].serializeHTML();

    def readExceptionMessage(self):
        """
        @fn readExceptionMessage(self)
        @brief read an exception message
        @return The exception message read from the socket

        This function reads line from the socket and concatenated them in a
        string until it reaches a "TASKDEATH END" line.
        """

        s = ""

        while (True):
            request = self.rfile.readline().strip()
            if (request == "TASKDEATH END"):
                break
            s += request + "\n"

        return s

    def addParameter(self, aTask):
        """
        @fn addParameter(self, aTask)
        @brief read one parameter from the socket and store it in the task
        @param aTask task to which we want to add a parameter
        @return Whether we should continue to read more parameters.
        @see [ADD-REFERENCE-TO-CONFIG-PARAMETERS-IN-MATHJAX-TEST-DOC]

        This function reads one line from the socket. If this line is

        "TASKEDITOR ADD END"

        then the function return False to indicate that no more parameters
        should be read. Otherwise, the function expects to read a line

        "parameterName = parameterValue"

        where the pair (parameterName, parameterValue) is a testing instance
        configuration option. If the option is known, then this parameter is
        added to the task::mParameters table of aTask. Otherwise it is ignored.
        In any case, the function return True.
        """
        request = self.rfile.readline().strip()

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
        """
        @fn addTask(self, aTaskName, aOutputDirectory)
        @brief add a new item in the task list
        @param aTaskName name of the task
        @param aOutputDirectory directory to store results of the task
        @return a message indicating whether the task has been successfully
        added or not.

        If the task with the same name is not already in the task list,
        this function creates a new task with the specified name, a status
        "Pending". The output directory is of the form DATE/aOutputDirectory.
        Task configuration are read from the socket and stored in the
        task::mParameters table of the task.
        """

        global gServer

        if aTaskName in gServer.mTasks.keys():
            return "'" + aTaskName + "' is already in the task list!" + "'\n"

        # create a new task
        t = task(aTaskName, "Pending",
                 datetime.utcnow().strftime("%Y-%m-%d/") +
                 aOutputDirectory + "/")

        # read the configuration parameters of the task
        while (self.addParameter(t)): None

        # add the task to the list
        gServer.mTasks[aTaskName] = t
        return "'" + aTaskName + "' added to the task list.\n"

    def removeTask(self, aTaskName):
        """
        @fn removeTask(self, aTaskName)
        @brief remove an item from the task list
        @param aTaskName name of the task to remove
        @return a message indicating whether the task has been successfully
        removed or not.

        The task is removed only if the task is in the list and not running.
        """
        global gServer

        if aTaskName not in gServer.mTasks.keys():
            return "'" + aTaskName + "' was not found in the task list!"

        t = gServer.mTasks[aTaskName]
        if (not t.isRunning()):
            # remove the task from the list
            del gServer.mTasks[aTaskName]
            return "'" + aTaskName + "' removed from the task list.\n"
        
        return "'" + aTaskName + "' is running and can not be removed!\n"

    def runTask(self, aTaskName, aRestart = False):
        """
        @fn runTask(self, aTaskName, aRestart = False)
        @brief launch the execution of a task
        @param aTaskName name of the task to run
        @param aRestart Whether we should run the task from the beginning or
        continue it if it was interrupted
        @return a message indicating whether the task has been successfully
        launched or not.

        The task can be run if it is in the task list, not running and no other
        task is already running on the given host. If aRestart is true, the
        parameter "startID" is reset, so that the testing instance will start
        from the beginning.
        
        If the task can be run, this function calls task::generateConfigFile(),
        task::execute() and store the task in the gServer's hash tables
        taskHandler::mRunningTaskFromPID and taskHandler::mRunningTaskFromHost.
        """

        global gServer

        if aTaskName not in gServer.mTasks.keys():
            return "'" + aTaskName + "' was not found in the task list!"

        t = gServer.mTasks[aTaskName]

        if (t.isRunning()):
            return "'" + aTaskName + "' is already running!\n"

        h = t.host()
        if (h in gServer.mRunningTaskFromHost.keys()):
            return "'" + gServer.mRunningTaskFromHost[h].mName + \
                "' is already running on this machine!\n"

        if (aRestart):
            t.mParameters["startID"] = ""

        t.generateConfigFile()
        t.mExceptionMessage = None
        t.mPopen = t.execute()
        gServer.mRunningTaskFromPID[str(t.mPopen.pid)] = t
        gServer.mRunningTaskFromHost[h] = t
        return "Run signal sent to '" + aTaskName + "'.\n"

    def stopTask(self, aTaskName):
        """
        @fn stopTask(self, aTaskName)
        @brief stop the execution of a task
        @return a message indicating whether the task has been successfully
        stopped or not.

        The task can be stopped if it is in the task list and running. In that
        case a SIGINT signal is sent to the corresponding testing instance
        process.
        """

        global gServer

        if aTaskName not in gServer.mTasks.keys():
            return "'" + aTaskName + "' was not found in the task list!"

        t = gServer.mTasks[aTaskName]

        if (t.isRunning()):
            t.mPopen.send_signal(SIGINT)
            return "Stop signal sent to '" + aTaskName + "'.\n"

        return "'" + aTaskName + "' is not running!\n"

    def handle(self):
        """
        @fn handle(self)
        @brief Handle a client request

        For security reasons, this function only accept request from clients on
        localhost (127.0.0.1). It reads a line from the socket and sends a
        response:

        - If the request is "TASKVIEWER", it sends the result of
        @ref getTaskList

        - If the request is "TASKINFO taskName", it send the result of
        @ref getTaskInfo for the corresponding task.

        - If the request is "TASK taskName status progress", it updates the
        members of the given task accordingly. If status is "Interrupted",
        progress is actually the startID to use to recover the testing instance.
        In particular, it can be ommited if the task was interrupted before
        any tests have been run (i.e. startID should be an empty string).

        - If the request is "TASKDEATH death pid" where death is either
          "EXPECTED" or "UNEXPECTED" and pid the PID of the process of a running
          task, then that task is removed from the hash tables of running tasks.
          If the death is unexpected, the @ref task::mStatus is set to
          "Killed" and @ref task::mExceptionMessage is read using
          @ref readExceptionMessage.

        - If the request starts by "TASKEDITOR command taskName", then it
        performs one of the following command and returns the information
        message:
            - "TASKEDITOR ADD taskName outputDirectory": @ref addTask
            - "TASKEDITOR REMOVE taskName": @ref removeTask
            - "TASKEDITOR RUN taskName": @ref runTask with aRestart = False
            - "TASKEDITOR RESTART taskName": @ref runTask with aRestart = True
            - "TASKEDITOR STOP taskName": @ref stopTask

        - other requests are ignored.
        """

        global gServer

        if (self.client_address[0] == "127.0.0.1"):
            # Only accept request from localhost
            request = self.rfile.readline().strip()
            print request
            items = request.split()
            client = items[0]
            if (client == "TASKVIEWER"):
                self.wfile.write(self.getTaskList())
            elif (client == "TASKINFO"):
                taskName = items[1]
                self.wfile.write(self.getTaskInfo(taskName))
            elif (client == "TASK"):
                taskName = items[1]
                if taskName in gServer.mTasks.keys():
                    t = gServer.mTasks[taskName]
                    if (items[2] in
                        ["Running", "Complete", "Interrupted"]):
                        t.mStatus = items[2]
                    if (t.mStatus == "Interrupted"):
                        if (len(items) >= 3):
                            t.mParameters["startID"] = items[3]
                        else:
                            t.mParameters["startID"] = ""
                    else:
                        t.mProgress = items[3]
            elif (client == "TASKDEATH"):
                death = items[1]
                if (death == "EXPECTED" or death == "UNEXPECTED"):
                    pid = items[2]
                    if (pid in gServer.mRunningTaskFromPID.keys()):
                        t = gServer.mRunningTaskFromPID[pid]
                        del gServer.mRunningTaskFromPID[pid]
                        h = t.host()
                        if h in gServer.mRunningTaskFromHost.keys():
                            del gServer.mRunningTaskFromHost[h]
                            if (death == "UNEXPECTED"):
                                t.mStatus = "Killed"
                                t.mExceptionMessage = \
                                    self.readExceptionMessage()
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
        else:
            print "Received request by unknown host " + self.client_address[0]

class task:
    """
    @class taskHandler::task
    @brief A class representing items in the task list.
    """

    def __init__(self, aName, aStatus, aOutputDirectory):
        """
        @fn __init__(self, aName, aStatus, aOutputDirectory)

        @param aName            Value to assign to @ref mName
        @param aStatus          Value to assign to @ref mStatus
        @param aOutputDirectory Value to assign to @ref mOutputDirectory

        @property mName
        Name of the task

        @property mStatus
        Status of the task:
          - Process not executed yet: "Pending", (TODO: "Scheduled"?)
          - Process executing: "Running"
          - Process executed: "Complete", "Interrupted", "Killed"

        @property mOutputDirectory
        Directory where the results of the task are stored.

        @property mProgress
        Either "-" or a fraction "numberOfTestsExecuted/totalNumberOfTests".

        @property mParameters
        Hash table of task parameters, corresponding to those in the config
        file.
        @see [ADD-REFERENCE-TO-CONFIG-PARAMETERS-IN-MATHJAX-TEST-DOC]

        @property mPopen
        The result of the subprocess.Popen or None if the task was never
        executed.

        @property mExceptionMessage
        If the task has the "Killed" status, the Exception message raised by
        the task process before dying or "No exception raised" if the death was
        not reported. Otherwise, it is None.

        This function initializes @ref mName, @ref mStatus and
        @ref mOutputDirectory with the given arguments ; @ref mProgress to "-",
        @ref mPopen and @ref mExceptionMessage to None ; @ref mParameters to an
        a hash table with a single "host" parameter with value None.
        """
        self.mName = aName
        self.mStatus = aStatus
        self.mProgress = "-"
        self.mParameters = {}
        self.mParameters["host"] = None
        self.mPopen = None
        self.mOutputDirectory = aOutputDirectory
        self.mExceptionMessage = None

    def host(self):
        """
        @fn host(self)
        @brief get the IP address of a machine
        @return the host corresponding to @ref mParameters["host"] or "Unknown"
        this parameter is None.
        """
        h = self.mParameters["host"]
        if h != None:
            return socket.gethostbyname(h)
        else:
            return "Unknown"

    def isRunning(self):
        """
        @fn isRunning(self)
        @brief Indicate whether a task is running according to the value of
        @ref mPopen.
        @return Whether the task is running.
        """
        return (self.mPopen != None and self.mPopen.poll() == None)

    def verifyStatus(self):
        """
        @fn verifyStatus(self)
        @brief Verify the consistency of the task @ref mStatus

        This function is intended to be used before providing the task status
        to the user. It verify that this status is consistent with the one
        provided by @ref isRunning.

        If the process is not running but @ref mStatus says it is, then we set
        the status to "Killed" and remove it from the task from the hash tables
        of running process. This may happen if the runTestsuite process died
        unexpectedly, without raising a BaseException.

        If the process is running but the @ref mStatus says "Pending", set the
        status to "Running". This may happen if the runTestsuite did not send
        the "Running" status yet.
        """
        running = self.isRunning()

        if ((not running) and self.mStatus == "Running"):
            self.mStatus = "Killed"
            self.mExceptionMessage = "No exception raised"
            h = self.host()
            if h in gServer.mRunningTaskFromHost.keys():
                del gServer.mRunningTaskFromHost[h]
            pid = str(self.mPopen.pid)
            if pid in gServer.mRunningTaskFromPID.keys():
                del gServer.mRunningTaskFromPID[pid]
        elif (running and self.mStatus == "Pending"):
            self.mStatus = "Running"

    def serialize(self):
        """
        @fn serialize(self)
        @brief Provide a short serialization of the task
        @return "host status progress outputDirectory"

        host, status, progress and outputDirectory correspond to the data
        members of the task.
        """
        self.verifyStatus()

        s = ""
        s += self.mParameters["host"] + " "
        s += self.mStatus + " ";
        s += self.mProgress + " "
        s += self.mOutputDirectory

        return s

    def serializeMember(self, aName, aValue):
        """
        @fn serializeMember(self, aName, aValue)
        @brief serialize a pair (aName, aValue) as an HTML row
        @return an HTML row tr(th(aName), td(aValue)) in text format
        """
        return "<tr><th>" + aName + "</th><td>" + aValue + "</td></tr>"

    def serializeParameter(self, aKey):
        """
        @fn serializeParameter(self, aKey)
        @brief serialize a (aKey, @ref mParameters[aKey]) as an HTML row
        @return an HTML row tr(th(aKey), td(aValue)) in text format
        """
        return self.serializeMember(aKey, self.mParameters[aKey].__str__())

    def serializeHTML(self):
        """
        @fn serializeHTML(self)
        @brief Provide an HTML serialization of the task.
        @return string representation of HTML tables with the task info.
        """
        self.verifyStatus()

        s = ""

        s += "<h2>Task</h2>"
        s += "<p><table>"
        s += self.serializeMember("Name", self.mName)
        s += self.serializeMember("Status", self.mStatus)
        s += self.serializeMember("Progress", self.mProgress)

        s += "<tr><th>Result directory</th><td>"

        if (self.mStatus == "Pending"):
            s += self.mOutputDirectory
        else:
            s += "<a href=\"results/" + self.mOutputDirectory + "\">"
            s += self.mOutputDirectory + "</a></td></tr>"

        if (self.mExceptionMessage != None):
            s += "<tr style=\"color: red;\">"
            s += "<th id='exceptionError'>Exception Error</th>"
            s += "<td>" + self.mExceptionMessage + "</td></tr>"

        s += "</table></p>"


        s += "<h2>Framework Configuration</h2>"
        s += "<p><table>"
        s += self.serializeParameter("host")
        s += self.serializeParameter("port")
        s += self.serializeParameter("mathJaxPath")
        s += self.serializeParameter("mathJaxTestPath")
        s += self.serializeParameter("timeOut")
        s += self.serializeParameter("fullScreenMode")
        s += self.serializeParameter("formatOutput")
        s += self.serializeParameter("compressOutput")
        s += "</table></p>"
        
        s += "<h2>Platform Configuration</h2>"
        s += "<p><table>"
        s += self.serializeParameter("operatingSystem")
        s += self.serializeParameter("browser")
        s += self.serializeParameter("browserMode")
        s += self.serializeParameter("browserPath")
        s += self.serializeParameter("font")
        s += self.serializeParameter("nativeMathML")
        s += "</table></p>"

        s += "<h2>Testsuite Configuration</h2>"
        s += "<p><table>"
        s += self.serializeParameter("runSlowTests")
        s += self.serializeParameter("runSkipTests")
        s += self.serializeParameter("listOfTests")
        s += self.serializeParameter("startID")
        s += "</table></p>"

        return s

    def getConfigPath(self):
        """
        @fn getConfigPath(self)
        @brief Get a configuration path
        @return path to the configuration file for this task

        The path is the concatenation of "config/", the name of the task
        and the extension ".cfg".
        """
        return "config/" + self.mName + ".cfg"

    def generateConfigFile(self):
        """
        @fn generateConfigFile(self)
        @brief generate a configuration file for this task

        This function creates a configuration file at the @ref getConfigPath
        path, with respect to the data members of the task.
        """
        p = self.mParameters;

        fp = file(self.getConfigPath(), "w")

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
        """
        @fn execute(self)
        @brief Execute a new runTestsuite.py subprocess
        @return Python's subprocess.Popen instance representing the subprocess

        Call "python runTestsuite.py -c configName -o outputDirectory -t"
        where configName is the value returned by @ref getConfigPath and
        outputDirectory is @ref mOutputDirectory.
        """
        return subprocess.Popen(['python', 'runTestsuite.py',
                                 '-c', self.getConfigPath(),
                                 '-o', self.mOutputDirectory,
                                 '-t'])
   
class taskHandler:
    """
    @class taskHandler::taskHandler
    @brief A class representing a server handling a task list.
    """

    def __init__(self, aHost, aPort):
        """
        @fn __init__(self, aHost, aPort)

        @param aHost Value to assign to mHost
        @param aPort Value to assign to mPort

        @property mHost
        Host on which the task handler is running.
        
        @property mPort
        Port on which the task handler is running.
        
        @property mTasks
        A hash table of tasks in the task handler, indexed by the task names.
        
        @property mRunningTaskFromHost
        A hash table of tasks which are currently running, indexed by the hosts.

        @property mRunningTaskFromPID
        A hash table of tasks which are currently running, indexed by the PIDs.
        """
        self.mHost = aHost
        self.mPort = aPort
        self.mTasks = {}
        self.mRunningTaskFromHost = {}
        self.mRunningTaskFromPID = {}

    def start(self):
        """
        @fn start(self)
        @brief start the server
        """
        server = SocketServer.TCPServer((self.mHost, self.mPort),
                                        requestHandler)
        server.serve_forever()

gServer = taskHandler(TASK_HANDLER_HOST, TASK_HANDLER_PORT)
 
if __name__ == "__main__":
    gServer.start()
