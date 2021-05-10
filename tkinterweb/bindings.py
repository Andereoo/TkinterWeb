import sys
import os.path
import platform

from PIL import ImageTk, Image

try:
    from urllib.request import Request, urlopen
    from urllib.parse import urlparse, urljoin, urlunparse
    import tkinter as tk
except ImportError: # Python 2
    from urllib2 import urlopen, Request
    from urlparse import urlparse, urljoin, urlunparse
    import Tkinter as tk

from utils import _ScrolledText, DEFAULTSTYLE

try:
    import cairo
    cairoimport = True
except ImportError:
    cairoimport = False
try:
    import rsvg
    rsvgimport = "rsvg"
except ImportError:
    try:
        import cairosvg
        rsvgimport = "cairosvg"
    except ImportError:
        try:
            import gi
            try:
                gi.require_version('Rsvg', '1.0')
            except:
                gi.require_version('Rsvg', '2.0')
            from gi.repository import Rsvg
            rsvgimport = "girsvg"
        except:
            rsvgimport = None
if cairoimport and rsvgimport:
    try:
        from io import BytesIO
    except ImportError:
        import BytesIO


_tkhtml_loaded = False
_combobox_loaded = False


def load_tkhtml(master, location=None, force=False):
    """Load nessessary Tkhtml files"""
    global _tkhtml_loaded
    if (not _tkhtml_loaded) or force:
        if location:
            master.tk.eval("global auto_path; lappend auto_path {%s}" % location)
        master.tk.eval("package require Tkhtml")
        _tkhtml_loaded = True


def load_combobox(master, force=False):
    """Load combobox.tcl"""
    global _combobox_loaded
    if not (_combobox_loaded) or force:
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                            "tkhtml",
                            "combobox.tcl")
        if platform.system() == "Windows":
            path = path.replace("\\", "/")
        master.tk.eval("source {0}".format(path))
        _combobox_loaded = True        


def get_tkhtml_folder():
    """Fetch the Tkhtml3 folder for the current platform"""
    return os.path.join (os.path.abspath(os.path.dirname(__file__)),"tkhtml",
                         platform.system(),
                         "64-bit" if sys.maxsize > 2**32 else "32-bit")


class Combobox(tk.Widget):
    """Bindings for Bryan Oakley's combobox widget"""
    def __init__(self, master):
        load_combobox(master)
        try:
            tk.Widget.__init__(self, master, "::combobox::combobox")
        except tk.TclError:
            load_combobox(master, force=True)
            tk.Widget.__init__(self, master, "::combobox::combobox")
        self.configure(highlightthickness=0, borderwidth=0, editable=False,
                               takefocus=0, selectbackground="#6eb9ff",
                               relief="flat", elementborderwidth=0,
                               buttonbackground="white")
        self.data = [""]
        self.values = [""]
        
    def insert(self, data, values):
        for elem in reversed(data):
            self.tk.call(self._w, "list", "insert", 0, elem)
        self.tk.call(self._w, "select", 0)
        self.data = data
        self.values = values

    def reset(self):
        self.tk.call(self._w, "select", 0)

    def get(self):
        val = self.tk.call(self._w, "curselection")[0]
        return self.values[val]


