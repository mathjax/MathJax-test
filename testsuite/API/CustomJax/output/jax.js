/*************************************************************
 *
 *  Copyright (c) 2012-2015 MathJax Consortium, Inc.
 * 
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 * 
 *      http://www.apache.org/licenses/LICENSE-2.0
 * 
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 */

(function (CUSTOM) {
  CUSTOM.Augment({
    Startup: function () {
      //  Set up event handling
      EVENT = MathJax.Extension.MathEvents.Event;
      TOUCH = MathJax.Extension.MathEvents.Touch;
      HOVER = MathJax.Extension.MathEvents.Hover;
      this.ContextMenu = EVENT.ContextMenu;
      this.Mousedown   = EVENT.AltContextMenu;
      this.Mouseover   = HOVER.Mouseover;
      this.Mouseout    = HOVER.Mouseout;
      this.Mousemove   = HOVER.Mousemove;
    },

    preTranslate: function (state) {
      var scripts = state.jax[this.id], i, m = scripts.length,
      for (i = 0; i < m; i++) {
        script = scripts[i]; if (!script.parentNode) continue;
        var prev = script.previousSibling;
        if (prev && prev.className == "MathJax_Custom") {
          prev.parentNode.removeChild(prev);
        }
        var jax = script.MathJax.elementJax;
        var ul = HTML.Element("ul", {
 	  className: "MathJax_Custom",
          id: jax.inputID+"-Frame",
          isMathJax: true,
          jaxID: this.id,
          oncontextmenu: EVENT.Menu,
          onmousedown: EVENT.Mousedown,
          onmouseover: EVENT.Mouseover,
          onmouseout: EVENT.Mouseout,
          onmousemove: EVENT.Mousemove,
	  onclick: EVENT.Click,
          ondblclick: EVENT.DblClick
        });

	if (HUB.Browser.noContextMenu) {
	  span.ontouchstart = TOUCH.start;
	  span.ontouchend = TOUCH.end;
	}

        script.parentNode.insertBefore(span, script);
      }
    },

    Translate: function (script, state) {
      if (!script.parentNode) return;
      var jax = script.MathJax.elementJax;
      var ul = document.getElementById(jax.inputID+"-Frame");
      for (t in jax.tree) {
        var li = document.createElement("li");
        li.appendChild(document.createTextNode(t));
        ul.appendChild(li);
      }
    },

    postTranslate: function (state) {
      // Not implemented
      // var scripts = state.jax[this.id];
    },

    getJaxFromMath: function (math) {
      return HUB.getJaxFor(math.nextSibling);
    },
    
    Zoom: function (jax, span, math, Mw, Mh) {
      // Not implemented
      return {Y:0, mW: mW, mH: mH, zW: zW, zH: zH};
    },

    Remove: function (jax) {
      var div = document.getElementById(jax.inputID+"-Frame");
      if (div) {
        div.parentNode.removeChild(div);
      }
    }
    
  });
  
})(MathJax.OutputJax.Custom);
