"""
Various constants and utilities used by TkinterWeb

Some of the CSS code in this file is modified from the Tkhtml/Hv3 project. See tkhtml/COPYRIGHT.

Copyright (c) 2025 Andereoo
"""

import mimetypes
import os
import platform
import sys
import threading

import ssl
from urllib.request import Request, urlopen

import tkinter as tk
from tkinter import colorchooser, filedialog, ttk

try:
    from lrucache import lru_cache
except (ImportError, SyntaxError, ):
    # On Python 2 and Python 3.0 - 3.1, functools' lru_cache does not work
    # We simply replace functools' lru_cache with a fake lru_cache function that does nothing
    # We also write some extremely annoying messages to persuade users to not use a version of Python that is no longer supported
    sys.stderr.write(
        "Warning: Caching has been disabled because you are using an outdated Python installation.\n"
    )
    sys.stderr.write("Consider installing Python 3.2+ for improved performance.\n\n")

    def lru_cache():
        def decorator(func):
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
# we need this information here so the builtin pages can access it
__title__ = 'TkinterWeb'
__author__ = "Andereoo"
__copyright__ = "Copyright (c) 2025 Andereoo"
__license__ = "MIT"
__version__ = '4.1.3'


ROOT_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "tkhtml")
WORKING_DIR = os.getcwd()
PLATFORM = platform.uname()
PYTHON_VERSION = platform.python_version_tuple()


