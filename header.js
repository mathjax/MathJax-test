/* -*- Mode: Java; tab-width: 2; indent-tabs-mode:nil; -*- */
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
 * ***** END LICENSE BLOCK ***** */

function getDefaultMathJaxPath()
{
src = location.protocol + "//" + location.host + location.pathname;
return src.substring(0, src.search(/MathJax-test/)) + "MathJax/";
}

var gMathJaxPath = getDefaultMathJaxPath();
var gUseNativeMathML = false;

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
    if (paramname == "useNativeMathML") {
      gUseNativeMathML = (paramvalue == "true");
    }
  }
}

function startMathJax()
{
  var script = document.createElement("script");
  script.type = "text/javascript";
  src = location.href;
  script.src = gMathJaxPath + "MathJax.js";
  var config =
    'MathJax.Hub.Config({' +
    'messageStyle: "none",' +
    'extensions: ["tex2jax.js", "mml2jax.js"],' +
    'jax: ["input/TeX", "input/MathML", ' +
       (gUseNativeMathML ? '"output/NativeMML"' : '"output/HTML-CSS"') + ']' +
    '});' +
    'MathJax.Hub.Startup.onload();' +
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

parseQueryString();
// XXXfred: Reftests executed with Mozilla's runreftest.py should really
// call startMathJax when the MozReftestInvalidate event happens. 
if (window.addEventListener) {
  window.addEventListener("load", startMathJax, false);
} else if (window.attachEvent){
  window.attachEvent("onload", startMathJax);
}

