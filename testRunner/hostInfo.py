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
@file hostInfo.py
@brief Script to view the list of running/pending tasks on a host
"""

from config import TASK_HANDLER_HOST, TASK_HANDLER_PORT

import SocketServer
import socket
import sys

def usage():
    """
    @fn usage()
    @brief Display command line usage for this script
    """
    print
    print("Usage:")
    print
    print("python hostInfo.py host")
    print
    exit(1)

if __name__ == "__main__":
    l = len(sys.argv)
    
    if (l != 2):
        usage()

    host = sys.argv[1]

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((TASK_HANDLER_HOST, TASK_HANDLER_PORT))
    sock.send("HOSTINFO " + host + "\n")

    response = sock.recv(4096)
    print(response)