HEADERS = {
    "User-Agent": "Mozilla/5.1 (X11; U; Linux i686; en-US; rv:1.8.0.3) Gecko/20060425 Firefox/4.0"
    # The official Hv3 user agent is Mozilla/5.1 (X11; U; Linux i686; en-US; rv:1.8.0.3) Gecko/20060425 SUSE/1.5.0.3-7 Hv3/alpha
}
DEFAULT_PARSE_MODE = "xml"
DEFAULT_ENGINE_MODE = "standards"
BROKEN_IMAGE = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x19\x00\x00\x00\x1e\x08\x03\x00\x00\x00\xee2E\xe9\x00\x00\x03\x00PLTE\xc5\xd5\xf4\xcd\xdb\xf4\xdf\xe8\xfc\xd5\xdd\xf4\xa5\xa3\xa5\x85\x83\x85\xfc\xfe\xfc\xf4\xf6\xf9\x95\x93\x95S\xb39\x9d\x9f\x9d\xc5\xd3\xedo\xbbg\xd5\xe3\xf4\xd5\xdf\xfc\xd5\xe3\xfc\xb5\xcf\xd5\x9d\xc7\xb5\xc5\xdf\xe5S\xaf9\x8d\xc7\x8d\x15\x15\x15\x16\x16\x16\x17\x17\x17\x18\x18\x18\x19\x19\x19\x1a\x1a\x1a\x1b\x1b\x1b\x1c\x1c\x1c\x1d\x1d\x1d\x1e\x1e\x1e\x1f\x1f\x1f   !!!"""###$$$%%%&&&\'\'\'((()))***+++,,,---...///000111222333444555666777888999:::;;;<<<===>>>???@@@AAABBBCCCDDDEEEFFFGGGHHHIIIJJJKKKLLLMMMNNNOOOPPPQQQRRRSSSTTTUUUVVVWWWXXXYYYZZZ[[[\\\\\\]]]^^^___```aaabbbcccdddeeefffggghhhiiijjjkkklllmmmnnnooopppqqqrrrssstttuuuvvvwwwxxxyyyzzz{{{|||}}}~~~\x7f\x7f\x7f\x80\x80\x80\x81\x81\x81\x82\x82\x82\x83\x83\x83\x84\x84\x84\x85\x85\x85\x86\x86\x86\x87\x87\x87\x88\x88\x88\x89\x89\x89\x8a\x8a\x8a\x8b\x8b\x8b\x8c\x8c\x8c\x8d\x8d\x8d\x8e\x8e\x8e\x8f\x8f\x8f\x90\x90\x90\x91\x91\x91\x92\x92\x92\x93\x93\x93\x94\x94\x94\x95\x95\x95\x96\x96\x96\x97\x97\x97\x98\x98\x98\x99\x99\x99\x9a\x9a\x9a\x9b\x9b\x9b\x9c\x9c\x9c\x9d\x9d\x9d\x9e\x9e\x9e\x9f\x9f\x9f\xa0\xa0\xa0\xa1\xa1\xa1\xa2\xa2\xa2\xa3\xa3\xa3\xa4\xa4\xa4\xa5\xa5\xa5\xa6\xa6\xa6\xa7\xa7\xa7\xa8\xa8\xa8\xa9\xa9\xa9\xaa\xaa\xaa\xab\xab\xab\xac\xac\xac\xad\xad\xad\xae\xae\xae\xaf\xaf\xaf\xb0\xb0\xb0\xb1\xb1\xb1\xb2\xb2\xb2\xb3\xb3\xb3\xb4\xb4\xb4\xb5\xb5\xb5\xb6\xb6\xb6\xb7\xb7\xb7\xb8\xb8\xb8\xb9\xb9\xb9\xba\xba\xba\xbb\xbb\xbb\xbc\xbc\xbc\xbd\xbd\xbd\xbe\xbe\xbe\xbf\xbf\xbf\xc0\xc0\xc0\xc1\xc1\xc1\xc2\xc2\xc2\xc3\xc3\xc3\xc4\xc4\xc4\xc5\xc5\xc5\xc6\xc6\xc6\xc7\xc7\xc7\xc8\xc8\xc8\xc9\xc9\xc9\xca\xca\xca\xcb\xcb\xcb\xcc\xcc\xcc\xcd\xcd\xcd\xce\xce\xce\xcf\xcf\xcf\xd0\xd0\xd0\xd1\xd1\xd1\xd2\xd2\xd2\xd3\xd3\xd3\xd4\xd4\xd4\xd5\xd5\xd5\xd6\xd6\xd6\xd7\xd7\xd7\xd8\xd8\xd8\xd9\xd9\xd9\xda\xda\xda\xdb\xdb\xdb\xdc\xdc\xdc\xdd\xdd\xdd\xde\xde\xde\xdf\xdf\xdf\xe0\xe0\xe0\xe1\xe1\xe1\xe2\xe2\xe2\xe3\xe3\xe3\xe4\xe4\xe4\xe5\xe5\xe5\xe6\xe6\xe6\xe7\xe7\xe7\xe8\xe8\xe8\xe9\xe9\xe9\xea\xea\xea\xeb\xeb\xeb\xec\xec\xec\xed\xed\xed\xee\xee\xee\xef\xef\xef\xf0\xf0\xf0\xf1\xf1\xf1\xf2\xf2\xf2\xf3\xf3\xf3\xf4\xf4\xf4\xf5\xf5\xf5\xf6\xf6\xf6\xf7\xf7\xf7\xf8\xf8\xf8\xf9\xf9\xf9\xfa\xfa\xfa\xfb\xfb\xfb\xfc\xfc\xfc\xfd\xfd\xfd\xfe\xfe\xfe\xff\xff\xff\x01\xb3\x9a&\x00\x00\x01+IDATx\x9c\x9d\x91\xe9\x92\x84 \x0c\x84s (\x08A\xc6\xf7\x7f\xd6M8\x9c\x9d\xa9\xda?\xdb\x96W\x7f\xb6\xd5\x04\xf0\x7f\t\xdcT\x9c\xf7}\x0f\xf4I\x16U\x12\x16\t\x1f\xdaw\xe7\x16!\xcay\x9cL\xac\xc4\xfb\x18\x06\xc9\x81\x14\xd0\xd4o\xc2\x88\xa5X\x1e\x0b"\x1a\xf1\xd1\x05\x0f1f3\x06\xc9\x85\xb6Nb\x08\xe0\xa2d\x9cK\xd00\xefKF\x16\xf0E\ti?\xb2\x8aJ2\xf9\'\x83\xa8]Fy#\xa8\x1d\x00\x91\xa1\x01d\xad\x9e1h\x11m EM(\xa2vA\xe0\xc2,T,\xe3\x98$\xc1T\xd307 \xda6[)C\xea\x16\x1aK\x8c\rDv#BF\xd4\x03\xb4\x0b\xa4\x02,:\x83\xe8H i\xc2<\xec,%\xa2>\x1d\xc9)\x8dD\xad\xfd\x89a\xce\xad\x10\xdbw\xa0\xa0Z.\xa54v!\x8a@\x85\xeb:^\xaf\xe38\xcfZ\x19\xfc"E\xbf\xbf.\x03F\x1a\xf0 Q\xbbUM\xbc\xd5\xfd\xbeR\xa2\xda\x9d\xb3\x1f\xdd\x97\xbc\xf5Y\xf35\xc9\x93\xd0\x19\xe8\xdc\\k_\x7f\xf2g\xb6\x19\xc4\xf8\x90s\x91\x17\xe5\xbe\x0b\xf7\xf9\x99\xd0\x87\xfbV\xb2\xbd\xd5\xfd\xe7\xed?\xe4\x07\xca\xeb\x13o\x88}\xa9\x12\x00\x00\x00\x00IEND\xaeB`\x82'
CURSOR_MAP = {
    "crosshair": "crosshair",
    "default": "",
    "pointer": "hand2",
    "move": "fleur",
    "text": "xterm",
    "wait": "watch",
    "progress": "watch",
    "help": "question_arrow",
    "e-resize": "right_side",
    "ne-resize": "top_right_corner",
    "nw-resize": "top_left_corner",
    "n-resize": "top_side",
    "se-resize": "bottom_right_corner",
    "sw-resize": "bottom_left_corner",
    "s-resize": "bottom_side",
    "w-resize": "left_side",
    # the following cursors only work with experimental Tkhtml
    "context-menu": "",
    "cell": "cross",
    "vertical-text": "xterm",
    "alias": "hand2",
    "copy": "cross",
    "no-drop": "X_cursor",
    "not-allowed": "X_cursor", # circle works too on some platforms
    "grab": "hand2",
    "grabbing": "fleur",
    "all-scroll": "",
    "col-resize": "sb_h_double_arrow",
    "row-resize": "sb_v_double_arrow",
    "ew-resize": "sb_h_double_arrow",
    "ns-resize": "sb_v_double_arrow",
    "nesw-resize": "top_right_corner",
    "nwse-resize": "bottom_right_corner",
    "zoom-in": "",
    "zoom-out": "",
    "none": "none",
    "gobbler": "gobbler" # purely for humor :)
}
DEFAULT_STYLE = r"""
/* Default stylesheet to be loaded whenever HTML is parsed. */
/* This is a modified version of the stylesheet that comes bundled with Tkhtml. */
/* Display types for non-table items. */
  ADDRESS, BLOCKQUOTE, BODY, DD, DIV, DL, DT, FIELDSET, 
  FRAME, H1, H2, H3, H4, H5, H6, NOFRAMES, 
  OL, P, UL, APPLET, CENTER, DIR, HR, MENU, PRE, FORM
                { display: block }
HEAD, SCRIPT, TITLE { display: none }
BODY {
  margin:8px;
}
/* Rules for lists */
LI                   { display: list-item }
OL, UL, DIR, MENU, DD  { padding-left: 40px ; margin-left: 1em }
OL[type]         { list-style-type : tcl(::tkhtml::ol_liststyletype) }
UL>LI { list-style-type : disc }
UL>UL>LI { list-style-type : circle }
UL>UL UL>LI { list-style-type : square }
UL[type="square"]>LI { list-style-type : square } 
UL[type="disc"]>LI   { list-style-type : disc   } 
UL[type="circle"]>LI { list-style-type : circle } 
LI[type="circle"]    { list-style-type : circle }
LI[type="square"]    { list-style-type : square }
LI[type="disc"]      { list-style-type : disc   }
NOBR {
  white-space: nowrap;
}
/* Map the 'align' attribute to the 'float' property. Todo: This should
 * only be done for images, tables etc. "align" can mean different things
 * for different elements.
 */
