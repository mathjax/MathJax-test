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
# ***** END LICENSE BLOCK *****

import time
import selenium
import base64
import StringIO
from PIL import Image, ImageChops
import difflib

class seleniumMathJax(selenium.selenium):

    def __init__(self, aHost, aPort, aBrowserStartCommand, aBrowserURL,
                 aMathJaxPath, aBrowser, aUseNativeMathML, aTimeOut,
                 aFullScreenMode):
        selenium.selenium.__init__(self, aHost, aPort, aBrowserStartCommand,
                                   aBrowserURL)
        self.mMathJaxPath = aMathJaxPath
        self.mBrowser = aBrowser
        self.mUseNativeMathML = aUseNativeMathML
        self.mTimeOut = aTimeOut
        self.mFullScreenMode = aFullScreenMode
        self.mCanvas = None
        # Size of screenshots used by Mozilla
        self.mReftestSize = (800, 1000)

    def open(self, aUrl, aUseNativeMathML, aWaitTime = 0.5):

        aUrl += "?" # assuming query string is empty
        aUrl += "useNativeMathML=true&"
        aUrl += "mathJaxPath=" + self.mMathJaxPath

        selenium.selenium.open(self, aUrl)
        self.wait_for_condition(
            "selenium.browserbot.getCurrentWindow().\
             document.documentElement.className == ''", self.mTimeOut)
        time.sleep(aWaitTime)

    def start(self):
        selenium.selenium.start(self)

        # Open the blank page and maximize it
        self.open("blank.html", self.mUseNativeMathML, 3)
        self.window_focus()
        self.window_maximize()
        time.sleep(2)

        # For Konqueror, we remove some bars to get a true fullscreen mode
        if self.mBrowser == "Konqueror":
            # Location Bar: alt+s, t, l
            self.key_down_native(18) # alt
            time.sleep(.1)
            self.key_press_native(83) # s
            time.sleep(.1)
            self.key_up_native(18) # alt
            time.sleep(.1)
            self.key_press_native(84) # t
            time.sleep(.1)
            self.key_press_native(76) # l
            time.sleep(1)

            # Main Toolbar: alt+s, t, m
            self.key_down_native(18) # alt
            time.sleep(.1)
            self.key_press_native(83) # s
            time.sleep(.1)
            self.key_up_native(18) # alt
            time.sleep(.1)
            self.key_press_native(84) # t
            time.sleep(.1)
            self.key_press_native(77) # m
            time.sleep(1)

            # Menu Bar: ctrl+m
            self.key_down_native(17) # control
            time.sleep(.1)
            self.key_press_native(77) # m
            time.sleep(.1)
            self.key_up_native(17) # control
            time.sleep(1)

        if self.mFullScreenMode and \
           (self.mBrowser == "Firefox" or self.mBrowser == "Chrome" or \
            self.mBrowser == "Opera"   or self.mBrowser == "MSIE" or \
            self.mBrowser == "Konqueror"):
            # FullScreen Mode: 
            self.key_press_native(122) # F11
            time.sleep(3)

        # Determine the canvas
        image1 = self.takeScreenshot(1.0)
        self.click("id=button")
        time.sleep(.5)
        image2 = self.takeScreenshot(1.0)
        image3 = ImageChops.difference(image1, image2)
        box = image3.getbbox()
        if box != None:
            # Take a bounding box of size at most mReftestSize
            self.mCanvas = \
                box[0], box[1], \
                min(box[2], box[0] + self.mReftestSize[0]), \
                min(box[3], box[1] + self.mReftestSize[1])
        else:
            # We failed to determine the bounding box...
            self.mCanvas = self.mReftestSize

    def takeScreenshot(self, aWaitTime = 0.5):
        # Remarks:
        #   - ImageGrab works on Windows only.
        #   - selenium::capture_entire_page_screenshot_to_string does not
        #     work in all browsers.
        data = self.capture_screenshot_to_string()
        time.sleep(aWaitTime)
        image = Image.open(StringIO.StringIO(base64.b64decode(data)))
        image = image.convert("RGB")
        if self.mCanvas != None:
          image = image.crop(self.mCanvas)
        return image

    def encodeImageToBase64(self, aImage):
        stringIO = StringIO.StringIO()
        box = (0, 0, self.mReftestSize[0], self.mReftestSize[1])
        image = aImage.crop(box)
        image.save(stringIO, "PNG")
        return "data:image/png;base64," + base64.b64encode(stringIO.getvalue())

    def visualReftest(self, aId, aType, aImage, aImageRef):
        # Compare aImage and aImageRef
        box = ImageChops.difference(aImage, aImageRef).getbbox()
        isEqual = (box == None or (box[0] == box[2] and box[1] == box[3]))

        # Return Success
        if (aType == '==' and isEqual) or (aType == '!=' and (not isEqual)):
            return True, None

        # Return failure together with base64 images of the reftest
        msg = "REFTEST TEST-UNEXPECTED-FAIL | " + aId + " | " + \
            "image comparison ("+ aType +") \n"
        if aType == '==':
            msg += "REFTEST   IMAGE 1 (TEST): " + \
                self.encodeImageToBase64(aImage) + "\n"
            msg += "REFTEST   IMAGE 2 (REFERENCE): " + \
                self.encodeImageToBase64(aImageRef) + "\n"
        elif aType == '!=':
            msg += "REFTEST   IMAGE: " + \
                self.encodeImageToBase64(aImage) + "\n"

        return False, msg

    def serializeReftest(self):
        return self.get_eval(
            "selenium.browserbot.getCurrentWindow().getMathJaxSourceMathML()")

    def treeReftest(self, aId, aType, aSource, aSourceRef):

        # Compare aSource == aSourceRef
        isEqual = (aSource == aSourceRef)

        # Return Success
        if (aType == '==' and isEqual) or (aType == '!=' and (not isEqual)):
            return True, None

        # Return failure together with a diff of the sources
        msg = "REFTEST TEST-UNEXPECTED-FAIL | " + aId + " | " + \
            "source comparison ("+ aType +") \n"

        if aType == '==':
            msg += "REFTEST   SOURCE 1 (TEST): " + \
                aSource + "\n"
            msg += "REFTEST   SOURCE 2 (REFERENCE): " + \
                aSourceRef + "\n"

            msg += "REFTEST   DIFF:\n"
            generator = difflib.unified_diff(aSource.splitlines(1),
                                             aSourceRef.splitlines(1))
            for line in generator:
                msg += line
        elif aType == '!=':
            msg += "REFTEST   SOURCE: " + \
                aSource + "\n"

        return False, msg
