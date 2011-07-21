#!gmake
#
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

PYTHON   = python

all: config doc

config:
	 # generate web/.htaccess, testRunner/config.py and web/config.php
	python generateConfigFiles.py;
	 # generate selectReftests.js
	cd testRunner/; python runTestsuite.py -p ; cd -;

doc:
	 # build doxygen and html documentation
	cd web/docs ; make; cd -;

.PHONY: config doc
