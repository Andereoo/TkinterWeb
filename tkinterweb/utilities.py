"""
Various constants and utilities used by TkinterWeb

Copyright (c) 2021-2025 Andrew Clarke

Some of the CSS code in this file is modified from the Tkhtml/Hv3 project. Tkhtml is copyright (c) 2005 Dan Kennedy.
The lru_cache function in this file is modified from functools. Functools is copyright (c) Python Software Foundation.
"""

import os
import platform
import sys
import threading

from _thread import RLock
from functools import wraps, update_wrapper, _make_key

import ssl, gzip, zlib
from urllib.request import Request, urlopen
from urllib.parse import urlunparse, urlparse

try:
    import brotli
    brotli_installed = True
except ImportError:
    brotli_installed = False


# We need this information here so the built-in pages can access it
__title__ = "TkinterWeb"
__author__ = "Andrew Clarke"
__copyright__ = "(c) 2021-2025 Andrew Clarke"
__license__ = "MIT"
__version__ = "4.17.5"


ROOT_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "resources")
WORKING_DIR = os.getcwd()
PLATFORM = platform.uname()
PYTHON_VERSION = platform.python_version_tuple()


HEADERS = {
    "User-Agent": "Mozilla/5.1 (X11; U; Linux i686; en-US; rv:1.8.0.3) Gecko/20060425 SUSE/1.5.0.3-7 Hv3/alpha",
    "Accept-Encoding": ("gzip, deflate, br" if brotli_installed else "gzip, deflate"),
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
    # The following cursors only work with Tkhtml 3.1+
    "context-menu": "",
    "cell": "cross",
    "vertical-text": "xterm",
    "alias": "hand2",
    "copy": "cross",
    "no-drop": "X_cursor",
    "not-allowed": "X_cursor", # Circle works too on some platforms
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
    "gobbler": "gobbler" # Why not?
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
  margin: 8px;
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
IMG[alt]:before        { content: attr(alt) }
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

DARK_STYLE = """
/* Additional stylesheet to be loaded whenever dark mode is enabled. */
/* Display properties document body. */
HTML, BODY {
  background-color: #0d0b1a;
  color: #ffffff;
}

/* Display properties for mark elements. */
MARK {
    background: #8c7c00;
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

TEXTWRAP_STYLE = "BODY { white-space: nowrap; }"

class BuiltinPageGenerator():
    """BUILTIN_PAGES used to be a dictionary of URIs and corresponding HTML code.
    Instead, we use this page generator class so that we can generate debugging information on demand."""
    def __init__(self):
        self._html = None
        self._pages = {
    "about:blank": "<html><head><style>html,body{{background-color:{bg};color:{fg};cursor:gobbler;width:100%;height:100%;margin:0}}</style><title>about:blank</title></head><body></body></html>{i1}{i2}",
    "about:tkinterweb": "<html tkinterweb-overflow-x=auto><head>\
        <style>html,body{{{{background-color:{bg};color:{fg}}}}}\
            code{{{{display:block}}}}\
            span{{{{margin-right:10px;border:1px solid black;width:20px;padding-left:45px}}}}\
            .header{{{{display:block;text-decoration:underline;margin-top:25px}}}}\
            .closeheader{{{{display:block;text-decoration:underline}}}}\
            .section{{{{margin-left:10px;border-left:2px solid lightgrey;padding-left:10px}}}}\
            .indented{{{{margin-left:20px}}}}\
            .colourbox{{{{margin-right:75px;display:inline}}}}</style>\
        <title>about:tkinterweb</title></head><body>\
        <code>Welcome to {title}!</code><code>Licenced under the {license} licence</code><code>Copyright {copyright}</code>\
        <code>✉ <a href=https://github.com/Andereoo/TkinterWeb>github.com/Andereoo/TkinterWeb</a></code>\
        <code>✨ <a href=https://tkinterweb.readthedocs.io>tkinterweb.readthedocs.io</a></code>\
        <code>☕ <a href=https://buymeacoffee.com/andereoo>buymeacoffee.com/andereoo</a></code>\
        <code class='header'>Debugging information</code><code class='section'>\
            <code class='closeheader'>Versioning</code>\
            <code>Version: {__version__}</code><code>Tkhtml version: {tkhtml_version}</code><code>TkinterWeb-Tkhtml version: {tkw_tkhtml_version}</code>\
            <code>Python version: {python_version}</code><code>Tcl version: {tcl_version}</code><code>Tk version: {tk_version}</code>\
            <code class='header'>Resource loading</code>\
            <code>Use prebuilt Tkhtml: {use_prebuilt_tkhtml}</code>\
            <code>Available Tkhtml binaries: {tkhtml_binaries}</code>\
            <code>Resource directories: {root}{tkhtml_root}{tkhtml_extras_root}</code><code>Working directory: {working_dir}</code>\
            <code>Tcl paths: {tcl_path}</code>\
            <code>System dependency paths: {path}</code>\
            <code class='header'>System specs</code>\
            <code>Platform: {platform}</code><code>Machine: {machine}</code><code>Processor: {processor}</code>\
        </code>\
         <iframe src=\"about:tkinterweb\" height=\"200\" width=\"300\" title=\"Iframe Example\"></iframe> \
        <code class='header'>Preferences</code><code class='section'>\
            <code class='closeheader'>Renderer settings</code>\
            <code>Parse mode: {parse_mode}</code>\
            <code>Rendering engine mode: {rendering_mode}</code>\
            <code>Zoom: {zoom}</code>\
            <code>Font scale: {font_scale}</code>\
            <code class='header'>HTTP settings</code>\
            <code>Headers: {headers}</code>\
            <code>Insecure HTTPS: {insecure_https}</code>\
            <code>CA file path: {ssl_cafile}</code>\
            <code>Request timeout: {request_timeout}s</code>\
            <code class='header'>Threading settings</code>\
            <code>Threading enabled: {threading_enabled}</code>\
            <code>Tcl allows threading: {allow_threading}</code>\
            <code>Maximum thread count: {maximum_thread_count}</code>\
            <code class='header'>Image settings</code>\
            <code>Images enabled: {images_enabled}</code>\
            <code>Ignore invalid images: {ignore_invalid_images}</code>\
            <code>Image alt text: {image_alternate_text_enabled}</code>\
            <code class='header'>Flags</code>\
            <code>Experimental mode: {experimental}</code>\
            <code>Caret browsing mode: {caret_mode}</code>\
            <code>Stylesheets enabled: {stylesheets_enabled}</code>\
            <code>Javascript enabled: {javascript_enabled}</code>\
            <code>Forms enabled: {forms_enabled}</code>\
            <code>Objects enabled: {objects_enabled}</code>\
            <code>Caches enabled: {caches_enabled}</code>\
            <code>Crash prevention enabled: {crash_prevention_enabled}</code>\
            <code>Debug messages enabled: {messages_enabled}</code>\
            <code>Events enabled: {events_enabled}</code>\
            <code>Selection enabled: {selection_enabled}</code>\
            <code class='header'>Colours</code>\
            <span style='background-color:{find_match_highlight_color}'>&nbsp;</span><code class='colourbox'>Found text highlight colour: {find_match_highlight_color}</code><code></code>\
            <span style='background-color:{find_match_text_color}'>&nbsp;</span><code class='colourbox'>Found text colour: {find_match_text_color}</code><code></code>\
            <span style='background-color:{find_current_highlight_color}'>&nbsp;</span><code class='colourbox'>Current found match highlight colour: {find_current_highlight_color}</code><code></code>\
            <span style='background-color:{find_current_text_color}'>&nbsp;</span><code class='colourbox'>Current found match text colour: {find_current_text_color}</code><code></code>\
            <span style='background-color:{selected_text_highlight_color}'>&nbsp;</span><code class='colourbox'>Selected text highlight colour: {selected_text_highlight_color}</code><code></code>\
            <span style='background-color:{selected_text_color}'>&nbsp;</span><code class='colourbox'>Selected text colour: {selected_text_color}</code><code></code>\
            <span style='background-color:{bg}'>&nbsp;</span><code class='colourbox'>About page background colour: {bg}</code><code></code>\
            <span style='background-color:{fg}'>&nbsp;</span><code class='colourbox'>About page foreground colour: {fg}</code><code></code>\
            <code class='header'>Dark mode settings</code>\
            <code>Dark mode: {dark_theme_enabled}</code>\
            <code>Image inversion: {image_inversion_enabled}</code>\
            <code>Dark theme general regexes: {general_dark_theme_regexes}</code>\
            <code>Dark theme inline regexes: {inline_dark_theme_regexes}</code>\
            <code>Dark theme style regex: {style_dark_theme_regex}</code>\
            <code>Colour threshold: {dark_theme_limit}</code>\
        </code>\
        <code class='header'>Site memory</code>\
        <code>Visited hyperlinks: {visited_links}</code>\
            </body></html>{i1}{i2}",
    "about:error": "<html><head><style>html,body,table,tr,td{{background-color:{bg};color:{fg};width:100%;height:100%;margin:0}}</style><title>Error {i1}</title></head>\
        <body><table><tr><td tkinterweb-full-page style='text-align:center;vertical-align:middle'>\
        <h2 style='margin:0;padding:0;font-weight:normal'>Oops</h2>\
        <h3 style='margin-top:10px;margin-bottom:25px;font-weight:normal'>The page you've requested could not be found :(</h3>\
        <object handleremoval allowscrolling style='cursor:pointer' data='{i2}'></object>\
        </td></tr></table></body></html>",
    "about:loading": "<html><head><style>html,body,table,tr,td{{background-color:{bg};color:{fg};width:100%;height:100%;margin:0}}</style></head>\
        <body><table><tr><td tkinterweb-full-page style='text-align:center;vertical-align:middle'>\
        <p>Loading...</p>\
        </td></tr></table></body></html>{i1}{i2}",
    "about:image": "<html><head><style>html,body,table,tr {{background-color:{bg};color:{fg};width:100%;height:100%;margin:0}}</style></head><body>\
        <table><tr><td tkinterweb-full-page style='text-align:center;vertical-align:middle;padding:4px 4px 0px 4px'><img style='max-width:100%;max-height:100%' src='{i1}'><h3 style='margin:0;padding:0;font-weight:normal'></td></tr></table></body></html>{i2}",
    "about:view-source": "<html tkinterweb-overflow-x=auto><head><style>\
        html,body{{background-color:{bg};color:{fg};}}\
        pre::before{{counter-reset:listing}}\
        code{{counter-increment:listing}}\
        code::before{{content:counter(listing);display:inline-block;width:{i1}px;margin-left:5px;padding-right:5px;margin-right:5px;text-align:right;border-right:1px solid grey60;color:grey60}}\
        </style></head><body><pre style='margin:0;padding:0'>{i2}</pre></body></html>",
}
    
    def __getitem__(self, key):
        import tkinterweb_tkhtml

        if key == "about:tkinterweb":
            return self._pages[key].format(bg="{bg}", fg="{fg}", i1="{i1}", i2="{i2}", 
                title=__title__, license=__license__, copyright=__copyright__, __version__=__version__, 
                
                headers=("".join(f"<br><code class='indented'>{k}: {v}</code>" for k, v in self._html.headers.items())), 
                general_dark_theme_regexes=("".join(f"<code class='indented'>{i.replace('{', '{{').replace('}', '}}')}</code>" for i in self._html.general_dark_theme_regexes)), 
                inline_dark_theme_regexes=("".join(f"<br><code class='indented'>{i.replace('{', '{{').replace('}', '}}')}</code>" for i in self._html.inline_dark_theme_regexes)),
                style_dark_theme_regex=f"<code class='indented'>{self._html.style_dark_theme_regex.replace('{', '{{').replace('}', '}}')}</code>", 
                visited_links=(("".join(f"<code class='indented'>{i}</code>" for i in self._html.visited_links)) if self._html.visited_links else None),
                tkhtml_binaries=("".join(f"<code class='indented'>{os.path.join(i, e)}</code>" for i, e in tkinterweb_tkhtml.TKHTML_BINARIES)),
                root=f"<code class='indented'>{ROOT_DIR}</code>", 
                tkhtml_root=f"<code class='indented'>{tkinterweb_tkhtml.TKHTML_ROOT_DIR}</code>", 
                tkhtml_extras_root=f"<code class='indented'>{tkinterweb_tkhtml.TKHTML_EXTRAS_ROOT_DIR}</code>" if tkinterweb_tkhtml.TKHTML_EXTRAS_ROOT_DIR else "", 
                working_dir=f"<code class='indented'>{WORKING_DIR}</code>", 
                tcl_path=("".join(f"<code class='indented'>{i}</code>" for i in self._html.tk.getvar("auto_path"))),
                path=("".join(f"<code class='indented'>{i}</code>" for i in os.environ["PATH"].split(os.pathsep))),

                parse_mode=self._html.cget("parsemode"), rendering_mode=self._html.cget("mode"),
                zoom=self._html.cget("zoom"), font_scale=self._html.cget("fontscale"), 
                
                tkw_tkhtml_version=tkinterweb_tkhtml.__version__, python_version=".".join(PYTHON_VERSION), tcl_version=self._html.tk.call("info", "patchlevel"), tk_version=self._html.tk.call("package", "present", "Tk"),
                platform=PLATFORM.system, machine=PLATFORM.machine, processor=PLATFORM.processor,
                
                insecure_https=self._html.insecure_https, ssl_cafile=self._html.ssl_cafile, request_timeout=self._html.request_timeout, use_prebuilt_tkhtml=self._html.use_prebuilt_tkhtml,
                allow_threading=self._html.allow_threading, threading_enabled=self._html.threading_enabled, 
                caches_enabled=self._html.caches_enabled, dark_theme_enabled=self._html.dark_theme_enabled,
                image_inversion_enabled=self._html.image_inversion_enabled, crash_prevention_enabled=self._html.crash_prevention_enabled, 
                javascript_enabled=self._html.javascript_enabled, messages_enabled=self._html.messages_enabled, 
                events_enabled=self._html.events_enabled, selection_enabled=self._html.selection_enabled, 
                stylesheets_enabled=self._html.stylesheets_enabled, images_enabled=self._html.images_enabled, 
                forms_enabled=self._html.forms_enabled, objects_enabled=self._html.objects_enabled, 
                ignore_invalid_images=self._html.ignore_invalid_images, image_alternate_text_enabled=self._html.image_alternate_text_enabled, 
                find_match_highlight_color=self._html.find_match_highlight_color, find_match_text_color=self._html.find_match_text_color, 
                find_current_highlight_color=self._html.find_current_highlight_color, find_current_text_color=self._html.find_current_text_color,
                selected_text_highlight_color=self._html.selected_text_highlight_color, selected_text_color=self._html.selected_text_color,
                maximum_thread_count=self._html.maximum_thread_count, experimental=self._html.experimental, caret_mode=self._html.caret_browsing_enabled,
                dark_theme_limit=self._html.dark_theme_limit, tkhtml_version=tkinterweb_tkhtml.get_loaded_tkhtml_version(self._html)
            )
        else:
            return self._pages[key]

    def __len__(self):
        return len(self._pages)

    def __iter__(self):
        return iter(self._pages)

    def keys(self):
        return self._pages.keys()

    def items(self):
        return self._pages.items()

    def values(self):
        return self._pages.values()

# We make this dictionary a class so that we can generate debugging information on the fly
BUILTIN_PAGES = BuiltinPageGenerator()

BUILTIN_ATTRIBUTES = {
    "overflow-x": "tkinterweb-overflow-x",
    "vertical-align": "tkinterweb-full-page"
}

DOWNLOADING_RESOURCE_EVENT = "<<DownloadingResource>>"
DONE_LOADING_EVENT = "<<DoneLoading>>"
DOM_CONTENT_LOADED_EVENT = "<<DOMContentLoaded>>"
URL_CHANGED_EVENT = "<<UrlChanged>>"
ICON_CHANGED_EVENT = "<<IconChanged>>"
TITLE_CHANGED_EVENT = "<<TitleChanged>>"
FIELD_CHANGED_EVENT = "<<Modified>>"
ELEMENT_LOADED_EVENT = "<<ElementLoaded>>"

tkhtml_loaded = False
combobox_loaded = False

# These events are handled through the JS event system
EVENT_MAP = {
    "<Button-1>": "onmousedown",
    "<ButtonPress-1>": "onmousedown",
    "<B1-Press>": "onmousedown",
    "<ButtonRelease-1>": "onmouseup",
    "<B1-Release>": "onmouseup",
    "<Double-Button-1>": "ondblclick",

    "<Button-2>": "onmiddlemouse",
    "<ButtonPress-2>": "onmiddlemouse",
    "<B2-Press>": "onmiddlemouse",

    "<Button-3>": "oncontextmenu",
    "<ButtonPress-3>": "oncontextmenu",
    "<B3-Press>": "oncontextmenu",

    "<Button-4>": "onscrollup",
    "<Button-5>": "onscrolldown",
    "<MouseWheel>": "onscroll",

    "<Enter>": "onmouseover",
    "<Leave>": "onmouseout",

    "<Motion>": "onmousemove",
    "<B1-Motion>": "onmouseb1move",

    ELEMENT_LOADED_EVENT: "onload",
    FIELD_CHANGED_EVENT: "onchange"
}

# Events with the following words are allowed to be handled independently
UNHANDLED_EVENT_WHITELIST = [
    "Button", "B1", "B2", "B3", "B4", "B5"
]

# These JS events don't exist but are used internally. Translate them when needed.
JS_EVENT_MAP = {
    "onscrollup": "onscroll",
    "onscrolldown": "onscrollup",
    "onmiddlemouse": "onmousedown",
    "onmouseb1move": None,
}

class StoppableThread(threading.Thread):
    "A thread that stores a state flag that can be set and used to check if the thread is supposed to be running"

    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.daemon = True
        self.running = True

        self.is_subthread = True

    def stop(self):
        self.running = False

    def isrunning(self):
        return self.running


class PlaceholderThread:
    """Fake StoppableThread. The only purpose of this is to provide fake methods that mirror the StoppableThread class.
    This means that if a download is running in the MainThread, the stop flags can still be set without raising errors, though they won't do anything."""

    def __init__(self, *args, **kwargs):
        self.is_subthread = False

    def stop(self):
        return

    def isrunning(self):
        return True

class Empty:
    __slots__ = ()
    def __init__(self, *args, **kwargs):
        pass
    def __call__(self, *args, **kwargs):
        return None
    def __getattr__(self, name):
        return self
    def __getitem__(self, key):
        return self
    def __bool__(self):
        return False
    def __repr__(self):
        return "None"

empty = Empty()

class PlaceholderClass:
    def __getattr__(self, name):
        return empty
    
    def __getitem__(self, key):
        return empty

class BaseManager:
    def __init__(self, html):
        self.html = html
        html._managers.add(self)

    def reset(self):
        pass

placebo = PlaceholderClass()

def lazy_manager(setting):
    def decorator(func):
        attr_name = f"_{func.__name__}"

        @property
        @wraps(func)
        def wrapper(self):
            if setting is not None and not getattr(self, setting, False):
                return placebo

            if attr_name not in self.__dict__:
                manager = func(self)
                self.__dict__[attr_name] = manager

            return self.__dict__[attr_name]
    
        return wrapper
    
    return decorator


def special_setting(default=None):
    def decorator(func):
        attr_name = f"_{func.__name__}"

        @property
        def prop(self):
            return getattr(self, attr_name, default)

        @prop.setter
        def prop(self, value):
            old = getattr(self, attr_name, default)
            setattr(self, attr_name, value)
            func(self, old, value)

        return prop
    return decorator

def _lru_cache_wrapper(user_function):
    """This function is a modified version of the one that comes built-in with functools.
    It only adds to the cache if the data is not None.
    This means that if a page load is stopped, re-loading the page will not cause the page to be blank."""
    make_key = _make_key
    PREV, NEXT, KEY, RESULT = 0, 1, 2, 3

    cache = {}
    hits = misses = 0
    maxsize = 128
    typed = False
    full = False
    cache_get = cache.get
    cache_len = cache.__len__
    lock = RLock()
    root = []
    root[:] = [root, root, None, None]

    def wrapper(*args, **kwds):
        nonlocal root, hits, misses, full
        key = make_key(args, kwds, typed)
        with lock:
            link = cache_get(key)
            if link is not None:
                link_prev, link_next, _key, result = link
                link_prev[NEXT] = link_next
                link_next[PREV] = link_prev
                last = root[PREV]
                last[NEXT] = root[PREV] = link
                link[PREV] = last
                link[NEXT] = root
                hits += 1
                return result
            misses += 1
        result = user_function(*args, **kwds)
        if result[0]:
            with lock:
                if key in cache:
                    pass
                elif full:
                    oldroot = root
                    oldroot[KEY] = key
                    oldroot[RESULT] = result
                    root = oldroot[NEXT]
                    oldkey = root[KEY]
                    oldresult = root[RESULT]
                    root[KEY] = root[RESULT] = None
                    del cache[oldkey]
                    cache[key] = oldroot
                else:
                    last = root[PREV]
                    link = [last, root, key, result]
                    last[NEXT] = root[PREV] = cache[key] = link
                    full = (cache_len() >= maxsize)
        return result
    return wrapper


def lru_cache():
    def decorator(func):
        wrapper = _lru_cache_wrapper(func)
        return update_wrapper(wrapper, func)
    return decorator


def download(url, data=None, method="GET", decode=None, insecure=False, cafile=None, headers=(), timeout=15):
    "Fetch files. Note that headers should be converted from dict to tuple before calling download() as dicts aren't hashable."
    if insecure or cafile:
        context = ssl.create_default_context(cafile=cafile)
        if insecure:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
    else:
        context = None
    
    # Remove the query string if it exists and the url points to a local file
    if url.startswith("file://") and ("?" in url):
        parsed = urlparse(url)
        url = urlunparse(parsed._replace(query=""))

    url = url.replace(" ", "%20")
    if data and (method == "POST"):
        req = Request(url, data, headers=dict(headers))
    else:
        req = Request(url, headers=dict(headers))
    
    with urlopen(req, context=context, timeout=timeout) as res:
        data = res.read()
        url = res.geturl()
        info = res.info()
        code = res.getcode()

        if not url.startswith("file://") and not url.startswith("data:"):
            enc = res.getheader("Content-Encoding", "").lower()
            if enc == "gzip":
                data = gzip.decompress(data)
            elif enc == "deflate":
                try:
                    data = zlib.decompress(data)
                except zlib.error:
                    data = zlib.decompressobj(-zlib.MAX_WBITS).decompress(data)
            elif enc == "br" and brotli_installed:
                data = brotli.decompress(data)

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

        return url, data, filetype, code


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
    # Py 3.4+: Use is threading.main_thread()
    if thread.name == "MainThread":
        thread = PlaceholderThread()
    return thread


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


def notifier(text):
    "Notifications printer"
    try:
        sys.stdout.write(str(text) + "\n\n")
    except Exception:
        """sys.stdout.write doesn't work in .pyw files.
        Since .pyw files have no console, we won't bother printing messages."""


def tkhtml_notifier(name, text, *args):
    "Tkhtml -logcmd printer"
    try:
        sys.stdout.write("DEBUG " + str(name) + ": " + str(text) + "\n\n")
    except Exception:
        """sys.stdout.write doesn't work in .pyw files.
        Since .pyw files have no console, we won't bother printing messages."""


def deprecate(name, manager, new_name=None, message=None):
    import warnings
    if not new_name: new_name = name
    warnings.warn(f"{name} is deprecated. Please use {manager}.{new_name}.", FutureWarning, stacklevel=3)

def deprecate_param(name, new_name):
    import warnings
    if not new_name: new_name = name
    warnings.warn(f"{name} is deprecated. Please use {new_name}.", FutureWarning, stacklevel=4)

def warn(message):
    import warnings
    return warnings.warn(message, UserWarning, stacklevel=3)
    

def TclOpt(options):
    "Format string into Tcl option command-line names"
    return tuple(o if o.startswith("-") else "-"+o for o in options)


def placeholder(*args, **kwargs):
    """Blank placeholder function. The only purpose of this is to
    improve readability by avoiding `lambda a, b, c, d: None` statements."""


def safe_tk_eval(html, expr):
    """Always evaluate the given expression on the main thread."""
    if threading.current_thread() is threading.main_thread():
        return html.tk.eval(expr)
    else:
        result = [None]
        event = threading.Event()

        def wrapper():
            result[0] = html.tk.eval(expr)
            event.set()

        html.after(0, wrapper)
        event.wait()
        return result[0]