TABLE[align="left"]       { float:left } 
TABLE[align="right"]      { 
    float:right; 
    text-align: inherit;
}
TABLE[align="center"]     { 
    margin-left:auto;
    margin-right:auto;
    text-align:inherit;
}
IMG[align="left"]         { float:left }
IMG[align="right"]        { float:right }
/* If the 'align' attribute was not mapped to float by the rules above, map
 * it to 'text-align'. The rules above take precedence because of their
 * higher specificity. 
 *
 * Also the <center> tag means to center align things.
 */
[align="right"]              { text-align: -tkhtml-right }
[align="left"]               { text-align: -tkhtml-left  }
CENTER, [align="center"]     { text-align: -tkhtml-center }
/* Rules for unordered-lists */
/* Todo! */
TD, TH {
  padding: 1px;
  border-bottom-color: grey60;
  border-right-color: grey60;
  border-top-color: grey25;
  border-left-color: grey25;
}
/* For a horizontal line, use a table with no content. We use a table
 * instead of a block because tables are laid out around floating boxes, 
 * whereas regular blocks are not.
 */
/*
HR { 
  display: table; 
  border-top: 1px solid grey45;
  background: grey80;
  height: 1px;
  width: 100%;
  text-align: center;
  margin: 0.5em 0;
}
*/
HR {
  display: block;
  border-top:    1px solid grey45;
  border-bottom: 1px solid grey80;
  margin: 0.5em auto 0.5em auto;
}
/* Basic table tag rules. */
TABLE { 
  display: table;
  border-spacing: 0px;
  border-bottom-color: grey25;
  border-right-color: grey25;
  border-top-color: grey60;
  border-left-color: grey60;
  text-align: left;
}
TR              { display: table-row }
THEAD           { display: table-header-group }
TBODY           { display: table-row-group }
TFOOT           { display: table-footer-group }
COL             { display: table-column }
COLGROUP        { display: table-column-group }
TD, TH          { display: table-cell }
CAPTION         { display: table-caption }
TH              { font-weight: bolder; text-align: center }
CAPTION         { text-align: center }
H1              { font-size: 2em; margin: .67em 0 }
H2              { font-size: 1.5em; margin: .83em 0 }
H3              { font-size: 1.17em; margin: 1em 0 }
H4, P,
BLOCKQUOTE, UL,
FIELDSET, 
OL, DL, DIR,
MENU            { margin-top: 1.0em; margin-bottom: 1.0em }
H5              { font-size: .83em; line-height: 1.17em; margin: 1.67em 0 }
H6              { font-size: .67em; margin: 2.33em 0 }
H1, H2, H3, H4,
H5, H6, B,
STRONG          { font-weight: bolder }
BLOCKQUOTE      { margin-left: 40px; margin-right: 40px }
I, CITE, EM,
VAR, ADDRESS    { font-style: italic }
PRE, TT, CODE,
KBD, SAMP       { font-family: monospace }
BIG             { font-size: 1.17em }
SMALL, SUB, SUP { font-size: .83em }
SUB             { vertical-align: sub }
SUP             { vertical-align: super }
S, STRIKE, DEL  { text-decoration: line-through }
OL              { list-style-type: decimal }
OL UL, UL OL,
UL UL, OL OL    { margin-top: 0; margin-bottom: 0 }
U, INS          { text-decoration: underline }
ABBR, ACRONYM   { font-variant: small-caps; letter-spacing: 0.1em }
/* Formatting for <pre> etc. */
PRE, PLAINTEXT, XMP { 
  display: block;
  white-space: pre;
  margin: 1em 0;
  font-family: monospace;
}
/* Formatting for <mark> */
MARK {
    background: yellow;
}
/* Display properties for hyperlinks */
:link    { color: darkblue; text-decoration: underline ; cursor: pointer }
:visited { color: purple; text-decoration: underline ; cursor: pointer }
A:active {
    color:red;
    cursor:pointer;
}
/* Deal with the "nowrap" HTML attribute on table cells. */
TD[nowrap] ,     TH[nowrap]     { white-space: nowrap; }
TD[nowrap="0"] , TH[nowrap="0"] { white-space: normal; }
BR { 
    display: block;
}
/* BR:before       { content: "\A" } */
/*
 * Default decorations for form items. 
 */
