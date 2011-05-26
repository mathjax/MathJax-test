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

/**
 *  @file
 *  This file is for test pages of type @ref reftest::treeReftest
 */

/**
 * serialize a node
 *
 * @tparam  Node   aNode the node to serialize
 *
 * @treturn String       an XML string describing the node
 *
 */
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

/**
 * a basic serializer for browsers that do not support XMLSerializer
 * it is not claimed to be complete.
 *
 * @tparam  Node   aNode the node to serialize
 *
 * @treturn String       an XML string describing the node
 *
 * @exception "serialization error"
 *
 */
function serialize2(aNode)
{
    var s = "";

    // XXXfred: Versions of IE <= 8 do not know the Node constants
    switch(aNode.nodeType)
    {
    case 3: // Node.TEXT_NODE:
        s += aNode.data;
        break;
        
    case 8: // Node.COMMENT_NODE:
        s += "<!--"
        s += aNode.value;
        s += "-->"
        break;

    case 4: // Node.CDATA_SECTION_NODE:
        s += "<![CDATA["
        s += aNode.value;
        s += "]]>"
        break;

    case 2: // Node.ATTRIBUTE_NODE:
          s += " " + aNode.name;
          s += '=';
          s += '"' + aNode.value + '"';
        break;

    case 1: // Node.ELEMENT_NODE:
        s += "<";
        s += aNode.tagName;
        var attributes = aNode.attributes;
        for (var i = 0; i < attributes.length; i++) {
            s += serialize2(attributes[i]);
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

/**
 * Serialize a math element inside aNode. The function looks for
 * the first descendant of class "MathJax_MathML" and then the first
 * math descendant.
 * 
 * @tparam Node    aNode the scope of the search for the math element
 *
 * @treturn String       the serialized math element
 *
 * @exception "MathJax_MathML not found."
 *
 */
function getMathJaxSourceMathML(aNode)
{
    try {
        var divs = aNode.getElementsByClassName("MathJax_MathML");
        if (divs.length == 0) {
            throw "MathJax_MathML not found.";
        }
        return serialize(divs[0].getElementsByTagName("math")[0]);
    } catch(e) {
        if (e instanceof TypeError) {
            // XXXfred Internet Explorer lacks support for
            // getElementsByClassName)
            var children = aNode.children;
            for (var i = 0; i < children.length; i++) {
                if (children[i].className == "MathJax_MathML") {
                    return serialize(children[i].
                                     getElementsByTagName("math")[0]);
                }
            }
            throw "MathJax_MathML not found.";
        } else {
            throw e;
        }
    }
}

/**
 * initialize the tree reftest
 * Basically, we set the output to native MathML, so that we can get the math
 * element and serialize it.
 *
 */
function initTreeReftests()
{
    var config = getConfigObject();
    // Always use native MathML for tree reftests
    config.jax = ["input/TeX", "input/MathML", "output/NativeMML"];
}

/**
 * finalize the tree reftest
 * The function gets the element of id "reftest-element", serialize the math
 * inside and create a textarea of id "source" with the serialization.
 *
 * @exception "reftest-element not found"
 *
 */
function finalizeTreeReftests()
{
    var node = document.getElementById("reftest-element");
    if (!node) {
        throw "reftest-element not found";
    }
    
    var textarea = document.createElement("textarea");
    textarea.cols = 80;
    textarea.rows = 20;
    textarea.value = getMathJaxSourceMathML(node);
    textarea.id = "source";
    document.body.appendChild(textarea);

    document.documentElement.className = "";
}
