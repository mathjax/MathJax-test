<!-- -*- Mode: nXML; tab-width: 2; indent-tabs-mode: nil; -*- -->
<!-- vim: set tabstop=2 expandtab shiftwidth=2 textwidth=80:  -->
<!--
   Copyright 2013-2015 MathJax Consortium, Inc.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
-->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:l="http://www.mathjax.org/namespace/LiPlus"
                exclude-result-prefixes="l">

  <!-- Default action: copy everything -->
  <xsl:template match="@* | node()">
    <xsl:copy>
      <xsl:apply-templates select="@* | node()"/>
    </xsl:copy>
  </xsl:template>

  <!-- Do not copy the element marked with the "LiPlus remove" attribute -->
  <xsl:template match="*[@l:liplusrm]">
    <xsl:apply-templates select="*"/>
  </xsl:template>

  <!-- Do not copy the attributes from the LiPlus namespace -->
  <xsl:template match="*/@l:*">
  </xsl:template>

</xsl:stylesheet>
