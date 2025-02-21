"""
The core Python bindings to Tkhtml3

Copyright (c) 2025 Andereoo
"""

from re import IGNORECASE, MULTILINE, split, sub, finditer

from urllib.parse import urlencode, urljoin, urlparse

import tkinter as tk
from tkinter.ttk import Scale, Style

from imageutils import newimage, blankimage
from utilities import (PLATFORM, PYTHON_VERSION, DEFAULT_PARSE_MODE, BROKEN_IMAGE, CURSOR_MAP, DEFAULT_STYLE, DARK_STYLE, 
                       DEBUG_MESSAGE_EVENT, DONE_LOADING_EVENT, ICON_CHANGED_EVENT, TITLE_CHANGED_EVENT, 
                       DOWNLOADING_RESOURCE_EVENT, LINK_CLICK_EVENT, FORM_SUBMISSION_EVENT,
                       ScrolledTextBox, FileSelector, ColourSelector, StoppableThread,
                       get_tkhtml_folder, load_combobox, load_tkhtml, rgb_to_hex, shorten, 
                       download, cachedownload, strip_css_url, threadname, placeholder, notifier)


class Combobox(tk.Widget):
    "Bindings for Bryan Oakley's combobox widget"

    def __init__(self, master):
        try:
            load_combobox(master)
            tk.Widget.__init__(self, master, "::combobox::combobox")
        except tk.TclError:
            load_combobox(master, force=True)
            tk.Widget.__init__(self, master, "::combobox::combobox")
        self.configure(
            highlightthickness=0,
            borderwidth=0,
            editable=False,
            takefocus=0,
            selectbackground="#6eb9ff",
            relief="flat",
            elementborderwidth=0,
            buttonbackground="white",
        )
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
    "Bindings for the Tkhtml3 HTML widget"

    def __init__(self, master, embed_obj, manage_vsb_func, manage_hsb_func, messages_enabled=False, overflow_scroll_frame=None, cfg={}, **kwargs):
        self.master = master
        self.manage_vsb_func = manage_vsb_func
        self.manage_hsb_func = manage_hsb_func
        self.messages_enabled = messages_enabled
        self.overflow_scroll_frame = overflow_scroll_frame

        # widget settings 
        self.allow_threading = master.tk.eval('set tcl_platform(threaded)')

        self.events_enabled = True   
        self.selection_enabled = True
        self.stylesheets_enabled = True
        self.images_enabled = True
        self.forms_enabled = True
        self.objects_enabled = True
        self.ignore_invalid_images = True
        self.crash_prevention_enabled = True
        self.dark_theme_enabled = False
        self.image_inversion_enabled = False
        self.caches_enabled = True

        self.recursive_hovering_count = 10
        self.maximum_thread_count = self.default_maximum_thread_count = 20
        self.image_alternate_text_enabled = True
        
        self.find_match_highlight_color = "#ef0fff"
        self.find_match_text_color = "#fff"
        self.find_current_highlight_color = "#38d878"
        self.find_current_text_color = "#fff"
        self.selected_text_highlight_color = "#3584e4"
        self.selected_text_color = "#fff"
        self.visited_links = []
        self.insecure_https = False
        self.dark_theme_limit = 160
        self.style_dark_theme_regex = r"([^:;\s{]+)\s?:\s?([^;{!]+)(?=!|;|})"
        self.general_dark_theme_regexes = [r'(<[^>]+bgcolor=")([^"]*)',r'(<[^>]+text=")([^"]*)',r'(<[^>]+link=")([^"]*)']
        self.inline_dark_theme_regexes = [r'(<[^>]+style=")([^"]*)', r'([a-zA-Z-]+:)([^;]*)']
        self.radiobutton_token = "TKWtsvLKac1"

        # widget status variables
        self.base_url = ""
        self.title = ""
        self.icon = ""

        self.embed_obj = embed_obj
        self.style_count = 0
        self.active_threads = []
        self.stored_widgets = {}
        self.loaded_images = set()
        self.image_directory = {}
        self.image_name_prefix = f"_tkinterweb_img_{id(self)}_"
        self.is_selecting = False
        self.downloads_have_occured = False
        self.unstoppable = True
        self.on_embedded_node = None
        self.selection_start_node = None
        self.selection_start_offset = None
        self.selection_end_node = None
        self.selection_end_offset = None
        self.prev_active_node = None
        self.current_node = None
        self.hovered_nodes = []
        self.current_cursor = ""
        self.vsb_type = 2
        self.selection_type = 0
        self.motion_frame_bg = "white"

        # enable form resetting and submission
        self.form_get_commands = {}
        self.form_reset_commands = {}
        self.form_elements = {}
        self.loaded_forms = {}
        self.radio_buttons = {}
        self.waiting_forms = 0

        # get tkhtml folder
        folder = get_tkhtml_folder()

        # provide OS information for troubleshooting
        self.post_event(DEBUG_MESSAGE_EVENT, data=f"Starting TkinterWeb for {PLATFORM.processor} {PLATFORM.system} with Python {".".join(PYTHON_VERSION)}", direct_notify=True)

        # pre-load custom stylesheet, set default parse mode, and register image loading infrastructure
        if "imagecmd" not in kwargs:
            kwargs["imagecmd"] = master.register(self.on_image)
        if "drawcleanupcrashcmd" not in kwargs:
            kwargs["drawcleanupcrashcmd"] = master.register(self.on_drawcleanupcrash)
        if "defaultstyle" not in kwargs:
            kwargs["defaultstyle"] = DEFAULT_STYLE
        if "parsemode" not in kwargs:
            kwargs["parsemode"] = DEFAULT_PARSE_MODE
        # if "logcmd" not in kwargs:
        #    kwargs["logcmd"] = tkhtml_notifier

        # load the Tkhtml3 widget
        try:
            load_tkhtml(master, folder)
            tk.Widget.__init__(self, master, "html", cfg, kwargs)
        except tk.TclError:
            load_tkhtml(master, folder, force=True)
            tk.Widget.__init__(self, master, "html", cfg, kwargs)
            

        self.post_event(DEBUG_MESSAGE_EVENT, data=f"Tkhtml3 successfully loaded from {folder}")

        # create a tiny, blank frame for cursor updating
        self.motion_frame = tk.Frame(self, bg=self.motion_frame_bg, width=1, height=1)
        self.motion_frame.place(x=0, y=0)

        # set up bindtags
        self.node_tag = f"tkinterweb.{id(self)}.nodes"
        self.scrollable_node_tag = f"tkinterweb.{id(self)}.scrollablenodes"
        self.add_bindtags(self, False)

        # bindings
        self.bind("<<Copy>>", self.copy_selection, True)
        self.bind("<B1-Motion>", self.extend_selection, True)
        self.bind("<Button-1>", self.on_click, True)
        self.bind("<Double-Button-1>", self.on_double_click, True)
        self.bind("<ButtonRelease-1>", self.on_click_release, True)
        self.bind_class(self.node_tag, "<Motion>", self.on_mouse_motion, True)

        # register node handlers
        self.register_handler("script", "script", self.on_script)
        self.register_handler("script", "style", self.on_style)
        self.register_handler("node", "link", self.on_link)
        self.register_handler("node", "title", self.on_title)
        self.register_handler("node", "a", self.on_a)
        self.register_handler("node", "base", self.on_base)
        self.register_handler("node", "input", self.on_input)
        self.register_handler("node", "textarea", self.on_textarea)
        self.register_handler("node", "select", self.on_select)
        self.register_handler("node", "form", self.on_form)
        self.register_handler("node", "object", self.on_object)
        self.register_handler("node", "iframe", self.on_iframe)
        self.register_handler("node", "table", self.on_table)
        self.register_handler("node", "img", self.on_image_node)
        self.register_handler("parse", "body", self.on_body) # for some reason using "node" and "body" doesn't return anyting
        self.register_handler("parse", "html", self.on_body) # for some reason using "node" and "html" doesn't return anyting

    @property
    def maximum_thread_count(self):
        return self._maximum_thread_count
    
    @maximum_thread_count.setter
    def maximum_thread_count(self, count):
        "Ensure that maximum_thread_count is always zero if Tcl/Tk is not built with thread support"
        count = int(count)
        if count: 
            self.default_maximum_thread_count = count
        if self.allow_threading:
            self._maximum_thread_count = count
        else:
            self.post_event(DEBUG_MESSAGE_EVENT, data="WARNING: not using threading because your Tcl/Tk library does not have thread support")
            self._maximum_thread_count = 0

    def post_event(self, event, url=None, data=None, method=None, direct_notify=False):
        "Generate a virtual event"
        if not self.messages_enabled and event == DEBUG_MESSAGE_EVENT: return
        if direct_notify: notifier(data)
        if self.events_enabled:
            # thread safety
            self.after(0, self.finish_posting_event, event, url, data, method)
    
    def finish_posting_event(self, event, url, data, method):
        "Finish generating a virtual event"
        tk.Event.url = url
        tk.Event.data = data
        tk.Event.method = method
        self.event_generate(event)

    def parse(self, html):
        "Parse HTML code"
        self.downloads_have_occured = False
        self.unstoppable = True
        html = self.crash_prevention(html)
        html = self.dark_mode(html)
        self.tk.call(self._w, "parse", html)
        # we assume that if no downloads have been made by now the document has finished loading, so we send the done loading signal
        if not self.downloads_have_occured:
            self.post_event(DONE_LOADING_EVENT)
            
    def update_default_style(self, stylesheet=None):
        "Update the default stylesheet based on color theme"
        if stylesheet:
            self.config(defaultstyle=stylesheet)
        elif self.dark_theme_enabled:
            self.config(defaultstyle=DEFAULT_STYLE + DARK_STYLE)
        else:
            self.config(defaultstyle=DEFAULT_STYLE)

    def check_colors(self, rgb, match):
        "Check colour, invert if necessary, and convert"
        if ("background" in match and sum(rgb) < self.dark_theme_limit) or (
            match == "color" and sum(rgb) > self.dark_theme_limit
        ):
            return rgb_to_hex(*rgb)
        else:
            rgb[0] = max(1, min(255, 240 - rgb[0]))
            rgb[1] = max(1, min(255, 240 - rgb[1]))
            rgb[2] = max(1, min(255, 240 - rgb[2]))
            return rgb_to_hex(*rgb)

    def generate_altered_colour(self, match, matchtype=1):
        "Invert document colours. Highly experimental."
        colors = match.group(2).replace("\n", "")
        colors = split(r"\s(?![^()]*\))", colors)
        changed = False

        for count, color in enumerate(colors):
            try:
                if color.startswith("#"):
                    color = color.lstrip("#")
                    lv = len(color)
                    if lv == 3:
                        color = color + color
                        lv = len(color)
                    colors[count] = self.check_colors(
                        list(
                            int(color[i : i + lv // 3], 16)
                            for i in range(0, lv, lv // 3)
                        ),
                        match.group(1),
                    )
                    changed = True
                elif color.startswith("rgb(") or color.startswith("rgba("):
                    colors[count] = self.check_colors(
                        list(
                            map(
                                int,
                                color.lstrip("rgba(")
                                .lstrip("rgb(")
                                .rstrip(")")
                                .strip(" ")
                                .split(","),
                            )
                        ),
                        match.group(1),
                    )
                    changed = True
                else:
                    try:
                        color = list(self.winfo_rgb(color))
                        colors[count] = self.check_colors(color, match.group(1))
                        changed = True
                    except tk.TclError:
                        pass
            except ValueError as error:
                pass
        
        if changed:
            if matchtype:
                return match.group(1) + " ".join(colors)
            else:
                return match.group(1) + ": " + " ".join(colors)
        else:
            return match.group()
            
    def dark_mode(self, html):
        if self.dark_theme_enabled:
            html = sub(self.inline_dark_theme_regexes[0], lambda match: match.group(1) + sub(self.inline_dark_theme_regexes[1], self.generate_altered_colour, match.group(2)), html)
            for regex in self.general_dark_theme_regexes:
                html = sub(regex, self.generate_altered_colour, html, flags=IGNORECASE)
        return html

    def parse_css(self, sheetid=None, importcmd=None, data="", override=False):
        "Parse CSS code"
        data = self.crash_prevention(data)
        if self.dark_theme_enabled:
            data = sub(self.style_dark_theme_regex, lambda match, matchtype=0: self.generate_altered_colour(match, matchtype), data)
        if sheetid and importcmd:
            self.tk.call(
                self._w, "style", "-id", sheetid, "-importcmd", importcmd, data
            )
        elif override:
            self.style_count += 1
            self.tk.call(
                self._w, "style", "-id", "author" + str(self.style_count).zfill(4), data
            )
        else:
            self.tk.call(self._w, "style", data)

    def reset(self):
        "Reset the widget"
        self.stop()
        self.loaded_images = set()
        self.image_directory = {}
        self.form_get_commands = {}
        self.form_elements = {}
        self.loaded_forms = {}
        self.waiting_forms = 0
        self.radio_buttons = {}
        self.hovered_nodes = []
        self.current_node = None
        self.on_embedded_node = None
        self.selection_start_node = None
        self.selection_end_node = None
        self.title = ""
        self.icon = ""
        self.vsb_type = self.manage_vsb_func()
        self.manage_hsb_func()
        self.set_cursor("default")
        self.tk.call(self._w, "reset")

    def stop(self):
        "Stop loading resources"
        self.unstoppable = False
        for thread in self.active_threads:
            thread.stop()

    def node(self, *args):
        """Retrieve one or more document
        node handles from the current document"""
        nodes = self.tk.call(self._w, "node", *args)
        if nodes:
            return nodes
        else:
            return None, None

    def text(self, *args):
        "Enable interaction with the text of the HTML document"
        return self.tk.call(self._w, "text", *args)

    def tag(self, subcommand, tag_name, *args):
        """Return the name of the Html tag that generated this
        document node, or an empty string if the node is a text node"""
        return self.tk.call(self._w, "tag", subcommand, tag_name, *args)

    def search(self, selector, cnf={}, **kw):
        """Search the document for the specified CSS
        selector; return a Tkhtml3 node if found"""
        return self.tk.call((self._w, "search", selector)+self._options(cnf, kw))

    def xview(self, *args):
        "Used to control horizontal scrolling"
        if args:
            return self.tk.call(self._w, "xview", *args)
        coords = map(float, self.tk.call(self._w, "xview").split())
        return tuple(coords)

    def xview_scroll(self, number, what):
        """Shifts the view in the window left or right, according to number and what.
        "number" is an integer, and "what" is either "units" or "pages"."""
        return self.xview("scroll", number, what)

    def xview_moveto(self, number):
        "Shifts the view horizontally to the specified position"
        return self.xview("moveto", number)

    def yview(self, *args):
        "Used to control the vertical position of the document"
        return self.tk.call(self._w, "yview", *args)

    def yview_scroll(self, number, what):
        """Shifts the view in the window up or down, according to number and what.
        "number" is an integer, and "what" is either "units" or "pages"."""
        return self.yview("scroll", number, what)

    def yview_moveto(self, number):
        "Shifts the view vertically to the specified position"
        return self.yview("moveto", number)

    def bbox(self, node=None):
        "Get the bounding box of the viewport or a specified node"
        return self.tk.call(self._w, "bbox", node)

    def parse_fragment(self, html):
        """Parse a document fragment.
        A document fragment isn't part of the active document but is comprised of nodes like the active document.
        Changes made to the fragment don't affect the document.
        Returns a root node."""
        self.downloads_have_occured = False
        self.unstoppable = True
        html = self.crash_prevention(html)
        html = self.dark_mode(html)
        fragment = self.tk.call(self._w, "fragment", html)
        # We assume that if no downloads have been made by now the document has finished loading, so we send the done loading signal
        if not self.downloads_have_occured:
            self.post_event(DONE_LOADING_EVENT)
        return fragment
    
    def get_zoom(self):
        "Return the page zoom"
        return self.tk.call(self._w, "cget", "-zoom")
    
    def set_zoom(self, multiplier):
        "Set the page zoom"
        self.tk.call(self._w, "configure", "-zoom", float(multiplier))

    def get_fontscale(self):
        "Return the font zoom"
        return self.tk.call(self._w, "cget", "-fontscale")
    
    def set_fontscale(self, multiplier):
        "Set the font zoom"
        self.tk.call(self._w, "configure", "-fontscale", multiplier)

    def get_parsemode(self):
        "Return the page render mode"
        return self.tk.call(self._w, "cget", "-parsemode")

    def set_parsemode(self, mode):
        "Set the page render mode"
        self.tk.call(self._w, "configure", "-parsemode", mode)

    def get_shrink(self):
        "Get the shrink value for the html widget"
        return self.tk.call(self._w, "cget", "-shrink") 

    def set_shrink(self, value):
        "Set shrink value for the html widget"
        self.tk.call(self._w, "configure", "-shrink", value) 
    
    def enable_imagecache(self, enabled):
        "Enable or disable the tkhtml imagecache"
        self.tk.call(self._w, "configure", "-imagecache", enabled)

    def get_node_text(self, node_handle, *args):
        "Get the text content of the given node"
        return self.tk.call(node_handle, "text", *args)

    def set_node_text(self, node_handle, new):
        "Set the text content of the given node"
        return self.tk.call(node_handle, "text", "set", new)

    def get_node_tag(self, node_handle):
        "Get the HTML tag of the given node"
        return self.tk.call(node_handle, "tag")

    def get_node_parent(self, node_handle):
        "Get the parent of the given node"
        return self.tk.call(node_handle, "parent")

    def get_node_children(self, node_handle):
        "Get the children of the given node"
        return self.tk.call(node_handle, "children")

    def get_node_attribute(self, node_handle, attribute, default="", value=None):
        "Get the specified attribute of the given node"
        if value:  # backwards compatability
            return self.tk.call(node_handle, "attribute", attribute, value)
        else:
            return self.tk.call(
                node_handle, "attribute", "-default", default, attribute
            )

    def set_node_attribute(self, node_handle, attribute, value):
        "Set the specified attribute of the given node"
        return self.tk.call(node_handle, "attribute", attribute, value)

    def get_node_attributes(self, node_handle):
        "Get the attributes of the given node"
        attr = self.tk.call(node_handle, "attribute")
        return dict(zip(attr[0::2], attr[1::2]))

    def get_node_property(self, node_handle, node_property, *args):
        "Get the specified CSS property of the given node"
        return self.tk.call(node_handle, "property", *args, node_property)

    def get_node_properties(self, node_handle, *args):
        "Get the CSS properties of the given node"
        prop = self.tk.call(node_handle, "property", *args)
        return dict(zip(prop[0::2], prop[1::2]))

    def override_node_properties(self, node_handle, *props):
        """Get/set the CSS property override list"""
        if props: return self.tk.call(node_handle, "override", " ".join(props))
        return self.tk.call(node_handle, "override")

    def insert_node(self, node_handle, child_nodes):
        "Experimental, insert the specified nodes into the parent node"
        return self.tk.call(node_handle, "insert", child_nodes)

    def insert_node_before(self, node_handle, child_nodes, before):
        "Experimental, place the specified nodes is before another node"
        return self.tk.call(node_handle, "insert", "-before", before, child_nodes)

    def delete_node(self, node_handle):
        "Delete the given node"
        return self.tk.call(node_handle, "destroy")

    def set_node_flags(self, node, name):
        "Set dynamic flags on the given node"
        self.tk.call(node, "dynamic", "set", name)

    def remove_node_flags(self, node, name):
        "Set dynamic flags on the given node"
        self.tk.call(node, "dynamic", "clear", name)

    def get_node_tkhtml(self, node_handle):
        "Get pathName of node (I think)"
        return self.tk.call(node_handle, "html")

    def get_current_node(self, event):
        "Get current node"
        return self.tk.eval(
            f"""set node [lindex [lindex [{self} node {event.x} {event.y}] end] end]"""
        )

    def get_current_node_parent(self, node):
        "Get the parent of the given node"
        return self.tk.eval(f"""set node [lindex [lindex [{node} parent] end] end]""")
    
    def register_handler(self, handler_type, node_tag, callback):
        self.tk.call(self._w, "handler", handler_type, node_tag, self.register(callback))

    def image(self, full=False):
        """Return the name of a new Tk image containing the rendered document.
        The returned image should be deleted when the script has finished with it.
        Note that this command is mainly intended for automated testing.
        Be wary of running this command on large documents."""
        full = "-full" if full else ""
        name = self.tk.call(self._w, "image", full)
        return name, self.tk.call(name, "data")

    def postscript(self, cnf={}, **kw):
        """Print the contents of the canvas to a postscript file.
        Valid options: colormap, colormode, file, fontmap, height, 
        pageanchor, pageheight, pagesize, pagewidth, pagex, pagey, 
        nobg, noimages, rotate, width, x, and y"""
        return self.tk.call((self._w, "postscript")+self._options(cnf, kw))

    def preload_image(self, url):
        """Preload an image. 
        Only useful if caches are enabled and reset() is not called after preloading."""
        return self.tk.call(self._w, "preload", url)

    def on_script(self, attributes, tagcontents):
        """Currently ignoring script.
        A javascript engine could be used here to parse the script.
        Returning any HTMl code here causes it to be parsed in place of the script tag."""

    def on_style(self, attributes, tagcontents):
        "Handle <style> elements"
        if not self.stylesheets_enabled or not self.unstoppable:
            return
        self.downloads_have_occured = True
        self.style_count += 1
        ids = "user." + str(self.style_count).zfill(4)
        handler_proc = self.register(
            lambda new_url, parent_url=self.base_url: self.on_atimport(
                parent_url, new_url
            )
        )
        self.style_thread_check(sheetid=ids, handler=handler_proc, data=tagcontents)

    def on_link(self, node):
        "Handle <link> elements"
        try:
            rel = self.get_node_attribute(node, "rel").lower()
            media = self.get_node_attribute(node, "media", default="all").lower()
        except tk.TclError:
            return

        if (
            ("stylesheet" in rel)
            and ("all" in media or "screen" in media)
            and self.stylesheets_enabled
            and self.unstoppable
        ):
            self.downloads_have_occured = True
            href = self.get_node_attribute(node, "href")
            try:
                url = self.resolve_url(href)
                self.post_event(DEBUG_MESSAGE_EVENT, data=f"Fetching stylesheet from {shorten(url)}")
                self.style_count += 1
                ids = "user." + str(self.style_count).zfill(4)
                handler_proc = self.register(
                    lambda new_url, parent_url=url: self.on_atimport(
                        parent_url, new_url
                    )
                )
                self.style_thread_check(
                    sheetid=ids, handler=handler_proc, errorurl=href, url=url
                )
            except Exception as error:
                self.post_event(DEBUG_MESSAGE_EVENT, data=f"Error reading stylesheet {href}: {error}")
        elif "icon" in rel:
            href = self.get_node_attribute(node, "href")
            url = self.resolve_url(href)
            self.icon = url
            self.post_event(ICON_CHANGED_EVENT, url=url)

    def on_atimport(self, parent_url, new_url):
        "Load @import scripts"
        if not self.stylesheets_enabled or not self.unstoppable:
            return
        self.downloads_have_occured = True
        self.style_count += 1
        try:
            url = urljoin(parent_url, new_url)
            self.post_event(DEBUG_MESSAGE_EVENT, data=f"Loading stylesheet from {shorten(url)}")
            ids = "user." + str(self.style_count).zfill(4)
            handler_proc = self.register(
                lambda new_url, parent_url=url: self.on_atimport(parent_url, new_url)
            )

            self.style_thread_check(
                sheetid=ids, handler=handler_proc, errorurl=new_url, url=url
            )

        except Exception as error:
            self.post_event(DEBUG_MESSAGE_EVENT, data=f"Error loading stylesheet {new_url}: {error}")

    def on_title(self, node):
        "Handle <title> elements"
        for child in self.tk.call(node, "children"):
            self.title = self.tk.call(child, "text")
            self.post_event(TITLE_CHANGED_EVENT, data=self.title)

    def on_base(self, node):
        "Handle <base> elements"
        try:
            href = self.get_node_attribute(node, "href")
            self.base_url = self.resolve_url(href)
        except Exception:
            self.post_event(DEBUG_MESSAGE_EVENT, data="Error setting base url: a <base> element has been found without an href attribute")

    def on_a(self, node):
        "Handle <a> elements"
        self.set_node_flags(node, "link")
        try:
            href = self.get_node_attribute(node, "href")
            url = self.resolve_url(href)
            if url in self.visited_links:
                self.set_node_flags(node, "visited")
        except tk.TclError:
            pass

    def on_iframe(self, node):
        "Handle <iframe> elements"
        if not self.objects_enabled or not self.unstoppable:
            return

        src = self.get_node_attribute(node, "src")
        srcdoc = self.get_node_attribute(node, "srcdoc")

        if srcdoc:
            self.create_iframe(node, None, srcdoc)
        elif src and (src != self.base_url):
            src = self.resolve_url(src)
            self.post_event(DEBUG_MESSAGE_EVENT, data=f"Creating iframe from {shorten(src)}")
            self.create_iframe(node, src)

    def on_object(self, node):
        "Handle <object> elements"
        if not self.objects_enabled or not self.unstoppable:
            return

        name = self.image_name_prefix + str(len(self.loaded_images))
        url = self.get_node_attribute(node, "data")

        if url != "":
            try:
                # load widgets presented in <object> elements
                widgetid = self.nametowidget(url)
                if widgetid.winfo_ismapped():  # Don't display the same widget twice
                    return

                allowscrolling = self.get_node_attribute(node, "allowscrolling", "false") != "false"
                allowstyling = self.get_node_attribute(node, "allowstyling", "false") != "false"
                handleremoval = self.get_node_attribute(node, "handleremoval", "false") != "false"
                if allowstyling:
                    allowstyling = lambda node=node, widgetid=widgetid, widgettype="text": self.handle_node_style(node, widgetid, widgettype)
                else:
                    allowstyling = None
                if handleremoval:
                    handleremoval = lambda widgetid=widgetid: self.handle_node_removal(widgetid)
                else:
                    handleremoval = None

                self.stored_widgets[widgetid] = node
                self.handle_node_replacement(
                    node,
                    widgetid,
                    handleremoval,
                    allowstyling,
                    allowscrolling,
                    False,
                )
            except KeyError:
                url = self.resolve_url(url)
                if url == self.base_url:
                    # Don't load the object if it is the same as the current file
                    # Otherwise the page will load the same object indefinitely and freeze the GUI forever
                    return

                self.post_event(DEBUG_MESSAGE_EVENT, data=f"Creating object from {shorten(url)}")
                try:
                    if url.startswith("file://") or (not self.caches_enabled):
                        data, newurl, filetype, code = download(url, insecure=self.insecure_https)
                    elif url:
                        data, newurl, filetype, code = cachedownload(
                            url, insecure=self.insecure_https
                        )
                    else:
                        return

                    if data and filetype.startswith("image"):
                        image, error = newimage(
                            data, name, filetype, self.image_inversion_enabled
                        )
                        self.loaded_images.add(image)
                        self.tk.call(
                            node, "override", f"-tkhtml-replacement-image url(replace:{image})"
                        )
                    elif data and filetype == "text/html":
                        self.create_iframe(node, newurl, data)
                except Exception as error:
                    self.post_event(DEBUG_MESSAGE_EVENT, data=f"Error loading object element: {error}")

    def on_drawcleanupcrash(self):
        if self.crash_prevention_enabled:
            self.post_event(DEBUG_MESSAGE_EVENT, data="HtmlDrawCleanup has encountered a critical error. This is being ignored because crash prevention is enabled.")
        else:
            self.destroy()

    def on_image_node(self, node):
        url = self.resolve_url(self.get_node_attribute(node, "src"))
        self.image_directory[url] = node

    def on_image(self, url):
        "Handle images"
        if not self.images_enabled or not self.unstoppable:
            return

        self.downloads_have_occured = True
        name = self.image_name_prefix + str(len(self.loaded_images))

        image = blankimage(name)
        self.loaded_images.add(image)

        if url.startswith("replace:"):
            thread = self.begin_download()
            name = url.replace("replace:", "")
            self.finish_download(thread)
        elif any(
            [
                url.startswith("linear-gradient("),
                url.startswith("url("),
                url.startswith("radial-gradient("),
                url.startswith("repeating-linear-gradient("),
                url.startswith("repeating-radial-gradient("),
            ]
        ):
            done = False
            self.post_event(DEBUG_MESSAGE_EVENT, data=f"Fetching image: {shorten(url)}")
            for image in url.split(","):
                if image.startswith("url("):
                    url = url.split("'), url('", 1)[0]
                    image = strip_css_url(image)
                    url = self.resolve_url(image)
                    self.image_thread_check(url, name)
                    done = True
            if not done:
                self.load_alt_text(url, name)
                self.post_event(DEBUG_MESSAGE_EVENT, data=f"The image {shorten(url)} could not be shown because it is not supported yet")
        else:
            url = url.split("'), url('", 1)[0]
            url = self.resolve_url(url)
            self.image_thread_check(url, name)
        return name

    def on_form(self, node):
        "Handle <form> elements"
        if not self.forms_enabled:
            return

        inputs = []

        def scan(form):
            for i in self.get_node_children(form):
                tag = self.get_node_tag(i)
                if tag:
                    scan(i)
                if tag.lower() in {"input", "select", "textarea", "button"}:
                    inputs.append(i)
                    self.form_elements[i] = node

        scan(node)
        if len(inputs) == 0:
            self.waiting_forms += 1
        else:
            self.loaded_forms[node] = inputs
            self.post_event(DEBUG_MESSAGE_EVENT, data="Successfully setup form")

    def on_table(self, node):
        "Handle <form> elements in tables; workaround for Bug #48"
        if not self.forms_enabled:
            return

        if self.waiting_forms > 0:
            inputs = {}

            def scan(element, form):
                for i in self.get_node_children(element):
                    tag = self.get_node_tag(i).lower()
                    if tag == "form":
                        form = i
                    elif tag.lower() in {"input", "select", "textarea", "button"}:
                        if form in inputs:
                            inputs[form].append(i)
                        else:
                            inputs[form] = [i]
                        self.form_elements[i] = form
                    if tag:
                        scan(i, form)

            scan(node, node)
            for form in inputs:
                self.loaded_forms[form] = inputs[form]
                self.post_event(DEBUG_MESSAGE_EVENT, data="Successfully setup table form")
                self.waiting_forms -= 1

    def on_select(self, node):
        "Handle <select> elements"
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
        state = self.get_node_attribute(node, "disabled", False) != "0"
        if state:
            widgetid.configure(state="disabled")
        self.handle_node_replacement(
            node,
            widgetid,
            lambda widgetid=widgetid: self.handle_node_removal(widgetid),
            lambda node=node, widgetid=widgetid, widgettype="text": self.handle_node_style(
                node, widgetid, widgettype
            ),
        )

    def on_textarea(self, node):
        "Handle <textarea> elements"
        if not self.forms_enabled:
            return
        widgetid = ScrolledTextBox(
            self,
            borderwidth=0,
            selectborderwidth=0,
            highlightthickness=0,
        )

        self.form_get_commands[node] = lambda: widgetid.get("1.0", "end-1c")
        self.form_reset_commands[node] = lambda: widgetid.delete("0.0", "end")
        widgetid.insert("1.0", self.get_node_text(self.get_node_children(node), "-pre"))
        state = self.get_node_attribute(node, "disabled", False) != "0"
        if state:
            widgetid.configure(state="disabled")
        self.handle_node_replacement(
            node,
            widgetid,
            lambda widgetid=widgetid: self.handle_node_removal(widgetid),
            lambda node=node, widgetid=widgetid, widgettype="text": self.handle_node_style(
                node, widgetid, widgettype
            ),
        )

    def on_input(self, node):
        "Handle <input> elements"
        if not self.forms_enabled:
            return
        self.tk.eval('set type ""')
        nodetype = self.tk.eval(
            "set nodetype [string tolower [%s attr -default {} type]]" % node
        )
        nodevalue = self.get_node_attribute(node, "value")

        if any(
            (
                nodetype == "image",
                nodetype == "submit",
                nodetype == "reset",
                nodetype == "button",
            )
        ):
            widgetid = None
            self.form_get_commands[node] = placeholder
            self.form_reset_commands[node] = placeholder
        elif nodetype == "file":
            accept = self.get_node_attribute(node, "accept")
            multiple = (
                self.get_node_attribute(node, "multiple", self.radiobutton_token)
                != self.radiobutton_token
            )
            widgetid = FileSelector(self, accept, multiple)
            self.form_get_commands[node] = widgetid.get_value
            self.form_reset_commands[node] = widgetid.reset
            self.handle_node_replacement(
                node,
                widgetid,
                lambda widgetid=widgetid: self.handle_node_removal(widgetid),
                lambda node=node, widgetid=widgetid: self.handle_node_style(
                    node, widgetid
                ),
            )
        elif nodetype == "color":
            widgetid = ColourSelector(self, nodevalue)
            self.form_get_commands[node] = widgetid.get_value
            self.form_reset_commands[node] = widgetid.reset
            self.handle_node_replacement(
                node,
                widgetid,
                lambda widgetid=widgetid: self.handle_node_removal(widgetid),
                placeholder,
            )
        elif nodetype == "hidden":
            widgetid = None
            self.form_get_commands[node] = lambda node=node: self.get_node_attribute(
                node, "value"
            )
            self.form_reset_commands[node] = lambda: None
        elif nodetype == "checkbox":
            variable = tk.IntVar()
            widgetid = tk.Checkbutton(
                self,
                borderwidth=0,
                padx=0,
                pady=0,
                highlightthickness=0,
                variable=variable,
            )
            variable.trace(
                "w", lambda *_, widgetid=widgetid: self.on_input_change(widgetid)
            )
            self.form_get_commands[node] = lambda: variable.get()
            self.form_reset_commands[node] = lambda: variable.set(0)
            self.handle_node_replacement(
                node,
                widgetid,
                lambda widgetid=widgetid: self.handle_node_removal(widgetid),
                lambda node=node, widgetid=widgetid: self.handle_node_style(
                    node, widgetid
                ),
            )
        elif nodetype == "range":
            variable = tk.IntVar()
            variable.set(nodevalue)
            from_ = self.get_node_attribute(node, "min", 0)
            to = self.get_node_attribute(node, "max", 100)
            widgetid = Scale(self, variable=variable, from_=from_, to=to)
            variable.trace(
                "w", lambda *_, widgetid=widgetid: self.on_input_change(widgetid)
            )
            self.form_get_commands[node] = lambda: variable.get()
            self.form_reset_commands[node] = lambda: variable.set(0)
            self.handle_node_replacement(
                node,
                widgetid,
                lambda widgetid=widgetid: self.handle_node_removal(widgetid),
                lambda node=node, widgetid=widgetid, widgettype="range": self.handle_node_style(
                    node, widgetid, widgettype
                ),
            )
        elif nodetype == "radio":
            name = self.tk.call(node, "attr", "-default", "", "name")
            if name in self.radio_buttons:
                variable = self.radio_buttons[name]
                widgetid = tk.Radiobutton(
                    self,
                    value=nodevalue,
                    variable=variable,
                    tristatevalue=self.radiobutton_token,
                    borderwidth=0,
                    padx=0,
                    pady=0,
                    highlightthickness=0,
                )
            else:
                variable = tk.StringVar(self)
                widgetid = tk.Radiobutton(
                    self,
                    value=nodevalue,
                    variable=variable,
                    tristatevalue=self.radiobutton_token,
                    borderwidth=0,
                    padx=0,
                    pady=0,
                    highlightthickness=0,
                )
                variable.trace(
                    "w", lambda *_, widgetid=widgetid: self.on_input_change(widgetid)
                )
                self.radio_buttons[name] = variable
            self.form_get_commands[node] = lambda: variable.get()
            self.form_reset_commands[node] = lambda: variable.set("")
            self.handle_node_replacement(
                node,
                widgetid,
                lambda widgetid=widgetid: self.handle_node_removal(widgetid),
                lambda node=node, widgetid=widgetid: self.handle_node_style(
                    node, widgetid
                ),
            )
        else:
            widgetid = tk.Entry(
                self, validate="key", borderwidth=0, highlightthickness=0
            )
            widgetid.configure(
                validatecommand=lambda *_, widgetid=widgetid: self.on_input_change(
                    widgetid
                )
            )
            if nodetype == "password":
                widgetid.configure(show="*")
            widgetid.bind(
                "<Return>",
                lambda event, node=node: self.handle_form_submission(
                    node=node, event=event
                ),
            )
            self.form_get_commands[node] = lambda: widgetid.get()
            self.form_reset_commands[node] = (
                lambda widgetid=widgetid, content=nodevalue: self.handle_entry_reset(
                    widgetid, content
                )
            )
            self.handle_node_replacement(
                node,
                widgetid,
                lambda widgetid=widgetid: self.handle_node_removal(widgetid),
                lambda node=node, widgetid=widgetid, widgettype="text": self.handle_node_style(
                    node, widgetid, widgettype
                ),
            )

        if widgetid:
            state = self.get_node_attribute(node, "disabled", self.radiobutton_token)
            if state != self.radiobutton_token:
                widgetid.configure(state="disabled")

    def on_body(self, node, index):
        "Wait for style changes on the root node"
        self.tk.call(node,
                    "replace",
                    node,
                    "-stylecmd",
                    self.register(lambda node=node: self.set_overflow(node)))

    def on_input_change(self, widgetid):
        widgetid.event_generate("<<Modified>>")
        return True

    def crash_prevention(self, data):
        if self.crash_prevention_enabled:
            data = "".join(c for c in data if c <= "\uFFFF")
            data = sub(
                "font-family:[^;']*(;)?",
                self.remove_noto_emoji,
                data,
                flags=IGNORECASE,
            )
            data = sub(r"rgb\([^0-9](.*?)\)", "inherit", data, flags=IGNORECASE)
        return data

    def begin_download(self):
        thread = threadname()
        self.active_threads.append(thread)
        self.post_event(DOWNLOADING_RESOURCE_EVENT)
        return thread

    def finish_download(self, thread):
        self.active_threads.remove(thread)
        if len(self.active_threads) == 0:
            self.post_event(DONE_LOADING_EVENT)

    def fix_css_urls(self, match, url):
        "Make relative uris in CSS files absolute"
        newurl = match.group()
        newurl = strip_css_url(newurl)
        newurl = urljoin(url, newurl)
        newurl = f"url('{newurl}')"
        return newurl

    def remove_noto_emoji(self, match):
        "Remove noto color emoji font, which causes Tkinter to crash"
        match = match.group().lower()
        match = match.replace("noto color emoji", "arial")
        return match

    def style_thread_check(self, **kwargs):
        if self.maximum_thread_count == 0:
            self.fetch_styles(**kwargs)
        elif len(self.active_threads) >= self.maximum_thread_count:
            self.after(500, lambda kwargs=kwargs: self.style_thread_check(**kwargs))
        else:
            thread = StoppableThread(target=self.fetch_styles, kwargs=kwargs)
            thread.start()

    def image_thread_check(self, url, name):
        if self.maximum_thread_count == 0:
            self.fetch_images(url, name, url)
        elif len(self.active_threads) >= self.maximum_thread_count:
            self.after(
                500, lambda url=url, name=name: self.image_thread_check(url, name)
            )
        else:
            thread = StoppableThread(
                target=self.fetch_images,
                args=(
                    url,
                    name,
                    url,
                ),
            )
            thread.start()

    def fetch_styles(self, sheetid, handler, errorurl="", url=None, data=None):
        "Fetch stylesheets and parse the CSS code they contain"
        thread = self.begin_download()

        if url and self.unstoppable:
            try:
                if url.startswith("file://") or (not self.caches_enabled):
                    data = download(url, insecure=self.insecure_https)[0]
                else:
                    data = cachedownload(url, insecure=self.insecure_https)[0]

                matcher = lambda match, url=url: self.fix_css_urls(match, url)
                data = sub(r"url\((.*?)\)", matcher, data)

            except Exception as error:
                self.post_event(DEBUG_MESSAGE_EVENT, data=f"Error loading stylesheet {errorurl}: {error}")

        if data and self.unstoppable:
            self.parse_css(f"{sheetid}.9999", handler, data)
            if url:
                self.post_event(DEBUG_MESSAGE_EVENT, data=f"Successfully loaded {shorten(url)}")
        self.finish_download(thread)

    def load_alt_text(self, url, name):
        if (url in self.image_directory):
            node = self.image_directory[url]
            alt = self.get_node_attribute(node, "alt")
            if alt and self.image_alternate_text_enabled: self.insert_node(node, self.parse_fragment(alt))
        elif not self.ignore_invalid_images:
            image = newimage(BROKEN_IMAGE, name, "image/png", self.image_inversion_enabled)
            self.loaded_images.add(image)

    def fetch_images(self, url, name, urltype):
        "Fetch images and display them in the document"
        thread = self.begin_download()

        self.post_event(DEBUG_MESSAGE_EVENT, data=f"Fetching image from {shorten(url)}")

        try:
            if url.startswith("file://") or (not self.caches_enabled):
                data, newurl, filetype, code = download(url, insecure=self.insecure_https)
            else:
                data, newurl, filetype, code = cachedownload(
                    url, insecure=self.insecure_https
                )

            if self.unstoppable and data:
                # thread safety
                self.after(0, self.finish_fetching_images, data, name, filetype, url)

        except Exception as error:
            self.load_alt_text(url, name)
            self.post_event(DEBUG_MESSAGE_EVENT, data=f"Error loading image {url}: {error}")

        self.finish_download(thread)

    def finish_fetching_images(self, data, name, filetype, url):
        try:
            image, error = newimage(
                data, name, filetype, self.image_inversion_enabled
            )
            
            if image:
                self.loaded_images.add(image)
                self.post_event(DEBUG_MESSAGE_EVENT, data=f"Successfully loaded {shorten(url)}")
            elif error == "no_pycairo":
                self.load_alt_text(url, name)
                self.post_event(DEBUG_MESSAGE_EVENT, data=f"Error loading image {url}: Pycairo is not installed but is required to parse .svg files")
            elif error == "no_rsvg":
                self.load_alt_text(url, name)
                self.post_event(DEBUG_MESSAGE_EVENT, data=f"Error loading image {url}: Rsvg is not installed but is required to parse .svg files")
            elif error == "corrupt":
                self.load_alt_text(url, name)
                self.post_event(DEBUG_MESSAGE_EVENT, data=f"The image {url} could not be shown")
        except Exception as error:
            self.load_alt_text(url, name)
            self.post_event(DEBUG_MESSAGE_EVENT, data=f"Error loading image {url}: {error}")

    def handle_link_click(self, node_handle):
        "Handle link clicks"
        href = self.get_node_attribute(node_handle, "href")
        url = self.resolve_url(href)
        self.post_event(DEBUG_MESSAGE_EVENT, data=f"A link to '{shorten(url)}' has been clicked")
        self.visited_links.append(url)
        self.post_event(LINK_CLICK_EVENT, url, "", "GET")

    def handle_entry_reset(self, widgetid, content):
        "Reset tk.Entry widgets in HTML forms"
        widgetid.delete(0, "end")
        widgetid.insert(0, content)

    def handle_form_reset(self, node):
        "Reset HTML forms"
        if (node not in self.form_elements) or (not self.forms_enabled):
            return

        form = self.form_elements[node]
        #action = self.get_node_attribute(form, "action")

        for formelement in self.loaded_forms[form]:
            self.form_reset_commands[formelement]()

    def handle_form_submission(self, node, event=None):
        "Submit HTML forms"
        if (node not in self.form_elements) or (not self.forms_enabled):
            return

        data = []
        form = self.form_elements[node]
        action = self.get_node_attribute(form, "action")
        method = self.get_node_attribute(form, "method", "GET").upper()

        for formelement in self.loaded_forms[form]:
            nodeattrname = self.get_node_attribute(formelement, "name")
            if nodeattrname:
                nodevalue = self.form_get_commands[formelement]()
                nodetype = self.get_node_attribute(formelement, "type")
                if nodetype == "submit" or nodetype == "reset":
                    continue
                elif nodetype == "file":
                    for value in nodevalue:
                        data.append(
                            (nodeattrname, value),
                        )
                else:
                    data.append(
                        (nodeattrname, nodevalue),
                    )
        if not event:
            nodeattrname = self.get_node_attribute(node, "name")
            nodevalue = self.get_node_attribute(node, "value")
            if nodeattrname and nodevalue:
                data.append(
                    (nodeattrname, nodevalue),
                )

        data = urlencode(data)

        if action == "":
            url = urlparse(self.base_url)
            url = f"{url.scheme}://{url.netloc}{url.path}"
        else:
            url = self.resolve_url(action)

        if method == "GET":
            data = "?" + data
        else:
            data = data.encode()

        self.post_event(DEBUG_MESSAGE_EVENT, data=f"A form has been submitted to {shorten(url)}")
        self.post_event(FORM_SUBMISSION_EVENT, url, data, method)

    def handle_node_replacement(self, node, widgetid, deletecmd, stylecmd=None, allowscrolling=True, handledelete=True):
        "Replace a Tkhtml3 node with a Tkinter widget"
        if stylecmd:
            if handledelete:
                self.tk.call(
                    node,
                    "replace",
                    widgetid,
                    "-deletecmd",
                    self.register(deletecmd),
                    "-stylecmd",
                    self.register(stylecmd),
                )
            else:
                self.tk.call(
                    node, "replace", widgetid, "-stylecmd", self.register(stylecmd)
                )
        else:
            if handledelete:
                self.tk.call(
                    node, "replace", widgetid, "-deletecmd", self.register(deletecmd)
                )
            else:
                self.tk.call(node, "replace", widgetid)

        self.add_bindtags(widgetid, allowscrolling)

        widgetid.bind(
            "<Enter>",
            lambda event, node_handle=node: self.on_embedded_mouse_motion(
                event, node_handle=node_handle
            ),
        )
        widgetid.bind(
            "<Leave>",
            lambda event, node_handle=None: self.on_embedded_mouse_motion(
                event, node_handle=node_handle
            ),
        )

    def handle_node_removal(self, widgetid):
        widgetid.destroy()

    def handle_node_style(self, node, widgetid, widgettype="button"):
        if widgettype == "button":
            bg = "transparent"
            while bg == "transparent" and node != "":
                bg = self.get_node_property(node, "background-color")
                node = self.get_node_parent(node)
            if bg == "transparent":
                bg = "white"
            widgetid.configure(
                background=bg,
                highlightbackground=bg,
                highlightcolor=bg,
                activebackground=bg,
            )
        elif widgettype == "range":
            bg = "transparent"
            while bg == "transparent" and node != "":
                bg = self.get_node_property(node, "background-color")
                node = self.get_node_parent(node)
            if bg == "transparent":
                bg = "white"
            style = Style()
            stylename = f"Scale{widgetid}.Horizontal.TScale"
            style.configure(stylename, background=bg)
            widgetid.configure(style=stylename)
        elif widgettype == "text":
            bg = self.get_node_property(node, "background-color")
            fg = self.get_node_property(node, "color")
            font = self.get_node_property(node, "font")
            if bg == "transparent":
                bg = "white"
            if fg == "transparent":
                fg = "white"
            widgetid.configure(background=bg, foreground=fg, font=font)

    def handle_overflow_property(self, node, overflow_type, overflow_function):
        overflow = self.get_node_property(node, overflow_type) 
        if overflow != "visible": # visible is the tkhtml default, so it's largely meaningless
            overflow_map = {"hidden": 0,
                            "auto": 2,
                            "scroll": 1,
                            "clip": 0}
            overflow = overflow_map[overflow]
            return overflow_function(overflow)
        return None

    def set_overflow(self, node):
        "Look for and handle the overflow property"
        # Eventually we'll make overflow a composite property of overflow-x and overflow-y
        # But for now it's its own thing and the only one of the three that is actually respected by Tkhtml in rendering
        for overflow_type in ("overflow", "overflow-y"):
            overflow = self.handle_overflow_property(node, overflow_type, self.manage_vsb_func)
            if overflow:
                self.vsb_type = overflow
                break

        self.handle_overflow_property(node, "overflow-x", self.manage_hsb_func)

        background = self.get_node_property(node, "background-color")
        if background != "transparent" and self.motion_frame_bg != background: # transparent is the tkhtml default, so it's largely meaningless
            self.motion_frame_bg = background
            self.motion_frame.config(bg=background)

    def set_cursor(self, cursor):
        "Set document cursor"
        if self.current_cursor != cursor:
            cursor = CURSOR_MAP[cursor]
            self.master.config(cursor=cursor)
            self.current_cursor = cursor
            # I've noticed that the cursor won't always update when the binding is tied to a different widget than the one we are changing the cursor of
            # however, the html widget doesn't support the cursor property so there's not much we can do about this
            # update_idletasks() or update() have no effect, but print() and updating the color or text of another widget does
            # therefore we update the background color of a tiny frame that is barely visible to match the background color of the page whenever we need to change te cursor
            # it's wierd but hey, it works
            self.motion_frame.config(bg=self.motion_frame_bg)

    def handle_recursive_hovering(self, node_handle, count):
        "Set hover flags on the parents of the hovered element"
        self.set_node_flags(node_handle, "hover")
        self.hovered_nodes.append(node_handle)

        if count >= 1:
            parent = self.get_current_node_parent(node_handle)
            if parent:
                self.handle_recursive_hovering(parent, count - 1)            

    def remove_widget(self, widgetid):
        "Remove a stored widget"
        self.delete_node(self.stored_widgets[widgetid])
        del self.stored_widgets[widgetid]

    def replace_widget(self, widgetid, newwidgetid):
        "Replace a stored widget"
        node = self.stored_widgets[widgetid]
        self.tk.call(node, "replace", newwidgetid)

        if newwidgetid in self.stored_widgets:
            self.tk.call(self.stored_widgets[newwidgetid], "replace", widgetid)
            self.stored_widgets[widgetid] = self.stored_widgets[newwidgetid]
        else:
            del self.stored_widgets[widgetid]
        self.stored_widgets[newwidgetid] = node

    def replace_element(self, selector, widgetid):
        "Replace an HTML element with a widget"
        node = self.search(selector)[0]
        self.tk.call(node, "replace", widgetid)
        self.stored_widgets[widgetid] = node

    def find_text(self, searchtext, select, ignore_case, highlight_all):
        "Search for and highlight specific text in the document"
        self.clear_selection()

        nmatches = 0
        matches = []
        selected = []
        match_indexes = []

        self.tag("delete", "findtext")
        self.tag("delete", "findtextselected")

        if len(searchtext) == 0 or select <= 0:
            return nmatches, selected, matches

        doctext = self.text("text")

        try:
            # find matches
            if ignore_case:
                rmatches = finditer(
                    searchtext, doctext, flags=IGNORECASE | MULTILINE
                )
            else:
                rmatches = finditer(searchtext, doctext, flags=MULTILINE)

            for match in rmatches:
                match_indexes.append(
                    (
                        match.start(0),
                        match.end(0),
                    )
                )
                nmatches += 1

            if len(match_indexes) > 0:
                # highlight matches
                self.post_event(DEBUG_MESSAGE_EVENT, data=f"{nmatches} results for the search key '{searchtext}' have been found")
                if highlight_all:
                    for num, match in enumerate(match_indexes):
                        match = self.text("index", match_indexes[num][0])
                        match += self.text("index", match_indexes[num][1])
                        matches.append(match)

                selected = self.text("index", match_indexes[select - 1][0])
                selected += self.text("index", match_indexes[select - 1][1])

                for match in matches:
                    node1, index1, node2, index2 = match
                    self.tag("add", "findtext", node1, index1, node2, index2)
                    self.tag(
                        "configure",
                        "findtext",
                        "-bg",
                        self.find_match_highlight_color,
                        "-fg",
                        self.find_match_text_color,
                    )

                node1, index1, node2, index2 = selected
                self.tag("add", "findtextselected", node1, index1, node2, index2)
                self.tag(
                    "configure",
                    "findtextselected",
                    "-bg",
                    self.find_current_highlight_color,
                    "-fg",
                    self.find_current_text_color,
                )

                # scroll to node if selected match is not visible
                nodebox = self.text("bbox", node1, index1, node2, index2)
                docheight = float(self.bbox()[3])

                view_top = docheight * self.yview()[0]
                view_bottom = view_top + self.winfo_height()
                node_top = float(nodebox[1])
                node_bottom = float(nodebox[3])

                if (node_top < view_top) or (node_bottom > view_bottom):
                    self.yview("moveto", node_top / docheight)
            else:
                self.post_event(DEBUG_MESSAGE_EVENT, data=f"No results for the search key '{searchtext}' could be found")
            return nmatches, selected, matches
        except Exception as error:
            self.post_event(DEBUG_MESSAGE_EVENT, data=f"Error searching for {searchtext}: {error}")
            return nmatches, selected, matches

    def create_iframe(self, node, url, html=None):
        widgetid = self.embed_obj(self, False, overflow_scroll_frame=self)
        widgetid.copy_settings(self)

        if html:
            widgetid.load_html(html, url)
        elif url:
            widgetid.load_html("<p>Loading...</p>")
            widgetid.load_url(url, insecure=self.insecure_https)

        self.handle_node_replacement(
            node, widgetid, lambda widgetid=widgetid: self.handle_node_removal(widgetid)
        )

    def resolve_url(self, href):
        "Get full url from partial url"
        return urljoin(self.base_url, href)
    
    def on_click(self, event, redirected=False):
        "Set active element flags"
        if not self.current_node:
            # register current node if mouse has never moved
            self.on_mouse_motion(event)

        if not redirected:
            self.selection_type = 0

        self.focus_set()
        self.tag("delete", "selection")
        node_handle = self.get_current_node(event)

        if node_handle:
            self.selection_start_node, self.selection_start_offset = self.node(
                True, event.x, event.y
            )
            self.selection_end_node = None
            self.selection_end_offset = None

            if node_handle and self.stylesheets_enabled:
                if not self.get_node_tag(node_handle):
                    node_handle = self.get_current_node_parent(node_handle)
                self.set_node_flags(node_handle, "active")
                self.prev_active_node = node_handle

    def on_leave(self, event):
        "Reset cursor and node states when leaving this widget"
        self.set_cursor("default")
        if self.stylesheets_enabled:
            for node in self.hovered_nodes:
                try:
                    self.remove_node_flags(node, "hover")
                    self.remove_node_flags(node, "active")
                except tk.TclError:
                    pass
        self.hovered_nodes = []
        self.current_node = None

    def on_mouse_motion(self, event):
        "Set hover flags and handle the CSS 'cursor' property"

        if self.is_selecting:
            return
        if self.on_embedded_node:
            node_handle = self.on_embedded_node
        else:
            node_handle = self.get_current_node(event)
            if not node_handle:
                self.on_leave(None)
                return
        if (node_handle and node_handle != self.current_node and self.stylesheets_enabled):
            old_handle = self.current_node
            self.current_node = node_handle

            if node_handle != old_handle:
                is_text_node = False
                if not self.get_node_tag(node_handle):
                    node_handle = self.get_current_node_parent(node_handle)
                    is_text_node = True

                cursor = self.get_node_property(node_handle, "cursor")
                if cursor in CURSOR_MAP:
                    self.set_cursor(cursor)
                elif is_text_node:
                    self.set_cursor("text")
                else:
                    self.set_cursor("default")
                
                for node in self.hovered_nodes:
                    try:
                        self.remove_node_flags(node, "hover")
                    except tk.TclError:
                        # sometimes errors are thrown if the mouse is moving while the page is loading
                        pass

                self.hovered_nodes = []
                self.handle_recursive_hovering(
                    node_handle, self.recursive_hovering_count
                )

    def on_click_release(self, event):
        "Handle click releases on hyperlinks and form elements"
        if self.is_selecting:
            self.is_selecting = False
            self.current_node = None
            self.on_mouse_motion(event)
            return

        node_handle = self.get_current_node(event)

        try:
            if node_handle:
                node_tag = self.get_node_tag(node_handle).lower()

                if not node_tag:
                    node_handle = self.get_node_parent(node_handle)
                    node_tag = self.get_node_tag(node_handle).lower()

                node_type = self.get_node_attribute(node_handle, "type").lower()

                if self.prev_active_node and self.stylesheets_enabled:
                    self.remove_node_flags(self.prev_active_node, "active")
                if node_tag == "a":
                    self.set_node_flags(node_handle, "visited")
                    self.handle_link_click(node_handle)
                elif node_tag == "input" and node_type == "reset":
                    self.handle_form_reset(node_handle)
                elif node_tag == "input" and node_type == "submit":
                    self.handle_form_submission(node_handle)
                elif node_tag == "input" and node_type == "image":
                    self.handle_form_submission(node_handle)
                elif node_tag == "button" and node_type == "submit":
                    self.handle_form_submission(node_handle)
                else:
                    for node in self.hovered_nodes:
                        node_tag = self.get_node_tag(node).lower()
                        if node_tag == "a":
                            self.set_node_flags(node, "visited")
                            self.handle_link_click(node)
                            break
                        elif node_tag == "button":
                            if (self.get_node_attribute(node, "type").lower() == "submit"):
                                self.handle_form_submission(node)
                                break
        except tk.TclError:
            pass

        self.prev_active_node = None

    def word_in_node(self, node, offset):
        text = self.get_node_text(node)
        letters = list(text)

        beg = 0
        end = 0
        for index, letter in enumerate(reversed(letters[:offset])):
            beg = index + 1
            if letter == " ":
                beg = index
                break
        for index, letter in enumerate(letters[offset:]):
            end = index + 1
            if letter == " ":
                end = index
                break

        pre = len(letters[:offset])
        return pre - beg, pre + end

    def on_double_click(self, event):
        "Cycle between normal selection, text selection, and element selection on multi-clicks"
        self.on_click(event, True)

        if not self.selection_enabled:
            return
        
        if not self.selection_start_node:
            return

        self.selection_end_node = self.selection_start_node
        self.selection_end_offset = self.selection_start_offset
        
        try:
            if self.selection_type == 1:
                text = self.get_node_text(self.selection_start_node)
                self.tag(
                    "add",
                    "selection",
                    self.selection_start_node,
                    0,
                    self.selection_start_node,
                    len(text),
                )
                self.selection_type = 2

            elif self.selection_type == 2:
                self.tag("delete", "selection")
                self.selection_type = 0

            else:
                start_offset, end_offset = self.word_in_node(self.selection_start_node, self.selection_start_offset)
                self.tag(
                    "add",
                    "selection",
                    self.selection_start_node,
                    start_offset,
                    self.selection_start_node,
                    end_offset,
                )
                self.selection_type = 1

            self.tag(
                "configure",
                "selection",
                "-bg",
                self.selected_text_highlight_color,
                "-fg",
                self.selected_text_color,
            )
        except tk.TclError:
            self.set_cursor("default")

    def on_embedded_mouse_motion(self, event, node_handle):
        self.on_embedded_node = node_handle
        self.on_mouse_motion(event)

    def add_bindtags(self, widgetid, allowscrolling=True):
        "Add bindtags to allow scrolling and on_embedded_mouse function calls"
        if allowscrolling:
            tags = (
                self.node_tag,
                self.scrollable_node_tag,
            )
        else:
            tags = (self.node_tag,)
        widgetid.bindtags(widgetid.bindtags() + tags)

    def select_all(self):
        "Select all of the text in the document"
        if not self.selection_enabled:
            return
        
        self.clear_selection()
        beginning = self.text("index", 0)
        end = self.text("index", len(self.text("text")))
        self.selection_start_node = beginning[0]
        self.selection_start_offset = beginning[1]
        self.selection_end_node = end[0]
        self.selection_end_offset = end[1]
        self.tag("add", "selection", beginning[0], beginning[1], end[0], end[1])
        self.tag(
            "configure",
            "selection",
            "-bg",
            self.selected_text_highlight_color,
            "-fg",
            self.selected_text_color,
        )

    def clear_selection(self):
        "Clear current selection possible"
        self.tag("delete", "selection")
        self.selection_start_node = None

    def extend_selection(self, event):
        "Alter selection and HTML element states based on mouse movement"
        if not self.selection_enabled:
            return
                
        if self.selection_start_node is None:
            self.tag("delete", "selection")
            return

        try:
            self.selection_end_node, self.selection_end_offset = self.node(
                True, event.x, event.y
            )

            if self.selection_end_node is None:
                return

            self.tag("delete", "selection")

            if self.selection_type == 1:
                start_offset, end_offset = self.word_in_node(self.selection_start_node, self.selection_start_offset)
                start_offset2, end_offset2 = self.word_in_node(self.selection_end_node, self.selection_end_offset)
                self.tag(
                    "add",
                    "selection",
                    self.selection_start_node,
                    start_offset,
                    self.selection_end_node,
                    end_offset2,
                )
                self.tag(
                    "add",
                    "selection",
                    self.selection_start_node,
                    end_offset,
                    self.selection_end_node,
                    start_offset2,
                )

            elif self.selection_type == 2:
                text = self.get_node_text(self.selection_start_node)
                text2 = self.get_node_text(self.selection_end_node)
                self.tag(
                    "add",
                    "selection",
                    self.selection_start_node,
                    0,
                    self.selection_end_node,
                    len(text2),
                )

                self.tag(
                    "add",
                    "selection",
                    self.selection_start_node,
                    len(text),
                    self.selection_end_node,
                    0,
                )
                
            else:
                self.tag(
                    "add",
                    "selection",
                    self.selection_start_node,
                    self.selection_start_offset,
                    self.selection_end_node,
                    self.selection_end_offset,
                )

            self.tag(
                "configure",
                "selection",
                "-bg",
                self.selected_text_highlight_color,
                "-fg",
                self.selected_text_color,
            )

            if not self.is_selecting and self.prev_active_node:
                if len(self.get_selection()) > 0:
                    self.is_selecting = True
                    self.set_cursor("text")
                    if self.stylesheets_enabled:
                        self.remove_node_flags(self.prev_active_node, "active")
                        for node in self.hovered_nodes:
                            self.remove_node_flags(node, "hover")
                    self.prev_active_node = None
                    self.hovered_nodes = []
        except tk.TclError:
            self.set_cursor("default")

    def get_selection(self):
        "Return the currently selected text"
        if self.selection_start_node is None or self.selection_end_node is None:
            return
        if self.selection_type == 1:
            start_offset, end_offset = self.word_in_node(self.selection_start_node, self.selection_start_offset)
            start_offset2, end_offset2 = self.word_in_node(self.selection_end_node, self.selection_end_offset)
            start_index = self.text(
                "offset", self.selection_start_node, start_offset
            )
            end_index = self.text(
                "offset", self.selection_end_node, end_offset2
            )
            if start_index > end_index:
                start_index = self.text(
                    "offset", self.selection_end_node, start_offset2
                )
                end_index = self.text(
                    "offset", self.selection_start_node, end_offset
                )

        elif self.selection_type == 2:
            text = self.get_node_text(self.selection_start_node)
            text2 = self.get_node_text(self.selection_end_node)
            start_index = self.text(
                "offset", self.selection_start_node, 0
            )
            end_index = self.text(
                "offset", self.selection_end_node, len(text2)
            )
            if start_index > end_index:
                start_index = self.text(
                    "offset", self.selection_end_node, 0
                )
                end_index = self.text(
                    "offset", self.selection_start_node, len(text)
                )
        else:
            start_index = self.text(
                "offset", self.selection_start_node, self.selection_start_offset
            )
            end_index = self.text(
                "offset", self.selection_end_node, self.selection_end_offset
            )
            if start_index > end_index:
                start_index, end_index = end_index, start_index
                
        whole_text = self.text("text")
        return whole_text[start_index:end_index]

    def copy_selection(self, event=None):
        "Copy the selected text to the clipboard"
        selected_text = self.get_selection()
        self.clipboard_clear()
        self.clipboard_append(selected_text)
        self.post_event(DEBUG_MESSAGE_EVENT, data=f"The text '{selected_text}' has been copied to the clipboard")
        
    def scroll_x11(self, event, widget=None):
        "Manage scrolling on Linux"
        if not widget:
            widget = event.widget
            
        yview = widget.yview()  

        if event.num == 4:
            if widget.overflow_scroll_frame and (yview[0] == 0 or widget.vsb_type == 0):
                widget.overflow_scroll_frame.scroll_x11(event, widget.overflow_scroll_frame)
            else:
                if widget.vsb_type == 0:
                    return
                widget.yview_scroll(-4, "units")
        else:
            if widget.overflow_scroll_frame and (yview[1] == 1 or widget.vsb_type == 0):
                widget.overflow_scroll_frame.scroll_x11(event, widget.overflow_scroll_frame)
            else:
                if widget.vsb_type == 0:
                    return
                widget.yview_scroll(4, "units")

    def scroll(self, event):
        "Manage scrolling on Windows/MacOS"
        yview = self.yview()      

        if self.overflow_scroll_frame and event.delta > 0 and (yview[0] == 0 or self.vsb_type == 0):
            self.overflow_scroll_frame.scroll(event)
        elif self.overflow_scroll_frame and event.delta < 0 and (yview[1] == 1 or self.vsb_type == 0):
            self.overflow_scroll_frame.scroll(event)
        elif PLATFORM.system == "Darwin":
            if self.vsb_type == 0:
                return
            self.yview_scroll(int(-1*event.delta), "units")
        else:
            if self.vsb_type == 0:
                return
            self.yview_scroll(int(-1*event.delta/30), "units")