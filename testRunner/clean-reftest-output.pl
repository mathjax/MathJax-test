#!/usr/bin/perl
# -*- Mode: Perl; tab-width: 2; indent-tabs-mode: nil; -*-
# vim: set shiftwidth=4 tabstop=8 autoindent expandtab:
# ***** BEGIN LICENSE BLOCK *****
# Version: MPL 1.1/GPL 2.0/LGPL 2.1
#
# The contents of this file are subject to the Mozilla Public License Version
# 1.1 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
# http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
# The Original Code is clean-reftest-report.pl.
#
# The Initial Developer of the Original Code is the Mozilla Foundation.
# Portions created by the Initial Developer are Copyright (C) 2007
# the Initial Developer. All Rights Reserved.
#
# Contributor(s):
#   L. David Baron <dbaron@dbaron.org>, Mozilla Corporation (original author)
#   Frederic Wang <fred.wang@free.fr>
#
# Alternatively, the contents of this file may be used under the terms of
# either the GNU General Public License Version 2 or later (the "GPL"), or
# the GNU Lesser General Public License Version 2.1 or later (the "LGPL"),
# in which case the provisions of the GPL or the LGPL are applicable instead
# of those above. If you wish to allow use of your version of this file only
# under the terms of either the GPL or the LGPL, and not to allow others to
# use your version of this file under the terms of the MPL, indicate your
# decision by deleting the provisions above and replace them with the notice
# and other provisions required by the GPL or the LGPL. If you do not delete
# the provisions above, a recipient may use your version of this file under
# the terms of any one of the MPL, the GPL or the LGPL.
#
# ***** END LICENSE BLOCK *****

# This script is intended to be run over the standard output of a
# reftest run.  It will extract the parts of the output run relevant to
# reftest and convert it to an HTML page.

use strict;
use URI::Escape;

# root of the test framework
my $root = "/MathJax-test/";

# counter of tests
my $N_TESTS = 0;

# information for failure types
# [string in input file, class name, background color, counter of tests]
my @testTypes = (
 ["PASS", "pass", "lightgreen", 0],
 ["UNEXPECTED-FAIL", "unexpected_fail", "red", 0],
 ["UNEXPECTED-PASS", "unexpected_pass", "orange", 0],
 ["KNOWN-FAIL", "known_fail", "yellow", 0],
 ["PASS(EXPECTED RANDOM)", "random_pass", "blue", 0],
 ["KNOWN-FAIL(EXPECTED RANDOM)", "random_fail", "deeppink", 0]
);

################################################################################
# HTML header

print <<EOM
<!DOCTYPE html> 
<html>
<head>
<title>reftest output</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<style type="text/css">
  a {
    color: #005;
  }
EOM
;

# define CSS style for failure types
for(my $i = 0; $i <= $#testTypes ; $i++) {
print <<EOM
  div.$testTypes[$i][1] {
    background: $testTypes[$i][2];
    margin: .5em;
  }
EOM
;
}

print <<EOM
</style>
</head>
EOM
;
################################################################################
# HTML body

print <<EOM
<body onload="topOfPage()">
<div style="position: absolute; left: 0; top: 250px;
            font-family: monospace; white-space: pre;">
EOM
;

my $state = 0;
my $unparsedContent;
my $parsedContent;

while (<>) {
    next unless /^REFTEST/;
    chomp;
    chop if /\r$/;

# XXXfred: to be consistent with the IMAGE reftest, should we compute the diff
# in reftest-analyser (rather than in the Python program) using
# http://code.google.com/p/google-diff-match-patch/?

    if ($state == 0) {
        $unparsedContent = $_;
        
        if (/(TEST-)([^\|]*) \| ([^\|]*) \|(.*)/) {
            $N_TESTS++;
            for(my $i = 0; $i <= $#testTypes ; $i++) {
                if ($2 eq $testTypes[$i][0]) {
                    $testTypes[$i][3]++;
                    $unparsedContent;
                    s,(TEST-)([^\|]*) \| ([^\|]*) \|(.*),\1\2: <a href="$root\3">\3</a>\4,;
                    $parsedContent = "<div class=\"$testTypes[$i][1]\">" . $_;
                    last;
                }
            }
            if (!/TEST-PASS/ && /image|source comparison/) {
                $state = 1;
            } else {
                $unparsedContent = "";
                $state = 4;
            }
        } else {
            print "$unparsedContent\n";
        }
    } elsif ($state == 1) {
        if (/(IMAGE 1[^:]*): (data:.*)/) {
            $unparsedContent .= $_;
            s,(IMAGE[^:]*): (data:.*),<a href="\2">\1</a>,;
            $parsedContent .= $_;
            $state = 2;
        } elsif (/(IMAGE): (data:.*)/) {
            $unparsedContent .= $_;
            s,(IMAGE[^:]*): (data:.*),<a href="\2">\1</a>,;
            $parsedContent .= $_;
            $state = 4;
        } elsif (/(SOURCE 1[^:]*): (data:.*)/) {
            # $unparsedContent .= $_;
            s,(SOURCE[^:]*): (data:.*),<a href="\2">\1</a>,;
            $parsedContent .= $_;
            $state = 2;
        } elsif (/(SOURCE): (data:.*)/) {
            # $unparsedContent .= $_;
            s,(SOURCE[^:]*): (data:.*),<a href="\2">\1</a>,;
            $parsedContent .= $_;
            $unparsedContent = "";
            $state = 4;
        }
    } elsif ($state == 2) {
        if (/(IMAGE 2[^:]*): (data:.*)/) {
            $unparsedContent .= $_;
            s,(IMAGE[^:]*): (data:.*),<a href="\2">\1</a>,;
            $parsedContent .= $_;
            $state = 4;
        } elsif (/(SOURCE 2[^:]*): (data:.*)/) {
            # $unparsedContent .= $_;
            s,(SOURCE[^:]*): (data:.*),<a href="\2">\1</a>,;
            $parsedContent .= $_;
            $state = 3;
        }
    } elsif ($state == 3) {
        if (/(DIFF): (data:.*)/) {
            # $unparsedContent .= $_;
            s,(DIFF): (data:.*),<a href="\2">\1</a>,;
            $parsedContent .= $_;
            $state = 4;
            $unparsedContent = "";
        }
    }

    if ($state == 4) {
        if ($unparsedContent) {
            $parsedContent .= "\nREFTEST   <a href=\"".$root;
            $parsedContent .= "web/reftest-analyzer.xhtml#log=";
            $parsedContent .= uri_escape(uri_escape($unparsedContent));
            $parsedContent .= "\">DIFF</a>";
        }
        $parsedContent = "$parsedContent</div>";
        print $parsedContent;
        $state = 0;
    } else {
        $parsedContent .= "\n";
        $unparsedContent .= "\n";
    }
}

