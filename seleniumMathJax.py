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
@package seleniumMathJax
This module implements a selenium object augmented with features specific to
the MathJax testing framework.
"""

import time
import selenium
import string
import base64
import StringIO
from PIL import Image, ImageChops
import difflib
import urlparse

VK_TAB = 9
VK_ENTER = 10
VK_SHIFT = 16
VK_CONTROL = 17
VK_ALT = 18
VK_7 = 55
VK_8 = 56
VK_9 = 57
VK_L = 76
VK_M = 77
VK_Q = 81
VK_S = 83
VK_T = 84
VK_F4 = 115
VK_F11 = 122
VK_F12 = 123
VK_DELETE =	127

class seleniumMathJax(selenium.selenium):

    """
    @class seleniumMathJax::seleniumMathJax
    @brief a selenium object with MathJax testing framework features
    """

    def __init__(self, aHost, aPort, aMathJaxPath, aMathJaxTestPath,
                 aOperatingSystem,
                 aBrowser,
                 aBrowserMode,
                 aBrowserStartCommand, 
                 aFont,
                 aNativeMathML,
                 aTimeOut,
                 aFullScreenMode):
        """
        @fn __init__(self, aHost, aPort, aMathJaxPath, aMathJaxTestPath,
                     aOperatingSystem,
                     aBrowser,
                     aBrowserMode,
                     aBrowserStartCommand, 
                     aFont,
                     aNativeMathML,
                     aTimeOut,
                     aFullScreenMode)

        @param aHost host of the Selenium server
        @param aPort port of the Selenium server
        @param aMathJaxPath Value to assign to mMathJaxPath
        @param aMathJaxTestPath Value to assign to mMathJaxTestPath
        @param aOperatingSystem Value to assign to mOperatingSystem
        @param aBrowser Value to assign to mBrowser
        @param aBrowserMode Value to assign to mBrowserMode
        @param aBrowserStartCommand start command of the browser
        @param aFont Value to assign to mFont
        @param aNativeMathML Value to assign to mNativeMathML
        @param aTimeOut Value to assign to mTimeOut
        @param aFullScreenMode Value to assign to mFullScreenMode

        @property mMathJaxPath
        Path to MathJax
        @property mMathJaxTestPath
        Path to MathJax-test
        @property mOperatingSystem
        operating system of the slave machine: Windows, Linux, Mac
        @property mBrowser
        browser to run: Firefox, Safari, Chrome, Opera, MSIE, Konqueror
        @property mBrowserMode
        browser mode: StandardMode, Quirks, IE7, IE8, IE9
        @property mFont
        font to use: STIX, TeX, ImageTeX
        @property mNativeMathML
        whether the tests should use MathJax or the native MathML support of
        the browser
        @property mTimeOut
        time allowed before aborting a test
        @property mFullScreenMode
        whether the browser should be put in full screen mode, when possible

        @property mCanvas
        A 4-tuple defining the left, upper, right, and lower pixel coordinate
        of the browser canvas i.e the area to capture for screenshot.

        @property mReftestSize
        The dimension of reftest images. It is set to 800x1000 px, to follow
        the size of screenshots used by Mozilla
        """
        selenium.selenium.__init__(self, aHost, aPort, aBrowserStartCommand,
                                   aMathJaxTestPath)
        self.mMathJaxPath = aMathJaxPath
        self.mMathJaxTestPath = aMathJaxTestPath
        self.mOperatingSystem = aOperatingSystem
        self.mBrowser = aBrowser
        self.mBrowserMode = aBrowserMode
        self.mFont = aFont
        self.mNativeMathML = aNativeMathML
        self.mTimeOut = aTimeOut
        self.mFullScreenMode = aFullScreenMode

        self.mCanvas = None
        self.mReftestSize = (800, 1000)

    def open(self, aURI, aWaitTime = 0.5):

        """
        @fn open(self, aURI, aWaitTime = 0.5)
        @brief open a page in the browser
        
        @param aURI URI of the page to open
        @param aWaitTime time to wait

        @details This function open the specified page in the browser, appending
        the testing framework options to the query string. Then it waits for the
        'reftest-wait' removal and waits again aWaitTime. If 'reftest-error' is
        found, then a javascript error happened and is reported.

        @note The framework options are appended to the query string and
        @ref parseQueryString consider the last values found. Hence these
        framework options override those specified in the reftest manifest,
        in the URI of the test pages. If you want your test page to use a
        different configuration, do it in a preMathJax() function. Also,
        note that @ref initTreeReftests sets @ref gNativeMathML to true, so
        the query string nativeMathML is ignored for tree reftests.
        @raise Exception The javascript error that happened in the page.
        """

        # append the testing framework options to the URI
        a = urlparse.urlparse(aURI)
        query = a.query
        query += "&errorHandler=true"
        query += "&font=" + self.mFont
        if self.mNativeMathML:
            query += "&nativeMathML=true"
        query += "&mathJaxPath=" + self.mMathJaxPath
        newURI = urlparse.urlunparse((a.scheme,
                                      a.netloc,
                                      a.path,
                                      a.params,
                                      query,
                                      a.fragment))

        # open the page and wait for 'reftest-wait' removal
        selenium.selenium.open(self, newURI)
        self.wait_for_condition(
            "selenium.browserbot.getCurrentWindow().\
             document.documentElement.className != 'reftest-wait'",
            self.mTimeOut)
        time.sleep(aWaitTime)
        if (self.get_eval("selenium.browserbot.getCurrentWindow().\
             document.documentElement.className") == "reftest-error"):
            message = self.get_eval("selenium.browserbot.getCurrentWindow().\
             document.documentElement.lastChild.nodeValue")
            raise Exception, message

    def start(self):
        """
        @fn start(self)
        """
        selenium.selenium.start(self)

    def pre(self):
        """
        @fn pre(self)
        @brief initialize the testing instance

        @details This function opens the blank.html
        page and maximizes it. If the @ref mFullScreenMode is true, the page is
        put in fullscreen mode. For MSIE, the document mode is set according
        to @ref mBrowserMode.
        Then the area @ref mCanvas is determined by changing the
        background of the blank page from white to black and comparing the
        difference between the two screenshots.

        @note

        - If the environment changed between the two screenshots (for example
        the time displayed on your screen) then the canvas determination may
        fail. That's why it is recommended to launch the browser in fullscreen
        mode, when possible.

        - The control of the browser (maximize, fullscreenmode, simulation
        of keyboard press etc) by Selenium is not perfect and may fail. Sleep
        time are inserted to try to synchronize the actions, possibly causing a
        long delay before the tests actually start. Hopefully, this will be
        improved in future versions of Selenium :-)
        """
        # Open the blank page and maximize it
        self.open("blank.html", 3)
        self.window_focus()
        self.window_maximize()
        time.sleep(2)

        # For Konqueror, we remove some bars to get a true fullscreen mode
        if self.mFullScreenMode and self.mBrowser == "Konqueror":
            # Location Bar: alt+s, t, l
            self.key_down_native(VK_ALT)
            time.sleep(.1)
            self.key_press_native(VK_S)
            time.sleep(.1)
            self.key_up_native(VK_ALT)
            time.sleep(.1)
            self.key_press_native(VK_T)
            time.sleep(.1)
            self.key_press_native(VK_L)
            time.sleep(1)

            # Main Toolbar: alt+s, t, m
            self.key_down_native(VK_ALT)
            time.sleep(.1)
            self.key_press_native(VK_S)
            time.sleep(.1)
            self.key_up_native(VK_ALT)
            time.sleep(.1)
            self.key_press_native(VK_T)
            time.sleep(.1)
            self.key_press_native(VK_M)
            time.sleep(1)

            # Menu Bar: ctrl+m
            self.key_down_native(VK_CONTROL)
            time.sleep(.1)
            self.key_press_native(VK_M)
            time.sleep(.1)
            self.key_up_native(VK_CONTROL)
            time.sleep(1)

        if self.mFullScreenMode and \
           (self.mBrowser == "Firefox" or self.mBrowser == "Chrome" or \
            self.mBrowser == "Opera"   or self.mBrowser == "MSIE" or \
            self.mBrowser == "Konqueror"):
            # FullScreen Mode: 
            self.key_press_native(VK_F11)
            time.sleep(3)

        if (self.mBrowser == "MSIE" and
            not(self.mBrowserMode == "StandardMode")):
            # For MSIE, we choose the document mode

            #  opening developer tools
            self.key_down_native(VK_F12)
            time.sleep(3)

            if self.mBrowserMode == "Quirks":
                self.key_down_native(VK_ALT)
                time.sleep(.1)
                self.key_press_native(VK_Q)
                time.sleep(.1)
                self.key_up_native(VK_ALT)
                time.sleep(.1)
            elif self.mBrowserMode == "IE7":
                self.key_down_native(VK_ALT)
                time.sleep(.1)
                self.key_press_native(VK_7)
                time.sleep(.1)
                self.key_up_native(VK_ALT)
                time.sleep(.1)
            elif self.mBrowserMode == "IE8":
                self.key_down_native(VK_ALT)
                time.sleep(.1)
                self.key_press_native(VK_8)
                time.sleep(.1)
                self.key_up_native(VK_ALT)
                time.sleep(.1)
            elif self.mBrowserMode == "IE9":
                self.key_down_native(VK_ALT)
                time.sleep(.1)
                self.key_press_native(VK_9)
                time.sleep(.1)
                self.key_up_native(VK_ALT)
                time.sleep(.1)
            time.sleep(3)

            # closing developer tools
            self.key_down_native(123) # F12
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

    def post(self):
        if self.mFullScreenMode and \
           (self.mBrowser == "Firefox" or self.mBrowser == "Chrome" or \
                self.mBrowser == "Opera"   or self.mBrowser == "MSIE" or \
                self.mBrowser == "Konqueror"):
            # Leave FullScreen Mode: 
            self.key_press_native(VK_F11)
            time.sleep(3)

    def stop(self):
        """
        @fn stop(self)
        @brief stop selenium
        """
        # selenium.selenium.stop does not seem to close Konqueror/MSIE
        # correctly. Leave the browser manually instead.
        if (self.mBrowser == "Konqueror"):
            # Close the two windows with Ctrl+q
            self.key_down_native(VK_CONTROL)
            time.sleep(.1)
            self.key_press_native(VK_Q)
            time.sleep(.1)
            self.key_press_native(VK_Q)
            time.sleep(.1)
            self.key_up_native(VK_CONTROL)
            time.sleep(.1)
            time.sleep(3)
        elif (self.mBrowser == "MSIE"):
            # Close two tabs with Ctrl+F4
            self.key_down_native(VK_CONTROL)
            time.sleep(.1)
            self.key_press_native(VK_F4)
            time.sleep(.1)
            self.key_press_native(VK_F4)
            time.sleep(.1)
            self.key_up_native(VK_CONTROL)
            time.sleep(.1)
            time.sleep(3)

        selenium.selenium.stop(self)
        
    def clearBrowserData(self):
        print "clearBrowserData: not implemented"

    def takeScreenshot(self, aWaitTime = 0.5):
        """
        @fn takeScreenshot(self, aWaitTime = 0.5)
        @brief take a screenshot of the screen

        @param aWaitTime time to wait
        @return an image coded with the PIL structure

        @details This function takes a screenshot using Selenium's 
        capture_screenshot_to_string(). It waits aWaitTime and then extracts
        the area given by @ref mCanvas.

        @see http://www.pythonware.com/library/pil/handbook/
        """

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
        """
        @fn encodeImageToBase64(self, aImage)
        @brief encode an image into a base64 format
        
        @param aImage an image coded with the PIL structure
        @return a string with the Base64 format of the image, openable in a
        browser.
        """

        # XXXfred If aImage is smaller than self.mReftestSize, the rest of the
        # image is filled with black. Try to use white instead.
        stringIO = StringIO.StringIO()
        box = (0, 0, self.mReftestSize[0], self.mReftestSize[1])
        image = aImage.crop(box)
        image.save(stringIO, "PNG")
        return "data:image/png;base64," + base64.b64encode(stringIO.getvalue())

    def encodeSourceToBase64(self, aSource):
        """
        @fn encodeSourceToBase64(self, aSource)
        @brief encode a source code into a base64 format
        
        @param aSource a source code in text format
        @return a string with the Base64 format of the source, openable in a
        browser.
        """
        return ("data:text/plain;charset=utf-8;base64," +
                base64.b64encode(aSource.encode("utf-8")))

    def getMathJaxSourceMathML(self):
        """
        @fn getMathJaxSourceMathML(self)
        @brief retrieve a MathML source of a tree reftest
        
        @return the code source of the MathML element
        
        @details This function get the value of the textarea of id "source"
        in the test page. This textarea is generated by
        @ref finalizeTreeReftests 
        """
        return self.get_eval(
            "selenium.browserbot.getCurrentWindow().\
             document.getElementById('source').value")

    def getScriptReftestResult(self):
        """
        @fn getScriptReftestResult(self)
        @brief retrieve the result of a script reftest

        @return a pair (success, msg)

        @details The success is determined by verifying whether the class name
        of the document is "reftest-success". msg is the value of the textarea
        of id "results" in the test page, detailing the result of each test.
        This textarea is inserted by @ref finalizeScriptReftests.
        """

        # Strangely, get_eval converts to a string not a boolean...
        success = (self.get_eval(
            "selenium.browserbot.getCurrentWindow().\
             document.documentElement.className == 'reftest-success'")
        == "true")
        return (
            success,
            self.get_eval(
                "selenium.browserbot.getCurrentWindow().\
             document.getElementById('results').value"))
