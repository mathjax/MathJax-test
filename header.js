/* -*- Mode: Javascript; tab-width: 2; indent-tabs-mode:nil; -*- */
/* vim: set ts=2 et sw=2 tw=80: */
/* ***** BEGIN LICENSE BLOCK *****
   /* Version: Apache License 2.0
   *
   * Copyright (c) 2011 Design Science, Inc.
   *
   * Licensed under the Apache License, Version 2.0 (the "License");
   * you may not use this file except in compliance with the License.
   * You may obtain a copy of the License at
   *
   * http://www.apache.org/licenses/LICENSE-2.0
   *
   * Unless required by applicable law or agreed to in writing, software
   * distributed under the License is distributed on an "AS IS" BASIS,
   * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   * See the License for the specific language governing permissions and
   * limitations under the License.
   *
   * Contributor(s):
   *   Frederic Wang <fred.wang@free.fr> (original author)
   *
   * ***** END LICENSE BLOCK ***** */

var gMathJaxPath;
var gNativeMathML = false;
var gFont = "STIX";
var gConfigObject;

function getDefaultMathJaxPath()
{
    src = location.protocol + "//" + location.host + location.pathname;
    return src.substring(0, src.search(/MathJax-test/)) + "MathJax/";
}

function parseQueryString()
{
    var query = location.search.substring(1);
    var pairs = query.split("&");
    for(var i = 0; i < pairs.length; i++) {
        var pos = pairs[i].indexOf("=");
        if (pos == -1) {
            continue;
        }
        var paramname = pairs[i].substring(0, pos);
        var paramvalue = pairs[i].substring(pos + 1);
        if (paramname == "mathJaxPath") {
            gMathJaxPath = paramvalue;
        }
        if (paramname == "font") {
            gFont = paramvalue;
        }
        if (paramname == "nativeMathML") {
            gNativeMathML = (paramvalue == "true");
        }
    }
}

function defaultConfigObject()
{
  return {
      messageStyle: "none",

      extensions: ["tex2jax.js",  "mml2jax.js"],

      jax: ["input/TeX", "input/MathML",
            (gNativeMathML ? "output/NativeMML" : "output/HTML-CSS")],

      "HTML-CSS": {
          availableFonts: [(gFont == "ImageTeX" ? "" : gFont)],
          preferredFont: null,
          webFont: null
      },
  
      TeX: {
          extensions: ["AMSmath.js", "AMSsymbols.js"]
      }
  }
}

function getConfigObject()
{
    return gConfigObject;
}

function setConfigObject(aConfigObject)
{
    gConfigObject = aConfigObject;
}

function startMathJax()
{
    var script = document.createElement("script");
    script.type = "text/javascript";
    src = location.href;
    script.src = gMathJaxPath + "MathJax.js";

    var config =
        'MathJax.Hub.Config(getConfigObject());' +
        'MathJax.Hub.Startup.onload();';

    if (window.postMathJax) {
      config +=
        'MathJax.Hub.Queue(postMathJax);';
    }
    
    config +=
    'MathJax.Hub.Queue(function () {' +
    'document.documentElement.className = "";' +
    '});';

    if (window.opera) {
        script.innerHTML = config;
    } else {
        script.text = config;
    }

    document.getElementsByTagName("head")[0].appendChild(script);
}

gMathJaxPath = getDefaultMathJaxPath();
parseQueryString();
setConfigObject(defaultConfigObject());
if (window.preMathJax) {
    preMathJax();
}
// XXXfred: Reftests executed with Mozilla's runreftest.py should really
// call startMathJax when the MozReftestInvalidate event happens. 
if (window.addEventListener) {
    window.addEventListener("load", startMathJax, false);
} else if (window.attachEvent){
    window.attachEvent("onload", startMathJax);
}
