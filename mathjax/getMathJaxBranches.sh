#!/bin/bash
# -*- Mode: Shell-script; tab-width: 2; indent-tabs-mode:nil; -*-
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

# Import variables from custom.cfg
# SED is placed first as it is used by the others. 4 is the length of "SED=".
TMP=`egrep 'SED(\s)+=' ../custom.cfg | tr -d [:blank:]` ; SED=${TMP:4}
GIT=`egrep 'GIT(\s)+=' ../custom.cfg | $SED 's/.\+=//'`
MATHJAX_GIT_FONT_BRANCHES=\
`egrep 'MATHJAX_GIT_FONT_BRANCHES(\s)+=' ../custom.cfg | $SED 's/.\+=//'`
MATHJAX_GIT_DOC_BRANCHES=\
`egrep 'MATHJAX_GIT_DOC_BRANCHES(\s)+=' ../custom.cfg | $SED 's/.\+=//'`
MATHJAX_GIT_OBSOLETE_BRANCHES=\
`egrep 'MATHJAX_GIT_OBSOLETE_BRANCHES(\s)+=' ../custom.cfg | $SED 's/.\+=//'`

# Determine the GitHub user to get branches from.
if [ $# -eq 0 ]
then
    USER="mathjax"
elif [ $# -eq 1 ]
then
    USER=$1
else
    echo "usage: ./getMathJaxBranches.sh [user]"
    exit
fi

# Create a directory for that user if it does not exist.
if [ ! -d $USER ]
then
    mkdir $USER
fi
cd $USER

# Update or clone the user repository
if [ -d master ]
then
    cd master
    $GIT pull
else
    $GIT clone https://github.com/$USER/MathJax.git master
    cd master
fi

# Get the list of branches, excluding "master"
BRANCHES=`$GIT branch -r | $SED 's/  origin\///' | grep -v "master"`
cd ..

# Create/Update directories for each branch
for BRANCH in $BRANCHES
do
    echo "=== $USER/$BRANCH ==="

    if [[ "$MATHJAX_GIT_OBSOLETE_BRANCHES" == *"$BRANCH"* ]]; then
            echo "Skipped."
            continue
    fi

    if [ ! -d $BRANCH ]
    then
        # Create a new directory for this branch
	      cp -r master/ $BRANCH

        # Pull this branch
        cd $BRANCH
        $GIT pull origin $BRANCH || { cd .. ; rm -rf $BRANCH; continue; }

        if [[ "$MATHJAX_GIT_FONT_BRANCHES" != *"$BRANCH"* ]]; then
          # To save space, we remove the font directory and create a
          # symbolic link to the directory in the master branch.
          rm -rf fonts/
          ln -s ../master/fonts fonts

          # Do not track fonts.
          echo "fonts/*" >> .gitignore
          $GIT add .gitignore
          $GIT commit -m "Do not track fonts/."
        fi
        if [[ "$MATHJAX_GIT_DOC_BRANCHES" != *"$BRANCH"* ]]; then
          # To save space, we remove the docs and test directories and create a
          # symbolic link to the directories in the master branch.
          rm -rf docs/
          ln -s ../master/docs docs
          rm -rf test/
          ln -s ../master/test test

          # Do not track documentation.
          echo "docs/*" >> .gitignore
          echo "test/*" >> .gitignore
          $GIT add .gitignore
          $GIT commit -m "Do not track docs/, test/."
        fi
    else
        # Update the branch
        cd $BRANCH
        $GIT pull origin $BRANCH || { cd .. ; rm -rf $BRANCH; continue; }
    fi

    cd ..
done
