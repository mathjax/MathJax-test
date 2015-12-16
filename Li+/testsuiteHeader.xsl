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
                xmlns:h="http://www.w3.org/1999/xhtml">

  <xsl:param name="testsuiteHeader">header.js</xsl:param>

  <xsl:template match="@* | node()">
    <xsl:copy>
      <xsl:apply-templates select="@* | node()"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="h:html">
    <xsl:copy>
      <xsl:attribute name="class">
        <xsl:text>reftest-wait</xsl:text>
      </xsl:attribute>
      <xsl:apply-templates select="@* | node()"/>
    </xsl:copy>
  </xsl:template>    

  <xsl:template match="h:head">
    <xsl:copy>
      <xsl:apply-templates select="@* | node()"/>
      <h:script type="text/javascript">
        <xsl:attribute name="src">
          <xsl:value-of select="$testsuiteHeader"/>
        </xsl:attribute>
      </h:script>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