class TkinterWeb(tk.Widget):
    """Tkhtml3 widget bindings"""
    def __init__(self, master, message_func, cfg={}, **kw):
        # widget settings
        self.stylesheets_enabled = True
        self.images_enabled = True
        self._base_url = ""
        self.currently_hovered_node = ""
        self.visited_links = []
        self._recursive_hovering_count = 15
        self._recursive_link_count = 15
        self._message_func = message_func
        self._title_change_func = lambda title:None
        self._cursor_change_func = lambda url:None
        self._link_click_func = lambda url:None
        self._form_submit_func = lambda url, data, method: None
        
        self.cursors = {
          "crosshair": "crosshair",
          "default": "",
          "pointer": "hand2",
          "move": "fleur",
          "text": "xterm",
          "wait": "watch",
          "progress": "box_spiral",
          "help": "question_arrow",
          "none": "none",
        }
        
        # widget status variables
        self._style_count = 0
        self._prev_hovered_nodes = []
        self._stored_widgets = {}
        self._prev_active_node = None
        self._selecting = False
        self._prev_cursor = ""

        # input element settings
        self._on_embedded_node = None
        self._radio_buttons = {}
        
        # handle images
        self._broken_image = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x19\x00\x00\x00\x1e\x08\x03\x00\x00\x00\xee2E\xe9\x00\x00\x03\x00PLTE\xc5\xd5\xf4\xcd\xdb\xf4\xdf\xe8\xfc\xd5\xdd\xf4\xa5\xa3\xa5\x85\x83\x85\xfc\xfe\xfc\xf4\xf6\xf9\x95\x93\x95S\xb39\x9d\x9f\x9d\xc5\xd3\xedo\xbbg\xd5\xe3\xf4\xd5\xdf\xfc\xd5\xe3\xfc\xb5\xcf\xd5\x9d\xc7\xb5\xc5\xdf\xe5S\xaf9\x8d\xc7\x8d\x15\x15\x15\x16\x16\x16\x17\x17\x17\x18\x18\x18\x19\x19\x19\x1a\x1a\x1a\x1b\x1b\x1b\x1c\x1c\x1c\x1d\x1d\x1d\x1e\x1e\x1e\x1f\x1f\x1f   !!!"""###$$$%%%&&&\'\'\'((()))***+++,,,---...///000111222333444555666777888999:::;;;<<<===>>>???@@@AAABBBCCCDDDEEEFFFGGGHHHIIIJJJKKKLLLMMMNNNOOOPPPQQQRRRSSSTTTUUUVVVWWWXXXYYYZZZ[[[\\\\\\]]]^^^___```aaabbbcccdddeeefffggghhhiiijjjkkklllmmmnnnooopppqqqrrrssstttuuuvvvwwwxxxyyyzzz{{{|||}}}~~~\x7f\x7f\x7f\x80\x80\x80\x81\x81\x81\x82\x82\x82\x83\x83\x83\x84\x84\x84\x85\x85\x85\x86\x86\x86\x87\x87\x87\x88\x88\x88\x89\x89\x89\x8a\x8a\x8a\x8b\x8b\x8b\x8c\x8c\x8c\x8d\x8d\x8d\x8e\x8e\x8e\x8f\x8f\x8f\x90\x90\x90\x91\x91\x91\x92\x92\x92\x93\x93\x93\x94\x94\x94\x95\x95\x95\x96\x96\x96\x97\x97\x97\x98\x98\x98\x99\x99\x99\x9a\x9a\x9a\x9b\x9b\x9b\x9c\x9c\x9c\x9d\x9d\x9d\x9e\x9e\x9e\x9f\x9f\x9f\xa0\xa0\xa0\xa1\xa1\xa1\xa2\xa2\xa2\xa3\xa3\xa3\xa4\xa4\xa4\xa5\xa5\xa5\xa6\xa6\xa6\xa7\xa7\xa7\xa8\xa8\xa8\xa9\xa9\xa9\xaa\xaa\xaa\xab\xab\xab\xac\xac\xac\xad\xad\xad\xae\xae\xae\xaf\xaf\xaf\xb0\xb0\xb0\xb1\xb1\xb1\xb2\xb2\xb2\xb3\xb3\xb3\xb4\xb4\xb4\xb5\xb5\xb5\xb6\xb6\xb6\xb7\xb7\xb7\xb8\xb8\xb8\xb9\xb9\xb9\xba\xba\xba\xbb\xbb\xbb\xbc\xbc\xbc\xbd\xbd\xbd\xbe\xbe\xbe\xbf\xbf\xbf\xc0\xc0\xc0\xc1\xc1\xc1\xc2\xc2\xc2\xc3\xc3\xc3\xc4\xc4\xc4\xc5\xc5\xc5\xc6\xc6\xc6\xc7\xc7\xc7\xc8\xc8\xc8\xc9\xc9\xc9\xca\xca\xca\xcb\xcb\xcb\xcc\xcc\xcc\xcd\xcd\xcd\xce\xce\xce\xcf\xcf\xcf\xd0\xd0\xd0\xd1\xd1\xd1\xd2\xd2\xd2\xd3\xd3\xd3\xd4\xd4\xd4\xd5\xd5\xd5\xd6\xd6\xd6\xd7\xd7\xd7\xd8\xd8\xd8\xd9\xd9\xd9\xda\xda\xda\xdb\xdb\xdb\xdc\xdc\xdc\xdd\xdd\xdd\xde\xde\xde\xdf\xdf\xdf\xe0\xe0\xe0\xe1\xe1\xe1\xe2\xe2\xe2\xe3\xe3\xe3\xe4\xe4\xe4\xe5\xe5\xe5\xe6\xe6\xe6\xe7\xe7\xe7\xe8\xe8\xe8\xe9\xe9\xe9\xea\xea\xea\xeb\xeb\xeb\xec\xec\xec\xed\xed\xed\xee\xee\xee\xef\xef\xef\xf0\xf0\xf0\xf1\xf1\xf1\xf2\xf2\xf2\xf3\xf3\xf3\xf4\xf4\xf4\xf5\xf5\xf5\xf6\xf6\xf6\xf7\xf7\xf7\xf8\xf8\xf8\xf9\xf9\xf9\xfa\xfa\xfa\xfb\xfb\xfb\xfc\xfc\xfc\xfd\xfd\xfd\xfe\xfe\xfe\xff\xff\xff\x01\xb3\x9a&\x00\x00\x01+IDATx\x9c\x9d\x91\xe9\x92\x84 \x0c\x84s (\x08A\xc6\xf7\x7f\xd6M8\x9c\x9d\xa9\xda?\xdb\x96W\x7f\xb6\xd5\x04\xf0\x7f\t\xdcT\x9c\xf7}\x0f\xf4I\x16U\x12\x16\t\x1f\xdaw\xe7\x16!\xcay\x9cL\xac\xc4\xfb\x18\x06\xc9\x81\x14\xd0\xd4o\xc2\x88\xa5X\x1e\x0b"\x1a\xf1\xd1\x05\x0f1f3\x06\xc9\x85\xb6Nb\x08\xe0\xa2d\x9cK\xd00\xefKF\x16\xf0E\ti?\xb2\x8aJ2\xf9\'\x83\xa8]Fy#\xa8\x1d\x00\x91\xa1\x01d\xad\x9e1h\x11m EM(\xa2vA\xe0\xc2,T,\xe3\x98$\xc1T\xd307 \xda6[)C\xea\x16\x1aK\x8c\rDv#BF\xd4\x03\xb4\x0b\xa4\x02,:\x83\xe8H i\xc2<\xec,%\xa2>\x1d\xc9)\x8dD\xad\xfd\x89a\xce\xad\x10\xdbw\xa0\xa0Z.\xa54v!\x8a@\x85\xeb:^\xaf\xe38\xcfZ\x19\xfc"E\xbf\xbf.\x03F\x1a\xf0 Q\xbbUM\xbc\xd5\xfd\xbeR\xa2\xda\x9d\xb3\x1f\xdd\x97\xbc\xf5Y\xf35\xc9\x93\xd0\x19\xe8\xdc\\k_\x7f\xf2g\xb6\x19\xc4\xf8\x90s\x91\x17\xe5\xbe\x0b\xf7\xf9\x99\xd0\x87\xfbV\xb2\xbd\xd5\xfd\xe7\xed?\xe4\x07\xca\xeb\x13o\x88}\xa9\x12\x00\x00\x00\x00IEND\xaeB`\x82'
        self._ignore_invalid_images = False
        
        if "imagecmd" not in kw:
            kw["imagecmd"] = master.register(self._fetch_image)

        if "defaultstyle" not in kw:
            kw["defaultstyle"] = DEFAULTSTYLE

        folder = get_tkhtml_folder()
            
        # load the Tkhtml3 widget
        self._message_func(
            "Fetching Tkhtml3 for {0} {1} with Python {2}.".format(
                "64-bit" if sys.maxsize > 2**32 else "32-bit",
                platform.system().replace("Darwin", "MacOSX"),
                str(sys.version_info[0:3]).replace(", ", ".").replace(")", "").replace("(", "")),
            "Tkhtml3 found in {0}.".format(folder))
        load_tkhtml(master, folder)
        try:
            tk.Widget.__init__(self, master, "html", cfg, kw)
        except tk.TclError:
            load_tkhtml(master, folder, force=True)
            tk.Widget.__init__(self, master, "html", cfg, kw)
        self.bindtags(self.bindtags() + ("bc{0}.nodes".format(self),))
        
        # enable text selection, image loading, and pseudo-element flagging
        self._selection_start_node = None
        self._selection_start_offset = None
        self._selection_end_node = None
        self._selection_end_offset = None
        self.bind("<B1-Motion>", self._extend_selection, True)
        self.bind("<<Copy>>", self._copy_selection_to_clipboard, True)
        self.bind("<Button-1>", self._on_click, True)
        self.bind("<ButtonRelease-1>", self._on_click_release, True)
        self.bind_class("bc{0}.nodes".format(self), "<Motion>", self._mouse_motion, True)
        self.bind_class("bc{0}.embeddednodes".format(self), "<Button-1>", self._embedded_mouse_grab, True)
        self.bind_class("bc{0}.embeddednodes".format(self), "<ButtonRelease-1>", self._embedded_mouse_release, True)
        self._image_name_prefix = str(id(self)) + "_img_"
        self._images = set() # to avoid python garbage collector from stealing images

        # enable form resetting and submission
        self._form_get_commands = {}
        self._form_reset_commands = {}
        self._form_elements = {}
        self._forms = {}
        
        # handle tags
        self.tk.call(self._w, "handler", "script", "script", self.register(self._on_script))
        self.tk.call(self._w, "handler", "script", "style", self.register(self._on_style))
        self.tk.call(self._w, "handler", "node", "link", self.register(self._on_link))
        self.tk.call(self._w, "handler", "node", "title", self.register(self._on_title))
        self.tk.call(self._w, "handler", "node", "a", self.register(self._on_a))
        self.tk.call(self._w, "handler", "node", "base", self.register(self._on_base))
        self.tk.call(self._w, "handler", "node", "input", self.register(self._on_input))
        self.tk.call(self._w, "handler", "node", "textarea", self.register(self._on_input))
        self.tk.call(self._w, "handler", "node", "select", self.register(self._on_input))
        self.tk.call(self._w, "handler", "node", "button", self.register(self._on_input))
        self.tk.call(self._w, "handler", "node", "form", self.register(self._on_form))

    def node(self, *arguments):
        """Retrieve one or more document
        node handles from the current document."""
        return self.tk.call(self._w, "node", *arguments)

    def parse(self, *args):
        """Parse HTML code"""
        self._prev_hovered_nodes = []
        self.tk.call(self._w, "parse", *args)
        self._setup_widgets()

    def parse_css(self, *args):
        """Parse CSS code"""
        self.tk.call(self._w, "style", *args)
        
    def reset(self):
        """Reset the widget"""
        self._link_ids = {}
        self._images = set()
        self._form_get_commands = {}
        self._form_elements = {}
        self._forms = {}
        self._on_embedded_node = None
        self._radio_buttons = {}
        return self.tk.call(self._w, "reset")

    def tag(self, subcommand, tag_name, *arguments):
        """Return the name of the Html tag that generated this
        document node, or an empty string if the node is a text node. """
        return self.tk.call(self._w, "tag", subcommand, tag_name, *arguments)

    def search(self, selector):
        """Search the document for the specified CSS
        selector; return a Tkhtml3 node if found."""
        return self.tk.call(self._w, "search", selector)

    def text(self, *args):
        """Enable interaction with the text of the HTML document."""
        return self.tk.call(self._w, "text", *args)

    def xview(self, *args):
        """Used to control horizontal scrolling."""
        if args: return self.tk.call(self._w, "xview", *args)
        coords = map(float, self.tk.call(self._w, "xview").split())
        return tuple(coords)

    def xview_moveto(self, fraction):
        """Adjusts horizontal position of the widget so that fraction
        of the horizontal span of the document is off-screen to the left.
        """
        return self.xview("moveto", fraction)

    def xview_scroll(self, number, what):
        """Shifts the view in the window according to number and what;
        number is an integer, and what is either "units" or "pages".
        """
        return self.xview("scroll", number, what)

    def yview(self, *args):
        """Used to control the vertical position of the document."""
        if args: return self.tk.call(self._w, "yview", *args)
        coords = map(float, self.tk.call(self._w, "yview").split())
        return tuple(coords)

    def yview_name(self, name):
        """Adjust the vertical position of the document so that the tag
        <a name=NAME...> is visible and preferably near the top of the window.
        """
        return self.yview(name)

    def yview_moveto(self, fraction):
        """Adjust the vertical position of the document so that fraction of
        the document is off-screen above the visible region.
        """
        return self.yview("moveto", fraction)

    def yview_scroll(self, number, what):
        """Shifts the view in the window up or down, according to number and
        what. "number" is an integer, and "what" is either "units" or "pages".
        """
        return self.yview("scroll", number, what)

    def _on_script(self, *args):
        """Currently just ignoring script"""
        
    def _on_style(self, attributes, tagcontents):
        """Handle <style> elements"""
        if not self.stylesheets_enabled:
            return
        self._style_count += 1
        ids = "author."+ str(self._style_count).zfill(4)
        handler_proc = self.register(lambda new_url, parent_url=self._base_url: self._on_at_import(parent_url, new_url))
        self.parse_css("-id", ids+".9999", "-importcmd", handler_proc, tagcontents)
        self._message_func("Finished loading <style> element.", "")

    def _on_link(self, node):
        """Load <link> elements"""
        if not self.stylesheets_enabled:
            return
        try:
            rel = self._get_node_attr(node, "rel")
        except tk.TclError:
            return
        if rel == "stylesheet":
            try:
                url = urljoin(self._base_url, self._get_node_attr(node, "href"))
                urldata = urlopen(Request(url, headers={"User-Agent": "Mozilla"})).read().decode()
                self._style_count += 1
                ids = "author."+ str(self._style_count).zfill(4)
                handler_proc = self.register(lambda new_url, parent_url=url: self._on_at_import(parent_url, new_url))
                self.parse_css("-id", ids+".9999", "-importcmd", handler_proc, urldata)
                self._message_func("Finished loading stylesheet.", "Sheet found at {0}.".format(url))
            except Exception as e:
                self._message_func("Error reading stylesheet.", "Url: {0}.".format(self._get_node_attr(node, "href")))

    def _on_at_import(self, parent_url, new_url):
        """Load @import scripts"""
        try:
            self._style_count += 1
            url = urljoin(parent_url, new_url)
            urldata = urlopen(Request(url, headers={"User-Agent": "Mozilla/5.1 (X11; U; Linux i686; en-US; rv:1.8.0.3) Gecko/20060425 SUSE/1.5.0.3-7 Hv3/alpha"})).read().decode()
            ids = "author."+ str(self._style_count).zfill(4)
            handler_proc = self.register(lambda new_url, parent_url=url: self._on_at_import(parent_url, new_url))             
            self.parse_css("-id", ids+".9999", "-importcmd", handler_proc, urldata)
            self._message_func("Finished loading stylesheet.", "Sheet found at {0}.".format(url))
        except Exception:
            self._message_func("Error reading stylesheet.", "Url: {0}.".format(new_url))

    def _on_title(self, node):
        """Handle <title> elements"""
        for child in (self.tk.call(node, "children")):
            self._title_change_func(self.tk.call(child, "text"))

    def _on_base(self, node):
        """Handle <base> elements"""
        try:
            href = self._get_node_attr(node, "href")
            self._base_url = href
        except Exception:
            self._message_func("Error setting base url.", "A <base> element has been found without an href attribute.")

    def _on_a(self, node):
        """Handle <a> elements"""
        self.tk.call(node, "dynamic", "set", "link")
        try:
            href = self._get_node_attr(node, "href")
            url = urljoin(self._base_url, href)
            if url in self.visited_links:
                self.tk.call(node, "dynamic", "set", "visited")
        except tk.TclError:
            pass

    def _on_form(self, node):
        html = self.tk.call(node, "html")
        inputs = self.tk.call(html, "search", "INPUT,SELECT,TEXTAREA,BUTTON")
        for i in inputs:
            self._form_elements[i] = node
        self._forms[node] = inputs

    def _on_input(self, node):
        """Handle <input>, <textarea>, and <button> elements"""
        self.tk.eval('set type ""')
        nodetag = self.tk.eval("set tag [string tolower [%s tag]]" % node)
        nodetype = self.tk.eval("set nodetype [string tolower [%s attr -default {} type]]" % node)
        nodename = "{0}.{1}".format(nodetag, nodetype).lower()
        nodevalue = self._get_node_attr(node, "value")
        
        if nodetag == "select":
            text = []
            values = []
            for child in self._get_node_children(node):
                if self._get_node_tag(child) == "option":
                    child2 = self._get_node_children(child)[0]
                    text.append(self._get_node_text(child2))
                    values.append(self._get_node_attr(child, "value"))

            widgetid = Combobox(self)
            widgetid.insert(text, values)
            self._form_get_commands[node] = lambda: widgetid.get()
            self._form_reset_commands[node] = lambda: widgetid.reset()
            self._replace_node(node, widgetid, lambda widgetid=widgetid: self._delete_node(widgetid), lambda node=node, widgetid=widgetid, widgettype="text": self._style_node(node, widgetid, widgettype))
        elif nodetag == "textarea":
            widgetid = _ScrolledText(self, borderwidth=0, selectborderwidth=0, highlightthickness=0)
            self._form_get_commands[node] = lambda: widgetid.get("1.0",'end-1c')
            self._form_reset_commands[node] = lambda: widgetid.delete("0.0", "end")
            self._replace_node(node, widgetid, lambda widgetid=widgetid: self._delete_node(widgetid), lambda node=node, widgetid=widgetid, widgettype="text": self._style_node(node, widgetid, widgettype))
        elif nodetag == "button":
            children = self._get_node_children(node)
            if isinstance(children, tuple):
                children = self._get_node_text(children[0])
            if children != "":
                widgetid = tk.Button(self, text=children, borderwidth=1, padx=3, pady=2, highlightthickness=0)
                self._replace_node(node, widgetid, lambda widgetid=widgetid: self._delete_node(widgetid), lambda node=node, widgetid=widgetid: self._style_node(node, widgetid))
        elif nodename == "input.image":
            pass
        elif nodename == "input.submit":
            if nodevalue == "":
                nodevalue = "Submit"
            widgetid = tk.Button(self, text=nodevalue, borderwidth=1, padx=3, pady=2, highlightthickness=0)
            widgetid.config(command=lambda node=node: self._submit_form(node))
            self._replace_node(node, widgetid, lambda widgetid=widgetid: self._delete_node(widgetid), lambda node=node, widgetid=widgetid: self._style_node(node, widgetid))
        elif nodename == "input.reset":
            if nodevalue == "":
                nodevalue = "Reset"
            widgetid = tk.Button(self, text=nodevalue, borderwidth=1, padx=3, pady=2, highlightthickness=0)
            widgetid.config(command=lambda node=node: self._reset_form(node))
            self._replace_node(node, widgetid, lambda widgetid=widgetid: self._delete_node(widgetid), lambda node=node, widgetid=widgetid: self._style_node(node, widgetid))
        elif nodename == "input.button":
            widgetid = tk.Button(self, text=nodevalue, borderwidth=1, padx=3, pady=2, highlightthickness=0)
            self._replace_node(node, widgetid, lambda widgetid=widgetid: self._delete_node(widgetid), lambda node=node, widgetid=widgetid: self._style_node(node, widgetid))
        elif nodename == "input.hidden":
            self._form_get_commands[node] = lambda node=node: self._get_node_attr(node, "value")
            self._form_reset_commands[node] = lambda: None
        elif nodename == "input.checkbox":
            variable = tk.IntVar()
            widgetid = tk.Checkbutton(self, borderwidth=0, padx=0, pady=0, highlightthickness=0, variable=variable)
            self._form_get_commands[node] = lambda: variable.get()
            self._form_reset_commands[node] = lambda: variable.set(0)
            self._replace_node(node, widgetid, lambda widgetid=widgetid: self._delete_node(widgetid), lambda node=node, widgetid=widgetid: self._style_node(node, widgetid))
        elif nodename == "input.radio":
            name = self.tk.call(node, "attr", "-default", "", "name")
            if name in self._radio_buttons:
                variable = self._radio_buttons[name]
            else:
                variable = tk.StringVar(self, value=nodevalue)
                self._radio_buttons[name] = variable   
            widgetid = tk.Radiobutton(self, value=nodevalue, variable=variable, borderwidth=0, padx=0, pady=0, highlightthickness=0)
            self._form_get_commands[node] = lambda: variable.get()
            self._form_reset_commands[node] = lambda: variable.set("")
            self._replace_node(node, widgetid, lambda widgetid=widgetid: self._delete_node(widgetid), lambda node=node, widgetid=widgetid: self._style_node(node, widgetid))
        elif nodename == "input.file":
            pass
        else:
            widgetid = tk.Entry(self, borderwidth=0, highlightthickness=0)
            widgetid.insert(0, nodevalue)
            if nodetype == "password":
                widgetid.configure(show='*')
            self._form_get_commands[node] = lambda: widgetid.get()
            widgetid.bind("<Return>", lambda event, node=node: self._submit_form(node=node))
            self._form_reset_commands[node] = lambda widgetid=widgetid, content=nodevalue: self._clear_and_set(widgetid, content)
            self._replace_node(node, widgetid, lambda widgetid=widgetid: self._delete_node(widgetid), lambda node=node, widgetid=widgetid, widgettype="text": self._style_node(node, widgetid, widgettype))

    def _clear_and_set(self, widgetid, content):
        widgetid.delete(0, "end")
        widgetid.insert(0, content)

    def _reset_form(self, node):
        if node not in self._form_elements:
            return
        
        form = self._form_elements[node]
        action = self._get_node_attr(form, "action")
        
        for formelement in self._forms[form]:
            nodetag = self._get_node_tag(formelement)
            nodetype = self._get_node_attr(formelement, "type")
            nodename = "{0}.{1}".format(nodetag, nodetype).lower()

            if any([nodename == "input.image", nodename == "input.submit",
                     nodename == "input.reset", nodename == "input.button",
                     nodetag == "button"]):
                continue
            else:
                self._form_reset_commands[formelement]()

    def _submit_form(self, node, event=None):
        if node not in self._form_elements:
            return
        
        data = ""
        form = self._form_elements[node]
        action = self._get_node_attr(form, "action")
        method = self.tk.call(form, "attribute", "-default", "GET", "method").upper()
        
        for formelement in self._forms[form]:
            nodeattrname = self._get_node_attr(formelement, "name")
            if nodeattrname != "":
                nodetag = self._get_node_tag(formelement)
                nodetype = self._get_node_attr(formelement, "type")
                nodename = "{0}.{1}".format(nodetag, nodetype).lower()

                if any([nodename == "input.image", nodename == "input.submit",
                         nodename == "input.reset", nodename == "input.button",
                         nodetag == "button"]):
                    continue
                else:
                    value = self._form_get_commands[formelement]()
                    data += "&{0}={1}".format(nodeattrname, value)
                    
        if data != "":
            if action == "":
                url = list(urlparse(self._base_url))
                url = url[:-3]
                url.extend(['','',''])
                url = urlunparse(url)
            else:
                url = urljoin(self._base_url, action)

            self._message_func("Form submitted.", "Url: {0}.".format(url))  
            if method == "GET":
                self._form_submit_func(url, "?" + data[1:].replace(" ", "+"), "GET")
            else:
                self._form_submit_func(url, data[1:].encode(), "POST")


    def _replace_node(self, node, widgetid, deletecmd, stylecmd=None, allowscrolling=True, handledelete=True):
        """Replace a Tkhtml3 node with a Tkinter widget"""
        if stylecmd:
            if handledelete:
                self.tk.call(node, "replace", widgetid, "-deletecmd", self.register(deletecmd), "-stylecmd", self.register(stylecmd))
            else:
                self.tk.call(node, "replace", widgetid, "-stylecmd", self.register(stylecmd))
        else:
            if handledelete:
                self.tk.call(node, "replace", widgetid, "-deletecmd", self.register(deletecmd))
            else:
                self.tk.call(node, "replace", widgetid)

        if allowscrolling:
            widgetid.bindtags(widgetid.bindtags() + ("bc{0}.nodes".format(self),"bc{0}.embeddednodes".format(self),"bc{0}.scrollableembeddednodes".format(self)))
        else:
            widgetid.bindtags(widgetid.bindtags() + ("bc{0}.nodes".format(self),"bc{0}.embeddednodes".format(self),))

        widgetid.bind("<Enter>", lambda event, node_handle=node: self._embedded_mouse_motion(event, node_handle=node_handle))
        widgetid.bind("<Leave>", lambda event, node_handle=None: self._embedded_mouse_motion(event, node_handle=node_handle))

    def _delete_node(self, widgetid):
        widgetid.destroy()

    def _style_node(self, node, widgetid, widgettype="button"):
        bg = self.tk.call(node, "property", "background-color")
        if bg == "transparent":
            bg = "white"
        fg = self.tk.call(node, "property", "color")
        if fg == "transparent":
            fg = "white"
        font = self.tk.call(node, "property", "font")
        if widgettype == "button":
            widgetid.configure(bg=bg, activebackground=bg, activeforeground=fg, fg=fg, font=font)
        else:
            widgetid.configure(bg=bg, fg=fg, font=font)     

    def _attach_broken_image(self, name):
        """Attach the broken image icon"""
        self._message_func("File is not supported yet.", "")
        if not self._ignore_invalid_images:
            self._images.add(ImageTk.PhotoImage(name=name, data=self._broken_image))

    def _attach_image(self, url, name, urltype):
        """Attach images using the specified url"""
        path=urlparse(url).path
        
        self._message_func("Fetching image data.", "Pasting image: {0}.".format(url))
        if path.endswith('.svg') or url.startswith("data:image/svg"):
            if not cairoimport:
                self._message_func("TkinterWeb requires Pycairo to parse .svg files.", "Consider installing it as it is not found on your path.")
            if not rsvgimport:
                self._message_func("TkinterWeb requires rsvg to parse .svg files.", "Consider installing it as it is not found on your path.")
            try:
                code=urlopen(Request(url, headers={"User-Agent": "Mozilla"})).read().decode()
                if rsvgimport== 'girsvg':
                    handle = Rsvg.Handle()
                    svg = handle.new_from_data(code.encode("utf-8"))
                    dim = svg.get_dimensions()
                    img = cairo.ImageSurface(cairo.FORMAT_ARGB32, dim.width, dim.height)
                    ctx = cairo.Context(img)
                    svg.render_cairo(ctx)
                    png_io = BytesIO()
                    img.write_to_png(png_io)
                    svg.close()
                    self._images.add(ImageTk.PhotoImage(name=name, data=png_io.getvalue()))
                elif rsvgimport == 'rsvg':
                    svg = rsvg.Handle(data=code)
                    img = cairo.ImageSurface(cairo.FORMAT_ARGB32,svg.props.width,svg.props.height)
                    ctx = cairo.Context(img)
                    svg.render_cairo(ctx)
                    png_io = BytesIO()
                    img.write_to_png(png_io)
                    svg.close()
                    self._images.add(ImageTk.PhotoImage(name=name, data=png_io.getvalue()))
                elif rsvgimport == 'cairosvg':
                    image_data = cairosvg.svg2png(bytestring=code)
                    image = Image.open(BytesIO(image_data))
                    tk_image = ImageTk.PhotoImage(image)                    
                    self._images.add(tk_image)
                else:
                    self._attach_broken_image(name)
            except Exception as e:
                self._attach_broken_image(name)
        else:
            try:
                req = urlopen(Request(url, headers={'User-Agent': 'Mozilla/5.1 (X11; U; Linux i686; en-US; rv:1.8.0.3) Gecko/20060425 SUSE/1.5.0.3-7 Hv3/alpha'}))
                data = req.read()
                req.close()
                self._images.add(ImageTk.PhotoImage(name=name, data=data))
            except Exception:
                self._attach_broken_image(name)

    def _fetch_image(self, *args):
        """Fetch images"""
        if not self.images_enabled:
            return
        assert len(args) == 1
        url = args[0]
        name = self._image_name_prefix + str(len(self._images))
        
        if any([url.startswith("linear-gradient("),
                url.startswith("radial-gradient("),
                url.startswith("repeating-linear-gradient("),
                url.startswith("repeating-radial-gradient(")]):
            self._message_func("Fetching image data.", "Pasting image: {0}.".format(url))
            self._attach_broken_image(name)
        else:
            url = urljoin(self._base_url, url)
            self._attach_image(url, name, url)
        return name

    def _get_node_text(self, node_handle):
        """Get the text content of the given node_handle"""
        return self.tk.call(node_handle, "text")

    def _get_node_tag(self, node_handle):
        """Get the HTML tag of the given node_handle"""
        return self.tk.call(node_handle, "tag")

    def _get_node_parent(self, node_handle):
        """Get the parent of the given node_handle"""
        return self.tk.call(node_handle, "parent")

    def _get_node_children(self, node_handle):
        """Get the children of the given node_handle"""
        return self.tk.call(node_handle, "children")    

    def _get_node_attr(self, node_handle, attribute):
        """Get the specified attribute of the given node_handle"""
        return self.tk.call(node_handle, "attribute", "-default", "", attribute)

    def _on_click(self, event):
        """Set active element flags"""
        self._start_selection(event)
        try:
            node_handle = self._get_current_node(event)
            if node_handle == "":
                return
        except ValueError:
            self._selection_start_node = None
            return

        if self.stylesheets_enabled:
            try:
                self.tk.call(node_handle, "dynamic", "set", "active")
                self._prev_active_node = node_handle
            except Exception:
                try:
                    node_handle = self._get_current_node_parent(node_handle)
                    self.tk.call(node_handle, "dynamic", "set", "active")
                    self._prev_active_node = node_handle
                except Exception:
                    pass

    def _handle_link_click(self, node_handle):
        """Handle link clicks"""
        href = self._get_node_attr(node_handle, "href")
        url = urljoin(self._base_url, href)
        self._message_func("Link clicked.", "Url: {0}.".format(url))
        self.visited_links.append(url)
        self._link_click_func(url)

    def _on_click_release(self, event):
        """Handle click releases on <a> nodes"""
        self._selecting = False
        if self._prev_active_node is not None:
            if self.stylesheets_enabled:
                self.tk.call(self._prev_active_node, "dynamic", "clear", "active")
        else:
            return

        try:
            node_handle = self._get_current_node(event)
            parent = self._get_current_node_parent(node_handle)

            if self.stylesheets_enabled:
                done = False
                
                if node_handle == self._prev_active_node:
                    if self._get_node_tag(node_handle) == "a":
                        self._handle_link_click(node_handle)
                        done = True
                        
                elif parent == self._prev_active_node:
                    if self._get_node_tag(parent) == "a":
                        self._handle_link_click(parent)
                        done = True
                        
                if not done:                
                    for i in self._prev_hovered_nodes:
                        if self._get_node_tag(i) == "a":
                            self._handle_link_click(i)
                            break
            else:
                if self._get_node_tag(node_handle) == "a":
                    self._handle_link_click(node_handle)
                elif self._get_node_tag(parent) == "a":
                    self._handle_link_click(parent)
        except Exception:
            pass

        if self.stylesheets_enabled:
            self._prev_active_node = None

    def _change_cursor(self, node_handle):
        """Handle CSS 'cursor' property"""
        try:
            cursor = self.tk.call(node_handle, "property", "cursor")
            cursor = self.cursors[cursor]
            if self._prev_cursor != cursor:
                self._cursor_change_func(cursor=cursor)
                self._prev_cursor = cursor
        except KeyError:
            try:
                cursor = self.tk.call(self._get_current_node_parent(node_handle), "property", "cursor")
                cursor = self.cursors[cursor]
                if self._prev_cursor != cursor:
                    self._cursor_change_func(cursor=cursor)
                    self._prev_cursor = cursor
            except Exception:
                if self._get_node_tag(node_handle) == "":
                    if self._prev_cursor != "text":
                        cursor = self.cursors["text"]
                        self._cursor_change_func(cursor=cursor)
                        self._prev_cursor = cursor
                else:
                    if self._prev_cursor != "":
                        self._cursor_change_func(cursor="")
                        self._prev_cursor = ""
                        
    def _on_leave(self, event):
        """Set the cursor to the default when leaving this widget"""
        self._cursor_change_func(cursor="")
        self._prev_cursor = ""

        for node in self._prev_hovered_nodes:
            self.tk.call(node, "dynamic", "clear", "hover")
        self._prev_hovered_nodes = []

    def _get_current_node(self, event):
        """Get current node"""
        return self.tk.eval("""set node [lindex [lindex [{0} node {1} {2}] end] end]""".format(self, event.x, event.y))

    def _get_current_node_parent(self, event):
        return self.tk.eval("""set node [lindex [lindex [{0} parent] end] end]""".format(event))

    def _embedded_mouse_motion(self, event, node_handle):
        self._on_embedded_node = node_handle

    def _embedded_mouse_grab(self, event):
        self._selecting = True

    def _embedded_mouse_release(self, event):
        self._selecting = False

    def _mouse_motion(self, event):
        """Set hover flags and handle the CSS 'cursor' property"""
        if self._selecting:
            return
        if self._on_embedded_node is None:
            try:
                node_handle = self._get_current_node(event)
                if node_handle == "":
                    self._on_leave(None)
                    return

            except ValueError:
                self._on_leave(None)
                return
        else:
            node_handle = self._on_embedded_node

        self.currently_hovered_node = node_handle
        
        self._change_cursor(node_handle)

        can_set = False

        if self.stylesheets_enabled:
            try:
                if self._prev_hovered_nodes == []:
                    can_set = True
                elif node_handle != self._prev_hovered_nodes[0]:
                    can_set = True
                if can_set:
                    for node in self._prev_hovered_nodes:
                        self.tk.call(node, "dynamic", "clear", "hover")
                    self.tk.call(node_handle, "dynamic", "set", "hover")
                    self._prev_hovered_nodes = [node_handle]
            except Exception as e:
                try:
                    node_handle = self._get_current_node_parent(node_handle)
                    if self._prev_hovered_nodes == []:
                        can_set = True
                    elif node_handle != self._prev_hovered_nodes[0]:
                        can_set = True
                    if can_set:
                        for node in self._prev_hovered_nodes:
                            self.tk.call(node, "dynamic", "clear", "hover")
                        self.tk.call(node_handle, "dynamic", "set", "hover")
                        self._prev_hovered_nodes = [node_handle]
                except Exception as e:
                    can_set = False

            try:
                self._set_hover_recursively(self._get_current_node_parent(node_handle), self._recursive_hovering_count)
            except Exception:
                pass

    def _set_hover_recursively(self, node_handle, count):
        """Set hover flags to the parents of
        the hovered element as well"""
        try:
            self.tk.call(node_handle, "dynamic", "set", "hover")
            self._prev_hovered_nodes.append(node_handle)
        except Exception:
            pass
        try:
            if count >= 1:
                self._set_hover_recursively(self._get_current_node_parent(node_handle), count-1)
        except Exception:
            pass

    def _zoom(self, multiplier):
        """Set and get the page zoom"""
        if multiplier:
            self.tk.call(self._w, "configure", "-zoom", multiplier)
        else:
            return self.tk.call(self._w, "cget", "-zoom")

    def _shrink(self, value):
        self.tk.call(self._w, "configure", "-shrink", value)

    def _fontscale(self, multiplier):
        """Set and get the font zoom"""
        if multiplier:
            self.tk.call(self._w, "configure", "-fontscale", multiplier)
        else:
            return self.tk.call(self._w, "cget", "-fontscale")
                
    def _start_selection(self, event):
        """Make selection possible"""
        self.focus_set()
        self.tag("delete", "selection")
        try:
            self._selection_start_node, self._selection_start_offset = self.node(True, event.x, event.y)
        except ValueError:
            self._selection_start_node = None

    def _extend_selection(self, event):
        """Alter selection and HTML element states based on mouse movement"""
        self.tag("delete", "selection")
        if self._selection_start_node is None:
            return
        try:
            self._selection_end_node, self._selection_end_offset = self.node(True, event.x, event.y)

            self.tag("add", "selection", self._selection_start_node, self._selection_start_offset, self._selection_end_node, self._selection_end_offset)
            self.tag("configure", "selection", "-background", "#3584e4")
            
            if self.stylesheets_enabled:
                if self._prev_active_node is not None:
                    if len(self._get_selected_text()) > 0:
                        self._selecting = True
                        self.tk.call(self._prev_active_node, "dynamic", "clear", "active")
                        self._prev_active_node = None
                        if self._prev_cursor != "text":
                            cursor = self.cursors["text"]
                            self._cursor_change_func(cursor=cursor)
                            self._prev_cursor = cursor
                        for node in self._prev_hovered_nodes:
                            self.tk.call(node, "dynamic", "clear", "hover")
                        self._prev_hovered_nodes = []
              
        except ValueError:
            self._selection_end_node = None

    def _setup_widgets(self):
        """Replace Tkhtml nodes with Tk widgets when needed"""
        widgets = self.search("[widgetid]")
        for node in widgets:
            widgetid = self._get_node_attr(node, "widgetid")
            allowscrolling = self._get_node_attr(node, "allowscrolling")
            widgetid = self.nametowidget(widgetid)
            self._stored_widgets[widgetid] = node
            self._replace_node(node, widgetid, lambda widgetid=widgetid: self._delete_node(widgetid), allowscrolling= (True if allowscrolling == "yes" else False), handledelete=False)

    def _replace_widget(self, widgetid, newwidgetid):
        """Replace a stored widget"""
        node = self._stored_widgets[widgetid]
        self.tk.call(node, "replace", newwidgetid)
        
        if newwidgetid in self._stored_widgets:
            self.tk.call(self._stored_widgets[newwidgetid], "replace", widgetid)
            self._stored_widgets[widgetid] = self._stored_widgets[newwidgetid]
        else:
            del self._stored_widgets[widgetid]
        
        self._stored_widgets[newwidgetid] = node

    def _remove_widget(self, widgetid):
        """Remove a stored widget"""
        self.tk.call(self._stored_widgets[widgetid], "replace", "<p></p>")
        del self._stored_widgets[widgetid]

    def _replace_html(self, selector, widgetid):
        """Replace an HTML element with a widget"""
        node = self.search(selector)[0]
        self.tk.call(node, "replace", widgetid)
        self._stored_widgets[widgetid] = node
        
    def _get_selected_text(self):
        """Return the currently selected text"""
        if self._selection_start_node is None or self._selection_end_node is None:
            return
        start_index = self.text("offset", self._selection_start_node, self._selection_start_offset)
        end_index = self.text("offset", self._selection_end_node, self._selection_end_offset)
        if start_index > end_index:
            start_index, end_index = end_index, start_index
        whole_text = self.text("text")
        return whole_text[start_index:end_index]

    def _copy_selection_to_clipboard(self, event=None):
        """Copy the selected text to the clipboard"""
        selected_text = self._get_selected_text()
        self.clipboard_clear()
        self.clipboard_append(selected_text)
        self._message_func("Text copied to clipboard.", "Text: '{0}'.".format(selected_text))
