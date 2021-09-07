import sys, os
import platform
import threading

try:
    from urllib.request import Request, urlopen
except ImportError:
    from urllib2 import Request, urlopen

try:
    import tkinter as tk
    from tkinter import filedialog, ttk
except ImportError:
    import Tkinter as tk
    import tkFileDialog as filedialog
    import ttk

try:
    from lrucache import lru_cache
except (ImportError, SyntaxError, ):
    # On Python 2 and Python 3.0 - 3.1, functools' lru_cache does not work
    # We simply replace functools' lru_cache with a fake lru_cache function that does nothing
    # We also write some extremely annoying messages to persuade users to not use a version of Python that is no longer supported
    sys.stderr.write(
        "Warning: Caching has been disabled because you are using an outdated Python installation.\n")
    sys.stderr.write(
        "Consider installing Python 3.2+ for improved performance.\n\n")

    def lru_cache():
        def decorator(func):
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator



HEADER = {'User-Agent': 'Mozilla/5.1 (X11; U; Linux i686; en-US; rv:1.8.0.3) Gecko/20060425 SUSE/1.5.0.3-7 Hv3/alpha'}
DEFAULTSTYLE = """
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

/* Rules for unordered-lists */
LI                   { display: list-item }
UL[type="square"]>LI { list-style-type : square } 
UL[type="disc"]>LI   { list-style-type : disc   } 
UL[type="circle"]>LI { list-style-type : circle } 
LI[type="circle"]    { list-style-type : circle }
LI[type="square"]    { list-style-type : square }
LI[type="disc"]      { list-style-type : disc   }

OL, UL, DIR, MENU, DD  { padding-left: 40px ; margin-left: 1em }

OL[type]         { list-style-type : tcl(::tkhtml::ol_liststyletype) }

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
KBD, SAMP       { font-family: courier }
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
  font-family: courier;
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
  border: 1px solid black;
  background-color: white;
  line-height: normal;
  vertical-align: middle;
}

INPUT[type="image"][src] {
  -tkhtml-replacement-image: attr(src);
  cursor: pointer;
}

INPUT[type="checkbox"], INPUT[type="radio"], input[type="file"] {
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
  border: 1px solid black;
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
[bgcolor]          { background-color: attr(bgcolor) }

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

/* Allow background images to be specified using the "background" attribute.
 * According to HTML 4.01 this is only allowed for <body> elements, but
 * many websites use it arbitrarily.
 */
[background] { background-image: attr(background) }

/* The vspace and hspace attributes map to margins for elements of type
 * <IMG>, <OBJECT> and <APPLET> only. Note that this attribute is
 * deprecated in HTML 4.01.
 */
IMG[vspace], OBJECT[vspace], APPLET[vspace] {
    margin-top: attr(vspace l);
    margin-bottom: attr(vspace l);
}
IMG[hspace], OBJECT[hspace], APPLET[hspace] {
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
"""
tkhtml_loaded = False
combobox_loaded = False


class AutoScrollbar(ttk.Scrollbar):
    "Scrollbar that hides itself when not needed."

    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.tk.call("grid", "remove", self)
        else:
            self.grid()
        ttk.Scrollbar.set(self, lo, hi)

    def pack(self, **kw):
        raise tk.TclError("cannot use pack with this widget")

    def place(self, **kw):
        raise tk.TclError("cannot use place with this widget")


