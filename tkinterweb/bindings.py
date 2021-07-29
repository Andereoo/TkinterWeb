try:
    from urllib.parse import urljoin, urlparse, urlunparse, urlencode
except ImportError:
    from urlparse import urljoin, urlparse, urlunparse
    from urllib import urlencode

try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk

from utilities import *
from imageutils import *

import re
import sys
import platform


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
        self.default = 0

    def insert(self, data, values, selected):
        for elem in reversed(data):
            self.tk.call(self._w, "list", "insert", 0, elem)
        self.data = data
        self.values = values
        if selected:
            self.default = self.values.index(selected)
        self.reset()

    def reset(self):
        self.tk.call(self._w, "select", self.default)

    def get(self):
        val = self.tk.call(self._w, "curselection")[0]
        return self.values[val]


class TkinterWeb(tk.Widget):
    """Bindings for the Tkhtml3 HTML widget"""

    def __init__(self, master, message_func, embed_obj, cfg={}, **kwargs):
        self.message_func = message_func
        folder = get_tkhtml_folder()

        # provide OS information for troubleshooting
        self.message_func(
            "Starting TkinterWeb for {} {} with Python {}.".format(
                "64-bit" if sys.maxsize > 2**32 else "32-bit",
                platform.system(),
                str(sys.version_info[0:3]).replace(", ", ".").replace(")", "").replace("(", "")))

        # pre-load custom stylesheet and register the image loading infrastructure
        if "imagecmd" not in kwargs:
            kwargs["imagecmd"] = master.register(self.on_image)
        if "defaultstyle" not in kwargs:
            kwargs["defaultstyle"] = DEFAULTSTYLE

        # catch htmldrawcleanup crashes on supported platforms
        if (platform.system() == "Windows") or (platform.system() == "Linux" and sys.maxsize > 2**32):
            if "drawcleanupcrashcmd" not in kwargs:
                kwargs["drawcleanupcrashcmd"] = master.register(self.on_drawcleanupcrash)

        # load the Tkhtml3 widget
        try:
            load_tkhtml(master, folder)
            tk.Widget.__init__(self, master, "html", cfg, kwargs)
        except tk.TclError:
            load_tkhtml(master, folder, force=True)
            tk.Widget.__init__(self, master, "html", cfg, kwargs)

        self.message_func("Tkhtml3 successfully loaded from {}.".format(folder))

        # widget settings
        self.stylesheets_enabled = True
        self.images_enabled = True
        self.forms_enabled = True
        self.caches_enabled = True
        self.objects_enabled = True
        self.ignore_invalid_images = True
        self.prevent_crashes = True
        self.base_url = ""
        self.currently_hovered_node = ""
        self.recursive_hovering_count = 5
        self.max_thread_count = 20
        self.visited_links = []
        self.title_change_func = self.placeholder
        self.icon_change_func = self.placeholder
        self.cursor_change_func = self.placeholder
        self.link_click_func = self.placeholder
        self.form_submit_func = self.placeholder
        self.done_loading_func = self.placeholder
        self.downloading_resource_func = self.placeholder

        # widget status variables
        self.embed_obj = embed_obj
        self.style_count = 0
        self.active_threads = []
        self.stored_widgets = {}
        self.loaded_images = set()
        self.image_name_prefix = "_tkinterweb_img_{}_".format(id(self))
        self.is_selecting = False
        self.downloads_have_occured = False
        self.unstoppable = True
        self.on_embedded_node = None
        self.selection_start_node = None
        self.selection_start_offset = None
        self.selection_end_node = None
        self.selection_end_offset = None
        self.prev_active_node = None
        self.prev_hovered_nodes = []
        self.prev_cursor = ""

        # enable form resetting and submission
        self.form_get_commands = {}
        self.form_reset_commands = {}
        self.form_elements = {}
        self.loaded_forms = {}
        self.radio_buttons = {}

        # other UI variables
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
        self.broken_image = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x19\x00\x00\x00\x1e\x08\x03\x00\x00\x00\xee2E\xe9\x00\x00\x03\x00PLTE\xc5\xd5\xf4\xcd\xdb\xf4\xdf\xe8\xfc\xd5\xdd\xf4\xa5\xa3\xa5\x85\x83\x85\xfc\xfe\xfc\xf4\xf6\xf9\x95\x93\x95S\xb39\x9d\x9f\x9d\xc5\xd3\xedo\xbbg\xd5\xe3\xf4\xd5\xdf\xfc\xd5\xe3\xfc\xb5\xcf\xd5\x9d\xc7\xb5\xc5\xdf\xe5S\xaf9\x8d\xc7\x8d\x15\x15\x15\x16\x16\x16\x17\x17\x17\x18\x18\x18\x19\x19\x19\x1a\x1a\x1a\x1b\x1b\x1b\x1c\x1c\x1c\x1d\x1d\x1d\x1e\x1e\x1e\x1f\x1f\x1f   !!!"""###$$$%%%&&&\'\'\'((()))***+++,,,---...///000111222333444555666777888999:::;;;<<<===>>>???@@@AAABBBCCCDDDEEEFFFGGGHHHIIIJJJKKKLLLMMMNNNOOOPPPQQQRRRSSSTTTUUUVVVWWWXXXYYYZZZ[[[\\\\\\]]]^^^___```aaabbbcccdddeeefffggghhhiiijjjkkklllmmmnnnooopppqqqrrrssstttuuuvvvwwwxxxyyyzzz{{{|||}}}~~~\x7f\x7f\x7f\x80\x80\x80\x81\x81\x81\x82\x82\x82\x83\x83\x83\x84\x84\x84\x85\x85\x85\x86\x86\x86\x87\x87\x87\x88\x88\x88\x89\x89\x89\x8a\x8a\x8a\x8b\x8b\x8b\x8c\x8c\x8c\x8d\x8d\x8d\x8e\x8e\x8e\x8f\x8f\x8f\x90\x90\x90\x91\x91\x91\x92\x92\x92\x93\x93\x93\x94\x94\x94\x95\x95\x95\x96\x96\x96\x97\x97\x97\x98\x98\x98\x99\x99\x99\x9a\x9a\x9a\x9b\x9b\x9b\x9c\x9c\x9c\x9d\x9d\x9d\x9e\x9e\x9e\x9f\x9f\x9f\xa0\xa0\xa0\xa1\xa1\xa1\xa2\xa2\xa2\xa3\xa3\xa3\xa4\xa4\xa4\xa5\xa5\xa5\xa6\xa6\xa6\xa7\xa7\xa7\xa8\xa8\xa8\xa9\xa9\xa9\xaa\xaa\xaa\xab\xab\xab\xac\xac\xac\xad\xad\xad\xae\xae\xae\xaf\xaf\xaf\xb0\xb0\xb0\xb1\xb1\xb1\xb2\xb2\xb2\xb3\xb3\xb3\xb4\xb4\xb4\xb5\xb5\xb5\xb6\xb6\xb6\xb7\xb7\xb7\xb8\xb8\xb8\xb9\xb9\xb9\xba\xba\xba\xbb\xbb\xbb\xbc\xbc\xbc\xbd\xbd\xbd\xbe\xbe\xbe\xbf\xbf\xbf\xc0\xc0\xc0\xc1\xc1\xc1\xc2\xc2\xc2\xc3\xc3\xc3\xc4\xc4\xc4\xc5\xc5\xc5\xc6\xc6\xc6\xc7\xc7\xc7\xc8\xc8\xc8\xc9\xc9\xc9\xca\xca\xca\xcb\xcb\xcb\xcc\xcc\xcc\xcd\xcd\xcd\xce\xce\xce\xcf\xcf\xcf\xd0\xd0\xd0\xd1\xd1\xd1\xd2\xd2\xd2\xd3\xd3\xd3\xd4\xd4\xd4\xd5\xd5\xd5\xd6\xd6\xd6\xd7\xd7\xd7\xd8\xd8\xd8\xd9\xd9\xd9\xda\xda\xda\xdb\xdb\xdb\xdc\xdc\xdc\xdd\xdd\xdd\xde\xde\xde\xdf\xdf\xdf\xe0\xe0\xe0\xe1\xe1\xe1\xe2\xe2\xe2\xe3\xe3\xe3\xe4\xe4\xe4\xe5\xe5\xe5\xe6\xe6\xe6\xe7\xe7\xe7\xe8\xe8\xe8\xe9\xe9\xe9\xea\xea\xea\xeb\xeb\xeb\xec\xec\xec\xed\xed\xed\xee\xee\xee\xef\xef\xef\xf0\xf0\xf0\xf1\xf1\xf1\xf2\xf2\xf2\xf3\xf3\xf3\xf4\xf4\xf4\xf5\xf5\xf5\xf6\xf6\xf6\xf7\xf7\xf7\xf8\xf8\xf8\xf9\xf9\xf9\xfa\xfa\xfa\xfb\xfb\xfb\xfc\xfc\xfc\xfd\xfd\xfd\xfe\xfe\xfe\xff\xff\xff\x01\xb3\x9a&\x00\x00\x01+IDATx\x9c\x9d\x91\xe9\x92\x84 \x0c\x84s (\x08A\xc6\xf7\x7f\xd6M8\x9c\x9d\xa9\xda?\xdb\x96W\x7f\xb6\xd5\x04\xf0\x7f\t\xdcT\x9c\xf7}\x0f\xf4I\x16U\x12\x16\t\x1f\xdaw\xe7\x16!\xcay\x9cL\xac\xc4\xfb\x18\x06\xc9\x81\x14\xd0\xd4o\xc2\x88\xa5X\x1e\x0b"\x1a\xf1\xd1\x05\x0f1f3\x06\xc9\x85\xb6Nb\x08\xe0\xa2d\x9cK\xd00\xefKF\x16\xf0E\ti?\xb2\x8aJ2\xf9\'\x83\xa8]Fy#\xa8\x1d\x00\x91\xa1\x01d\xad\x9e1h\x11m EM(\xa2vA\xe0\xc2,T,\xe3\x98$\xc1T\xd307 \xda6[)C\xea\x16\x1aK\x8c\rDv#BF\xd4\x03\xb4\x0b\xa4\x02,:\x83\xe8H i\xc2<\xec,%\xa2>\x1d\xc9)\x8dD\xad\xfd\x89a\xce\xad\x10\xdbw\xa0\xa0Z.\xa54v!\x8a@\x85\xeb:^\xaf\xe38\xcfZ\x19\xfc"E\xbf\xbf.\x03F\x1a\xf0 Q\xbbUM\xbc\xd5\xfd\xbeR\xa2\xda\x9d\xb3\x1f\xdd\x97\xbc\xf5Y\xf35\xc9\x93\xd0\x19\xe8\xdc\\k_\x7f\xf2g\xb6\x19\xc4\xf8\x90s\x91\x17\xe5\xbe\x0b\xf7\xf9\x99\xd0\x87\xfbV\xb2\xbd\xd5\xfd\xe7\xed?\xe4\x07\xca\xeb\x13o\x88}\xa9\x12\x00\x00\x00\x00IEND\xaeB`\x82'

        # set up bindtags
        self.node_tag = "tkinterweb.{0}.nodes".format(id(self))
        self.scrollable_node_tag = "tkinterweb.{0}.nodes".format(id(self))
        self.add_bindtags(self, False)

        # bindings
        self.bind("<<Copy>>", self.copy_selection, True)
        self.bind("<B1-Motion>", self.extend_selection, True)
        self.bind("<Button-1>", self.on_click, True)
        self.bind("<ButtonRelease-1>", self.on_click_release, True)
        self.bind_class(self.node_tag, "<Motion>", self.on_mouse_motion, True)

        # register node handlers
        self.tk.call(self._w, "handler", "script", "script",
                     self.register(self.on_script))
        self.tk.call(self._w, "handler", "script", "style",
                     self.register(self.on_style))
        self.tk.call(self._w, "handler", "node", "link",
                     self.register(self.on_link))
        self.tk.call(self._w, "handler", "node", "title",
                     self.register(self.on_title))
        self.tk.call(self._w, "handler", "node", "a",
                     self.register(self.on_a))
        self.tk.call(self._w, "handler", "node", "base",
                     self.register(self.on_base))
        self.tk.call(self._w, "handler", "node", "input",
                     self.register(self.on_input))
        self.tk.call(self._w, "handler", "node", "textarea",
                     self.register(self.on_textarea))
        self.tk.call(self._w, "handler", "node", "select",
                     self.register(self.on_select))
        self.tk.call(self._w, "handler", "node", "form",
                     self.register(self.on_form))
        self.tk.call(self._w, "handler", "node", "object",
                     self.register(self.on_object))
        self.tk.call(self._w, "handler", "node", "iframe",
                     self.register(self.on_iframe))

    def placeholder(self, *args, **kwargs):
        """Blank placeholder function. The only purpose of this is to
        improve readability by avoiding `lambda a, b, c: None` statements."""

    def parse(self, html):
        """Parse HTML code"""
        self.downloads_have_occured = False
        self.unstoppable = True
        html = self.crash_prevention(html)
        self.tk.call(self._w, "parse", html)
        self.setup_widgets()
        # We assume that if no downloads have been made by now the document has finished loading, so we send the done loading signal
        if not self.downloads_have_occured:
            self.done_loading_func()

    def parse_css(self, sheetid=None, importcmd=None, data=""):
        """Parse CSS code"""
        data = self.crash_prevention(data)
        if sheetid and importcmd:
            self.tk.call(self._w, "style", "-id", sheetid, "-importcmd", importcmd, data)
        else:
            self.tk.call(self._w, "style", data)

    def reset(self):
        """Reset the widget"""
        self.stop()
        self.loaded_images = set()
        self.form_get_commands = {}
        self.form_elements = {}
        self.loaded_forms = {}
        self.radio_buttons = {}
        self.prev_hovered_nodes = []
        self.on_embedded_node = None
        self.tk.call(self._w, "reset")

    def stop(self):
        """Stop loading resources"""
        self.unstoppable = False
        for thread in self.active_threads:
            thread.stop()

    def node(self, *args):
        """Retrieve one or more document
        node handles from the current document."""
        return self.tk.call(self._w, "node", *args)

    def text(self, *args):
        """Enable interaction with the text of the HTML document."""
        return self.tk.call(self._w, "text", *args)

    def tag(self, subcommand, tag_name, *args):
        """Return the name of the Html tag that generated this
        document node, or an empty string if the node is a text node."""
        return self.tk.call(self._w, "tag", subcommand, tag_name, *args)

    def search(self, selector):
        """Search the document for the specified CSS
        selector; return a Tkhtml3 node if found."""
        return self.tk.call(self._w, "search", selector)

    def zoom(self, multiplier):
        """Set and get the page zoom"""
        if multiplier:
            self.tk.call(self._w, "configure", "-zoom", multiplier)
        else:
            return self.tk.call(self._w, "cget", "-zoom")

    def shrink(self, value):
        """Set shrink value for html widget"""
        self.tk.call(self._w, "configure", "-shrink", value)

    def fontscale(self, multiplier):
        """Set and get the font zoom"""
        if multiplier:
            self.tk.call(self._w, "configure", "-fontscale", multiplier)
        else:
            return self.tk.call(self._w, "cget", "-fontscale")

    def xview(self, *args):
        """Used to control horizontal scrolling."""
        if args:
            return self.tk.call(self._w, "xview", *args)
        coords = map(float, self.tk.call(self._w, "xview").split())
        return tuple(coords)

    def yview(self, *args):
        """Used to control the vertical position of the document."""
        return self.tk.call(self._w, "yview", *args)

    def yview_scroll(self, number, what):
        """Shifts the view in the window up or down, according to number and
        what. "number" is an integer, and "what" is either "units" or "pages"."""
        return self.yview("scroll", number, what)

    def get_node_text(self, node_handle):
        """Get the text content of the given node"""
        return self.tk.call(node_handle, "text")

    def get_node_tag(self, node_handle):
        """Get the HTML tag of the given node"""
        return self.tk.call(node_handle, "tag")

    def get_node_parent(self, node_handle):
        """Get the parent of the given node"""
        return self.tk.call(node_handle, "parent")

    def get_node_children(self, node_handle):
        """Get the children of the given node"""
        return self.tk.call(node_handle, "children")

    def get_node_attribute(self, node_handle, attribute, default=""):
        """Get the specified attribute of the given node"""
        return self.tk.call(node_handle, "attribute", "-default", default, attribute)

    def get_node_property(self, node_handle, node_property):
        """Get the specified attribute of the given node"""
        return self.tk.call(node_handle, "property", node_property)

    def get_current_node(self, event):
        """Get current node"""
        return self.tk.eval("""set node [lindex [lindex [{0} node {1} {2}] end] end]""".format(self, event.x, event.y))

    def get_current_node_parent(self, node):
        """Get the parent of the given node"""
        return self.tk.eval("""set node [lindex [lindex [{0} parent] end] end]""".format(node))

    def on_script(self, *args):
        """Currently just ignoring script"""

    def on_style(self, attributes, tagcontents):
        """Handle <style> elements"""
        if not self.stylesheets_enabled or not self.unstoppable:
            return
        self.downloads_have_occured = True
        self.style_count += 1
        ids = "author." + str(self.style_count).zfill(4)
        handler_proc = self.register(lambda new_url,
                                     parent_url=self.base_url:
                                     self.on_atimport(parent_url, new_url)
                                     )
        self.message_func("Loading <style> element.")
        self.style_thread_check(sheetid=ids, handler=handler_proc, data=tagcontents)

    def on_link(self, node):
        """Handle <link> elements"""
        try:
            rel = self.get_node_attribute(node, "rel").lower()
            media = self.get_node_attribute(node, "media", default="all").lower()
        except tk.TclError:
            return

        if ("stylesheet" in rel) and ("all" in media or "screen" in media) and self.stylesheets_enabled and self.unstoppable:
            self.downloads_have_occured = True
            try:
                href = self.get_node_attribute(node, "href")
                url = urljoin(self.base_url, href)
                self.message_func(
                    "Loading stylesheet from {0}.".format(shorten(url)))
                self.style_count += 1
                ids = "author." + str(self.style_count).zfill(4)
                handler_proc = self.register(lambda new_url,
                                             parent_url=url:
                                             self.on_atimport(
                                                 parent_url, new_url)
                                             )
                self.style_thread_check(sheetid=ids, handler=handler_proc, errorurl=href, url=url)
            except Exception as error:
                self.message_func("Error reading stylesheet {}: {}.".format(
                    self.get_node_attribute(node, "href"), error))
        elif "icon" in rel:
            url = urljoin(self.base_url, self.get_node_attribute(node, "href"))
            self.icon_change_func(url)

    def on_atimport(self, parent_url, new_url):
        """Load @import scripts"""
        if not self.stylesheets_enabled or not self.unstoppable:
            return
        self.downloads_have_occured = True
        self.style_count += 1
        try:
            url = urljoin(parent_url, new_url)
            self.message_func(
                "Loading stylesheet from {}.".format(shorten(url)))
            ids = "author." + str(self.style_count).zfill(4)
            handler_proc = self.register(lambda new_url,
                                         parent_url=url:
                                         self.on_atimport(parent_url, new_url)
                                         )
            
            self.style_thread_check(sheetid=ids, handler=handler_proc, errorurl=new_url, url=url)
            
        except Exception as error:
            self.message_func(
                "Error reading stylesheet {}: {}.".format(new_url, error)) 

    def on_title(self, node):
        """Handle <title> elements"""
        for child in (self.tk.call(node, "children")):
            self.title_change_func(self.tk.call(child, "text"))

    def on_base(self, node):
        """Handle <base> elements"""
        try:
            href = self.get_node_attribute(node, "href")
            self.base_url = urljoin(self.base_url, href)
        except Exception:
            self.message_func(
                "Error setting base url: a <base> element has been found without an href attribute.")

    def on_a(self, node):
        """Handle <a> elements"""
        self.tk.call(node, "dynamic", "set", "link")
        try:
            href = self.get_node_attribute(node, "href")
            url = urljoin(self.base_url, href)
            if url in self.visited_links:
                self.tk.call(node, "dynamic", "set", "visited")
        except tk.TclError:
            pass

    def on_iframe(self, node):
        """Handle <iframe> elements"""
        if not self.objects_enabled or not self.unstoppable:
            return
        
        src = self.get_node_attribute(node, "src")
        srcdoc = self.get_node_attribute(node, "srcdoc")
        
        self.message_func("Loading <iframe> element.")
        if srcdoc:
            self.create_iframe(node, None, srcdoc)
        elif src and (src != self.base_url):
            src = urljoin(self.base_url, src)
            self.create_iframe(node, src)

    def on_object(self, node):
        """Handle <object> elements"""
        if not self.objects_enabled or not self.unstoppable:
            return
        
        name = self.image_name_prefix + str(len(self.loaded_images))
        url = self.get_node_attribute(node, "data")
            
        try:
            url = urljoin(self.base_url, url)
            if url == self.base_url:
                # Don't load the object if it is the same as the current file
                # Otherwise the page will load the same object indefinitely and freeze the GUI forever
                return
            
            self.message_func("Loading object: {}.".format(shorten(url)))

            # Download the data and display it if it is an image or html file
            # Ideally threading would be used here, but at the moment threading <object> elements breaks some images
            # It doesn't really matter though, since very few webpages use <object> elements anyway
            if url.startswith("file://") or (not self.caches_enabled):
                data, newurl, filetype = download(url)
            elif url:
                data, newurl, filetype = cachedownload(url)
            else:
                return
                
            if data and filetype.startswith("image"):
                image, error = newimage(data, name, filetype)
                self.loaded_images.add(image)
                self.tk.call(node, "override", "-tkhtml-replacement-image url(replace:{})".format(image))
            elif data and filetype == "text/html":
                self.create_iframe(node, newurl, data)
        except Exception as error:
            self.message_func("An error has been encountered while loading an <object> element: {}.".format(error))

    def on_drawcleanupcrash(self):
        if self.prevent_crashes:
            self.message_func("HtmlDrawCleanup has encountered a critical error. This is being ignored because crash prevention is enabled.")
        else:
            self.destroy()

    def on_image(self, url):
        """Handle images"""
        if not self.images_enabled or not self.unstoppable:
            return

        self.downloads_have_occured = True
        name = self.image_name_prefix + str(len(self.loaded_images))

        if not self.ignore_invalid_images:
            image = newimage(self.broken_image, name, "image/png")
            self.loaded_images.add(image)
        else:
            image = blankimage(name)
            self.loaded_images.add(image)

        if url.startswith("replace:"):
            thread = self.begin_download()
            name = url.replace("replace:", "")
            self.finish_download(thread)
        elif any([url.startswith("linear-gradient("),
                url.startswith("url("),
                url.startswith("radial-gradient("),
                url.startswith("repeating-linear-gradient("),
                url.startswith("repeating-radial-gradient(")]):
            done = False
            self.message_func("Fetching image: {0}.".format(shorten(url)))
            for image in url.split(","):
                if image.startswith("url("):
                    image = strip_css_url(image)
                    url = urljoin(self.base_url, image)
                    self.image_thread_check(url, name)
                    done = True
            if not done:
                self.message_func(
                    "The image {} could not be shown because it is not supported yet".format(shorten(url)))
        else:
            url = urljoin(self.base_url, url)
            self.image_thread_check(url, name)
        return name

    def on_form(self, node):
        """Handle <form> elements"""
        if not self.forms_enabled:
            return
        inputs = list(self.tk.call(self, "search", "INPUT,SELECT,TEXTAREA,BUTTON"))
        for i in inputs:
            if i in self.form_elements:
                inputs.remove(i)
            else:
                self.form_elements[i] = node
        self.loaded_forms[node] = inputs
        
        self.message_func("Successfully setup <form> element.")

    def on_select(self, node):
        """Handle <select> elements"""
        if not self.forms_enabled:
            return
        text = []
        values = []
        selected = None
        for child in self.get_node_children(node):
            if self.get_node_tag(child) == "option":
                try:
                    child2 = self.get_node_children(child)[0]
                    nodevalue = self.get_node_attribute(child, "value")
                    nodeselected = self.get_node_attribute(child, "selected")
                    values.append(nodevalue)
                    text.append(self.get_node_text(child2))
                    if nodeselected:
                        selected = nodevalue
                except IndexError:
                    continue
        if not selected and values:
            selected = values[0]
        widgetid = Combobox(self)
        widgetid.insert(text, values, selected)
        self.form_get_commands[node] = lambda: widgetid.get()
        self.form_reset_commands[node] = lambda: widgetid.reset()
        self.handle_node_replacement(node, widgetid, 
            lambda widgetid=widgetid: self.handle_node_removal(widgetid), 
            lambda node=node, widgetid=widgetid, widgettype="text": self.handle_node_style(node, widgetid, widgettype))

    def on_textarea(self, node):
        """Handle <textarea> elements"""
        if not self.forms_enabled:
            return
        widgetid = ScrolledTextBox(self, borderwidth=0, selectborderwidth=0, highlightthickness=0)
        widgetid.bind("<<ScrollbarShown>>", widgetid.reset_bindtags)
        widgetid.bind("<<ScrollbarHidden>>", lambda event, widgetid=widgetid: self.add_bindtags(widgetid))
        self.form_get_commands[node] = lambda: widgetid.get("1.0", 'end-1c')
        self.form_reset_commands[node] = lambda: widgetid.delete("0.0", "end")
        self.handle_node_replacement(node, widgetid, 
            lambda widgetid=widgetid: self.handle_node_removal(widgetid), 
            lambda node=node, widgetid=widgetid, widgettype="text": self.handle_node_style(node, widgetid, widgettype))

    def on_input(self, node):
        """Handle <input> elements"""
        if not self.forms_enabled:
            return
        self.tk.eval('set type ""')
        nodetype = self.tk.eval(
            "set nodetype [string tolower [%s attr -default {} type]]" % node)
        nodevalue = self.get_node_attribute(node, "value")

        if any((nodetype == "image", nodetype == "submit", nodetype == "reset", nodetype == "button")):
            self.form_get_commands[node] = self.placeholder
            self.form_reset_commands[node] = self.placeholder
        elif nodetype == "file":
            widgetid = FileSelector(self)
            self.form_get_commands[node] = widgetid.get_value
            self.form_reset_commands[node] = widgetid.reset
            self.handle_node_replacement(node, widgetid, 
                lambda widgetid=widgetid: self.handle_node_removal(widgetid), 
                lambda node=node, widgetid=widgetid: self.handle_node_style(node, widgetid))
        elif nodetype == "hidden":
            self.form_get_commands[node] = lambda node=node: self.get_node_attribute(
                node, "value")
            self.form_reset_commands[node] = lambda: None
        elif nodetype == "checkbox":
            variable = tk.IntVar()
            widgetid = tk.Checkbutton(self, borderwidth=0, padx=0, pady=0, highlightthickness=0, variable=variable)
            self.form_get_commands[node] = lambda: variable.get()
            self.form_reset_commands[node] = lambda: variable.set(0)
            self.handle_node_replacement(node, widgetid, 
                lambda widgetid=widgetid: self.handle_node_removal(widgetid), 
                lambda node=node, widgetid=widgetid: self.handle_node_style(node, widgetid))
        elif nodetype == "radio":
            name = self.tk.call(node, "attr", "-default", "", "name")
            if name in self.radio_buttons:
                variable = self.radio_buttons[name]
            else:
                variable = tk.StringVar(self)
                self.radio_buttons[name] = variable
            widgetid = tk.Radiobutton(self, value=nodevalue, variable=variable,tristatevalue="TKWtsvLKac1", borderwidth=0, padx=0, pady=0, highlightthickness=0)
            self.form_get_commands[node] = lambda: variable.get()
            self.form_reset_commands[node] = lambda: variable.set("")
            self.handle_node_replacement(node, widgetid, 
                lambda widgetid=widgetid: self.handle_node_removal(widgetid), 
                lambda node=node, widgetid=widgetid: self.handle_node_style(node, widgetid))
        else:
            widgetid = tk.Entry(self, borderwidth=0, highlightthickness=0)
            widgetid.insert(0, nodevalue)
            if nodetype == "password":
                widgetid.configure(show='*')
            widgetid.bind("<Return>", lambda event, node=node: self.handle_form_submission(node=node, event=event))
            self.form_get_commands[node] = lambda: widgetid.get()
            self.form_reset_commands[node] = lambda widgetid=widgetid, content=nodevalue: self.handle_entry_reset(widgetid, content)
            self.handle_node_replacement(node, widgetid, 
                lambda widgetid=widgetid: self.handle_node_removal(widgetid), 
                lambda node=node, widgetid=widgetid, widgettype="text": self.handle_node_style(node, widgetid, widgettype))

    def on_click(self, event):
        """Set active element flags"""
        self.start_selection(event)
        try:
            node_handle = self.get_current_node(event)
            if node_handle == "":
                return
        except ValueError:
            self.selection_start_node = None
            return

        if self.stylesheets_enabled:
            try:
                self.tk.call(node_handle, "dynamic", "set", "active")
            except Exception:
                try:
                    node_handle = self.get_current_node_parent(node_handle)
                    self.tk.call(node_handle, "dynamic", "set", "active")
                except Exception:
                    pass
        self.prev_active_node = node_handle

    def on_click_release(self, event):
        """Handle click releases on <a> nodes"""
        self.is_selecting = False

        try:
            node_handle = self.get_current_node(event)
            parent = self.get_current_node_parent(node_handle)

            node_tag = self.get_node_tag(node_handle).lower()
            parent_tag = self.get_node_tag(parent).lower()
            node_type = self.get_node_attribute(node_handle, "type").lower()
            parent_type = self.get_node_attribute(parent, "type").lower()

            if self.prev_active_node and self.stylesheets_enabled:
                self.tk.call(self.prev_active_node,"dynamic", "clear", "active")

            if node_handle != self.prev_active_node and parent != self.prev_active_node:
                for i in self.prev_hovered_nodes:
                    if self.get_node_tag(i) == "a":
                        self.tk.call(i, "dynamic", "set", "visited")
                        self.handle_link_click(i)
                        break
            elif node_tag == "input" and node_type == "reset":
                self.handle_form_reset(node_handle)
            elif node_tag == "input" and node_type == "submit":
                self.handle_form_submission(node_handle)
            elif node_tag == "input" and node_type == "image":
                self.handle_form_submission(node_handle)
            elif node_tag == "button" and node_type == "submit":
                self.handle_form_submission(node_handle)
            elif node_tag == "a":
                self.tk.call(node_handle, "dynamic", "set", "visited")
                self.handle_link_click(node_handle)
            elif parent_tag == "input" and parent_type == "reset":
                self.handle_form_submission(parent)
            elif parent_tag == "input" and parent_type == "submit":
                self.handle_form_submission(parent)
            elif parent_tag == "input" and parent_type == "image":
                self.handle_form_submission(parent)
            elif parent_tag == "button" and parent_type == "submit":
                self.handle_form_submission(parent)
            elif parent_tag == "a":
                self.tk.call(parent, "dynamic", "set", "visited")
                self.handle_link_click(parent)
            else:
                for i in self.prev_hovered_nodes:
                    if self.get_node_tag(i) == "a":
                        self.tk.call(i, "dynamic", "set", "visited")
                        self.handle_link_click(i)
                        break
        except Exception:
            pass

        self.prev_active_node = None

    def on_mouse_motion(self, event):
        """Set hover flags and handle the CSS 'cursor' property"""
        if self.is_selecting:
            return
        if self.on_embedded_node is None:
            try:
                node_handle = self.get_current_node(event)
                if node_handle == "":
                    self.on_leave(None)
                    return

            except ValueError:
                self.on_leave(None)
                return
        else:
            node_handle = self.on_embedded_node

        self.currently_hovered_node = node_handle
        can_set = False

        self.handle_cursor_change(node_handle)

        if self.stylesheets_enabled:
            try:
                if self.prev_hovered_nodes == []:
                    can_set = True
                elif node_handle != self.prev_hovered_nodes[0]:
                    can_set = True
                if can_set:
                    for node in self.prev_hovered_nodes:
                        self.tk.call(node, "dynamic", "clear", "hover")
                    self.tk.call(node_handle, "dynamic", "set", "hover")
            except Exception:
                try:
                    node_handle = self.get_current_node_parent(node_handle)
                    if self.prev_hovered_nodes == []:
                        can_set = True
                    elif node_handle != self.prev_hovered_nodes[0]:
                        can_set = True
                    if can_set:
                        for node in self.prev_hovered_nodes:
                            self.tk.call(node, "dynamic", "clear", "hover")
                        self.tk.call(node_handle, "dynamic", "set", "hover")
                except Exception:
                    can_set = False

        self.prev_hovered_nodes = [node_handle]
        try:
            self.handle_recursive_hovering(self.get_current_node_parent(node_handle), self.recursive_hovering_count)
        except Exception:
            pass

    def on_leave(self, event):
        """Set the cursor to the default when leaving this widget"""
        self.cursor_change_func(cursor="")
        self.prev_cursor = ""
        if self.stylesheets_enabled:
            for node in self.prev_hovered_nodes:
                try:
                    self.tk.call(node, "dynamic", "clear", "hover")
                except tk.TclError:
                    pass
        self.prev_hovered_nodes = []

    def on_embedded_mouse_motion(self, event, node_handle):
        self.on_embedded_node = node_handle

    def add_bindtags(self, widgetid, allowscrolling=True):
        """Add bindtags to allow scrolling and on_embedded_mouse function calls"""
        if allowscrolling:
            tags = (self.node_tag, self.scrollable_node_tag,)
        else:
            tags = (self.node_tag,)

        widgetid.bindtags(widgetid.bindtags() + tags)

    def crash_prevention(self, data):
        if self.prevent_crashes:
            data = ''.join(c for c in data if c <= u'\uFFFF')
            data = re.sub("font-family:[^;']*(;)?", self.remove_noto_emoji, data, flags=re.IGNORECASE)
            data = re.sub("rgb\([^0-9](.*?)\)", "inherit", data, flags=re.IGNORECASE)
        return data

    def begin_download(self):
        thread = threadname()
        self.active_threads.append(thread)
        self.downloading_resource_func()
        return thread

    def finish_download(self, thread):
        self.active_threads.remove(thread)
        if len(self.active_threads) == 0:
            self.done_loading_func()

    def fix_css_urls(self, match, url):
        """Make relative uris in CSS files absolute"""
        newurl = match.group()
        newurl = strip_css_url(newurl)
        newurl = urljoin(url, newurl)
        newurl = "url('{}')".format(newurl)
        return newurl

    def remove_noto_emoji(self, match):
        """Remove noto color emoji font, which causes Tkinter to crash"""
        match = match.group().lower()
        match = match.replace("noto color emoji", "arial")
        return match

    def style_thread_check(self, **kwargs):
        if self.max_thread_count == 0:
            self.fetch_styles(**kwargs)
        elif len(self.active_threads) >= self.max_thread_count:
            self.after(500, lambda kwargs=kwargs: self.style_thread_check(**kwargs))
        else:
            thread = StoppableThread(target=self.fetch_styles, kwargs=kwargs)
            thread.start()

    def image_thread_check(self, url, name):
        if self.max_thread_count == 0:
            self.fetch_images(url, name, url)
        elif len(self.active_threads) >= self.max_thread_count:
            self.after(500, lambda url=url, name=name: self.image_thread_check(url, name))
        else:
            thread = StoppableThread(target=self.fetch_images, args=(url, name, url,))
            thread.start()

    def fetch_styles(self, sheetid, handler, errorurl="", url=None, data=None):
        """Fetch stylesheets and parse the CSS code they contain"""
        thread = self.begin_download()
        
        if url and self.unstoppable:
            try:
                if url.startswith("file://") or (not self.caches_enabled):
                    data = download(url)[0]
                else:
                    data = cachedownload(url)[0]

                matcher = lambda match, url=url: self.fix_css_urls(match, url)
                data = re.sub("url\((.*?)\)", matcher, data)

            except Exception as error:
                self.message_func(
                    "Error reading stylesheet {}: {}.".format(errorurl, error))
        if data and self.unstoppable:

            self.parse_css("{}.9999".format(sheetid), handler, data)

        self.finish_download(thread)

    def fetch_images(self, url, name, urltype):
        """Fetch images and display them in the document"""
        thread = self.begin_download()

        path = urlparse(url).path
        self.message_func("Fetching image: {0}.".format(shorten(url)))

        try:
            if url.startswith("file://") or (not self.caches_enabled):
                data, newurl, filetype = download(url)
            else:
                data, newurl, filetype = cachedownload(url)

            if self.unstoppable and data:
                image, error = newimage(data, name, filetype)

                if image:
                    self.loaded_images.add(image)
                elif error == "no_pycairo":
                    self.message_func(
                        "Scalable Vector Graphics could not be shown because Pycairo is not installed but is required to parse .svg files.")
                elif error == "no_rsvg":
                    self.message_func(
                        "Scalable Vector Graphics could not be shown because Rsvg is not installed but is required to parse .svg files.")
                elif error == "corrupt":
                    self.message_func(
                        "The image {} could not be shown.".format(url))

        except Exception:
            self.message_func(
                "The image {} could not be shown because it is corrupt or is not supported yet.".format(url))

        self.finish_download(thread)
        
    def handle_link_click(self, node_handle):
        """Handle link clicks"""
        href = self.get_node_attribute(node_handle, "href")
        url = urljoin(self.base_url, href)
        self.message_func(
            "A link to '{}' has been clicked.".format(shorten(url)))
        self.visited_links.append(url)
        self.link_click_func(url)

    def handle_cursor_change(self, node_handle):
        """Handle CSS 'cursor' property"""
        try:
            cursor = self.get_node_property(node_handle, "cursor")
            cursor = self.cursors[cursor]
            if self.prev_cursor != cursor:
                self.cursor_change_func(cursor=cursor)
                self.prev_cursor = cursor
        except KeyError:
            try:
                cursor = self.get_node_property(self.get_current_node_parent(node_handle), "cursor")
                cursor = self.cursors[cursor]
                if self.prev_cursor != cursor:
                    self.cursor_change_func(cursor=cursor)
                    self.prev_cursor = cursor
            except Exception:
                if self.get_node_tag(node_handle) == "":
                    if self.prev_cursor != "text":
                        cursor = self.cursors["text"]
                        self.cursor_change_func(cursor=cursor)
                        self.prev_cursor = cursor
                else:
                    if self.prev_cursor != "":
                        self.cursor_change_func(cursor="")
                        self.prev_cursor = ""

    def handle_entry_reset(self, widgetid, content):
        """Reset tk.Entry widgets in HTML forms"""
        widgetid.delete(0, "end")
        widgetid.insert(0, content)

    def handle_form_reset(self, node):
        """Reset HTML forms"""
        if (node not in self.form_elements) or (not self.forms_enabled):
            return

        form = self.form_elements[node]
        action = self.get_node_attribute(form, "action")

        for formelement in self.loaded_forms[form]:
            self.form_reset_commands[formelement]()

    def handle_form_submission(self, node, event=None):
        """Submit HTML forms"""
        if (node not in self.form_elements) or (not self.forms_enabled):
            return

        data = {}
        form = self.form_elements[node]
        action = self.get_node_attribute(form, "action")
        method = self.get_node_attribute(form, "method", "GET").upper()

        for formelement in self.loaded_forms[form]:
            nodeattrname = self.get_node_attribute(formelement, "name")
            if nodeattrname:
                nodevalue = self.form_get_commands[formelement]()
                if nodevalue:
                    data[nodeattrname] = nodevalue
        if not event:
            nodeattrname = self.get_node_attribute(node, "name")
            nodevalue = self.get_node_attribute(node, "value")
            if nodeattrname and nodevalue:
                data[nodeattrname] = nodevalue

        data = urlencode(data)
        
        if action == "":
            url = list(urlparse(self.base_url))
            url = url[:-3]
            url.extend(['', '', ''])
            url = urlunparse(url)
        else:
            url = urljoin(self.base_url, action)
	
        if method == "GET":
            data = "?" + data
        else:
            data = data.encode()

        self.message_func(
            "A form has been submitted to {}.".format(shorten(url)))
        self.form_submit_func(url, data, method)

    def handle_node_replacement(self, node, widgetid, deletecmd, stylecmd=None, allowscrolling=True, handledelete=True):
        """Replace a Tkhtml3 node with a Tkinter widget"""
        if stylecmd:
            if handledelete:
                self.tk.call(node, "replace", widgetid, "-deletecmd",
                             self.register(deletecmd), "-stylecmd", 
                             self.register(stylecmd))
            else:
                self.tk.call(node, "replace", widgetid, "-stylecmd", 
                             self.register(stylecmd))
        else:
            if handledelete:
                self.tk.call(node, "replace", widgetid, "-deletecmd", 
                             self.register(deletecmd))
            else:
                self.tk.call(node, "replace", widgetid)

        if allowscrolling:
            self.add_bindtags(widgetid)
        else:
            self.add_bindtags(widgetid, False)

        widgetid.bind("<Enter>", lambda event, node_handle=node: self.on_embedded_mouse_motion(event, node_handle=node_handle))
        widgetid.bind("<Leave>", lambda event, node_handle=None: self.on_embedded_mouse_motion(event, node_handle=node_handle))

    def handle_node_removal(self, widgetid):
        widgetid.destroy()

    def handle_node_style(self, node, widgetid, widgettype="button"):
        if widgettype == "button":
            bg = "transparent"
            while (bg == "transparent" and node != ""):
                bg = self.get_node_property(node, "background-color")
                node = self.get_node_parent(node)
            if bg == "transparent":
                bg = "white"
            widgetid.configure(background=bg, highlightbackground=bg,
                               highlightcolor=bg, activebackground=bg)
        else:
            bg = self.get_node_property(node, "background-color")
            fg = self.get_node_property(node, "color")
            font = self.get_node_property(node, "font")
            if bg == "transparent":
                bg = "white"
            if fg == "transparent":
                fg = "white"
            widgetid.configure(background=bg, foreground=fg, font=font)

    def handle_recursive_hovering(self, node_handle, count):
        """Set hover flags to the parents of
        the hovered element as well"""
        try:
            if self.stylesheets_enabled:
                self.tk.call(node_handle, "dynamic", "set", "hover")
            self.prev_hovered_nodes.append(node_handle)
        except Exception:
            pass
        try:
            if count >= 1:
                self.handle_recursive_hovering(
                    self.get_current_node_parent(node_handle), count-1)
        except Exception:
            pass

    def setup_widgets(self):
        """Replace Tkhtml nodes with Tk widgets when needed"""
        widgets = self.search("[widgetid]")
        for node in widgets:
            widgetid = self.get_node_attribute(node, "widgetid")
            allowscrolling = self.get_node_attribute(node, "allowscrolling")
            widgetid = self.nametowidget(widgetid)
            self.stored_widgets[widgetid] = node
            self.handle_node_replacement(node, widgetid,
                                         lambda widgetid=widgetid: self.handle_node_removal(widgetid),
                                         allowscrolling=(True if allowscrolling == "yes" else False),
                                         handledelete=False)

    def remove_widget(self, widgetid):
        """Remove a stored widget"""
        self.tk.call(self.stored_widgets[widgetid], "replace", "<p></p>")
        del self.stored_widgets[widgetid]

    def replace_widget(self, widgetid, newwidgetid):
        """Replace a stored widget"""
        node = self.stored_widgets[widgetid]
        self.tk.call(node, "replace", newwidgetid)

        if newwidgetid in self.stored_widgets:
            self.tk.call(self.stored_widgets[newwidgetid], "replace", widgetid)
            self.stored_widgets[widgetid] = self.stored_widgets[newwidgetid]
        else:
            del self.stored_widgets[widgetid]
        self.stored_widgets[newwidgetid] = node

    def replace_html(self, selector, widgetid):
        """Replace an HTML element with a widget"""
        node = self.search(selector)[0]
        self.tk.call(node, "replace", widgetid)
        self.stored_widgets[widgetid] = node

    def find_text(self, searchtext, select, ignore_case, highlight_all):
        """Search for and highlight specific text in the document"""
        nmatches = 0
        matches = []
        selected = []
        match_indexes = []

        self.tag("delete", "findtext")
        self.tag("delete", "findtextselected")

        if len(searchtext) == 0 or select <= 0:
            return 0

        doctext = self.text("text")

        try:
            #find matches
            if ignore_case:
                rmatches = re.finditer(searchtext, doctext, flags=re.IGNORECASE)
            else:
                rmatches = re.finditer(searchtext, doctext)
                
            for match in rmatches:
                match_indexes.append((match.start(0), match.end(0),))
                nmatches += 1

            if len(match_indexes) > 0:
                #highlight matches
                self.message_func("{} results for the search key '{}' have been found.".format(nmatches, searchtext))
                if highlight_all:
                    for num, match in enumerate(match_indexes):
                        match = self.text("index", match_indexes[num][0])
                        match += self.text("index", match_indexes[num][1])
                        matches.append(match)   
                
                selected = self.text("index", match_indexes[select-1][0])
                selected += self.text("index", match_indexes[select-1][1])

                for match in matches:
                    node1, index1, node2, index2 = match
                    self.tag("add", "findtext", node1, index1, node2, index2)
                    self.tag("configure", "findtext", "-bg", "#ef0fff", "-fg", "white")
                    
                node1, index1, node2, index2 = selected
                self.tag("add", "findtextselected", node1, index1, node2, index2)
                self.tag("configure", "findtextselected", "-bg", "#38d878", "-fg", "white")

                #scroll to node if selected match is not visible
                nodebox = self.text("bbox", node1, index1, node2, index2)
                docheight = float(self.tk.call(self._w, "bbox")[3])
                
                view_top = docheight * self.yview()[0]
                view_bottom = view_top + self.winfo_height()
                node_top = float(nodebox[1])
                node_bottom = float(nodebox[3])

                if (node_top < view_top) or (node_bottom > view_bottom):
                    self.yview("moveto", node_top/docheight)
            else:
                self.message_func("No results for the search key '{}' could be found.".format(searchtext))            

            return nmatches
        except Exception as error:
            self.message_func(
            "An error has been encountered while searching the document for {}: {}.".format(searchtext, error))
            return 0

    def create_iframe(self, node, url, html=None):
        widgetid = self.embed_obj(self, False)
                
        widgetid.set_message_func(self.message_func)
        widgetid.set_recursive_hover_depth(self.recursive_hovering_count)
        widgetid.set_maximum_thread_count(self.max_thread_count)
        widgetid.ignore_invalid_images(self.ignore_invalid_images)
        widgetid.enable_stylesheets(self.stylesheets_enabled)
        widgetid.enable_images(self.images_enabled)
        widgetid.enable_forms(self.forms_enabled)
        widgetid.enable_objects(self.objects_enabled)
        widgetid.enable_caches(self.caches_enabled)

        if html:
            widgetid.load_html(html, url)
        elif url:
            widgetid.load_html("<p>Loading...</p>")
            widgetid.load_url(url)
            
        self.handle_node_replacement(node, widgetid, lambda widgetid=widgetid: self.handle_node_removal(widgetid))  

    def start_selection(self, event):
        """Make selection possible"""
        self.focus_set()
        self.tag("delete", "selection")
        try:
            self.selection_start_node, self.selection_start_offset = self.node(True, event.x, event.y)
        except ValueError:
            self.selection_start_node = None

    def extend_selection(self, event):
        """Alter selection and HTML element states based on mouse movement"""
        self.tag("delete", "selection")
        if self.selection_start_node is None:
            return
        try:
            self.selection_end_node, self.selection_end_offset = self.node(True, event.x, event.y)

            self.tag("add", "selection", 
                    self.selection_start_node,
                    self.selection_start_offset, 
                    self.selection_end_node, 
                    self.selection_end_offset)
            self.tag("configure", "selection", "-background", "#3584e4")

            if self.prev_active_node is not None:
                if len(self.get_selection()) > 0:
                    self.is_selecting = True
                    if self.prev_cursor != "text":
                        cursor = self.cursors["text"]
                        self.cursor_change_func(cursor=cursor)
                        self.prev_cursor = cursor
                    if self.stylesheets_enabled:
                        self.tk.call(self.prev_active_node, "dynamic", "clear", "active")
                        for node in self.prev_hovered_nodes:
                            self.tk.call(node, "dynamic", "clear", "hover")
                    self.prev_active_node = None
                    self.prev_hovered_nodes = []

        except ValueError:
            self.selection_end_node = None

    def get_selection(self):
        """Return the currently selected text"""
        if self.selection_start_node is None or self.selection_end_node is None:
            return
        start_index = self.text(
            "offset", self.selection_start_node, self.selection_start_offset)
        end_index = self.text(
            "offset", self.selection_end_node, self.selection_end_offset)
        if start_index > end_index:
            start_index, end_index = end_index, start_index
        whole_text = self.text("text")
        return whole_text[start_index:end_index]

    def copy_selection(self, event=None):
        """Copy the selected text to the clipboard"""
        selected_text = self.get_selection()
        self.clipboard_clear()
        self.clipboard_append(selected_text)
        self.message_func(
            "The text '{}' has been copied to the clipboard.".format(selected_text))
