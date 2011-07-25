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
#   Frederic Wang <fred.wang@ free.fr> (original author)
#
# ***** END LICENSE BLOCK *****

include custom.cfg

all: config doc

config:
	@ echo 'Generate $(CONDITION_PARSER), $(CONFIG_PY) and $(CONFIG_PHP)...'
	@ $(SED) 's|###||' <custom.cfg >custom.cfg.tmp
	@ $(PYTHON) generateConfigFiles.py
	@ rm custom.cfg.tmp

	@ echo 'Generate $(WEB_HTACCESS)...'
	@ cp $(WEB_HTACCESS)-tpl $(WEB_HTACCESS)
	@ $(SED) -i '1i\
# $(WARNING_GENERATED_FILE)' $(WEB_HTACCESS)
	@ $(SED) -i 's|QA_USER_NAME|$(QA_USER_NAME)|' $(WEB_HTACCESS)
	@ $(SED) -i 's|QA_PASSWORD_FILE|$(QA_PASSWORD_FILE)|' $(WEB_HTACCESS)

	@ echo 'Generate $(TESTSUITE_HEADER)'
	@ cp $(TESTSUITE_HEADER)-tpl $(TESTSUITE_HEADER)
	@ $(SED) -i '1i\
/* $(WARNING_GENERATED_FILE) */' $(TESTSUITE_HEADER)
	@ $(SED) -i 's|DEFAULT_MATHJAX_PATH|$(DEFAULT_MATHJAX_PATH)|' $(TESTSUITE_HEADER)

	@ echo 'Generate $(WEB_REFTEST_LIST)...'
	@ cd testRunner/; $(PYTHON) runTestsuite.py -p > /dev/null

	@ echo 'Generate $(DOXYGEN_CONFIG)...'
	@ $(DOXYGEN) -s -g $(DOXYGEN_CONFIG) > /dev/null
	@ $(SED) -i '1i\
# $(WARNING_GENERATED_FILE)' $(DOXYGEN_CONFIG)
	@ $(SED) -i '/PROJECT_NAME / c\
PROJECT_NAME = MathJax-test/' $(DOXYGEN_CONFIG)
	@ $(SED) -i '/INLINE_INHERITED_MEMB / c\
INLINE_INHERITED_MEMB = YES' $(DOXYGEN_CONFIG)
	@ $(SED) -i '/EXTENSION_MAPPING / c\
EXTENSION_MAPPING = py=Python js=Javascript' $(DOXYGEN_CONFIG)
	@ $(SED) -i '/HIDE_UNDOC_MEMBERS / c\
HIDE_UNDOC_MEMBERS = YES' $(DOXYGEN_CONFIG)
	@ $(SED) -i '/SHOW_DIRECTORIES / c\
SHOW_DIRECTORIES = YES' $(DOXYGEN_CONFIG)
	@ $(SED) -i '/INPUT / c\
INPUT = ../../web/ ../../testsuite/ ../../testRunner/ ./doxygenMain.txt' $(DOXYGEN_CONFIG)
	@ $(SED) -i '/FILE_PATTERNS / c\
FILE_PATTERNS = *.py *.pl *.php *.js' $(DOXYGEN_CONFIG)
	@ $(SED) -i '/EXCLUDE / c\
EXCLUDE = ../testRunner/parsetab.py ../testRunner/config.py ../web/config.php' $(DOXYGEN_CONFIG)
	@ $(SED) -i '/FILTER_PATTERNS / c\
FILTER_PATTERNS = *.py=$(DOXYGEN_PYTHON_FILTER) *.pl=$(DOXYGEN_PERL_FILER) *.js=$(DOXYGEN_JAVASCRIPT_FILTER)' $(DOXYGEN_CONFIG)
	@ $(SED) -i '/FILTER_SOURCE_FILES / c\
FILTER_SOURCE_FILES = YES' $(DOXYGEN_CONFIG)
	@ $(SED) -i '/HTML_OUTPUT / c\
HTML_OUTPUT = doxygen/' $(DOXYGEN_CONFIG)
	@ $(SED) -i '/GENERATE_LATEX / c\
GENERATE_LATEX = NO' $(DOXYGEN_CONFIG)

doc:
	@ echo 'Build doxygen documentation...'
	@ cd web/docs ; make doxygen > /dev/null

	@ echo 'Build html documentation...'
	@ cd web/docs ; make html > /dev/null

.PHONY: config doc
