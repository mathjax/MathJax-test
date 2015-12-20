# ***** BEGIN LICENSE BLOCK *****
# Version: Apache License 2.0
#
# Copyright (c) 2011-2015 MathJax Consortium, Inc.
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
@file seleniumMathJax.py
The file for the @ref seleniumMathJax module.

@package seleniumMathJax
This module implements a selenium object augmented with features specific to
the MathJax testing framework.
"""

from config import SELENIUM_SERVER_HUB_HOST, SELENIUM_SERVER_HUB_PORT

from PIL import Image, ImageChops, ImageDraw
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver, selenium
import StringIO
import base64
import difflib
import string
import sys
import time
import urlparse
import inspect

VK_TAB = 9
VK_ENTER = 10
VK_SHIFT = 16
VK_CONTROL = 17
VK_ALT = 18
VK_1 = 49
VK_5 = 53
VK_7 = 55
VK_8 = 56
VK_9 = 57
VK_E = 69
VK_L = 76
VK_M = 77
VK_Q = 81
VK_S = 83
VK_T = 84
VK_F4 = 115
VK_F11 = 122
VK_F12 = 123
VK_DELETE = 127

class ReftestError(Exception):
    """
    @class seleniumMathJax::ReftestError
    @brief an exception class used to represent a reftest error that has been
    indicated by @ref header.js
    """

    def __init__(self, aMessage, aIsReference):
        self.mMessage = aMessage
        self.mIsReference = aIsReference
    def __str__(self):
        s = repr(self.mMessage)
        if self.mIsReference:
            s += " (from *-ref page)"
        return s

class seleniumMathJax(object):

    """
    @class seleniumMathJax::seleniumMathJax
    @brief a selenium object with MathJax testing framework features
    """

    def __init__(self, aUseWebDriver, aUseGrid,
                 aHost, aPort, aMathJaxPath, aMathJaxTestPath,
                 aOperatingSystem,
                 aBrowser,
                 aBrowserVersion,
                 aBrowserMode,
                 aBrowserPath,
                 aFont,
                 aOutputJax,
                 aTimeOut,
                 aFullScreenMode):
        """
        @fn __init__(self, aUseWebDriver, aUseGrid,
                     aHost, aPort, aMathJaxPath, aMathJaxTestPath,
                     aOperatingSystem,
                     aBrowser,
                     aBrowserVersion,
                     aBrowserMode,
                     aBrowserPath, 
                     aFont,
                     aOutputJax,
                     aTimeOut,
                     aFullScreenMode)

        @param aUseWebDriver Whether to use Selenium 2 (Webdriver)
        @param aUseGrid Whether we use grid. In that case, requests are not
        sent directly to the Selenium server on the host machine, but to
        the Selenium Hub.
        @param aHost Value to assign to @ref mHost
        @param aPort Value to assign to @ref mPort
        @param aMathJaxPath Value to assign to @ref mMathJaxPath
        @param aMathJaxTestPath Value to assign to @ref mMathJaxTestPath
        @param aOperatingSystem Value to assign to @ref mOperatingSystem
        @param aBrowser Value to assign to @ref mBrowser
        @param aBrowserVersion Value to assign to @ref mBrowserVersion
        @param aBrowserMode Value to assign to @ref mBrowserMode
        @param aBrowserPath Path to the browser executable, or "default".
        @param aFont Value to assign to @ref mFont
        @param aOutputJax Value to assign to @ref mOutputJax
        @param aTimeOut Value to assign to @ref mTimeOut
        @param aFullScreenMode Value to assign to @ref mFullScreenMode

        @see http://devel.mathjax.org/testing/web/docs/html/components.html#test-runner-config

        @property mHost
        Host of the Selenium server
        @property mPort
        Port of the Selenium server
        @property mMathJaxPath
        URI of a MathJax installation
        @property mMathJaxTestPath
        URI of a testsuite
        @property mOperatingSystem
        Operating system of the test machine
        @property mBrowser
        Name of the browser to run
        @property mBrowserVersion
        Version of the browser to run
        @property mBrowserMode
        Browser mode for Internet Explorer
        @property mFont
        font to use: STIX, TeX, ImageTeX
        @property mOutputJax
        output Jax to use: HTML-CSS, SVG, NativeMML
        @property mTimeOut
        time allowed before aborting a test
        @property mFullScreenMode
        whether the browser should be put in full screen mode, when possible
        @property mCanvas
        A 4-tuple defining the left, upper, right, and lower pixel coordinate
        of the area to capture. Assumed to be of size at most mReftestSize.
        @property mReftestSize
        The dimension of reftest images. It is set to 800x1000 px, to follow
        the size of screenshots used by Mozilla
        """
        self.mHost = aHost
        self.mPort = aPort
        self.mMathJaxPath = aMathJaxPath
        self.mMathJaxTestPath = aMathJaxTestPath
        self.mOperatingSystem = aOperatingSystem
        self.mBrowser = aBrowser
        self.mBrowserVersion = aBrowserVersion
        self.mBrowserMode = aBrowserMode
        self.mFont = aFont
        self.mOutputJax = aOutputJax
        self.mTimeOut = aTimeOut
        self.mFullScreenMode = aFullScreenMode

        self.mCanvas = None
        self.mReftestSize = (800, 1000)

        if (aUseGrid):
            host = SELENIUM_SERVER_HUB_HOST
            port = SELENIUM_SERVER_HUB_PORT
        else:
            host = aHost
            port = aPort

        if (aUseGrid or aUseWebDriver):
            if aBrowser == "Firefox":
                desiredCapabilities = webdriver.DesiredCapabilities.FIREFOX
            elif aBrowser == "Chrome":
                desiredCapabilities = webdriver.DesiredCapabilities.CHROME
            elif aOperatingSystem == "Windows" and aBrowser == "MSIE":
                desiredCapabilities = \
                    webdriver.DesiredCapabilities.INTERNETEXPLORER
            elif aBrowser == "Opera":
                desiredCapabilities = webdriver.DesiredCapabilities.OPERA
            elif aBrowser == "HTMLUnit":
                desiredCapabilities = \
                    webdriver.DesiredCapabilities.HTMLUNITWITHJS
            elif aBrowser == "PhantomJS":
                desiredCapabilities = webdriver.DesiredCapabilities.PHANTOMJS
            elif aOperatingSystem == "Mac" and aBrowser == "iPhone":
                desiredCapabilities = webdriver.DesiredCapabilities.IPHONE
            elif aOperatingSystem == "Mac" and aBrowser == "iPad":
                desiredCapabilities = webdriver.DesiredCapabilities.IPAD
            elif aOperatingSystem == "Linux" and aBrowser == "Android":
                desiredCapabilities = webdriver.DesiredCapabilities.ANDROID
            elif ((aOperatingSystem == "Windows" or
                   aOperatingSystem == "Mac") and aBrowser == "Safari"):
                desiredCapabilities = webdriver.DesiredCapabilities.SAFARI
            else:
                raise Exception("Webdriver: OS/browser not available")

            desiredCapabilities["platform"] = aOperatingSystem.upper()

            if aBrowserVersion == "default":
                desiredCapabilities["version"] = ""
            else:
                desiredCapabilities["version"] = aBrowserVersion

            if aBrowserPath != "default":
                # TODO: add support for other browsers
                if aBrowser == "Chrome":
                    desiredCapabilities["chrome.binary"] = aBrowserPath
                else:
                    raise Exception("Webdriver: browserPath is not supported")

            self.mWebDriver = webdriver.Remote("http://" + host + ":" +
                                               str(port) + "/wd/hub",
                                               desiredCapabilities)
            self.mWebDriver.implicitly_wait(aTimeOut / 1000)
            self.mWebDriver.set_script_timeout(aTimeOut / 1000)
            self.mSelenium = selenium(host, port, '*webdriver',
                                      aMathJaxTestPath)
            self.mCanvas = 0, 0, self.mReftestSize[0], self.mReftestSize[1]
        else:
            self.mWebDriver = None
            if aBrowser == "Firefox":
                startCommand = "*firefox"
            elif (aOperatingSystem == "Windows" or
                  aOperatingSystem == "Mac") and aBrowser == "Safari":
                startCommand = "*safariproxy"
            elif aBrowser == "Chrome":
                startCommand = "*googlechrome"
            elif aBrowser == "Opera":
                startCommand = "*opera"
            elif aOperatingSystem == "Windows" and aBrowser == "MSIE":
                startCommand = "*iexploreproxy"
            elif aOperatingSystem == "Linux" and aBrowser == "Konqueror":
                startCommand = "*konqueror"
            else:
                startCommand = "*custom"
                
            if aBrowserVersion != "default":
                raise Exception("Selenium 1: browserVersion is not supported")

            if aBrowserPath == "default":
                if startCommand == "*custom":
                    raise Exception("Selenium 1: OS/browser not available ")
      
                # XXXfred: support for Konqueror is broken
                if aOperatingSystem == "Linux" and aBrowser == "Konqueror":
                    startCommand = startCommand + " /usr/bin/konqueror" 
            else:
                startCommand = startCommand + " " + aBrowserPath
              
            self.mSelenium = selenium(host, port, startCommand,
                                      aMathJaxTestPath)

    def open(self, aURI, aWaitTime = 0.5, aIsReference = False):

        """
        @fn open(self, aURI, aWaitTime = 0.5, aIsReference = False)
        @brief open a page in the browser
        
        @param aURI URI of the page to open
        @param aWaitTime time to wait
        @param aIsReference whether this is a reference page of a test

        @details This function open the specified page in the browser, appending
        the testing framework options to the query string. Then it waits for the
        'reftest-wait' removal and waits again aWaitTime. If 'reftest-error' is
        found, then a javascript error happened and is reported.

        @note The framework options are appended to the query string and
        @ref parseQueryString consider the last values found. Hence these
        framework options override those specified in the reftest manifest,
        in the URI of the test pages. If you want your test page to use a
        different configuration, do it in a preMathJax() function. Also,
        note that @ref initTreeReftests sets @ref gOutputJax to NativeMML, so
        the query string outputJax is ignored for tree reftests.
        @exception Exception The javascript error that happened in the page.
        """

        # append the testing framework options to the URI
        a = urlparse.urlparse(aURI)
        query = a.query
        query += "&errorHandler=true"
        query += "&font=" + self.mFont
        query += "&outputJax=" + self.mOutputJax
        query += "&mathJaxPath=" + self.mMathJaxPath
        newURI = urlparse.urlunparse((a.scheme,
                                      a.netloc,
                                      a.path,
                                      a.params,
                                      query,
                                      a.fragment))

        # open the page and wait for 'reftest-wait' removal
        if self.mWebDriver:
            self.mWebDriver.get(self.mMathJaxTestPath + newURI)

            # wait_for_condition no longer exists in Selenium 2. Use an explicit
            # wait method. We wait for the insertion of an element with id
            # "webdriver_test_complete".
            WebDriverWait(self.mWebDriver, self.mTimeOut / 1000).\
                until(lambda x: x.find_element_by_id("webdriver_test_complete"))

            if (self.mWebDriver.execute_script(\
                    "return document.documentElement.className ==\
                     'reftest-error'")):
                message = self.mWebDriver.\
                    execute_script("return document.documentElement.\
                                    lastChild.nodeValue")
                raise ReftestError(message, aIsReference)
        else:
            self.mSelenium.open(newURI)
            self.mSelenium.wait_for_condition(
                "selenium.browserbot.getCurrentWindow().\
                 document.documentElement.className != 'reftest-wait'",
                self.mTimeOut)
            time.sleep(aWaitTime)
            if (self.mSelenium.get_eval("selenium.browserbot.\
                getCurrentWindow().document.documentElement.className") ==
                "reftest-error"):
                message = self.mSelenium.get_eval("selenium.browserbot.\
                          getCurrentWindow().document.documentElement.\
                          lastChild.nodeValue")
                raise ReftestError(message, aIsReference)

    def start(self):
        """
        @fn start(self)
        @brief start Selenium
        """
        if self.mWebDriver:
            self.mSelenium.start(driver=self.mWebDriver)
        else:
            self.mSelenium.start()

#     def chooseInternetExplorerDocumentMode(self):
#         """
#         @fn chooseInternetExplorerDocumentMode(self)
#         @brief function to choose the internet explorer mode
#         """
#         #  open developer tools
#         self.mSelenium.key_down_native(VK_F12)
#         time.sleep(3)
# 
#         if self.mBrowserMode == "Quirks":
#             self.mSelenium.key_down_native(VK_ALT)
#             time.sleep(.1)
#             self.mSelenium.key_press_native(VK_Q)
#             time.sleep(.1)
#             self.mSelenium.key_up_native(VK_ALT)
#             time.sleep(.1)
#         elif self.mBrowserMode == "IE7":
#             self.mSelenium.key_down_native(VK_ALT)
#             time.sleep(.1)
#             self.mSelenium.key_press_native(VK_7)
#             time.sleep(.1)
#             self.mSelenium.key_up_native(VK_ALT)
#             time.sleep(.1)
#         elif self.mBrowserMode == "IE8":
#             self.mSelenium.key_down_native(VK_ALT)
#             time.sleep(.1)
#             self.mSelenium.key_press_native(VK_8)
#             time.sleep(.1)
#             self.mSelenium.key_up_native(VK_ALT)
#             time.sleep(.1)
#         elif self.mBrowserMode == "IE9":
#             self.mSelenium.key_down_native(VK_ALT)
#             time.sleep(.1)
#             self.mSelenium.key_press_native(VK_9)
#             time.sleep(.1)
#             self.mSelenium.key_up_native(VK_ALT)
#             time.sleep(.1)
#             time.sleep(3)
# 
#         # close developer tools
#         self.mSelenium.key_down_native(123) # F12
#         time.sleep(3)

    def chooseInternetExplorerDocumentMode(self):
        """
        @fn chooseInternetExplorerDocumentMode(self)
        @brief function to choose the internet explorer mode
        """

        #
        #  Open developer tools
        #  (They must be set to open in a separate window, and
        #  have the "Persist Emulation" icon selected)
        #  
        self.mSelenium.key_press_native(VK_F12)
        time.sleep(3)

        #
        #  Select Emulation page
        #
        self.mSelenium.key_down_native(VK_CONTROL)
        time.sleep(.1)
        self.mSelenium.key_press_native(VK_8)
        time.sleep(.1)
        self.mSelenium.key_up_native(VK_CONTROL)
        time.sleep(.1)

        #
        #  Tab to Document Mode
        #
        self.mSelenium.key_press_native(VK_TAB)
        time.sleep(.1)

        #
        #  Select mode
        #
        if self.mBrowserMode == "Quirks":
            self.mSelenium.key_press_native(VK_5)
        elif self.mBrowserMode == "IE7":
            self.mSelenium.key_press_native(VK_7)
        elif self.mBrowserMode == "IE8":
            self.mSelenium.key_press_native(VK_8)
        elif self.mBrowserMode == "IE9":
            self.mSelenium.key_press_native(VK_9)
        elif self.mBrowserMode == "IE10":
            self.mSelenium.key_press_native(VK_1)
        elif self.mBrowserMode == "IE11":
            self.mSelenium.key_press_native(VK_E)

        time.sleep(.1)
        time.sleep(3)

        #
        #  Close developer tools
        #
        self.mSelenium.key_down_native(VK_ALT)
        time.sleep(.1)
        self.mSelenium.key_press_native(VK_F4)
        time.sleep(.1)
        self.mSelenium.key_up_native(VK_ALT)
        time.sleep(3)

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

        if self.mWebDriver:
            # Only open the blank page...
            self.open("blank.html")

            if (self.mBrowser == "MSIE" and
                not(self.mBrowserMode == "default")):
                # For MSIE, we choose the document mode
                self.chooseInternetExplorerDocumentMode()

            if (self.mBrowser == "Opera"):
                # Screenshots taken by OperaDriver have random noise at the
                # bottom. Hence we reduce the dimension of the canvas.
                self.mCanvas = 0, 0, self.mReftestSize[0], 600
        else:
            # Open the blank page and maximize it
            self.open("blank.html", 3)
            self.mSelenium.window_focus()
            self.mSelenium.window_maximize()
            time.sleep(2)

            # For Konqueror, we remove some bars to get a true fullscreen mode
            if self.mFullScreenMode and self.mBrowser == "Konqueror":
                # Location Bar: alt+s, t, l
                self.mSelenium.key_down_native(VK_ALT)
                time.sleep(.1)
                self.mSelenium.key_press_native(VK_S)
                time.sleep(.1)
                self.mSelenium.key_up_native(VK_ALT)
                time.sleep(.1)
                self.mSelenium.key_press_native(VK_T)
                time.sleep(.1)
                self.mSelenium.key_press_native(VK_L)
                time.sleep(1)

                # Main Toolbar: alt+s, t, m
                self.mSelenium.key_down_native(VK_ALT)
                time.sleep(.1)
                self.mSelenium.key_press_native(VK_S)
                time.sleep(.1)
                self.mSelenium.key_up_native(VK_ALT)
                time.sleep(.1)
                self.mSelenium.key_press_native(VK_T)
                time.sleep(.1)
                self.mSelenium.key_press_native(VK_M)
                time.sleep(1)

                # Menu Bar: ctrl+m
                self.mSelenium.key_down_native(VK_CONTROL)
                time.sleep(.1)
                self.mSelenium.key_press_native(VK_M)
                time.sleep(.1)
                self.mSelenium.key_up_native(VK_CONTROL)
                time.sleep(1)

            if self.mFullScreenMode and \
                    (self.mBrowser == "Firefox" or
                     self.mBrowser == "Chrome" or
                     self.mBrowser == "Opera" or
                     self.mBrowser == "MSIE" or
                     self.mBrowser == "Konqueror"):
                    # FullScreen Mode: 
                    self.mSelenium.key_press_native(VK_F11)
                    time.sleep(3)

            if (self.mBrowser == "MSIE" and
                not(self.mBrowserMode == "default")):
                self.chooseInternetExplorerDocumentMode()

            # Determine the canvas
            image1 = self.takeScreenshot(1.0)
            self.mSelenium.click("id=button")
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
                # We failed to determine the bounding box: use mReftestSize
                self.mCanvas = 0, 0, self.mReftestSize[0], self.mReftestSize[1]

    def post(self):
        if (not self.mWebDriver):
            if self.mFullScreenMode and \
                    (self.mBrowser == "Firefox" or
                     self.mBrowser == "Chrome" or
                     self.mBrowser == "Opera" or
                     self.mBrowser == "MSIE" or
                     self.mBrowser == "Konqueror"):
                    # Leave FullScreen Mode: 
                    self.mSelenium.key_press_native(VK_F11)
                    time.sleep(3)

    def stop(self):
        """
        @fn stop(self)
        @brief stop selenium
        """
        if self.mWebDriver:
            self.mWebDriver.quit()
        else:
            # selenium.stop does not seem to close Konqueror/MSIE
            # correctly. Leave the browser manually instead.
            if (self.mBrowser == "Konqueror"):
                # Close the two windows with Ctrl+q
                self.mSelenium.key_down_native(VK_CONTROL)
                time.sleep(.1)
                self.mSelenium.key_press_native(VK_Q)
                time.sleep(.1)
                self.mSelenium.key_press_native(VK_Q)
                time.sleep(.1)
                self.mSelenium.key_up_native(VK_CONTROL)
                time.sleep(.1)
                time.sleep(4)
            elif (self.mBrowser == "MSIE"):
                # Close two tabs with Ctrl+F4
                self.mSelenium.key_down_native(VK_CONTROL)
                time.sleep(.1)
                self.mSelenium.key_press_native(VK_F4)
                time.sleep(.1)
                self.mSelenium.key_press_native(VK_F4)
                time.sleep(.1)
                self.mSelenium.key_up_native(VK_CONTROL)
                time.sleep(.1)
                time.sleep(4)

                self.mSelenium.stop()
        
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

        # Get the base64-encoded image from Selenium
        if self.mWebDriver:
            data = self.mWebDriver.get_screenshot_as_base64()
        else:
            data = self.mSelenium.capture_screenshot_to_string()
            time.sleep(aWaitTime)

        image = Image.open(StringIO.StringIO(base64.b64decode(data)))
        image = image.convert("RGB")

        if (self.mCanvas == None):
            # This is used in function "pre" for Selenium 1, to determine
            # the browser canvas. In that case, we return the whole screenshot.
            return image

        # Only keep the rectangular region given by mCanvas
        image = image.crop(self.mCanvas)

        # The Internet Explorer Driver sends screenshots with black background
        # at the bottom. So only keep the "bounding box".
        if (self.mWebDriver and self.mBrowser == "MSIE"):
            box = image.getbbox()
            if box:
                image = image.crop(box)

        # Verify if the image has the size mReftestSize
        size = image.size
        if (size[0] == self.mReftestSize[0] and
            size[1] == self.mReftestSize[1]):
            return image

        # Otherwise, fill the rest of the image with white...
        image = image.crop((0, 0, self.mReftestSize[0], self.mReftestSize[1]))
        draw = ImageDraw.Draw(image)
        white = (255, 255, 255)

        # Draw a white rectangle on the right hand side
        if (size[0] < self.mReftestSize[0]):
            draw.rectangle((size[0], 0,
                            self.mReftestSize[0], self.mReftestSize[1]),
                           fill=white)

        # Draw a white rectangle a the bottom                            
        if (size[1] < self.mReftestSize[1]):
            draw.rectangle((0, size[1],
                            size[0], self.mReftestSize[1]),
                           fill=white)
        del draw
        
        return image

    def encodeImageToBase64(self, aImage):
        """
        @fn encodeImageToBase64(self, aImage)
        @brief encode an image into a base64 format
        
        @param aImage an image coded with the PIL structure
        @return a string with the Base64 format of the image, openable in a
        browser.
        """
        stringIO = StringIO.StringIO()
        aImage.save(stringIO, "PNG")
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
        if self.mWebDriver:
            return self.mWebDriver.\
                execute_script("return document.getElementById('source').value")
        else:
            return self.mSelenium.get_eval(
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

        if self.mWebDriver:
            success = self.mWebDriver.\
                execute_script("return document.documentElement.className ==\
                              'reftest-success'")
            return (success,
                    self.mWebDriver.execute_script(
                    "return document.getElementById('results').value"))
        else:
            # Strangely, get_eval converts to a string not a boolean...
            success = (self.mSelenium.get_eval(
                    "selenium.browserbot.getCurrentWindow().\
                     document.documentElement.className == 'reftest-success'")
                       == "true")
            return (
                success,
                self.mSelenium.get_eval(
                    "selenium.browserbot.getCurrentWindow().\
                     document.getElementById('results').value"))
