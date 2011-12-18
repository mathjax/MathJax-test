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

VERSION=$(SELENIUM_SERVER_VERSION)

help:
	@echo ''
	@echo 'The following commands are available:'
	@echo '  make help'
	@echo '  make config'
	@echo '  make doc'
	@echo '  make updateSeleniumDriver'
	@echo '  make downloadSeleniumServer VERSION=$(SELENIUM_SERVER_VERSION)'
	@echo '  make updateMathJaxBranches'
	@echo '  make clearMathJaxBranches'
	@echo '  make clearTaskList'
	@echo '  make runTaskHandler'
	@echo '  make runSeleniumServer'
	@echo '  make runSeleniumHub'
	@echo '  make runSeleniumNodes OS=[your operating system]'

config:
	@ echo 'Generate $(CONDITION_PARSER), $(CONFIG_PY), $(CONFIG_PHP) and $(CONFIG_JS)...'
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

	@ echo 'Generate $(WEB_BRANCH_LIST)...'
	@ echo '<?php' > $(WEB_BRANCH_LIST)
	@ echo '/* $(WARNING_GENERATED_FILE) */' >> $(WEB_BRANCH_LIST)
	@ echo '$$BRANCH_LIST = array(' >> $(WEB_BRANCH_LIST)
	@ for USER in $(MATHJAX_GIT_USERS); \
	  do \
	  for BRANCH in `ls mathjax/$$USER/`; \
	    do \
            echo \'$$USER/$$BRANCH/\',  >> $(WEB_BRANCH_LIST); \
	    done; \
	  done
	@ $(SED) -i '$$s/,//' $(WEB_BRANCH_LIST)
	@ echo ');' >> $(WEB_BRANCH_LIST)
	@ echo '?>' >> $(WEB_BRANCH_LIST)

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

updateSeleniumDriver:
	@ echo 'Updating Selenium python driver...'
	@ $(PIP) install --upgrade selenium

downloadSeleniumServer:
	@ echo 'Downloading the selenium server...'
	@ $(WGET) http://selenium.googlecode.com/files/selenium-server-standalone-$(VERSION).jar
	@ mv -f selenium-server-standalone-$(VERSION).jar testRunner/seleniumServer.jar

updateMathJaxBranches:
	@ for USER in $(MATHJAX_GIT_USERS); \
	  do \
	  echo "Updating `echo $$USER` branches..."; \
	  cd mathjax; ./getMathJaxBranches.sh $$USER; cd ..; \
	  done

clearMathJaxBranches:
	@ echo 'Clearing MathJax branches...'
	@ for USER in $(MATHJAX_GIT_USERS); \
	  do \
	  echo "Clearing `echo $$USER` branches..."; \
	  rm -rf mathjax/$$USER; \
	  done

clearTaskList:
	@ echo 'Clearing task list...'
	rm -f testRunner/taskList.txt
	rm -f testRunner/config/taskList/*.cfg

runTaskHandler:
	@ echo 'Running the task handler...'
	@ cd testRunner/ ; python taskHandler.py

runSeleniumServer:
	@ echo 'Running selenium server (default mode)...'
	@ cd testRunner/; $(JAVA) -jar seleniumServer.jar

runSeleniumHub:
	@ echo 'Running selenium server (Hub mode)...'
	@ cd testRunner/; $(JAVA) -jar seleniumServer.jar -role hub

runSeleniumNodes:
	@ echo 'Running selenium servers (Node mode)...'
	@ echo 'Not implemented yet!'
