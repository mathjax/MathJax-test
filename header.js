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

function getCurrentPath()
{
    return location.protocol + "//" + location.host + location.pathname;
}

function getCurrentDirectory()
{
    src = getCurrentPath();
    return src.substring(0, src.lastIndexOf("/") + 1);
}

function getDefaultMathJaxPath()
{
    src = getCurrentPath();
    return src.substring(0, src.indexOf("MathJax-test")) + "MathJax/";
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

function getQueryString(aParamName)
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
        if (paramname == aParamName) {
            return paramvalue;
            break;
        }
    }

    return null;
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

function startMathJax()
{
    // Width of screenshots used by Mozilla
    document.body.style.width = "800px";
    document.body.style.height = "1000px";
    document.body.style.border = document.body.style.margin = "0px";

    if (window.initTreeReftests) {
        initTreeReftests();
    }

    if (window.preMathJax) {
        preMathJax();
    }

    var script1 = document.createElement("script");
    var script2 = document.createElement("script");
    script1.type = "text/x-mathjax-config";
    script2.type = "text/javascript";
    script2.src = gMathJaxPath + "MathJax.js?config=default";

    var config =
        'MathJax.Message.Remove();' + // XXXfred workaround for issue 115
        'MathJax.Hub.Config(getConfigObject());' +
        'MathJax.Hub.Startup.onload();';

    if (window.postMathJax) {
      config +=
        'MathJax.Hub.Queue(postMathJax);';
    }
    
    config +=
        'MathJax.Hub.Queue(finalizeTest);';

    if (window.opera) {
        script1.innerHTML = config;
    } else {
        script1.text = config;
    }

    var head = document.getElementsByTagName("head")[0];
    head.appendChild(script1);
    head.appendChild(script2);
}

function finalizeTest()
{
    // The finalize function is not directly called after postMathJax but put
    // in the queue, just in case new actions have been added during the test.
    MathJax.Hub.Queue(function () {
        if (window.finalizeTreeReftests) {
            finalizeTreeReftests();
        } else if (window.finalizeScriptReftests) {
            finalizeScriptReftests();
        } else {
            document.documentElement.className = "";
        }
    });
}

gMathJaxPath = getDefaultMathJaxPath();
parseQueryString();
gConfigObject = defaultConfigObject();
if (window.addEventListener) {
    window.addEventListener("load", startMathJax, false);
} else if (window.attachEvent){
    window.attachEvent("onload", startMathJax);
}

