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

MathJax.OutputJax.Custom = MathJax.OutputJax({
  id: "customOutput",
});
MathJax.OutputJax.Custom.Augment({
  Init: function (aVersion, aDirectory) {
    this.version = aVersion;
    this.directory = aDirectory;
  }
}

if (!MathJax.Hub.config.delayJaxRegistration) {
  MathJax.OutputJax.Custom.Register("jax/custom")
}

MathJax.OutputJax.Custom.loadComplete("config.js");
