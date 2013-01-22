#!/usr/bin/env python
import sys, os

# This is taken from Jesse Ruderman's original Lithium. I'm not sure about
# the license...

def importRelativeOrAbsolute(f):
    # maybe there's a way to do this more sanely with the |imp| module...
    if f.endswith(".py"):
        f = f[:-3]
    if f.rfind(os.path.sep):
        # Add the path part of the filename to the import path
        (p, _, f) = f.rpartition(os.path.sep)
        sys.path.append(p)
    else:
        # Add working directory to the import path
        sys.path.append(".")
    module = __import__(f)
    del sys.path[0]
    return module
