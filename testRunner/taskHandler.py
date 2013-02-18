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

@var TASK_LIST_DIRECTORY
Path to the taskList directory
"""

from __future__ import print_function

from config import PYTHON, PERL
from config import TASK_HANDLER_HOST, TASK_HANDLER_PORT
from config import HOST_LIST, HOST_LIST_OS, OS_LIST, BROWSER_LIST
from config import FONT_LIST, OUTPUT_JAX_LIST, SELENIUM_SERVER_PORT
from config import DEFAULT_TIMEOUT
from config import MONTH_LIST, WEEKDAY_LIST

from config import MATHJAX_TEST_PUBLIC_URI, MATHJAX_TEST_LOCAL_URI
from config import DEFAULT_MATHJAX_PATH

TASK_LIST_DIRECTORY = "config/taskList/"
TASK_LIST_TXT = "taskList.txt"
MATHJAX_WEB_PATH = "../web/"

from crontab import CronTab
from datetime import datetime, timedelta
from signal import SIGINT
import ConfigParser
import SocketServer
import collections
import os
import socket
import subprocess
import cgi
import copy
import heapq

def boolToString(aBoolean):
    """
    @fn boolToString(aBoolean)
    @brief A simple function to convert a boolean to a string

    @return the string "true" or "false"
    """
    if aBoolean:
        return "true"
    return "false"

def getDirectoryFromDate():
    """
    @fn getDirectoryFromDate()
    @brief generate a directory name from the current date of the day

    @return "YEAR-MONTH-DATE/"
    """
    return datetime.utcnow().strftime("%Y-%m-%d/")

class requestHandler(SocketServer.StreamRequestHandler):
    """
    @class taskHandler::requestHandler
    @brief A class inheriting from SocketServer.StreamRequestHandler and dealing
    with the requests received by the task handler.
    """

    def readExceptionMessage(self):
        """
        @fn readExceptionMessage(self)
        @brief read an exception message
        @return The exception message read from the socket

        This function reads line from the socket and concatenated them in a
        string until it reaches a "TASK DEATH END" line.
        """

        s = ""

        while (True):
            request = self.rfile.readline().strip()
            if (request == "TASK DEATH END"):
                break
            s += request + "\n"

        return s

    def editTask(self, aTaskName, aConfigFile, aOutputDirectory, aSchedule):
        """
        @fn editTask(self, aTaskName, aConfigFile, aOutputDirectory, aSchedule)
        @brief add/edit an item of the task list
        @param aTaskName name of the task
        @param aConfigFile configuration file to use. If it is None, the
        config parameters will be read from the socket.
        @param aOutputDirectory directory to store results of the task. If it
        is None, the task name is used instead.
        @param aSchedule @ref taskHandler::task::mSchedule of the task
        @return a message indicating whether the task has been successfully
        added/edited or not.

        If the task with the same name is not already in the task list,
        this function creates a new task with the specified name, a status
        "Inactive". The output directory is of the form DATE/aOutputDirectory.
        Task configuration are read from the socket and stored in the
        task::mParameters table of the task.

        If a task is already in the task list and is not running, then this
        function updates the task parameters.
        """

        global gServer

        if aOutputDirectory == None:
            # Default directory is the task name
            aOutputDirectory = aTaskName

        if aSchedule == None:
            # if the task is not scheduled, store the results in a directory
            # with the date of the day
            aOutputDirectory = getDirectoryFromDate() + aOutputDirectory

        aOutputDirectory += "/"

        if aTaskName in gServer.mTasks.keys():
            # The task already exists, try to edit it
            t = gServer.mTasks[aTaskName]
            if t.isRunning():
                return "'" + aTaskName + \
                    "' is running and can not be edited!" + "'\n"

            if (t.isPending()):
                # Before editing the task (in particular its host, name and
                # priority queue) we remove it from the pending queue.
                gServer.removeTaskFromPendingQueue(t)

            msg = "updated"
            if t.mSchedule:
                # remove the task from the scheduler
                gServer.removeScheduledTask(t)

            t.mStatus = "Inactive"
            t.mProgress = "-"
            t.mOutputDirectory = aOutputDirectory
            t.mOutputFileName = None
            t.mExceptionMessage = None
            t.mSchedule = aSchedule
        else:
            # create a new task
            t = task(aTaskName, "Inactive", aOutputDirectory, None, aSchedule)
            msg = "added to the task list"

        # read the configuration parameters of the task:
        #   - First look at the parameters given in the request
        t.readParametersFromSocket(self)
        #   - If a config file is given, overwrite some values
        if aConfigFile:
            if (not os.path.exists(aConfigFile)):
                return "File '" + aConfigFile + "' not found."
            t.readParametersFromConfigFile(aConfigFile)
        t.chooseDefaultHost()
        
        if aTaskName not in gServer.mTasks.keys():
            # add the task to the list
            gServer.mTasks[aTaskName] = t

        t.generateConfigFile()

        if t.mSchedule:
            # add the task to the scheduler
            gServer.addScheduledTask(t)

        return "'" + aTaskName + "' " + msg + ".\n"

    def renameTask(self, aOldName, aNewName):
        """
        @fn renameTask(self, aOldName, aNewName)
        @brief rename a task
        @param aOldName old name of the task
        @param aNewName new name to give to the task
        @return a message indicating whether the task has been successfully
        renamed or not.
        """

        global gServer

        if aOldName not in gServer.mTasks.keys():
            return "'" + aOldName + "' was not found in the task list!"

        if aNewName in gServer.mTasks.keys():
            return "'" + aNewName + "' is already in the task list!"

        t = gServer.mTasks[aOldName]
        gServer.mTasks[aNewName] = t
        t.removeConfigFile()
        if t.mSchedule:
            gServer.removeScheduledTask(t)
        del gServer.mTasks[aOldName]

        t.mName = aNewName
        t.generateConfigFile()
        if t.mSchedule:
            gServer.addScheduledTask(t)

        return "'" + aOldName + "' renamed into '" + aNewName + "'!"

    def cloneTask(self, aTaskName, aCloneName):
        """
        @fn cloneTask(self, aTaskName, aNewName)
        @brief clone a task
        @param aTaskName task to clone
        @param aNewName new name to give to the task
        @return a message indicating whether the task has been successfully
        cloned or not.
        """

        global gServer

        if aTaskName not in gServer.mTasks.keys():
            return "'" + aTaskName + "' was not found in the task list!"

        if aCloneName in gServer.mTasks.keys():
            return "'" + aCloneName + "' is already in the task list!"

        t = copy.deepcopy(gServer.mTasks[aTaskName])
        t.mName = aCloneName
        t.mStatus = "Inactive"
        t.mProgress = "-"
        t.mPopen = None
        t.mExceptionMessage = None
        gServer.mTasks[aCloneName] = t

        t.generateConfigFile()

        if t.mSchedule:
            # add the task to the scheduler
            gServer.addScheduledTask(t)

        return "'" + aTaskName + "' cloned into '" + aCloneName + "'!"

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
            if t.isPending():
                # remove the task from the pending queue
                gServer.removeTaskFromPendingQueue(t)

            if t.mSchedule:
                # remove the task from the scheduler
                gServer.removeScheduledTask(t)

            # remove the task from the list
            t.removeConfigFile()
            del gServer.mTasks[aTaskName]
            return "'" + aTaskName + "' removed from the task list.\n"
       
        return "'" + aTaskName + "' is running and can not be removed!\n"

    def runTask(self, aTaskName, aRestart = False):
        """
        @fn runTask(self, aTaskName, aRestart = False)
        @brief launch the execution of a task or put it in the pending queue.
        @param aTaskName name of the task to run
        @param aRestart Whether we should run the task from the beginning or
        continue it if it was interrupted
        @return a message indicating the result of this action.
        """

        global gServer

        if aTaskName not in gServer.mTasks.keys():
            return "'" + aTaskName + "' was not found in the task list!"

        t = gServer.mTasks[aTaskName]

        if (t.isRunning()):
            return "'" + aTaskName + "' is already running!\n"

        if (aRestart):
            t.mParameters["startID"] = ""
            t.mOutputFileName = None

        h = t.host()
        if h == None:
            return "Unknown host '" + t.mParameters["host"] + "'\n"

        if (h in gServer.mRunningTasksFromHost.keys()):
            # Tasks are already running on this host: verify the status.
            # This may change the list of running/pending tasks!
            gServer.verifyHostStatus(h)
            if (t.isRunning()):
                return "'" + aTaskName + "' is already running!\n"

        if (t.isPending()):
            return "'" + aTaskName + "' is already pending!\n"

        gServer.addTaskToPendingQueue(t)
        gServer.runNextTasksFromPendingQueue(h)

        return "'" + aTaskName + "' added to the pending queue.\n"

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

    def formatTask(self, aTaskName):
        """
        @fn formatTask(self, aTaskName)
        @brief format the text output into of a task
        @return a message indicating whether the operation succeeded
        """

        global gServer

        if aTaskName not in gServer.mTasks.keys():
            return "'" + aTaskName + "' was not found in the task list!"

        t = gServer.mTasks[aTaskName]

        output = MATHJAX_WEB_PATH + "results/"
        output += t.mOutputDirectory + t.mOutputFileName
        outputTxt  = output + ".txt"
        outputHTML = output + ".html"

        if (os.path.exists(outputTxt)):
            pipe = subprocess.Popen([PERL, "clean-reftest-output.pl",
                                     outputTxt,
                                     MATHJAX_TEST_PUBLIC_URI],
                                    stdout=subprocess.PIPE)
            fp = file(outputHTML, "w")
            print(pipe.stdout.read(), file=fp)
            fp.close()
            return "Output of '" + aTaskName + "' formatted!\n"

        return "Could not format '" + aTaskName + "'!\n"

    def handle(self):
        """
        @fn handle(self)
        @brief Handle a client request

        The task handler accept request from any host, so be sure to configure
        your firewall appropriately. This function reads a line from the socket
        and sends a response:

        - If the request is "TASKVIEWER", it sends the result of
        @ref taskHandler::getTaskList

        - If the request is "TASKINFO taskName", it sends the result of
        @ref taskHandler::getTaskInfo for the corresponding task.

        - If the request is "HOSTINFO host", it sends the the result of
        @ref taskHandler::getHostInfo for the corresponding host.

        - If the request is "SAVETASKLIST", it saves the task list and returns
        a message.

        - If the request is "TASK UPDATE pid status progress", where pid the PID
        of the process of a running task, it updates the members of the given
        task accordingly. If status is "Interrupted", progress is actually the
        startID to use to recover the testing instance.
        In particular, it can be ommited if the task was interrupted before
        any tests have been run (i.e. startID should be an empty string).

        - If the request is "TASK *_DEATH pid" where * is either
          "EXPECTED" or "UNEXPECTED" and pid the PID of the process of a running
          task, then that task is removed from the hash tables of running tasks.
          If the death is unexpected, the @ref task::mStatus is set to
          "Killed" and @ref task::mExceptionMessage is read using
          @ref readExceptionMessage.

        - If the request starts by "TASKEDITOR command taskName", then it
        performs one of the following command and returns the information
        message:
            - "TASKEDITOR EDIT taskName configFile outputDirectory":
              @ref editTask
            - "TASKEDITOR CLONE taskName cloneName": @ref cloneTask
            - "TASKEDITOR RENAME oldName newName": @ref renameTask
            - "TASKEDITOR REMOVE taskName": @ref removeTask
            - "TASKEDITOR RUN taskName": @ref runTask with aRestart = False
            - "TASKEDITOR RESTART taskName": @ref runTask with aRestart = True
            - "TASKEDITOR STOP taskName": @ref stopTask
            - "TASKEDITOR FORMAT taskName": @ref formatTask

        - other requests are ignored.
        """

        global gServer

        request = self.rfile.readline().strip()
        print(request)
        items = request.split()
        client = items[0]
        if (client == "TASKVIEWER"):
            self.wfile.write(gServer.getTaskList())
        elif (client == "TASKINFO"):
            taskName = items[1]
            self.wfile.write(gServer.getTaskInfo(taskName))
        elif (client == "HOSTINFO"):
            host = items[1]
            self.wfile.write(gServer.getHostInfo(host))
        elif (client == "SAVETASKLIST"):
            gServer.saveTaskList()
            self.wfile.write("Task list saved!")
        elif (client == "TASK"):
            command = items[1]
            pid = items[2]
            if pid in gServer.mRunningTaskFromPID.keys():
                t = gServer.mRunningTaskFromPID[pid]
                if (command == "UPDATE"):
                    status = items[3]
                    if (status in
                        ["Running", "Complete", "Interrupted"]):
                        t.mStatus = status
                        if (t.mStatus == "Interrupted"):
                            if (len(items) >= 5):
                                t.mParameters["startID"] = items[4]
                            else:
                                t.mParameters["startID"] = ""
                        else:
                            t.mProgress = items[4]
                elif (command == "EXPECTED_DEATH" or
                      command == "UNEXPECTED_DEATH"):
                    del gServer.mRunningTaskFromPID[pid]
                    gServer.removeTaskFromRunningList(t)
                    if (command == "UNEXPECTED_DEATH"):
                        t.mStatus = "Killed"
                        t.mExceptionMessage = self.readExceptionMessage()
                    gServer.runNextTasksFromPendingQueue(t.host())
                elif (command == "OUTPUTFILENAME"):
                    t.mOutputFileName = items[3]
                        
        elif (client == "TASKEDITOR"):
            # One can only edit one task at once. This means that the
            # requester have to call run and restart operations in the right
            # order (i.e. respecting the priorities of task).
            command = items[1]
            taskName = items[2]
            if command == "EDIT":
                if items[3] == "None":
                    configFile = None
                else:
                    configFile = items[3]
                if items[4] == "None":
                    outputDirectory = None
                else:
                    outputDirectory = items[4]
                if items[5] == "None":
                    schedule = None
                else:
                    schedule = items[5]
                self.wfile.write(self.editTask(taskName,
                                               configFile,
                                               outputDirectory,
                                               schedule))
            elif command == "CLONE":
                cloneName = items[3]
                self.wfile.write(self.cloneTask(taskName, cloneName))
            elif command == "RENAME":
                newName = items[3]
                self.wfile.write(self.renameTask(taskName, newName))
            elif command == "REMOVE":
                self.wfile.write(self.removeTask(taskName))
            elif command == "RUN":
                self.wfile.write(self.runTask(taskName, False))
            elif command == "RESTART":
                self.wfile.write(self.runTask(taskName, True))
            elif command == "STOP":
                self.wfile.write(self.stopTask(taskName))
            elif command == "FORMAT":
                self.wfile.write(self.formatTask(taskName))

class task:
    """
    @class taskHandler::task
    @brief A class representing items in the task list.
    """

    def __init__(self, aName, aStatus, aOutputDirectory, aOutputFileName,
                 aSchedule):
        """
        @fn __init__(self, aName, aStatus, aOutputDirectory,  aOutputFileName,
                     aSchedule)

        @param aName            Value to assign to @ref mName
        @param aStatus          Value to assign to @ref mStatus
        @param aOutputDirectory Value to assign to @ref mOutputDirectory
        @param aOutputFileName  Value to assign to @ref mOutputFileName
        @param aSchedule        Value to assign to @ref mSchedule

        @property mName
        Name of the task

        @property mStatus
        Status of the task:
          - Process not executed yet: "Inactive"
          - Process waiting to execute: "Pending"
          - Process executing: "Running"
          - Process executed: "Complete", "Interrupted", "Killed"

        @property mOutputDirectory
        Directory where the results of the task are stored.

        @property mOutputFileName
        Name to use for output files.

        @property mProgress
        Either "-" or a fraction "numberOfTestsExecuted/totalNumberOfTests".

        @property mParameters
        Hash table of task parameters, corresponding to those in the config
        file.
        @see ../html/components.html\#test-runner-config

        @property mPopen
        The result of the subprocess.Popen or None if the task was never
        executed.

        @property mExceptionMessage
        If the task has the "Killed" status, the Exception message raised by
        the task process before dying or "No exception raised" if the death was
        not reported. Otherwise, it is None.

        @property mSchedule
        If the task is scheduled, the string "m,h,dom,mon,dow" representing an
        entry in the crontab. Otherwise, it is None.

        This function initializes @ref mName, @ref mStatus and
        @ref mOutputDirectory with the given arguments ; @ref mProgress to "-",
        @ref mPopen and @ref mExceptionMessage to None ; @ref mParameters to an
        a hash table with a single "host" parameter with value None.
        """
        self.mName = aName
        self.mStatus = aStatus
        self.mProgress = "-"
        self.mParameters = {}
        self.mParameters["host"] = HOST_LIST[0]
        self.mParameters["priority"] = 0

        # Default values for boolean parameters. This should match
        # getBooleanOption in runTestsuite.py
        self.mParameters["useGrid"] = False
        self.mParameters["fullScreenMode"] = True
        self.mParameters["formatOutput"] = True
        self.mParameters["compressOutput"] = True
        self.mParameters["useWebDriver"] = False
        self.mParameters["runSlowTests"] = False
        self.mParameters["runSkipTests"] = False

        self.mPopen = None
        self.mOutputDirectory = aOutputDirectory
        self.mOutputFileName = aOutputFileName
        self.mExceptionMessage = None
        self.mSchedule = aSchedule

    def host(self):
        """
        @fn host(self)
        @brief get the IP address of a machine
        @return the host corresponding to @ref mParameters["host"] or "Unknown"
        this parameter is None.
        """
        h = self.mParameters["host"]
        try:
            return socket.gethostbyname(h)
        except socket.gaierror, err:
            self.mExceptionMessage = \
                "can't resolve hostname %s: %s" % (h, err[1])
            return None

    def priority(self):
        """
        @fn priority(self)
        @brief Priority of the task
        @return self.mParameters["priority"]
        """
        return self.mParameters["priority"]
        
    def isPending(self):
        """
        @fn isPending(self)
        """
        return (self.mStatus == "Pending")

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

        If the process is running but the @ref mStatus says "Inactive" or
        "Pending", set the status to "Running". This may happen if the
        runTestsuite did not send the "Running" status yet.
        """
        global gServer

        running = self.isRunning()

        if ((not running) and self.mStatus == "Running"):
            self.mStatus = "Killed"
            self.mExceptionMessage = "No exception raised"
            gServer.removeTaskFromRunningList(self)
            pid = str(self.mPopen.pid)
            if pid in gServer.mRunningTaskFromPID.keys():
                del gServer.mRunningTaskFromPID[pid]
            gServer.runNextTasksFromPendingQueue(self.host())
        elif (running and
              (self.mStatus == "Inactive" or
               self.mStatus == "Pending")):
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
        s += str(self.mParameters["priority"]) + " "
        s += self.mStatus + " ";
        s += self.mProgress + " "
        s += self.mOutputDirectory + " "
        if self.mOutputFileName:
            s += self.mOutputFileName
        else:
            s += "None"
        s += " "
        if self.mSchedule:
            s += self.mSchedule
        else:
            s += "None"

        return s

    def serializeMember(self, aName, aValue):
        """
        @fn serializeMember(self, aName, aValue)
        @brief serialize a pair (aName, aValue) as an HTML row
        @return an HTML row tr(th(aName), td(aValue)) in text format
        """
        return "<tr><th>" + aName + "</th><td>" + \
            cgi.escape(aValue) + "</td></tr>"

    def serializeParameter(self, aKey):
        """
        @fn serializeParameter(self, aKey)
        @brief serialize a (aKey, @ref mParameters[aKey]) as an HTML row
        @return an HTML row tr(th(aKey), td(aValue)) in text format
        """
        return self.serializeMember(aKey, self.mParameters[aKey].__str__())

    def serializeSchedule(self, aSchedule):
        """
        @fn serializeSchedule(self, aSchedule)
        @brief serialize the date of scheduled task
        """
        items = aSchedule.split(",")
        date = "<span id=\"taskSchedule\"></span>"

        date += "<span id=\"crontabDow\">"
        if (items[4] == "*"):
            date += "*"
        else:
            date += WEEKDAY_LIST[int(items[4]) - 1]
        date += "</span> "

        date += "<span id=\"crontabDom\">"
        if (items[2] == "*"):
            date += "*"
        else:
            date += items[2]
        date += "</span> "

        date += "<span id=\"crontabMon\">"
        if (items[3] == "*"):
            date += "*"
        else:
            date += MONTH_LIST[int(items[3]) - 1]
        date += "</span> ; "

        date += "<span id=\"crontabH\">"
        if (items[1] == "*"):
            date += "*"
        else:
            if (len(items[1]) == 1):
                # add a 0 if hours are < 10
                date += "0"
                date += items[1]
        date += "</span>:"

        date += "<span id=\"crontabM\">"
        if (items[0] == "*"):
            date += "*"
        else:
            if (len(items[0]) == 1):
                # add a 0 if minutes are < 10
                date += "0"
                date += items[0]
        date += "</span>"

        return self.serializeMember("Scheduled", date)

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

        if (self.mOutputDirectory and
            os.path.exists(MATHJAX_WEB_PATH + "results/" +
            self.mOutputDirectory)):
            s += "<a href=\"results/" + self.mOutputDirectory + "\""
            s += " id=\"outputDirectory\">"
            s += self.mOutputDirectory + "</a>"
        else:
            s += "<span id=\"outputDirectory\">"
            s += self.mOutputDirectory
            s += "</span>"

        s += "</td></tr>"

        if self.mOutputFileName:
            s += "<tr><th>Output file</th><td>"
            outputFile = MATHJAX_WEB_PATH + "results/" + self.mOutputDirectory
            outputFile += self.mOutputFileName
            if (os.path.exists(outputFile + ".html.gz")):
                ext = ".html.gz"
            elif (os.path.exists(outputFile + ".html")):
                ext = ".html"
            elif (os.path.exists(outputFile + ".txt.gz")):
                ext = ".txt.gz"
            elif (os.path.exists(outputFile + ".txt")):
                ext = ".txt"
            else:
                ext = None
            
            if ext:
                s += "<a href=\"results/" + self.mOutputDirectory
                s += self.mOutputFileName + ext + "\">"
                s += self.mOutputFileName
                s += "</a>"
            else:
                s += self.mOutputFileName

            s += "</td></tr>"

        if (self.mSchedule):
            s += self.serializeSchedule(self.mSchedule)

        if (self.mExceptionMessage):
            s += "<tr style=\"color: red;\">"
            s += "<th id='exceptionError'>Exception Error</th>"
            s += "<td>" + cgi.escape(self.mExceptionMessage) + "</td></tr>"

        s += "</table></p>"

        s += "<h2>Framework Configuration</h2>"
        s += "<p><table>"
        s += self.serializeParameter("useGrid")
        s += self.serializeParameter("host")
        s += self.serializeParameter("port")
        s += self.serializeParameter("mathJaxPath")
        s += self.serializeParameter("mathJaxTestPath")
        s += self.serializeParameter("timeOut")
        s += self.serializeParameter("useWebDriver")
        s += self.serializeParameter("fullScreenMode")
        s += self.serializeParameter("priority")
        s += self.serializeParameter("formatOutput")
        s += self.serializeParameter("compressOutput")
        s += "</table></p>"
        
        s += "<h2>Platform Configuration</h2>"
        s += "<p><table>"
        s += self.serializeParameter("operatingSystem")
        s += self.serializeParameter("browser")
        s += self.serializeParameter("browserVersion")
        s += self.serializeParameter("browserMode")
        s += self.serializeParameter("browserPath")
        s += self.serializeParameter("font")
        s += self.serializeParameter("outputJax")
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
        return TASK_LIST_DIRECTORY + self.mName + ".cfg"

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
        fp.write("useGrid = " + boolToString(p["useGrid"]) + "\n")
        fp.write("host = " + p["host"] + "\n")
        fp.write("port = " + str(p["port"]) + "\n")
        fp.write("mathJaxPath = " + p["mathJaxPath"] + "\n")
        fp.write("mathJaxTestPath = " + p["mathJaxTestPath"] + "\n")
        fp.write("timeOut = " + str(p["timeOut"]) + "\n")
        fp.write("useWebDriver = " + boolToString(p["useWebDriver"]) + "\n")
        fp.write("fullScreenMode = " + boolToString(p["fullScreenMode"]) + "\n")
        fp.write("priority = " + str(p["priority"]) + "\n")
        fp.write("formatOutput = " + boolToString(p["formatOutput"]) + "\n")
        fp.write("compressOutput = " + boolToString(p["compressOutput"]) + "\n")
        fp.write("\n")

        fp.write("[platform]\n")
        fp.write("operatingSystem = " + p["operatingSystem"] + "\n")
        fp.write("browser = " + p["browser"] + "\n")
        fp.write("browserVersion = " + p["browserVersion"] + "\n")
        fp.write("browserMode = " + p["browserMode"] + "\n")
        fp.write("browserPath = " + p["browserPath"] + "\n")
        fp.write("font = " + p["font"] + "\n")
        fp.write("outputJax = " + p["outputJax"] + "\n")
        fp.write("\n")

        fp.write("[testsuite]\n")
        fp.write("runSlowTests = " + boolToString(p["runSlowTests"]) + "\n")
        fp.write("runSkipTests = " + boolToString(p["runSkipTests"]) + "\n")
        fp.write("listOfTests = " + p["listOfTests"] + "\n")
        fp.write("startID = " + p["startID"] + "\n")

        fp.close()

    def removeConfigFile(self):
        """
        @fn removeConfigFile(self)
        @brief remove the configuration file for this task
        """
        os.remove(self.getConfigPath())

    def execute(self):
        """
        @fn execute(self)
        @brief Execute a new runTestsuite.py subprocess
        @return Python's subprocess.Popen instance representing the subprocess

        Call "python runTestsuite.py -c configName -o outputDirectory -t"
        where configName is the value returned by @ref getConfigPath and
        outputDirectory is @ref mOutputDirectory.
        """
        global gServer
        self.generateConfigFile()
        self.mExceptionMessage = None
        command = [PYTHON, 'runTestsuite.py',
                   '-c', self.getConfigPath(),
                   '-o', self.mOutputDirectory,
                   '-t']
        if self.mOutputFileName:
            command.extend(['-f', self.mOutputFileName])

        self.mPopen = subprocess.Popen(command)
        gServer.mRunningTaskFromPID[str(self.mPopen.pid)] = self
        gServer.addTaskToRunningList(self)

    def setParameter(self, aParameterName, aParameterValue,
                     aOverwrite = True):
        """
        @fn setParameter(self, aParameterName, aParameterValue, aOverwrite)
        @param aParameterName name of the parameter
        @param aParameterValue value of the parameter
        @param aOverwrite Whether we overwrite the operator when it has a
        default value. Default value is True.        
        @see ../html/components.html\#test-runner-config
        @note multiple option values and unknown parameters are rejected
        """
        parameterName = aParameterName.strip()
        parameterValue = aParameterValue.strip().split()
        if (len(parameterValue) == 0):
            parameterValue = ""
        else:
            if (len(parameterValue) > 1):
                print("warning: the task handler does not accept multiple\
option values")
            parameterValue = parameterValue[0]
    
        if (not(aOverwrite) and
            (parameterName in self.mParameters) and
            (parameterValue == "default" or parameterValue == -1)):
            # If the parameter is already set and a default value is passed to
            # this function, then we don't overwrite
            return

        if (parameterName == "useGrid" or
            parameterName == "useWebDriver" or
            parameterName == "fullScreenMode" or
            parameterName == "formatOutput" or
            parameterName == "compressOutput" or
            parameterName == "runSlowTests" or
            parameterName == "runSkipTests"):
            self.mParameters[parameterName] = (parameterValue == "true")
        elif (parameterName == "port" or
              parameterName == "timeOut" or
              parameterName == "priority"):
            parameterValue = int(parameterValue)
            if (parameterValue == -1):
                if (parameterName == "port"):
                    parameterValue = SELENIUM_SERVER_PORT
                elif (parameterName == "priority"):
                    parameterValue = 0
                else: # timeout
                    parameterValue = DEFAULT_TIMEOUT
            self.mParameters[parameterName] = parameterValue
        elif (parameterName == "host" or
              parameterName == "mathJaxPath" or
              parameterName == "mathJaxTestPath" or
              parameterName == "operatingSystem" or
              parameterName == "browser" or
              parameterName == "browserVersion" or
              parameterName == "browserMode" or
              parameterName == "browserPath" or
              parameterName == "font" or
              parameterName == "outputJax" or
              parameterName == "listOfTests" or
              parameterName == "startID"):
            if (parameterValue == "default"):
                if (parameterName == "mathJaxPath"):
                    parameterValue = DEFAULT_MATHJAX_PATH
                elif (parameterName == "mathJaxTestPath"):
                    parameterValue = MATHJAX_TEST_LOCAL_URI + "testsuite/"
                elif (parameterName == "operatingSystem"):
                    parameterValue = OS_LIST[0]
                elif (parameterName == "browser"):
                    parameterValue = BROWSER_LIST[0]
                elif (parameterName == "font"):
                    parameterValue = FONT_LIST[0]
                elif (parameterValue == "outputJax"):
                    parameterValue = OUTPUT_JAX_LIST[0]
                else:
                    # host: handled later, when the operating system is known
                    # browserVersion, browserPath, listeOfTests, startID
                    #   It is safe to keep the "default" value here, the test
                    #   runner will take care of them.
                    pass
            self.mParameters[parameterName] = parameterValue
        else:
            print("Unknown parameter " + parameterName)

    def chooseDefaultHost(self):
        """
        @fn chooseDefaultHost(self)
        @brief Choose a default host according to the operating system
        """
        if (self.mParameters["host"] == "default"):
            self.mParameters["host"] = HOST_LIST[HOST_LIST_OS.index(OS_LIST.index(self.mParameters["operatingSystem"]))]

    def readParametersFromSocket(self, aRequestHandler):
        """
        @fn readParametersFromSocket(self, aRequestHandler)
        @brief read parameters from the socket and store it in the task

        This function reads lines from the socket until it reaches

        "TASKEDITOR EDIT END"

        The function expects to read lines

        "parameterName = parameterValue"

        where the pair (parameterName, parameterValue) is a testing instance
        configuration option. If the option is known, then this parameter is
        added to the task::mParameters table of the task. Otherwise it is
        ignored.
        In any case, the function return True.
        """

        while(True):
            request = aRequestHandler.rfile.readline().strip()
            print(request)

            if (request == "TASKEDITOR EDIT END"):
                break

            item = request.split("=", 1)
            self.setParameter(item[0], item[1])

    def readParametersFromConfigFile(self, aConfigFile):
        """
        @fn readParametersFromConfigFile(self, aConfigFile)
        @brief read parameters from a configuration file
        @param aConfigFile configuration file to use
        """
        configParser = ConfigParser.ConfigParser()
        configParser.optionxform = str # to preserve the case of parameter name
        configParser.readfp(open(aConfigFile))

        for section in ["framework", "platform", "testsuite"]:
            for item in configParser.items(section):
                self.setParameter(item[0], item[1], False)

    def getScheduledCommand(self):
        """
        @fn getScheduledCommand(self)
        @return the shell command to RESTART the task
        """
        cmd = PYTHON + " "
        cmd += os.getcwdu() + "/taskEditor.py "
        cmd += "RESTART "
        cmd += self.mName
        return cmd
  