class ScrolledTextBox(tk.Frame):
    "Text widget with a scrollbar."

    def __init__(self, parent, **kwargs):

        tk.Frame.__init__(self, parent)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.tbox = tbox = tk.Text(self, **kwargs)
        tbox.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        self.vsb = vsb = AutoScrollbar(self, command=tbox.yview)
        vsb.grid(row=0, column=1, sticky='nsew')
        tbox['yscrollcommand'] = self.check

    def check(self, *args):
        self.vsb.set(*args)
        if self.vsb.winfo_ismapped():
            self.event_generate("<<ScrollbarShown>>")
        else:
            self.event_generate("<<ScrollbarHidden>>")

    def bindtags(self, *args):
        return self.tbox.bindtags(*args)

    def reset_bindtags(self, event=None):
        self.tbox.bindtags((self.tbox, 'Text', '.', 'all'))

    def configure(self, *args, **kwargs):
        self.tbox.configure(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self.tbox.get(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.tbox.delete(*args, **kwargs)


class FileSelector(tk.Frame):
    "File selector widget."

    def __init__(self, parent, **kwargs):
        tk.Frame.__init__(self, parent)
        self.selector = selector = tk.Button(
            self, text="Browse", command=self.select_file)
        self.label = label = tk.Label(self, text="No files selected.")

        selector.pack(side="left")
        label.pack(side="right", fill="both")

    def select_file(self):
        name = filedialog.askopenfilename()
        if name:
            name = name.replace("\\", "/").split("/")[-1]
            self.label.config(text=name)
        else:
            self.label.config(text="No files selected.")

    def reset(self):
        self.label.config(text="No files selected.")

    def get_value(self):
        text = self.label["text"]
        if text == "No files selected.":
            return ""
        else:
            return text

    def configure(self, *args, **kwargs):
        self.selector.config(*args, **kwargs)
        if "activebackground" in kwargs:
            del kwargs["activebackground"]
        self.label.config(*args, **kwargs)
        self.config(*args, **kwargs)

class Notebook(ttk.Frame):
    """Drop-in replacement for the ttk.Notebook widget,
    The ttk.Notebook widget is incompatable with Tkhtml on some platforms, causing crashes when selecting tabs
    Workaround for Bug #19, this widget manages pages itself while a ttk.Notebook handles tabs. 
    Designed to look and behave exactly like a ttk.Notebook, just without any crashes."""
    
    def __init__(self, master, takefocus=True, **kwargs):
        ttk.Frame.__init__(self, master, **kwargs)
        self.notebook = notebook = ttk.Notebook(self, takefocus=takefocus)
        self.blankframe = lambda: tk.Frame(self.notebook, height=0, bd=0, highlightthickness=0)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        notebook.grid(row=0, column=0, sticky="ew")

        notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

        self.pages = []
        self.previous_page = None

    def on_tab_change(self, event):
        self.event_generate("<<NotebookTabChanged>>")
        tabId = self.notebook.index(self.notebook.select())
        newpage = self.pages[tabId]
        if self.previous_page:
            self.previous_page.grid_forget()
        newpage.grid(row=1, column=0, sticky="nsew")
        self.previous_page = newpage
        
    def add(self, child, **kwargs):
        if child in self.pages:
            raise ValueError("{} is already managed by {}.".format(child, self))
        self.notebook.add(self.blankframe(), **kwargs)
        self.pages.append(child)

    def insert(self, where, child, **kwargs):
        if child in self.pages:
            raise ValueError("{} is already managed by {}.".format(child, self))
        self.notebook.insert(where, self.blankframe(), **kwargs)
        self.pages.insert(where, child)
        
    def enable_traversal(self):
        self.notebook.enable_traversal()

    def select(self, tabId):
        if not isinstance(tabId, int) and tabId in self.pages:
            tabId = self.pages.index(tabId)
        self.notebook.select(tabId)
    
    def tab(self, tabId, option=None, **kwargs):
        if not isinstance(tabId, int) and tabId in self.pages:
            tabId = self.pages.index(tabId)
        self.notebook.tab(tabId, option, **kwargs)

    def forget(self, tabId):
        if not isinstance(tabId, int):
            tabId = self.pages.index(tabId)
            self.pages.remove(child)
        else:
            del self.pages[tabId]
        self.notebook.forget(self.pages.index(child))

    def index(self, child):
        try:
            return self.pages.index(child)
        except IndexError:
            return self.notebook.index(child)
    
    def tabs(self):
        return self.pages


class StoppableThread(threading.Thread):
    "A thread that stores a state flag that can be set and used to check if the thread is supposed to be running."

    def __init__(self,  *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.setDaemon(True)
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


def download(url, data=None, method="GET", decode=None):
    "Fetch files."
    "Technically this isn't thread-safe (even though it is being used inside threads by Tkinterweb, "
    "but as long as install_opener() is not called and a string is used as the url parameter we are okay."
    thread = threadname()
    url = url.replace(" ", "%20")
    if data and (method == "POST"):
        req = urlopen(Request(url, data, headers=HEADER))
    else:
        req = urlopen(Request(url, headers=HEADER))
    if not thread.isrunning():
        return None, url, ""
    data = req.read()
    url = req.geturl()
    info = req.info()
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
        return None, url, ""
    else:
        return data, url, filetype


@lru_cache()
def cachedownload(*args, **kwargs):
    "Fetch files and add them to the lru cache."
    return download(*args, **kwargs)


def shorten(string):
    "Shorten text to avoid overloading the terminal."
    if (len(string) > 100):
        string = string[:100] + "..."
    return string


def threadname():
    "Return the currently running thread."
    thread = threading.current_thread()
    if thread.name == 'MainThread':
        thread = PlaceholderThread()
    return thread


def currentpath(use_file=True):
    if use_file:
        return os.path.abspath(os.path.dirname(__file__))
    else:
        return os.getcwd()

def strip_css_url(url):
    return url[4:-1].replace("'", "").replace('"', '')

def get_tkhtml_folder():
    return os.path.join(currentpath(), "tkhtml",
                        platform.system(),
                        "64-bit" if sys.maxsize > 2**32 else "32-bit")


def load_tkhtml(master, location=None, force=False):
    """Load nessessary Tkhtml files"""
    global tkhtml_loaded
    if (not tkhtml_loaded) or force:
        if location:
            master.tk.eval(
                "global auto_path; lappend auto_path {%s}" % location)
        master.tk.eval("package require Tkhtml")
        tkhtml_loaded = True


def load_combobox(master, force=False):
    """Load combobox.tcl"""
    global combobox_loaded
    if not (combobox_loaded) or force:
        path = os.path.join(currentpath(), "tkhtml")
        master.tk.eval(
                "global auto_path; lappend auto_path {%s}" % path)
        master.tk.eval("package require combobox")
        combobox_loaded = True


def notifier(text):
    "Notifications printer."
    try:
        sys.stdout.write(str(text)+"\n\n")
    except Exception:
        "sys.stdout.write doesn't work in .pyw files."
        "Since .pyw files have no console, we can simply not bother printing messages."
