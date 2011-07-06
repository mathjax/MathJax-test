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
        request = self.rfile.readline().strip().split();
        client = request[0]
        if (client == "TASKVIEWER"):
            print "Received request by TASKVIEWVER"
            for k in gServer.mTasks.keys():
                self.wfile.write(k + " " + gServer.mTasks[k].serialize())
        elif (client == "TASK"):
            print "Received request by TASK"
            # command = request[1]
        else:
            print "Received request by unknown client"

class task:

    def __init__(self, aHost):
        self.mHost = aHost
        self.mStatus = "pending"
        self.mProgress = 0

    def serialize(self):
        return self.mHost + " " + self.mStatus + " " + \
            str(self.mProgress) + "%" + \
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

gServer = taskHandler("localhost", 5557)
 
if __name__ == "__main__":
    gServer.start()
