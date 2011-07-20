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
@file config.py
The file for the @ref config module.

@package config
This module contains general configuration for the task controller
"""

TASK_HANDLER_HOST = "localhost"
TASK_HANDLER_PORT = 4445

KNOWN_HOSTS = ["fred-VirtualBox.local", "192.168.0.20"]
DEFAULT_SELENIUM_PORT = 4444
DEFAULT_MATHJAX_PATH = "http://localhost/MathJax/"
DEFAULT_MATHJAX_TEST_PATH = "http://localhost/MathJax-test/testsuite/"
DEFAULT_TIMEOUT = 20000

MATHJAX_WEB_URI = "http://localhost/MathJax-test/web/"
MATHJAX_WEB_PATH = "../web/"
MATHJAX_TESTSUITE_PATH = "../testsuite/"
