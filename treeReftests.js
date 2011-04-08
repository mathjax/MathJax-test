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

function serialize(aNode)
{
    try {
        var source = (new XMLSerializer()).serializeToString(aNode);
    } catch(e) {
        if (e instanceof TypeError) {
            // XXXfred: Internet Explorer only supports XMLSerializer since
            // version 9
            source = serialize2(aNode);
        } else {
            throw e;
        }
    }

    // add linebreaks to help diffing source
    source = source.replace(/>(?!<)/g, ">\n");
    source = source.replace(/</g, "\n<");

    return source;
}

function serialize2(aNode)
{
    // a basic serializer for browsers that do not support XMLSerializer
    // it is not claimed to be complete

    var s = "";

    switch(aNode.nodeType)
    {
    case Node.TEXT_NODE:
        s += aNode.data;
        break;
        
    case Node.COMMENT_NODE:
        s += "<!--"
        s += aNode.value;
        s += "-->"
        break;

    case Node.CDATA_SECTION_NODE:
        s += "<![CDATA["
        s += aNode.value;
        s += "]]>"
        break;

    case Node.ATTRIBUTE_NODE:
        s += aNode.name;
        s += '=';
        s += '"' + aNode.value + '"';
        break;

    case Node.ELEMENT_NODE:
        s += "<";
        s += aNode.tagName;
        var attributes = aNode.attributes;
        for (var i = 0; i < attributes.length; i++) {
            s += " " + serialize2(attributes[i]);
        }
        s += ">";
        var children = aNode.childNodes;
        for (var i = 0; i < children.length; i++) {
            s += serialize2(children[i]);
        }
        s += "</";
        s += aNode.tagName;
        s += ">"
        break;

    default:
        throw "serialization error";
        break;
    }

    return s;
}

function getMathJaxSourceMathML(aNode, aClassName)
{
    try {
        var divs = aNode.getElementsByClassName(aClassName);
        if (divs.length == 0) {
            throw "MathJax_MathML not found.";
        }
        return serialize(divs[0]);
    } catch(e) {
        if (e instanceof TypeError) {
            // XXXfred Internet Explorer lacks support for
            // getElementsByClassName)
            var children = aNode.children;
            for (var i = 0; i < children.length; i++) {
                if (children[i].className == aClassName) {
                    return serialize(children[i]);
                }
            }
            throw "MathJax_MathML not found.";
        } else {
            throw e;
        }
    }
}

function initTreeReftests()
{
    var config = getConfigObject();
    // Always use native MathML for tree reftests
    config.jax = ["input/TeX", "input/MathML", "output/NativeMML"];
}

function finalizeTreeReftests()
{
    var node = document.getElementById("reftest-element");
    if (!node) {
        throw "reftest-element not found";
    }
    
    var textarea = document.createElement("textarea");
    textarea.cols = 80;
    textarea.rows = 20;
    textarea.value = getMathJaxSourceMathML(node, "MathJax_MathML");
    textarea.id = "source";
    document.body.appendChild(textarea);

    document.documentElement.className = "";
}