INPUT[type="hidden"] { display: none }
INPUT, TEXTAREA, SELECT, BUTTON { 
  border: 1px solid #828282;
  background-color: white;
  line-height: normal;
  vertical-align: middle;
}
INPUT[type="image"][src] {
  -tkhtml-replacement-image: attr(src);
  cursor: pointer;
  border-width: 0;
}
INPUT[type="checkbox"], INPUT[type="radio"], input[type="file"], input[type="range"], input[type="color"] {
  background-color: transparent;
  border: none;
}
INPUT[type="submit"],INPUT[type="button"], INPUT[type="reset"], BUTTON {
  display: -tkhtml-inline-button;
  position: relative;
  white-space: nowrap;
  cursor: pointer;
  border: 1px solid;
  border-top-color:    tcl(::tkhtml::if_disabled #828282 #e7e9eb);
  border-left-color:   tcl(::tkhtml::if_disabled #828282 #e7e9eb);
  border-right-color:  tcl(::tkhtml::if_disabled #e7e9eb #828282);
  border-bottom-color: tcl(::tkhtml::if_disabled #e7e9eb #828282);
  padding-top: 3px;
  padding-left: 8px;
  padding-right: 8px;
  padding-bottom: 3px;
  background-color: #d9d9d9;
  color: #000000;
  color: tcl(::tkhtml::if_disabled #666666 #000000);
}
INPUT[type="color"] {
  cursor: pointer;
  padding: 5px;
  background-color: #ccc;
}
INPUT[disabled], BUTTON[disabled] {
    cursor: auto;
}
INPUT[type="submit"]:after {
  content: "Submit";
}
INPUT[type="reset"]:after {
  content: "Reset";
}
INPUT[type="submit"][value]:after,INPUT[type="button"][value]:after, INPUT[type="reset"][value]:after {
  content: attr(value);
}
INPUT[type="submit"]:hover:active, INPUT[type="reset"]:hover:active,INPUT[type="button"]:hover:active, BUTTON:hover:active {
  border-top-color:    tcl(::tkhtml::if_disabled #e7e9eb #828282);
  border-left-color:   tcl(::tkhtml::if_disabled #e7e9eb #828282);
  border-right-color:  tcl(::tkhtml::if_disabled #828282 #e7e9eb);
  border-bottom-color: tcl(::tkhtml::if_disabled #828282 #e7e9eb);
}
INPUT[size] { width: tcl(::tkhtml::inputsize_to_css) }
/* Handle "cols" and "rows" on a <textarea> element. By default, use
 * a fixed width font in <textarea> elements.
 */
TEXTAREA[cols] { width: tcl(::tkhtml::textarea_width) }
TEXTAREA[rows] { height: tcl(::tkhtml::textarea_height) }
TEXTAREA {
  font-family: fixed;
}
FRAMESET {
  display: none;
}
/* Default size for <IFRAME> elements */
IFRAME {
  width: 300px;
  height: 200px;
  border: 1px solid #828282;
}
/*
 *************************************************************************
 * Below this point are stylesheet rules for mapping presentational 
 * attributes of Html to CSS property values. Strictly speaking, this 
 * shouldn't be specified here (in the UA stylesheet), but it doesn't matter
 * in practice. See CSS 2.1 spec for more details.
 */
/* 'color' */
[color]              { color: attr(color) }
body a[href]:link    { color: attr(link x body) }
body a[href]:visited { color: attr(vlink x body) }
/* 'width', 'height', 'background-color' and 'font-size' */
[width]            { width:            attr(width l) }
[height]           { height:           attr(height l) }
basefont[size]     { font-size:        attr(size) }
font[size]         { font-size:        tcl(::tkhtml::size_to_fontsize) }
BR[clear]          { clear: attr(clear) }
BR[clear="all"]    { clear: both; }
/* Standard html <img> tags - replace the node with the image at url $src */
IMG[src]              { -tkhtml-replacement-image: attr(src) }
IMG                   { -tkhtml-replacement-image: "" }
/*
 * Properties of table cells (th, td):
 *
 *     'border-width'
 *     'border-style'
 *     'padding'
 *     'border-spacing'
 */
TABLE[border], TABLE[border] TD, TABLE[border] TH {
    border-top-width:     attr(border l table);
    border-right-width:   attr(border l table);
    border-bottom-width:  attr(border l table);
    border-left-width:    attr(border l table);
    border-top-style:     attr(border x table solid);
    border-right-style:   attr(border x table solid);
    border-bottom-style:  attr(border x table solid);
    border-left-style:    attr(border x table solid);
}
TABLE[border=""], TABLE[border=""] td, TABLE[border=""] th {
    border-top-width:     attr(border x table solid);
    border-right-width:   attr(border x table solid);
    border-bottom-width:  attr(border x table solid);
    border-left-width:    attr(border x table solid);
}
TABLE[cellpadding] td, TABLE[cellpadding] th {
    padding-top:    attr(cellpadding l table);
    padding-right:  attr(cellpadding l table);
    padding-bottom: attr(cellpadding l table);
    padding-left:   attr(cellpadding l table);
}
TABLE[cellspacing], table[cellspacing] {
    border-spacing: attr(cellspacing l);
}
/* Map the valign attribute to the 'vertical-align' property for table 
 * cells. The default value is "middle", or use the actual value of 
 * valign if it is defined.
 */
TD,TH                        {vertical-align: middle}
TR[valign]>TD, TR[valign]>TH {vertical-align: attr(valign x tr)}
TR>TD[valign], TR>TH[valign] {vertical-align: attr(valign)}
/* Support the "text" attribute on the <body> tag */
body[text]       {color: attr(text)}
body[bgcolor]    { background-color: attr(bgcolor) }
/* Allow background images to be specified using the "background" attribute.
 * According to HTML 4.01 this is only allowed for <body> elements, but
 * many websites use it arbitrarily.
 */
[background] { background-image: attr(background) }
/* The vspace and hspace attributes map to margins for elements of type
 * <IMG>, <OBJECT> and <APPLET> only. Note that this attribute is
 * deprecated in HTML 4.01.
 */
IMG[vspace], OBJECT[vspace], IFRAME[vspace], APPLET[vspace] {
    margin-top: attr(vspace l);
    margin-bottom: attr(vspace l);
}
IMG[hspace], OBJECT[hspace], IFRAME[hspace], APPLET[hspace] {
    margin-left: attr(hspace l);
    margin-right: attr(hspace l);
}
/* marginheight and marginwidth attributes on <BODY> */
BODY[marginheight] {
  margin-top: attr(marginheight l);
  margin-bottom: attr(marginheight l);
}
BODY[marginwidth] {
  margin-left: attr(marginwidth l);
  margin-right: attr(marginwidth l);
}
SPAN[spancontent]:after {
  content: attr(spancontent);
}
IFRAME[frameborder]{
  border-width: attr(frameborder l);
}
"""

DARK_STYLE = DEFAULT_STYLE + """
/* Additional stylesheet to be loaded whenever dark mode is enabled. */
/* Display properties document body. */
HTML, BODY {
  background-color: #0d0b1a;
  color: #ffffff;
}
/* Display properties for hyperlinks */
:link    { color: #7768d9; }
:visited { color: #5245a8; }

/* Display properties for form items. */
INPUT, TEXTAREA, SELECT, BUTTON { 
  background-color: #171524;
  color: #ffffff;
}
INPUT[type="submit"],INPUT[type="button"], INPUT[type="reset"], BUTTON {
  background-color: #171524;
  color: #ffffff;
  color: tcl(::tkhtml::if_disabled #666666 #ffffff);
}
"""
BUILTIN_PAGES = {
    "about:blank": "<html><head><style>html,body{{background-color:{};color:{};cursor:gobbler;width:100%;height:100%;margin:0}}</style><title>about:blank</title></head><body></body></html>",
    "about:tkinterweb": "<html tkinterweb-overflow-x=auto><head><style>html,body{{background-color:{};color:{};}}</style><title>about:tkinterweb</title><style>code{{display:block}}</style></head><body>\
        <code>Welcome to "+__title__+"!</code><code>Licenced under the "+__license__+" licence</code><code>"+__copyright__+"</code>\
        <code style=\"display:block;text-decoration:underline;margin-top:35px\">Debugging information</code>\
        <code>Version: "+__version__+"</code><code>Default headers: "+HEADERS["User-Agent"]+"</code><code>Default parse mode: "+DEFAULT_PARSE_MODE+"</code>\
        <code>Default rendering engine mode: "+DEFAULT_ENGINE_MODE+"</code>\
        <code style=\"display:block\">Root directory: "+ROOT_DIR+"</code><code style=\"display:block\">Working directory: "+WORKING_DIR+"</code>\
        <code style=\"display:block;text-decoration:underline;margin-top:35px\">System specs</code>\
        <code>Python version: "+".".join(PYTHON_VERSION)+"</code><code>Tcl version: "+str(tk.TclVersion)+"</code><code>Tk version: "+str(tk.TkVersion)+"</code>\
        <code>Platform: "+str(PLATFORM.system)+"</code><code>Machine: "+str(PLATFORM.machine)+"</code><code>Processor: "+str(PLATFORM.processor)+"</code></body></html>",
    "about:error": "<html><head><style>html,body,table,tr,td{{background-color:{};color:{};width:100%;height:100%;margin:0}}</style><title>Error {}</title></head>\
        <body><table><tr><td tkinterweb-full-page style=\"text-align:center;vertical-align:middle\">\
        <h2 style=\"margin:0;padding:0;font-weight:normal\">Oops</h2>\
        <h3 style=\"margin-top:10px;margin-bottom:25px;font-weight:normal\">The page you've requested could not be found :(</h3>\
        <object handleremoval allowscrolling style=\"cursor:pointer\" data=\"{}\"></object>\
        </td></tr></table></body></html>",
    "about:loading": "<html><head><style>html,body,table,tr,td{{background-color:{};color:{};width:100%;height:100%;margin:0}}</style></head>\
        <body><table><tr><td tkinterweb-full-page style=\"text-align:center;vertical-align:middle\">\
        <p>Loading...</p>\
        </td></tr></table></body></html>",
    "about:image": "<html><head><style>html,body,table,tr {{background-color:{};color:{};width:100%;height:100%;margin:0}}</style></head><body>\
        <table><tr><td tkinterweb-full-page style='text-align:center;vertical-align:middle;padding:4px 4px 0px 4px'><img style='max-width:100%;max-height:100%' src='replace:{}'><h3 style=\"margin:0;padding:0;font-weight:normal\"></td></tr></table></body></html>",
    "about:view-source": "<html tkinterweb-overflow-x=auto><head><style>\
        html,body{{background-color:{};color:{};}}\
        pre::before{{counter-reset:listing}}\
        code{{counter-increment:listing}}\
        code::before{{content:counter(listing);display:inline-block;width:{}px;margin-left:5px;padding-right:5px;margin-right:5px;text-align:right;border-right:1px solid grey60;color:grey60}}\
        </style></head><body><pre style=\"margin:0;padding:0\">{}</pre></body></html>",
}
BUILTIN_ATTRIBUTES = {
    "overflow-x": "tkinterweb-overflow-x",
    "vertical-align": "tkinterweb-full-page"
}

DOWNLOADING_RESOURCE_EVENT = "<<DownloadingResource>>"
DONE_LOADING_EVENT = "<<DoneLoading>>"
URL_CHANGED_EVENT = "<<UrlChanged>>"
ICON_CHANGED_EVENT = "<<IconChanged>>"
TITLE_CHANGED_EVENT = "<<TitleChanged>>"

tkhtml_loaded = False
combobox_loaded = False


class AutoScrollbar(ttk.Scrollbar):
    "Scrollbar that hides itself when not needed"
    def __init__(self, *args, scroll=2, **kwargs):
        ttk.Scrollbar.__init__(self, *args, **kwargs)
        self.scroll = scroll
        self.visible = True

    def set(self, lo, hi):
        if self.visible and (self.scroll == 0):
            self.tk.call("grid", "remove", self)
            self.visible = False
        elif (self.visible == False) and (self.scroll == 1):
            self.grid()
            self.visible = True
        elif self.scroll == 2:
            if float(lo) <= 0.0 and float(hi) >= 1.0:
                self.tk.call("grid", "remove", self)
                self.visible = False
            else:
                self.grid()
                self.visible = True
        ttk.Scrollbar.set(self, lo, hi)
    
    def set_type(self, scroll):
        if self.scroll != scroll:
            self.scroll = scroll
            lo, hi = self.get()
            self.set(lo, hi)

    def pack(self, **kwargs):
        raise tk.TclError("cannot use pack with this widget")

    def place(self, **kwargs):
        raise tk.TclError("cannot use place with this widget")


class ScrolledTextBox(tk.Frame):
    "Text widget with a scrollbar"

    def __init__(self, parent, content="", onchangecommand=None, **kwargs):
        self.parent = parent
        self.onchangecommand = onchangecommand

        tk.Frame.__init__(self, parent)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.tbox = tbox = tk.Text(self, 
                                    borderwidth=0,
                                    selectborderwidth=0,
                                    highlightthickness=0,
                                    **kwargs)
        tbox.grid(row=0, column=0, sticky="nsew")

        tbox.insert("1.0", content)
    
        self.vsb = vsb = AutoScrollbar(self, command=tbox.yview)
        vsb.grid(row=0, column=1, sticky="nsew")
        tbox.configure(yscrollcommand=vsb.set)

        tbox.bind("<MouseWheel>", self.scroll)
        tbox.bind("<Button-4>", self.scroll_x11)
        tbox.bind("<Button-5>", self.scroll_x11)
        tbox.bind("<Control-Key-a>", self.select_all)
        tbox.bind('<KeyRelease>', lambda event: onchangecommand(self) if onchangecommand else None)

    def select_all(self, event):
        self.tbox.tag_add("sel", "1.0", "end")
        self.tbox.mark_set("insert", "1.0")
        self.tbox.see("insert")
        return "break"

    def scroll(self, event):
        yview = self.tbox.yview()
        if yview[0] == 0 and event.delta > 0:
            self.parent.scroll(event)
        elif yview[1] == 1 and event.delta < 0:
            self.parent.scroll(event)

    def scroll_x11(self, event):
        yview = self.tbox.yview()
        if event.num == 4 and yview[0] == 0:
            self.parent.scroll_x11(event, self.parent)
        elif event.num == 5 and yview[1] == 1:
            self.parent.scroll_x11(event, self.parent)

    def configure(self, *args, **kwargs):
        self.tbox.configure(*args, **kwargs)

    def insert(self, *args, **kwargs):
        return self.tbox.insert(*args, **kwargs)

    def get(self, *args, **kwargs):
        if not args and not kwargs:
            args = ("1.0", "end-1c")
        return self.tbox.get(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.tbox.delete(*args, **kwargs)

    def set(self, value):
        self.tbox.delete("0.0", "end")
        self.tbox.insert("1.0", value)
        if self.onchangecommand:
            self.onchangecommand(self)

class FormEntry(tk.Entry):
    def __init__(self, parent, value="", entry_type="", onchangecommand=None, **kwargs):
        tk.Entry.__init__(self, parent, borderwidth=0, highlightthickness=0, **kwargs)
        self.insert(0, value)

        self.bind("<KeyRelease>", lambda event: onchangecommand(self) if onchangecommand else None)
        if entry_type == "password":
            self.configure(show="*")
            
    def set(self, value):
        self.delete(0, "end")
        self.insert(0, value)

class FormCheckbox(ttk.Checkbutton):
    def __init__(self, parent, value=0, onchangecommand=None, **kwargs):
        self.variable = variable = tk.IntVar(parent, value=value)

        tk.Checkbutton.__init__(
            self,
            parent,
            borderwidth=0,
            padx=0,
            pady=0,
            highlightthickness=0,
            variable=variable,
            **kwargs
        )
        variable.trace_add("write", lambda *args: onchangecommand(self) if onchangecommand else None)

class FormRadioButton(ttk.Checkbutton):
    def __init__(self, parent, token, value=0, checked=False, variable=None, onchangecommand=None, **kwargs):
        if not variable: 
            variable = tk.StringVar(parent)
            variable.trace_add("write", lambda *args: onchangecommand(self) if onchangecommand else None)
        self.variable = variable

        tk.Radiobutton.__init__(
            self,
            parent,
            value=value,
            variable=variable,
            tristatevalue=token,
            borderwidth=0,
            padx=0,
            pady=0,
            highlightthickness=0,
            **kwargs
        )
        if checked:
            variable.set(value)

    def set(self, value):
        self.variable.set(value)
        
    def get(self):
        return self.variable.get()

class FormRange(ttk.Scale):
    def __init__(self, parent, value=50, from_=0, to=100, step=1, onchangecommand=None, **kwargs):
        step_str = str(step)
        self.step = self._check_value(step, 1)
        self.from_ = from_ = self._check_value(from_, 0)
        self.to = to = self._check_value(to, 100)
        self.onchangecommand = onchangecommand
        self.decimal_places = len(step_str.split('.')[-1]) if '.' in step_str else 0
        self.variable = variable = tk.DoubleVar(parent, value=self._check_value(value, (to - from_) / 2))

        ttk.Scale.__init__(self, parent, variable=variable, from_=from_, to=to)

        variable.trace_add("write", self._update_value)

    def _update_value(self, *args):
        value = round(self.variable.get() / self.step) * self.step
        self.set(round(value, self.decimal_places))
        self.onchangecommand(self)

    def _check_value(self, value, default):
        try: 
            return float(value)
        except ValueError:
            return default
        
    def set(self, value):
        super().set(self._check_value(value, (self.to - self.from_) / 2))

class FileSelector(tk.Frame):
    "File selector widget"

    def __init__(self, parent, accept, multiple, onchangecommand=None, **kwargs):
        self.multiple = multiple
        self.onchangecommand = onchangecommand
        self.files = []

        tk.Frame.__init__(self, parent)
        self.selector = selector = tk.Button(
            self, text="Browse", command=self.select_file
        )
        self.label = label = tk.Label(self, bg="red", text="No files selected.")

        selector.grid(row=0, column=1)
        label.grid(row=0, column=2, padx=5)

        self.generate_filetypes(accept)

    def generate_filetypes(self, accept):
        if accept:
            accept_list = [a.strip() for a in accept.split(",")]
            all_extensions = set()
            filetypes = []

            # First find all the MIME types
            for mimetype in [a for a in accept_list if not a.startswith(".")]:
                # the HTML spec specifies these three wildcard cases only:
                if mimetype in ("audio/*", "video/*", "image/*"):
                    extensions = [
                        k
                        for k, v in mimetypes.types_map.items()
                        if v.startswith(mimetype[:-1])
                    ]
                else:
                    extensions = mimetypes.guess_all_extensions(mimetype)
                filetypes.append((mimetype, " ".join(extensions)))
                all_extensions.update(extensions)

            # Now add any non-MIME types not already included as part of a MIME type.
            for suffix in [a for a in accept_list if a.startswith(".")]:
                if suffix not in all_extensions:
                    mimetype = mimetypes.guess_type(f" {suffix}", suffix)[0]
                    if mimetype:
                        extensions = mimetypes.guess_all_extensions(mimetype)
                        filetypes.append((mimetype, " ".join(extensions)))
                        all_extensions.update(extensions)
                    else:
                        filetypes.append((f"{suffix} files", suffix))

            if len(filetypes) > 1:
                filetypes.insert(
                    0, ("All Supported Types", " ".join(sorted(all_extensions)))
                )

            self.filetypes = filetypes
        else:
            self.filetypes = []

    def select_file(self):
        if self.multiple:
            files = filedialog.askopenfilenames(
                title="Select files", filetypes=self.filetypes
            )
            if files:
                self.files = []
                for file in files:
                    self.files.append(os.path.basename(file.replace('\\', '/')))
                files = self.files
        else:
            files = filedialog.askopenfilename(
                title="Select file", filetypes=self.filetypes
            )
            if files:
                self.files = files = (os.path.basename(files.replace('\\', '/')),)
        number = len(files)
        if number == 0:
            self.label.config(text="No files selected.")
        elif number == 1:
            files = files[0].replace("\\", "/").split("/")[-1]
            self.label.config(text=files)
        else:
            self.label.config(text=f"{number} files selected.")
        self.event_generate("<<Modified>>")
        if self.onchangecommand:
            self.onchangecommand(self)

    def set(self, value):
        self.label.config(text="No files selected.")
        self.event_generate("<<Modified>>")
        if self.onchangecommand:
            self.onchangecommand(self)

    def get(self):
        return self.files

    def configure(self, *args, **kwargs):
        self.selector.config(*args, **kwargs)
        if "activebackground" in kwargs:
            del kwargs["activebackground"]
        self.label.config(*args, **kwargs)
        if "state" in kwargs:
            del kwargs["state"]
        self.config(*args, **kwargs)


class ColourSelector(tk.Frame):
    "Colour selector widget"

    def __init__(self, parent, colour="#000000", onchangecommand=None, **kwargs):
        self.onchangecommand = onchangecommand
        colour = colour if colour else "#000000"
        tk.Button.__init__(self, parent,
            bg=colour,
            command=self.select_colour,
            activebackground=colour,
            highlightthickness=0,
            borderwidth=0,
            **kwargs
        )

    def select_colour(self):
        colour = colorchooser.askcolor(title="Choose color", initialcolor=self.cget("bg"))[1]
        if colour:
            self.set(colour)

    def set(self, colour):
        colour = colour if colour else "#000000"
        self.config(bg=colour, activebackground=colour)
        self.event_generate("<<Modified>>")
        if self.onchangecommand:
            self.onchangecommand(self)

    def get(self):
        return self.cget("bg")


class Notebook(ttk.Frame):
    "Drop-in replacement for the :py:class:`ttk.Notebook` widget."

    def __init__(self, master, takefocus=True, **kwargs):
        ttk.Frame.__init__(self, master, **kwargs)
        self.notebook = notebook = ttk.Notebook(self, takefocus=takefocus)
        self.blankframe = lambda: tk.Frame(
            notebook, height=0, bd=0, highlightthickness=0
        )

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        notebook.grid(row=0, column=0, sticky="ew")

        notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

        self.pages = []
        self.previous_page = None

    def on_tab_change(self, event):
        self.event_generate("<<NotebookTabChanged>>")
        try:
            tabId = self.notebook.index(self.notebook.select())
            newpage = self.pages[tabId]
            if self.previous_page:
                self.previous_page.grid_forget()
            newpage.grid(row=1, column=0, sticky="nsew")
            self.previous_page = newpage
        except tk.TclError:
            pass

    def add(self, child, **kwargs):
        "Adds a new tab to the notebook."
        if child in self.pages:
            raise ValueError(f"{child} is already managed by {self}.")
        frame = self.blankframe()
        self.notebook.add(frame, **kwargs)
        self.pages.append(child)

    def insert(self, where, child, **kwargs):
        "Adds a new tab at the specified position."
        if child in self.pages:
            raise ValueError(f"{child} is already managed by {self}.")
        frame = self.blankframe()
        self.notebook.insert(where, frame, **kwargs)
        self.pages.insert(where, child)

    def enable_traversal(self):
        "Enable keyboard traversal for a toplevel window containing this notebook."
        self.notebook.enable_traversal()

    def select(self, tabId=None):
        "Select the given tabId."
        if tabId in self.pages:
            tabId = self.pages.index(tabId)
            return self.notebook.select(tabId)
        else:
            self.notebook.select(tabId)
            return self.transcribe(self.notebook.select())

    def transcribe(self, item, reverse=False):
        return self.pages[self.notebook.index(item)]

    def tab(self, tabId, option=None, **kwargs):
        "Query or modify the options of the given tabId."
        if not isinstance(tabId, int) and tabId in self.pages:
            tabId = self.pages.index(tabId)
        return self.notebook.tab(tabId, option, **kwargs)

    def forget(self, tabId):
        "Removes the tab specified by tabId and unmaps the associated window."
        if isinstance(tabId, int):
            del self.pages[tabId]
            self.notebook.forget(tabId)
        else:
            index = self.pages.index(tabId)
            self.pages.remove(tabId)
            self.notebook.forget(index)

    def index(self, child):
        "Returns the numeric index of the tab specified by child, or the total number of tabs if child is the string “end”."
        try:
            return self.pages.index(child)
        except (IndexError, ValueError):
            return self.transcribe(self.notebook.index(child))

    def tabs(self):
        "Returns a list of widgets managed by the notebook."
        return self.pages


class StoppableThread(threading.Thread):
    "A thread that stores a state flag that can be set and used to check if the thread is supposed to be running"

    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.daemon = True
        self.running = True

    def stop(self):
        self.running = False

    def isrunning(self):
        return self.running


class PlaceholderThread:
    "Fake StoppableThread. The only purpose of this is to provide fake methods that mirror the StoppableThread class."
    "This means that if a download is running in the MainThread, the stop flags can still be set without raising errors, though they won't do anything."

    def stop(self):
        return

    def isrunning(self):
        return True


def download(url, data=None, method="GET", decode=None, insecure=False, headers=()):
    "Fetch files"
    "Note that headers should be converted from dict to tuple before calling download() as dicts aren't hashable"
    ctx = ssl.create_default_context()
    if insecure:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

    thread = get_current_thread()
    url = url.replace(" ", "%20")
    if data and (method == "POST"):
        req = urlopen(Request(url, data, headers=dict(headers)), context=ctx)
    else:
        req = urlopen(Request(url, headers=dict(headers)), context=ctx)
    if not thread.isrunning():
        return None, url, "", ""
    data = req.read()
    url = req.geturl()
    info = req.info()
    code = req.getcode()

    try:
        maintype = info.get_content_maintype()
        filetype = info.get_content_type()
    except AttributeError:
        maintype = info.maintype
        filetype = info.type
    if (maintype != "image") or ("svg" in filetype):
        if decode:
            data = data.decode(decode, errors="ignore")
        else:
            data = data.decode(errors="ignore")
    if not thread.isrunning():
        return None, url, "", code
    else:
        return data, url, filetype, code


@lru_cache()
def cache_download(*args, **kwargs):
    "Fetch files and add them to the lru cache"
    return download(*args, **kwargs)


def shorten(string):
    "Shorten text to avoid overloading the terminal"
    if len(string) > 100:
        string = string[:100] + "..."
    return string


def get_current_thread():
    "Return the currently running thread"
    thread = threading.current_thread()
    if thread.name == "MainThread":
        thread = PlaceholderThread()
    return thread


def strip_css_url(url):
    "Extract the address from a css url"
    return url[4:-1].replace("'", "").replace('"', "")


def rgb_to_hex(red, green, blue, *args):
    "Convert RGB colour code to HEX"
    return f"#{red:02x}{green:02x}{blue:02x}"

def invert_color(rgb, match, limit):
    "Check colour, invert if necessary, and convert"
    if ("background" in match and sum(rgb) < limit) or (
        match == "color" and sum(rgb) > limit
    ):
        return rgb_to_hex(*rgb)
    else:
        rgb[0] = max(1, min(255, 240 - rgb[0]))
        rgb[1] = max(1, min(255, 240 - rgb[1]))
        rgb[2] = max(1, min(255, 240 - rgb[2]))
        return rgb_to_hex(*rgb)

def get_alt_font():
    "Get the location of the truetype file to be used for image alternate text"
    return os.path.join(ROOT_DIR, "opensans.ttf")

def get_tkhtml_folder():
    "Get the location of the platform's tkhtml binary"
    # Universal sdist
    if platform.system() == "Linux":
       if "arm" in PLATFORM.machine:  # 32 bit arm Linux - Raspberry Pi and others
           return os.path.join(ROOT_DIR, "linux_armv71")
       elif "aarch64" in PLATFORM.machine:  # 64 bit arm Linux - Raspberry Pi and others
           return os.path.join(ROOT_DIR, "manylinux2014_aarch64")
       elif sys.maxsize > 2**32:  # 64 bit Linux
           return os.path.join(ROOT_DIR, "manylinux1_x86_64")
       else:  # 32 bit Linux
           return os.path.join(ROOT_DIR, "manylinux1_i686")
    elif platform.system() == "Darwin":
       if "arm" in PLATFORM.machine:  # M1 Mac
           return os.path.join(ROOT_DIR, "macosx_11_0_arm64")
       else:  # other Macs
           return os.path.join(ROOT_DIR, "macosx_10_6_x86_64")
    else:
       if sys.maxsize > 2**32:  # 64 bit Windows
           return os.path.join(ROOT_DIR, "win_amd64")
       else:  # 32 bit Windows
           return os.path.join(ROOT_DIR, "win32")
    # Platform-specific wheel
    return os.path.join(ROOT_DIR, "binaries")


def load_tkhtml(master, location=None, force=False):
    "Load nessessary Tkhtml files"
    global tkhtml_loaded
    if (not tkhtml_loaded) or force:
        if location:
            master.tk.eval("set auto_path [linsert $auto_path 0 {" + location + "}]")
        master.tk.eval("package require Tkhtml")
        tkhtml_loaded = True


def load_combobox(master, force=False):
    "Load combobox.tcl"
    global combobox_loaded
    if not (combobox_loaded) or force:
        master.tk.call("lappend", "auto_path", ROOT_DIR)
        master.tk.call("package", "require", "combobox")
        combobox_loaded = True


def notifier(text):
    "Notifications printer"
    try:
        sys.stdout.write(str(text) + "\n\n")
    except Exception:
        "sys.stdout.write doesn't work in .pyw files."
        "Since .pyw files have no console, we won't bother printing messages."


def tkhtml_notifier(name, text, *args):
    "Tkhtml -logcmd printer"
    try:
        sys.stdout.write("DEBUG " + str(name) + ": " + str(text) + "\n\n")
    except Exception:
        "sys.stdout.write doesn't work in .pyw files."
        "Since .pyw files have no console, we won't bother printing messages."

def placeholder(*args, **kwargs):
    """Blank placeholder function. The only purpose of this is to
    improve readability by avoiding `lambda a, b, c, d: None` statements."""