class pendingTaskInfo:
    """
    @class taskHandler::pendingTaskInfo
    @brief Info of a task in the pending queue
    """
    def __init__(self, aTask):
        """
        @fn __init__(self, aTask)

        @param aTask task to represent

        @property mName
        Name of the task

        @property mHost
        Host on which the task should run.

        @property mPriority
        Priority of the task
        
        @property mRemoved
        Whether the task has been removed from the pending queue.
        """

        self.mName = aTask.mName
        self.mHost = aTask.host()
        self.mPriority = aTask.priority()
        self.mRemoved = False

    def __le__(self, other):
        return self.mPriority <= other.mPriority

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
        
        @property mRunningTasksFromHost
        A hash table of tasks which are currently running, indexed by the hosts.

        @property mRunningTaskFromPID
        A hash table of tasks which are currently running, indexed by the PIDs.

        @property mPendingTasksFromHost
        A hash table of task queues, indexed by the hosts. Each task queue is
        the list of tasks which are waiting to run on the host.

        @property mCronTab
        A representation of the crontab used for task scheduling
        """
        self.mHost = aHost
        self.mPort = aPort
        self.mTasks = {}
        self.mRunningTasksFromHost = {}
        self.mRunningTaskFromPID = {}
        self.mPendingTasksFromHost = {}
        self.mCronTab = CronTab()

    def start(self):
        """
        @fn start(self)
        @brief start the server
        """
        print("Task Handler started.")
        if (not os.path.exists(TASK_LIST_TXT)):
            # save an empty task list
            self.saveTaskList()
        else:
            self.loadTaskList()
        server = SocketServer.TCPServer((self.mHost, self.mPort),
                                        requestHandler)

        server.serve_forever()

    def stop(self):
        """
        @fn start(self)
        @brief stop the server
        """
        print("Task Handler received SIGINT!")
        self.saveTaskList()

    def getTaskInfo(self, aTaskName):
        """
        @fn getTaskInfo(self, aTaskName)
        @brief Get an HTML representation of properties of a given task.
        @param aTaskName Name of the task from which to retrieve information.
        
        If the task is not in the list, this function returns a message
        indicating so. Otherwise, it calls the task::serializeHTML function.
        """
        if aTaskName not in self.mTasks.keys():
            return "<p>No task '" + aTaskName + "' in the task list.</p>"

        return self.mTasks[aTaskName].serializeHTML();

    def getHostInfo(self, aHost):
        """
        @fn getHostInfo(self, aHost)
        @brief get the lists of running/pending tasks on the host
        """
     
        try:
            h = socket.gethostbyname(aHost)
        except socket.gaierror, err:
            return "UNKNOWN_HOST\n"
           
        s = ""

        s += "HOST " + aHost
        if aHost != h:
            s += " (" + h + ")"
        s += "\n"

        s += "RUNNING_TASKS\n"

        if h in gServer.mRunningTasksFromHost.keys():
            for t in gServer.mRunningTasksFromHost[h]:
                s += t.mName + " "
            s += "\n"

        s += "RUNNING_TASKS END\n"
        
        s += "PENDING_TASKS\n"

        if h in gServer.mPendingTasksFromHost.keys():
            for t in gServer.mPendingTasksFromHost[h]:
                s += t.mName + "\n"

        s += "PENDING_TASKS END\n"

        return s

    def getTaskList(self):
        """
        @fn getTaskList(self)
        @brief return a string representing a task list

        If the task list is empty, one line

        "TASK LIST EMPTY"

        is returned. Otherwise, the returned string starts with the line

        "TASK LIST NONEMPTY"

        and continue with one line per task, each one of the form

        "Task Name	Host Status Progress outputDirectory outputFileName"
        """
        if (len(self.mTasks) == 0):
            return "TASK LIST EMPTY\n"

        taskList = "TASK LIST NONEMPTY\n"
        for k in self.mTasks.keys():
            taskList += k + " " + self.mTasks[k].serialize() + "\n"
        return taskList

    def loadTaskList(self):
        """
        @fn loadTaskList(self)
        @brief Load the task list from taskList.txt
        """
        fp = file(TASK_LIST_TXT, "r")
        line = fp.readline().strip()
        if (line == "TASK LIST NONEMPTY"):
            while line:
                line = fp.readline().strip()
                items = line.split()
                if (len(items) > 0):
                    # name = items[0]

                    # host = items[1] and priority = items[2]
                    # are already saved in the config file.

                    # status = items[3]
                    if (items[3] == "Running"):
                        status = "Interrupted"
                    elif (items[3] == "Pending"):
                        status = "Inactive"
                    else:
                        status = items[3]

                    # progress = items[4]

                    # outputdirectory = items[5]

                    # outputfilename = item[6]
                    if (items[6] == "None"):
                        items[6] = None

                    # schedule = items[7]
                    if (items[7] == "None"):
                        items[7] = None

                    t = task(items[0], status, items[5], items[6], items[7])
                    t.mProgress = items[4]

                    t.readParametersFromConfigFile(t.getConfigPath())
                    t.chooseDefaultHost()
                    self.mTasks[t.mName] = t
        fp.close()
    
    def saveTaskList(self):
        """
        @fn saveTaskList(self)
        @brief Save the task list in taskList.txt
        """
        fp = file(TASK_LIST_TXT, "w")
        fp.write(self.getTaskList())
        fp.close()

    def verifyHostStatus(self, aHost):
        """
        @fn verifyHostStatus(self, aHost)
        @brief Call task::verifyStatus for all the tasks running on this host
        """
        for t in gServer.mRunningTasksFromHost[aHost]:
            t.verifyStatus()

    def addTaskToPendingQueue(self, aTask):
        """
        @fn addTaskToPendingQueue(self, aTask)
        @brief add the specified task on the pending queue of aTask.host()
        @param aTask task to add to the pending list
        """
        aTask.mStatus = "Pending"
        h = aTask.host()
        if h:
            if h in self.mPendingTasksFromHost.keys():
                q = self.mPendingTasksFromHost[h]
                heapq.heappush(q, pendingTaskInfo(aTask))
            else:
                q = []
                heapq.heappush(q, pendingTaskInfo(aTask))
                self.mPendingTasksFromHost[h] = q

    def removeTaskFromPendingQueue(self, aTask):
        """
        @fn removeTaskFromPendingQueue(self, aTask)
        @brief Remove a task from the pending queue.
        @param aTask task to remove
        """
        # Note: we may have to read the whole heap, but the number of pending
        # tasks is assumed to be small, so that's not a problem. We only
        # mark the task "removed" so that we don't need to build the heap
        # structure again.
        h = aTask.host()
        if h and h in self.mPendingTasksFromHost.keys():
            q = self.mPendingTasksFromHost[h]
            for i in range(len(q)):
                if (not q[i].mRemoved and q[i].mName == aTask.mName):
                    q[i].mRemoved = True

    def runNextTasksFromPendingQueue(self, aHost):
        """
        @fn runNextTasksFromPendingQueue(self, aHost)
        @brief run the next pending tasks for the specified host
        @param aHost on which we want to run the next task
        @details This function runs the tasks of lowest priorities from the
        pending queue of aHost
        """
        if aHost == None:
            return

        if aHost in self.mPendingTasksFromHost.keys():
            q = self.mPendingTasksFromHost[aHost]

            if aHost in self.mRunningTasksFromHost.keys():
                # Set maxpriority to the maximum priority of running tasks
                running = self.mRunningTasksFromHost[aHost]
                maxpriority = 0
                for item in running:
                    maxpriority = max(maxpriority, item.priority())
            else:
                # No tasks are running: set maxpriority to the minimum
                # priority of pending tasks. Ignore the taskInfo marked
                # "removed".
                while (len(q) > 0):
                    taskInfo = heapq.heappop(q)
                    if not taskInfo.mRemoved:
                        heapq.heappush(q, taskInfo)
                        maxpriority = taskInfo.mPriority
                        break

            # Execute all tasks in the pending queue with priority at most
            # maxpriority. Ignore the taskInfo marked "removed".
            while (len(q) > 0 and q[0].mPriority <= maxpriority):
                taskInfo = heapq.heappop(q)
                if (not taskInfo.mRemoved and
                    taskInfo.mName in gServer.mTasks.keys()):
                    gServer.mTasks[taskInfo.mName].execute()

            if len(q) == 0:
                del self.mPendingTasksFromHost[aHost]

    def addTaskToRunningList(self, aTask):
        """
        @fn addTaskToRunningList(self, aTask)
        @brief add aTask to the list of running tasks on aTask.host()
        """
        h = aTask.host()
        if h:
            if h not in self.mRunningTasksFromHost.keys():
                self.mRunningTasksFromHost[h] = [aTask]
            else:
                self.mRunningTasksFromHost[h].append(aTask)

    def removeTaskFromRunningList(self, aTask):
        """
        @fn removeTaskFromRunningList(self, aTask)
        @brief remove aTask from the list of running tasks on aTask.host()
        """
        h = aTask.host()
        if h:
            l = self.mRunningTasksFromHost[h]
            l.remove(aTask)
            if (len(l) == 0):
                del self.mRunningTasksFromHost[h]

    def addScheduledTask(self, aTask):
        """
        @fn addScheduledTask(self, aTask)
        @brief add the task to the scheduler
        @param aTask task to add
        """
        items = aTask.mSchedule.split(",")
        entry = self.mCronTab.new(aTask.getScheduledCommand(), aTask.mName)
        for i in range(0, 5):
            if (items[i] != "*"):
                entry.slices[i] = int(items[i])

        self.mCronTab.write()

    def removeScheduledTask(self, aTask):
        """
        @fn removeScheduledTask(self, aTask)
        @brief remove the task from the scheduler
        @param aTask task to remove
        """
        self.mCronTab.remove_all(aTask.getScheduledCommand())
        self.mCronTab.write()

gServer = taskHandler(TASK_HANDLER_HOST, TASK_HANDLER_PORT)
 
if __name__ == "__main__":
    if not os.path.exists(TASK_LIST_DIRECTORY):
        os.makedirs(TASK_LIST_DIRECTORY)
    try:
        gServer.start()
    except KeyboardInterrupt:
        gServer.stop()
