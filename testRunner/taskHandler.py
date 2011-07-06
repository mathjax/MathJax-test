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

class requestHandler(SocketServer.StreamRequestHandler):

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
                    self.wfile.write(k + " " + gServer.mTasks[k].serialize())
            elif (client == "TASK"):
                taskName = items[1]
                if taskName in gServer.mTasks.keys():
                    gServer.mTasks[taskName].mHost = items[2]
                    gServer.mTasks[taskName].mStatus = items[3]
                    gServer.mTasks[taskName].mProgress = items[4]
            elif (client == "TASKEDITOR"):
                command = items[1]
                taskName = items[2]
                if command == "ADD":
                    if taskName not in gServer.mTasks.keys():
                        self.add(taskName, task(items[3]))
                elif command == "REMOVE"
                    if taskName in gServer.mTasks.keys():
                        del gServer.mTasks[taskName]
        else:
            print "Received request by unknown host " + self.client_address[0]

class task:

    def __init__(self, aHost):
        self.mHost = aHost
        self.mStatus = "Unknown"
        self.mProgress = "Unknown"

    def serialize(self):
        return self.mHost + " " + self.mStatus + " " + \
            self.mProgress + \
            "\n"
   
class taskHandler:

    def __init__(self, aHost, aPort):
        self.mHost = aHost
        self.mPort = aPort
        self.mTasks = {}
        self.add("task1", task("machine1"))
        self.add("task2", task("machine2"))
        self.add("task3", task("machine3"))

    def add(self, aName, aTask):
        if aName not in self.mTasks:
            self.mTasks[aName] = aTask

    def start(self):
        server = SocketServer.TCPServer((self.mHost, self.mPort),
                                        requestHandler)
        server.serve_forever()

gServer = taskHandler("localhost", 4445)
 
if __name__ == "__main__":
    gServer.start()
