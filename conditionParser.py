# -*- Mode: Python; tab-width: 2; indent-tabs-mode:nil; -*-
# vim: set ts=2 et sw=2 tw=80:
# ***** BEGIN LICENSE BLOCK *****
# Version: Apache License 2.0
#
# Copyright (c) 2011 Design Science, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Contributor(s):
#   Frederic Wang <fred.wang@free.fr> (original author)
#
# ***** END LICENSE BLOCK *****

import seleniumMathJax
import ply.lex as lex
import ply.yacc as yacc

gSelenium = None

################################################################################

tokens = (
   "NOT",
   "AND",
   "OR",
   'LEFTPARENTHESIS',
   'RIGHTPARENTHESIS',
   "OPERATINGSYSTEM",
   "BROWSER",
   "BROWSERMODE",
   "FONT",
   "NATIVEMATHML"
)

t_ignore = " \t"

def t_error(t):
    raise NameError("conditionParser: invalid condition")

t_NOT = r"\!"
t_AND = r"\&\&"
t_OR = r"\|\|"
t_LEFTPARENTHESIS = r"\("
t_RIGHTPARENTHESIS = r"\)"

def t_OPERATINGSYSTEM(t):
    r"Windows|Linux|Mac"
    t.value = (gSelenium == None or t.value == gSelenium.mOperatingSystem)
    return t

def t_BROWSER(t):
    r"Firefox|Safari|Chrome|Opera|MSIE|Konqueror"
    t.value = (gSelenium == None or t.value == gSelenium.mBrowser)
    return t

def t_BROWSERMODE(t):
    r"StandardMode|Quirks|IE7|IE8|IE9"
    t.value = (gSelenium == None or t.value == gSelenium.mBrowserMode)
    return t

def t_FONT(t):
    r"STIX|TeX|ImageTeX"
    t.value = (gSelenium == None or t.value == gSelenium.mFont)
    return t

def t_NATIVEMATHML(t):
    r"nativeMathML"
    t.value = (gSelenium == None or gSelenium.mNativeMathML)
    return t

lexer = lex.lex()

################################################################################

def p_error(p):
    raise NameError("conditionParser: invalid condition")

def p_closedTerm_token(p):
    '''closedTerm : OPERATINGSYSTEM
                  | BROWSER
                  | BROWSERMODE
                  | FONT
                  | NATIVEMATHML'''
    p[0] = p[1]

def p_closeTerm_parenthesis(p):
    'closedTerm : LEFTPARENTHESIS expr RIGHTPARENTHESIS'
    p[0] = p[2]

def p_expr1_(p):
    'expr1 : closedTerm'
    p[0] = p[1]

def p_expr1_not(p):
    'expr1 : NOT expr1'
    p[0] = not p[2]

def p_expr2_(p):
    'expr2 : expr1'
    p[0] = p[1]

def p_expr2_and(p):
    'expr2 : expr2 AND expr1'
    p[0] = p[1] and p[3]

def p_expr3_(p):
    'expr3 : expr2'
    p[0] = p[1]

def p_expr3_or(p):
    'expr3 : expr3 OR expr2'
    p[0] = p[1] or p[3]

def p_expr(p):
    'expr : expr3'
    p[0] = p[1]

parser = yacc.yacc()

################################################################################

def parse(aSelenium, aCondition):
    global gSelenium
    gSelenium = aSelenium
    return parser.parse(aCondition)