print <<EOM
  </div>
EOM
;

################################################################################
# Result summary

print <<EOM
  <div style="position: fixed; left: 0; top: 0; width: 100%; height: 250px;
              background: #f2f2f2;">

      <div style="float: left;">
        <h1 style="font-family: 'Trebuchet MS', sans-serif; font-weight: normal;
                   color: #20435c; background-color: #f2f2f2;">
            Reftest Output</h1>
        <input type="button" onclick="previousError()" value="Previous Error"/>
        <input type="button" onclick="topOfPage()" value="Top"/>
        <input type="button" onclick="nextError()" value="Next Error"/>
      </div>

      <div>
      <svg width="700" height="250">
        <g transform="translate(15,15)">
          <circle cx="100" cy="100" r="100"
                  style="fill: $testTypes[0][2]; stroke: black;"/>
EOM
;

# Draw the sectors and legend
# XXXfred If all the result stati are equal, the disk is painted with the PASS
# color, even if the status are not PASS.
if ($N_TESTS > 0) {
    my $s;
    my $e = $N_TESTS / 3; # random starting angle
    for(my $i = 0; $i <= $#testTypes ; $i++) {
        $s = $e;
        $e += $testTypes[$i][3];
        drawSector($s, $e, $testTypes[$i][2]);
        drawLegend($i);
    }
}

print <<EOM
        </g>
      </svg>
      </div>
  </div>
EOM
;

sub drawSector {
  my($start, $end, $color) = @_;
  my $c = 2 * 3.1415926535 / $N_TESTS;
  my $x1 = 100 * (1 + cos($c * $start));
  my $y1 = 100 * (1 - sin($c * $start));
  my $x2 = 100 * (1 + cos($c * $end));
  my $y2 = 100 * (1 - sin($c * $end));
  my $large_arc = ((($end - $start) > $N_TESTS/2) ? 1 : 0);
print <<EOM
  <path fill="$color" d="M100,100 L$x1,$y1 A100,100,0,$large_arc,0,$x2,$y2 z"/>
EOM
;
}

sub drawLegend {
  my $i = @_[0];
  my $y = 20 + $i*30;
print <<EOM
  <rect fill="$testTypes[$i][2]" stroke="black" x="240" y="$y"
        width="20" height="15"/>
  <text x="270" y="$y" dy="1em">
    $testTypes[$i][0] ($testTypes[$i][3] / $N_TESTS)
  </text>
EOM
;  
}

################################################################################
# Javascript


# Errors are UNEXPECTED-FAIL and UNEXPECTED-PASS
my $Nerrors = $testTypes[1][3] + $testTypes[2][3];

print <<EOM
  <script type="text/javascript">
    var error;
    function scrollToError()
     {
      var obj;
      if (error < $testTypes[1][3]) {
        obj = document.\
        getElementsByClassName("$testTypes[1][1]")[error];
      } else {
        obj = document.\
        getElementsByClassName("$testTypes[2][1]")[error - $testTypes[1][3]];
      }
      window.scrollTo(0, obj.offsetTop);
    }

    function nextError()
    {
      error++;
      if (error == $Nerrors) {
        error = 0;
      }
      scrollToError();
    }

    function previousError()
    {
      if (error == -1) {
        // case topOfPage
        error = 0;
      }

      error--;
      if (error == -1) {
        error += $Nerrors;
      }
      scrollToError();
    }

    function topOfPage() { error = -1; window.scrollTo(0, 0); }
  </script>

</body>
</html>
EOM
;
