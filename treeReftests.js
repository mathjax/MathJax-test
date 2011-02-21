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

function serialize(aNode)
{
  try {
    source = (new XMLSerializer()).serializeToString(aNode);
  }
  catch (e) {
    // XXXfred Internet Explorer will implement XMLSerializer in version 9
    source = "[XMLSerializer not supported]";
  }
  
  // add linebreaks to help diffing source
  source = source.replace(/>(?!<)/g, ">\n")
  source = source.replace(/</g, "\n<")

  return source;
}

function getElementsByClassName(aNode, aClassName)
{
  if (aNode.getElementsByClassName) {
    return aNode.getElementsByClassName(aClassName);
	} else {
    // XXXfred not supported?
	}
}

function getMathJaxSource(aNode, aClassName)
{
   if (getElementsByClassName) {
     divs = aNode.getElementsByClassName(aClassName);
     if (divs) {
       return serialize(divs[0]);
     }
   }

   return "";
}

function getMathJaxSourceMathML()
{
  node = document.getElementById("reftest-element");
  return getMathJaxSource(node, "MathJax_MathML");
}

