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

# XXXfred Should import this variable from custom.cfg
SED=sed
GIT=git

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

    if [ ! -d $BRANCH ]
    then
        # Create a new directory for this branch
	      cp -r master/ $BRANCH

        # Pull this branch
        cd $BRANCH
        $GIT pull origin $BRANCH || { cd .. ; rm -rf $BRANCH; continue; }

        # To save space, we remove the directory for image font and create a
        # symbolic link to the directory in the master branch.
        cd fonts/HTML-CSS/TeX/
        rm -rf png/
        ln -s ../../../../master/fonts/HTML-CSS/TeX/png/ png
        cd ../../..

        # Do not track image fonts.
        echo "fonts/HTML-CSS/TeX/png" >> .gitignore
        git add .gitignore
        git commit -m "Do not track image fonts."
    else
        # Update the branch
        cd $BRANCH
        $GIT pull origin $BRANCH || { cd .. ; rm -rf $BRANCH; continue; }
    fi

    cd ..
done
