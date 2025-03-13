"""
The core Python bindings to Tkhtml3

Copyright (c) 2025 Andereoo
"""

from re import IGNORECASE, MULTILINE, split, sub, finditer

from urllib.parse import urlencode, urljoin, urlparse

import tkinter as tk
from tkinter import ttk

from imageutils import text_to_image, data_to_image, blank_image
from utilities import *


class Combobox(tk.Widget):
    "Bindings for Bryan Oakley's combobox widget."

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

    def set(self, value):
        if value in self.values:
            self.tk.call(self._w, "select", self.values.index(value))

    def reset(self):
        self.tk.call(self._w, "select", self.default)

    def get(self):
        val = self.tk.call(self._w, "curselection")[0]
        return self.values[val]


class TkinterWeb(tk.Widget):
    "Bindings for the Tkhtml3 HTML widget."

    def __init__(self, master, tkinterweb_options=None, **kwargs):
        self.master = master

        self._setup_settings()
        self._setup_status_variables()

        # inherited settings
        waiting_options = {}
        if tkinterweb_options:
            for item, value in tkinterweb_options.items():
                try:
                    setattr(self, item, value)    
                except AttributeError:
                    waiting_options[item] = value

        # provide OS information for troubleshooting
        self.post_message(f"Starting TkinterWeb for {PLATFORM.processor} {PLATFORM.system} with Python {'.'.join(PYTHON_VERSION)}")

        if self.use_prebuilt_tkhtml:
            # get Tkhtml folder and register crash handling
            folder = get_tkhtml_folder()
            if "drawcleanupcrashcmd" not in kwargs:
                kwargs["drawcleanupcrashcmd"] = master.register(self._on_draw_cleanup_crash_cmd)
        else:
            folder = None

        # register image loading infrastructure
        if "imagecmd" not in kwargs:
            kwargs["imagecmd"] = master.register(self._on_image_cmd)
        # if "logcmd" not in kwargs:
        #    kwargs["logcmd"] = tkhtml_notifier

        # load the Tkhtml3 widget
        try:
            load_tkhtml(master, folder, )
            tk.Widget.__init__(self, master, "html", kwargs)
        except tk.TclError:
            load_tkhtml(master, folder, True)
            tk.Widget.__init__(self, master, "html", kwargs)

        # create a tiny, blank frame for cursor updating
        self.motion_frame = tk.Frame(self, bg=self.motion_frame_bg, width=1, height=1)
        self.motion_frame.place(x=0, y=0)

        # If a setting required the widget to be initialized and couldn't be changed, change it now
        if waiting_options:
            for item, value in waiting_options.items():
                setattr(self, item, value)    

        self._setup_bindings()
        self._setup_handlers()
        self.update_default_style()
        self.post_message(f"Tkhtml3 successfully loaded from {folder}")

    def _setup_settings(self):
        "Widget settings."
        self.allow_threading = self.master.tk.eval('set tcl_platform(threaded)') 

        self._caches_enabled = True
        self._dark_theme_enabled = False
        self._image_inversion_enabled = False
        self._crash_prevention_enabled = True
        self._javascript_enabled = False
        
        self.messages_enabled = True
        self.events_enabled = True   
        self.selection_enabled = True
        self.stylesheets_enabled = True
        self.images_enabled = True
        self.forms_enabled = True
        self.objects_enabled = True
        self.ignore_invalid_images = True
        self.image_alternate_text_enabled = True
        self.overflow_scroll_frame = None
        self.default_style = None
        self.dark_style = None
        self.use_prebuilt_tkhtml = True
        self.experimental = False

        self.find_match_highlight_color = "#ef0fff"
        self.find_match_text_color = "#fff"
        self.find_current_highlight_color = "#38d878"
        self.find_current_text_color = "#fff"
        self.selected_text_highlight_color = "#3584e4"
        self.selected_text_color = "#fff"
        self.visited_links = []

        self.image_alternate_text_font = get_alt_font()
        self.image_alternate_text_size = 14
        self.image_alternate_text_threshold = 10

        self.embed_obj = None
        self.manage_vsb_func = placeholder
        self.manage_hsb_func = placeholder
        self.on_link_click = placeholder
        self.on_form_submit = placeholder
        self.message_func = placeholder
        self.on_script = placeholder
        self.on_element_script = placeholder
        self.on_resource_setup = placeholder
        
        self.maximum_thread_count = 20
        self.insecure_https = False
        self.headers = {}
        self.dark_theme_limit = 160
        self.style_dark_theme_regex = r"([^:;\s{]+)\s?:\s?([^;{!]+)(?=!|;|})"
        self.general_dark_theme_regexes = [r'(<[^>]+bgcolor=")([^"]*)',r'(<[^>]+text=")([^"]*)',r'(<[^>]+link=")([^"]*)']
        self.inline_dark_theme_regexes = [r'(<[^>]+style=")([^"]*)', r'([a-zA-Z-]+:)([^;]*)']
        self.radiobutton_token = "TKWtsvLKac1"

        self.node_tag = f"tkinterweb.{id(self)}.nodes"
        self.scrollable_node_tag = f"tkinterweb.{id(self)}.scrollablenodes"

    def _setup_status_variables(self):
        "Widget status variables."
        self.base_url = ""
        self.title = ""
        self.icon = ""

        self.style_count = 0
        self.active_threads = []
        self.stored_widgets = {}
        self.loaded_images = set()
        self.image_directory = {}
        self.image_name_prefix = f"_tkinterweb_img_{id(self)}_"
        self.is_selecting = False
        self.downloads_have_occured = False
        self.pending_scripts = []
        self.unstoppable = True
        self.on_embedded_node = None
        self.selection_start_node = None
        self.selection_start_offset = None
        self.selection_end_node = None
        self.selection_end_offset = None
        self.prev_active_node = None
        self.current_node = None
        self.hovered_nodes = []
        self.loaded_elements = []
        self.current_cursor = ""
        self.vsb_type = 2
        self.selection_type = 0
        self.motion_frame_bg = "white"

        self.form_widgets = {}
        self.form_nodes = {}
        self.loaded_forms = {}
        self.radio_buttons = {}
        self.waiting_forms = 0

        self.loaded_iframes = {}

    def _setup_bindings(self):
        "Widget bindtags and bindings."
        self._add_bindtags(self, False)
        self.bind("<<Copy>>", self.copy_selection, True)
        self.bind("<B1-Motion>", self._extend_selection, True)
        self.bind("<Button-1>", self._on_click, True)
        self.bind("<Button-2>", self._on_middle_click, True)
        self.bind("<Button-3>", self._on_right_click, True)
        self.bind("<Double-Button-1>", self._on_double_click, True)
        self.bind("<ButtonRelease-1>", self._on_click_release, True)
        self.bind_class(self.node_tag, "<Motion>", self._on_mouse_motion, True)

    def _setup_handlers(self):
        "Register node handlers."
        self.register_handler("script", "script", self._on_script)
        self.register_handler("script", "style", self._on_style)
        self.register_handler("node", "link", self._on_link)
        self.register_handler("node", "title", self._on_title)
        self.register_handler("node", "a", self._on_a)
        self.register_handler("node", "base", self._on_base)
        self.register_handler("node", "input", self._on_input)
        self.register_handler("node", "textarea", self._on_textarea)
        self.register_handler("node", "select", self._on_select)
        self.register_handler("node", "form", self._on_form)
        self.register_handler("node", "object", self._on_object)
        self.register_handler("node", "iframe", self._on_iframe)
        self.register_handler("node", "table", self._on_table)
        self.register_handler("node", "img", self._on_image)

        # Node handlers don't work on body and html elements. 
        # These elements also cannot be removed without causing a segfault. 
        # Wierd.
        self.register_handler("parse", "body", self._on_body)
        self.register_handler("parse", "html", self._on_body)

        self.register_handler("attribute", "input", self._on_input_value_change)
        self.register_handler("attribute", "select", self._on_input_value_change)
        self.register_handler("attribute", "a", self._on_a_value_change)
        self.register_handler("attribute", "object", self._on_object_value_change)
        self.register_handler("attribute", "iframe", self._on_iframe_value_change)

    @property
    def caches_enabled(self):
        return self._caches_enabled
    
    @caches_enabled.setter
    def caches_enabled(self, enabled):
        "Disable the Tkhtml image cache when disabling caches."
        if self._caches_enabled != enabled:
            self._caches_enabled = enabled
            self.enable_imagecache(enabled)
        
    @property
    def javascript_enabled(self):
        return self._javascript_enabled
    
    @javascript_enabled.setter
    def javascript_enabled(self, enabled):
        "Warn the user when enabling JavaScript."
        if self._javascript_enabled != enabled:
            self._javascript_enabled = enabled
            if enabled:
                self.post_message("WARNING: JavaScript support was enabled. This feature is a work in progress. Only enable JavaScript support on documents you know and trust.")

    @property
    def crash_prevention_enabled(self):
        return self._crash_prevention_enabled
    
    @crash_prevention_enabled.setter
    def crash_prevention_enabled(self, enabled):
        "Warn the user when disabling crash prevention."
        if self._crash_prevention_enabled != enabled:
            self._crash_prevention_enabled = enabled
            if not enabled:
                self.post_message("WARNING: Crash prevention was disabled. You may encounter segmentation faults on some pages.")
    
    @property
    def dark_theme_enabled(self):
        return self._dark_theme_enabled
    
    @dark_theme_enabled.setter
    def dark_theme_enabled(self, enabled):
        "Warn the user when enabling dark mode."
        if self._dark_theme_enabled != enabled:
            self._dark_theme_enabled = enabled    
            if enabled:
                self.post_message("Dark theme was enabled. This feature may cause hangs or crashes on some pages.")
            self.update_default_style()

    @property
    def image_inversion_enabled(self):
        return self._image_inversion_enabled
    
    @image_inversion_enabled.setter
    def image_inversion_enabled(self, enabled):
        "Warn the user when enabling image inversion."
        if self._image_inversion_enabled != enabled:
            self._image_inversion_enabled = enabled
            if enabled:
                self.post_message("Image inversion was enabled. This feature may cause hangs or crashes on some pages.")

    @property
    def threading_enabled(self):
        return bool(self._maximum_thread_count)
    
    @threading_enabled.setter
    def threading_enabled(self, enabled):
        "Convenience setting to enable/disable threading by changing the maximum thread count. Not a real setting."
        if enabled:
            self.maximum_thread_count = self.default_maximum_thread_count
        else:
            self.maximum_thread_count = 0

    @property
    def maximum_thread_count(self):
        return self._maximum_thread_count
    
    @maximum_thread_count.setter
    def maximum_thread_count(self, count):
        "Ensure that maximum_thread_count is always zero if Tcl/Tk is not built with thread support."
        count = int(count)
        if self.allow_threading:
            self._maximum_thread_count = count
            if count:
                self.default_maximum_thread_count = count
        else:
            self.post_message("WARNING: threading is disabled because your Tcl/Tk library does not support threading")
            self.default_maximum_thread_count = self._maximum_thread_count = 0

    def post_event(self, event):
        "Generate a virtual event."
        if self.events_enabled:
            # thread safety
            self.after(0, lambda event=event: self._finish_posting_event(event))

    def post_message(self, message):
        "Post a message."
        if self.overflow_scroll_frame:
            message = "[EMBEDDED DOCUMENT] " + message
        if self.messages_enabled:
            self.message_func(message)

    def parse(self, html):
        "Parse HTML code."
        self.downloads_have_occured = False
        self.unstoppable = True
        html = self._crash_prevention(html)
        html = self._dark_mode(html)
        self.tk.call(self._w, "parse", html)

        # we assume that if no downloads have been made by now the document has finished loading, so we send the done loading signal
        if not self.downloads_have_occured:
            self.post_event(DONE_LOADING_EVENT)

        self._submit_deferred_scripts()
        self.send_onload()

    def send_onload(self, root=None, children=None):
        """Send the onload signal for nodes that aren't handled at runtime.
        We keep this a seperate command so that it can be run after inserting elements or changing the innerHTML"""
        if not self._javascript_enabled:
            return
        if children:
            for node in children:
                if self.get_node_tag(node) not in {"img", "object", "link"}:
                    self._submit_element_js(node, "onload")
        else:
            for node in self.search("[onload]", root=root):
                if self.get_node_tag(node) not in {"img", "object", "link"}:
                    self._submit_element_js(node, "onload")

    def update_default_style(self):
        "Update the default stylesheet based on color theme."
        if self._dark_theme_enabled and self.dark_style:
            self.config(defaultstyle=self.dark_style)
        elif self.default_style:
            self.config(defaultstyle=self.default_style)

    def parse_css(self, sheetid=None, data="", url=None, override=False):
        "Parse CSS code."
        if not url:
            url = self.base_url
        data = self._crash_prevention(data)
        if self._dark_theme_enabled:
            data = sub(self.style_dark_theme_regex, lambda match, matchtype=0: self._generate_altered_colour(match, matchtype), data)
        try:
            #urlcmd = self.register(self.resolve_url)
            importcmd = self.register(
                lambda new_url, parent_url=url: self._on_atimport(
                    parent_url, new_url
                )
            )
            if override:
                self.style_count += 1
                self.tk.call(
                    self._w, "style", "-id", "author" + str(self.style_count).zfill(4), "-importcmd", importcmd, data
                )
            elif sheetid:
                self.tk.call(
                    self._w, "style", "-id", sheetid, "-importcmd", importcmd, data
                )
            else:
                self.tk.call(self._w, "style", "-importcmd", importcmd, data)
        except tk.TclError:
            # the widget doesn't exist anymore
            pass

    def reset(self):
        "Reset the widget."
        self.stop()
        self.loaded_images = set()
        self.image_directory = {}
        self.form_get_commands = {}
        self.form_nodes = {}
        self.form_widgets = {}
        self.loaded_forms = {}
        self.waiting_forms = 0
        self.radio_buttons = {}
        self.loaded_iframes = {}
        self.hovered_nodes = []
        self.loaded_elements = []
        self.current_node = None
        self.on_embedded_node = None
        self.selection_start_node = None
        self.selection_end_node = None
        self.title = ""
        self.icon = ""
        self.vsb_type = self.manage_vsb_func()
        self.manage_hsb_func()
        self._set_cursor("default")
        self.tk.call(self._w, "reset")

    def stop(self):
        "Stop loading resources."
        self.unstoppable = False
        for thread in self.active_threads:
            thread.stop()

    def node(self, *args):
        "Retrieve one or more document node handles from the current document."
        nodes = self.tk.call(self._w, "node", *args)
        if nodes:
            return nodes
        else:
            return None, None

    def text(self, *args):
        "Enable interaction with the text of the HTML document."
        return self.tk.call(self._w, "text", *args)

    def tag(self, subcommand, tag_name, *args):
        "Return the name of the Html tag that generated this document node, or an empty string if the node is a text node."
        return self.tk.call(self._w, "tag", subcommand, tag_name, *args)

    def search(self, selector, cnf={}, **kwargs):
        """Search the document for the specified CSS selector; return a Tkhtml3 node if found."""
        return self.tk.call((self._w, "search", selector)+self._options(cnf, kwargs))

    def xview(self, *args):
        "Used to control horizontal scrolling."
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
        """Used to control vertical scrolling."""
        return self.tk.call(self._w, "yview", *args)

    def yview_scroll(self, number, what):
        """Shifts the view in the window left or right, according to number and what.
        "number" is an integer, and "what" is either "units" or "pages"."""
        return self.yview("scroll", number, what)

    def yview_moveto(self, number):
        "Moves the view vertically to the specified position."
        return self.yview("moveto", number)

    def bbox(self, node=None):
        "Get the bounding box of the viewport or a specified node."
        return self.tk.call(self._w, "bbox", node)

    def parse_fragment(self, html):
        """Parse a document fragment.
        A document fragment isn't part of the active document but is comprised of nodes like the active document.
        Changes made to the fragment don't affect the document.
        Returns a root node."""
        self.downloads_have_occured = False
        self.unstoppable = True
        html = self._crash_prevention(html)
        html = self._dark_mode(html)
        fragment = self.tk.call(self._w, "fragment", html)
        # We assume that if no downloads have been made by now the document has finished loading, so we send the done loading signal
        if not self.downloads_have_occured:
            self.post_event(DONE_LOADING_EVENT)
        self._submit_deferred_scripts()
        return fragment
    
    def enable_imagecache(self, enabled):
        "Enable or disable the Tkhtml imagecache."
        self.tk.call(self._w, "configure", "-imagecache", enabled)

    def get_node_text(self, node_handle, *args):
        "Get the text content of the given node."
        return self.tk.call(node_handle, "text", *args)

    def set_node_text(self, node_handle, new):
        "Set the text content of the given node."
        return self.tk.call(node_handle, "text", "set", new)

    def get_node_tag(self, node_handle):
        "Get the HTML tag of the given node."
        return self.tk.call(node_handle, "tag")

    def get_node_parent(self, node_handle):
        "Get the parent of the given node."
        return self.tk.call(node_handle, "parent")

    def get_node_children(self, node_handle):
        "Get the children of the given node."
        return self.tk.call(node_handle, "children")

    def get_node_attribute(self, node_handle, attribute, default="", value=None):
        "Get the specified attribute of the given node."
        if value:  # backwards compatability
            return self.tk.call(node_handle, "attribute", attribute, value)
        else:
            return self.tk.call(
                node_handle, "attribute", "-default", default, attribute
            )

    def set_node_attribute(self, node_handle, attribute, value):
        "Set the specified attribute of the given node."
        return self.tk.call(node_handle, "attribute", attribute, value)

    def get_node_attributes(self, node_handle):
        "Get the attributes of the given node."
        attr = self.tk.call(node_handle, "attribute")
        return dict(zip(attr[0::2], attr[1::2]))

    def get_node_property(self, node_handle, node_property, *args):
        "Get the specified CSS property of the given node."
        return self.tk.call(node_handle, "property", *args, node_property)

    def get_node_properties(self, node_handle, *args):
        "Get the CSS properties of the given node."
        prop = self.tk.call(node_handle, "property", *args)
        return dict(zip(prop[0::2], prop[1::2]))

    def override_node_properties(self, node_handle, *props):
        "Get/set the CSS property override list."
        if props: return self.tk.call(node_handle, "override", " ".join(props))
        return self.tk.call(node_handle, "override")

    def insert_node(self, node_handle, child_nodes):
        "Experimental, insert the specified nodes into the parent node."
        return self.tk.call(node_handle, "insert", child_nodes)

    def insert_node_before(self, node_handle, child_nodes, before):
        "Experimental, place the specified nodes is before another node."
        return self.tk.call(node_handle, "insert", "-before", before, child_nodes)

    def delete_node(self, node_handle):
        "Delete the given node."
        node_parent = self.get_node_parent(node_handle)
        if node_parent and self.get_node_tag(node_handle) != "body":
            # removing the body element causes a segfault
            self.tk.call(node_parent, "remove", node_handle)
        else:
            raise tk.TclError(f"the requested element cannot be removed")

    def destroy_node(self, node_handle):
        "Destroy a node. May cause crashes so avoid it whenever possible."
        self.tk.call(node_handle, "destroy")

    def set_node_flags(self, node, name):
        "Set dynamic flags on the given node."
        self.tk.call(node, "dynamic", "set", name)

    def remove_node_flags(self, node, name):
        "Set dynamic flags on the given node."
        self.tk.call(node, "dynamic", "clear", name)

    def get_node_tkhtml(self, node_handle):
        "Get pathName of node (I think)."
        return self.tk.call(node_handle, "html")

    def get_current_node(self, event):
        "Get current node."
        return self.tk.eval(
            f"""set node [lindex [lindex [{self} node {event.x} {event.y}] end] end]"""
        )

    def get_current_node_parent(self, node):
        "Get the parent of the given node."
        return self.tk.eval(f"""set node [lindex [lindex [{node} parent] end] end]""")
    
    def register_handler(self, handler_type, node_tag, callback):
        "Register a node handler"
        self.tk.call(self._w, "handler", handler_type, node_tag, self.register(callback))

    def image(self, full=False):
        """Return the name of a new Tk image containing the rendered document.
        The returned image should be deleted when the script has finished with it.
        Note that this command is mainly intended for automated testing.
        Be wary of running this command on large documents.
        Does not work on Windows unless experimental Tkhtml is used."""
        full = "-full" if full else ""
        name = self.tk.call(self._w, "image", full)
        return name, self.tk.call(name, "data")

    def postscript(self, cnf={}, **kwargs):
        """Print the contents of the canvas to a postscript file.
        Valid options: colormap, colormode, file, fontmap, height, 
        pageanchor, pageheight, pagesize, pagewidth, pagex, pagey, 
        nobg, noimages, rotate, width, x, and y.
        Does not work unless experimental Tkhtml is used."""
        return self.tk.call((self._w, "postscript")+self._options(cnf, kwargs))

    def preload_image(self, url):
        """Preload an image. 
        Only useful if caches are enabled and reset() is not called after preloading."""
        return self.tk.call(self._w, "preload", url)
    
    def get_computed_styles(self):
        "Get a tuple containing the computed CSS rules for each CSS selector"
        return self.tk.call(self._w, "_styleconfig")

    def fetch_scripts(self, attributes, url=None, data=None):
        "Fetch and run scripts"
        thread = self._begin_download()

        if url and self.unstoppable:
            self.post_message(f"Fetching script from {shorten(url)}")
            try:
                data = self._download_url(url)[0]
            except Exception as error:
                self.post_message(f"ERROR: could not load script {url}: {error}")
                self.on_resource_setup(url, "script", False)

        if data and self.unstoppable:
            if "defer" in attributes:
                self.pending_scripts.append((attributes, data))
            else:
                self.after(0, self.on_script, attributes, data) # thread safety
                
            if url:
                self.post_message(f"Successfully loaded {shorten(url)}")
                self.on_resource_setup(url, "script", True)
        self._finish_download(thread)

    def fetch_styles(self, node=None, url=None, data=None):
        "Fetch stylesheets and parse the CSS code they contain"
        thread = self._begin_download()

        if url and self.unstoppable:
            self.post_message(f"Fetching stylesheet from {shorten(url)}")
            try:
                data = sub(r"url\((.*?)\)", 
                           lambda match, url=url: self._fix_css_urls(match, url), 
                           self._download_url(url)[0]
                           )
            except Exception as error:
                self.post_message(f"ERROR: could not load stylesheet {url}: {error}")
                self.on_resource_setup(url, "stylesheet", False)

        if data and self.unstoppable:
            self.style_count += 1
            sheetid = "user." + str(self.style_count).zfill(4)

            self.parse_css(f"{sheetid}.9999", data, url)
            if node:
                # thread safety
                self.after(0, self._submit_element_js, node, "onload")
            if url:
                self.post_message(f"Successfully loaded {shorten(url)}")
                self.on_resource_setup(url, "stylesheet", True)
        self._finish_download(thread)

    def fetch_objects(self, node, url):
        thread = self._begin_download()

        try:
            data, newurl, filetype, code = self._download_url(url)

            if data and filetype.startswith("image"):
                name = self.image_name_prefix + str(len(self.loaded_images))
                image = data_to_image(data, name, filetype, self._image_inversion_enabled, self.dark_theme_limit)
                self.loaded_images.add(image) 
                self.override_node_properties(node, "-tkhtml-replacement-image", f"url(replace:{image})")
            elif data and filetype == "text/html":
                self.after(0, self._create_iframe, node, newurl, data)

            self.after(0, self._submit_element_js, node, "onload")
        except Exception as error:
            self.post_message(f"ERROR: could not load object element: {error}")
        
        self._finish_download(thread)

    def load_alt_text(self, url, name):
        if (url in self.image_directory):
            node = self.image_directory[url]
            if not self.ignore_invalid_images:
                image = data_to_image(BROKEN_IMAGE, name, "image/png", self._image_inversion_enabled, self.dark_theme_limit)
                self.loaded_images.add(image)
            elif self.image_alternate_text_enabled:
                alt = self.get_node_attribute(node, "alt")
                if alt and self.experimental:
                    self.insert_node(node, self.parse_fragment(alt))
                elif alt:
                    image = text_to_image(
                        name, alt, self.bbox(node),
                        self.image_alternate_text_font,
                        self.image_alternate_text_size,
                        self.image_alternate_text_threshold,
                    )
                    self.loaded_images.add(image)
        elif not self.ignore_invalid_images:
            image = data_to_image(BROKEN_IMAGE, name, "image/png", self._image_inversion_enabled, self.dark_theme_limit)
            self.loaded_images.add(image)

    def fetch_images(self, node, url, name):
        "Fetch images and display them in the document."
        thread = self._begin_download()

        self.post_message(f"Fetching image from {shorten(url)}")

        if url == self.base_url:
            self.load_alt_text(url, name)
            self.post_message(f"ERROR: image url not specified")
        else:
            try:
                data, newurl, filetype, code = self._download_url(url)

                if self.unstoppable and data:
                    # thread safety
                    self.after(0, self.finish_fetching_images, node, data, name, filetype, url)

            except Exception as error:
                self.load_alt_text(url, name)
                self.post_message(f"ERROR: could not load image {url}: {error}")
                self.on_resource_setup(url, "image", False)
        self._finish_download(thread)

    def finish_fetching_images(self, node, data, name, filetype, url):
        try:
            image = data_to_image(data, name, filetype, self._image_inversion_enabled, self.dark_theme_limit)
            
            if image:
                self.loaded_images.add(image)
                self.post_message(f"Successfully loaded {shorten(url)}")
                self.on_resource_setup(url, "image", True)
                if node:
                    # thread safety
                    self.after(0, self._submit_element_js, node, "onload")
                if self.experimental:
                    node = self.search(f'img[src="{url}"]')
                    if node:
                        if self.get_node_children(node): self.delete_node(self.get_node_children(node))
            else:
                self.load_alt_text(url, name)
                self.post_message(f"ERROR: the image {url} could not be shown: either PyGObject, CairoSVG, or both PyCairo and Rsvg must be installed to parse .svg files")
                self.on_resource_setup(url, "image", False)

        except Exception as error:
            self.load_alt_text(url, name)
            self.post_message(f"ERROR: could not load image {url}: {error}")
            self.on_resource_setup(url, "image", False)

    def handle_node_replacement(self, node, widgetid, deletecmd, stylecmd=None, allowscrolling=True, handledelete=True):
        "Replace a Tkhtml3 node with a Tkinter widget."
        if stylecmd:
            if handledelete:
                self.tk.call(
                    node, "replace", widgetid,
                    "-deletecmd", self.register(deletecmd),
                    "-stylecmd", self.register(stylecmd),
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

        self._add_bindtags(widgetid, allowscrolling)

        widgetid.bind(
            "<Enter>",
            lambda event, node_handle=node: self._on_embedded_mouse_motion(
                event, node_handle=node_handle
            ),
        )
        widgetid.bind(
            "<Leave>",
            lambda event, node_handle=None: self._on_embedded_mouse_motion(
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
            style = ttk.Style()
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

    
    def remove_widget(self, widgetid):
        "Remove the specified widget from the document."
        self.delete_node(self.stored_widgets[widgetid])
        del self.stored_widgets[widgetid]

    def replace_widget(self, widgetid, newwidgetid):
        "Remove the old widget from the document and replace it with the new widget."
        node = self.stored_widgets[widgetid]
        self.tk.call(node, "replace", newwidgetid)

        if newwidgetid in self.stored_widgets:
            self.tk.call(self.stored_widgets[newwidgetid], "replace", widgetid)
            self.stored_widgets[widgetid] = self.stored_widgets[newwidgetid]
        else:
            del self.stored_widgets[widgetid]
        self.stored_widgets[newwidgetid] = node

    def replace_element(self, selector, widgetid):
        "Replace the content of the element matching the specified CSS selector with the given widget."
        node = self.search(selector)[0]
        self.tk.call(node, "replace", widgetid)
        self.stored_widgets[widgetid] = node

    def find_text(self, searchtext, select, ignore_case, highlight_all):
        "Search for and highlight specific text in the document."
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
                self.post_message(f"{nmatches} results for the search key '{searchtext}' have been found")
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
                self.post_message(f"No results for the search key '{searchtext}' could be found")
            return nmatches, selected, matches
        except Exception as error:
            self.post_message(f"ERROR: an error was encountered while searching for {searchtext}: {error}")
            return nmatches, selected, matches
    
    def resolve_url(self, url):
        "Generate a full url from the specified url."
        return urljoin(self.base_url, url)
    
    def update_tags(self):
        "Update selection and find tag colors"
        self.tag("configure", "findtext", "-bg", self.find_match_highlight_color, "-fg", self.find_match_text_color)
        self.tag("configure", "findtextselected", "-bg", self.find_current_highlight_color, "-fg", self.find_current_text_color)
        self.tag("configure", "selection", "-bg", self.selected_text_highlight_color, "-fg", self.selected_text_color)

    def select_all(self):
        """Select all text in the document."""
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
        "Clear the current selection."
        self.tag("delete", "selection")
        self.selection_start_node = None
    
    def get_selection(self):
        "Return any selected text."
        if self.selection_start_node is None or self.selection_end_node is None:
            return
        if self.selection_type == 1:
            start_offset, end_offset = self._word_in_node(self.selection_start_node, self.selection_start_offset)
            start_offset2, end_offset2 = self._word_in_node(self.selection_end_node, self.selection_end_offset)
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
        "Copy the selected text to the clipboard."
        selected_text = self.get_selection()
        self.clipboard_clear()
        self.clipboard_append(selected_text)
        self.post_message(f"The text '{selected_text}' has been copied to the clipboard")
        
    def scroll_x11(self, event, widget=None):
        "Manage scrolling on Linux."
        if not widget:
            widget = event.widget
            
        yview = widget.yview()

        if self._javascript_enabled:
            for node_handle in widget.hovered_nodes:
                widget._submit_element_js(node_handle, "onscroll")

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
        "Manage scrolling on Windows/MacOS."
        yview = self.yview() 

        if self._javascript_enabled:
            for node_handle in self.hovered_nodes:
                self._submit_element_js(node_handle, "onscroll")     

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


    def _finish_posting_event(self, event):
        try:
            self.event_generate(event)
        except tk.TclError:
            # the widget doesn't exist anymore
            pass

    def _generate_altered_colour(self, match, matchtype=1):
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
                    colors[count] = invert_color(
                        list(
                            int(color[i : i + lv // 3], 16)
                            for i in range(0, lv, lv // 3)
                        ),
                        match.group(1), self.dark_theme_limit
                    )
                    changed = True
                elif color.startswith("rgb(") or color.startswith("rgba("):
                    colors[count] = invert_color(
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
                        match.group(1), self.dark_theme_limit
                    )
                    changed = True
                else:
                    try:
                        color = list(self.winfo_rgb(color))
                        colors[count] = invert_color(color, match.group(1), self.dark_theme_limit)
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
            
    def _dark_mode(self, html):
        if self._dark_theme_enabled:
            html = sub(self.inline_dark_theme_regexes[0], lambda match: match.group(1) + sub(self.inline_dark_theme_regexes[1], self._generate_altered_colour, match.group(2)), html)
            for regex in self.general_dark_theme_regexes:
                html = sub(regex, self._generate_altered_colour, html, flags=IGNORECASE)
        return html

    def _download_url(self, url):
        if url.startswith("file://") or (not self._caches_enabled):
            return download(url, insecure=self.insecure_https, headers=tuple(self.headers.items()))
        else:
            return cache_download(url, insecure=self.insecure_https, headers=tuple(self.headers.items()))
    
    def _thread_check(self, callback, *args, **kwargs):
        if not self.downloads_have_occured:
            self.downloads_have_occured = True
            
        if self._maximum_thread_count == 0:
            callback(*args, **kwargs)
        elif len(self.active_threads) >= self._maximum_thread_count:
            self.after(500, lambda callback=callback, args=args: self._thread_check(callback, *args, **kwargs))
        else:
            thread = StoppableThread(target=callback, args=args, kwargs=kwargs)
            thread.start()

    def _on_script(self, attributes, tag_contents):
        """A JavaScript engine could be used here to parse the script.
        Returning any HTMl code here (should) cause it to be parsed in place of the script tag."""
        if not self._javascript_enabled or not self.unstoppable:
            return

        attributes = attributes.split()
        attributes = dict(zip(attributes[::2], attributes[1::2])) # make attributes a dict

        if "src" in attributes:
            self._thread_check(self.fetch_scripts, attributes, self.resolve_url(attributes["src"]))
        elif "defer" in attributes:
            self.pending_scripts.append((attributes, tag_contents))
        else:
            return self.on_script(attributes, tag_contents)

    def _on_style(self, attributes, tag_contents):
        "Handle <style> elements."
        if not self.stylesheets_enabled or not self.unstoppable:
            return

        self._thread_check(self.fetch_styles, data=tag_contents)

    def _on_link(self, node):
        "Handle <link> elements."
        if not self.unstoppable:
            return
        
        try:
            rel = self.get_node_attribute(node, "rel").lower()
            media = self.get_node_attribute(node, "media", default="all").lower()
            href = self.get_node_attribute(node, "href")
            url = self.resolve_url(href)
        except tk.TclError:
            return

        if (
            ("stylesheet" in rel)
            and ("all" in media or "screen" in media)
            and self.stylesheets_enabled
        ):
            self._thread_check(self.fetch_styles, node, url)
            # onload is fired if and when the stylesheet is parsed
        elif "icon" in rel:
            self.icon = url
            self.post_event(ICON_CHANGED_EVENT)
            self._submit_element_js(node, "onload")
        else:
            self._submit_element_js(node, "onload")

    def _on_atimport(self, parent_url, new_url):
        "Load @import scripts."
        if not self.stylesheets_enabled or not self.unstoppable:
            return
        try:
            url = urljoin(parent_url, new_url)
            self.post_message(f"Loading stylesheet from {shorten(url)}")

            self._thread_check(self.fetch_styles, url=new_url)

        except Exception as error:
            self.post_message(f"ERROR: could not load stylesheet {new_url}: {error}")

    def _on_title(self, node):
        "Handle <title> elements. We could use a script handler but then the node is no longer visible to the DOM."
        self.title = self.get_node_text(self.get_node_children(node), "-pre")
        self.post_event(TITLE_CHANGED_EVENT)

    def _on_base(self, node):
        "Handle <base> elements."
        href = self.get_node_attribute(node, "href", "")
        if href:
            self.base_url = self.resolve_url(href)

    def _on_a(self, node):
        "Handle <a> elements."
        self.set_node_flags(node, "link")
        try:
            href = self.get_node_attribute(node, "href")
            url = self.resolve_url(href)
            if url in self.visited_links:
                self.set_node_flags(node, "visited")
        except tk.TclError:
            pass

    def _on_a_value_change(self, node, attribute, value):
        if attribute == "href":
            url = self.resolve_url(value)
            if url in self.visited_links:
                self.set_node_flags(node, "visited")
            else:
                self.remove_node_flags(node, "visited")

    def _on_iframe(self, node):
        "Handle <iframe> elements."
        if not self.objects_enabled or not self.unstoppable:
            return

        src = self.get_node_attribute(node, "src")
        srcdoc = self.get_node_attribute(node, "srcdoc")
        scrolling = "auto"
        if self.get_node_attribute(node, "scrolling") == "no":
            scrolling = False

        if srcdoc:
            self._create_iframe(node, None, srcdoc, scrolling)
        elif src and (src != self.base_url):
            src = self.resolve_url(src)
            self.post_message(f"Creating iframe from {shorten(src)}")
            self._create_iframe(node, src, vertical_scrollbar=scrolling)

    def _on_iframe_value_change(self, node, attribute, value):
        if attribute == "srcdoc":
            if node in self.loaded_iframes:
                self.loaded_iframes[node].load_html(value)
            else:
                self._create_iframe(node, None, value)
        elif attribute == "src" and (value != self.base_url):
            if node in self.loaded_iframes:
                self.loaded_iframes[node].load_url(self.resolve_url(value))
            else:
                self._create_iframe(node, value)

    def _on_object(self, node, data=None):
        "Handle <object> elements."
        if not self.objects_enabled or not self.unstoppable:
            return

        if data == None:
            # this doesn't work when in an attribute handler
            data = self.get_node_attribute(node, "data")

        if data != "":
            try:
                # load widgets presented in <object> elements
                widgetid = self.nametowidget(data)
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
                self._submit_element_js(node, "onload")
            except KeyError:
                data = self.resolve_url(data)
                if data == self.base_url:
                    # Don't load the object if it is the same as the current file
                    # Otherwise the page will load the same object indefinitely and freeze the GUI forever
                    return

                self.post_message(f"Creating object from {shorten(data)}")
                self._thread_check(self.fetch_objects, node, data)

    def _on_object_value_change(self, node, attribute, value):
        if attribute == "data":
            self._on_object(node, value)

    def _on_draw_cleanup_crash_cmd(self):
        if self._crash_prevention_enabled:
            self.post_message("ERROR: HtmlDrawCleanup has encountered a critical error. This is being ignored because crash prevention is enabled.")
        else:
            self.destroy()

    def _on_image(self, node):
        url = self.resolve_url(self.get_node_attribute(node, "src"))
        self.image_directory[url] = node

    def _on_image_cmd(self, url):
        "Handle images."
        if not self.images_enabled or not self.unstoppable:
            return

        name = self.image_name_prefix + str(len(self.loaded_images))

        image = blank_image(name)
        self.loaded_images.add(image)

        if url.startswith("replace:"):
            name = url.replace("replace:", "")
        elif any({
                url.startswith("linear-gradient("),
                url.startswith("radial-gradient("),
                url.startswith("repeating-linear-gradient("),
                url.startswith("repeating-radial-gradient("),
            }):
            self.post_message(f"Fetching image: {shorten(url)}")
            self.load_alt_text(url, name)
            for image in url.split(","):
                self.post_message(f"ERROR: the image {shorten(url)} could not be shown because it is not supported yet")
            self.on_resource_setup(url, "image", False)
        else:
            url = url.split("), url(", 1)[0].replace("'", "").replace('"', "")
            url = self.resolve_url(url)
            if url in self.image_directory:
                node = self.image_directory[url]
            else:
                node = None
            self._thread_check(self.fetch_images, node, url, name)
        return name

    def _on_form(self, node):
        "Handle <form> elements."
        if not self.forms_enabled:
            return

        inputs = self.search("input, select, textarea, button", root=node)
        for i in inputs:
            self.form_nodes[i] = node

        if len(inputs) == 0:
            self.waiting_forms += 1
        else:
            self.loaded_forms[node] = inputs
            self.post_message("Successfully setup form")

    def _on_table(self, node):
        """Handle <form> elements in tables; workaround for bug #48."
        In tables, Tkhtml doesn't seem to notice that forms have children.
        We get all children of the table and associate inputs with the previous form.
        Not perfect, but it usually works.
        If a <td> tag is not present, this fails, as Tkhtml seems to not even notice inputs at all"""

        if not self.forms_enabled:
            return
        
        if self.waiting_forms > 0:
            form = None
            inputs = {}

            for node in (self.search("*")):
                tag = self.get_node_tag(node)
                if tag == "form":
                    form = node
                    inputs[form] = []
                elif tag.lower() in {"input", "select", "textarea", "button"} and form:
                    self.form_nodes[node] = form
                    inputs[form].append(node)
           
            for form in inputs:
                self.loaded_forms[form] = inputs[form]
                self.post_message("Successfully setup table form")
                self.waiting_forms -= 1

    def _on_select(self, node):
        "Handle <select> elements."
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
        widgetid.configure(onchangecommand=lambda *_, widgetid=widgetid: self._on_input_change(node, widgetid))
        self.form_widgets[node] = widgetid
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

    def _on_textarea(self, node):
        "Handle <textarea> elements."
        if not self.forms_enabled:
            return
        widgetid = ScrolledTextBox(self, self.get_node_text(self.get_node_children(node), "-pre"), lambda widgetid, node=node: self._on_input_change(node, widgetid))

        self.form_widgets[node] = widgetid
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

    def _on_input(self, node):
        "Handle <input> elements."
        if not self.forms_enabled:
            return
        self.tk.eval('set type ""')
        nodetype = self.tk.eval(
            "set nodetype [string tolower [%s attr -default {} type]]" % node
        )
        nodevalue = self.get_node_attribute(node, "value")
        state = self.get_node_attribute(node, "disabled", "false")

        if nodetype in {"image", "submit", "reset", "button"}:
            return
        elif nodetype == "file":
            accept = self.get_node_attribute(node, "accept")
            multiple = (
                self.get_node_attribute(node, "multiple", self.radiobutton_token)
                != self.radiobutton_token
            )
            widgetid = FileSelector(self, accept, multiple, lambda widgetid, node=node: self._on_input_change(node, widgetid))
            stylecmd = lambda node=node, widgetid=widgetid: self.handle_node_style(
                node, widgetid
            )
        elif nodetype == "color":
            widgetid = ColourSelector(self, nodevalue, lambda widgetid, node=node: self._on_input_change(node, widgetid))
            stylecmd = placeholder
        elif nodetype == "checkbox":
            if self.get_node_attribute(node, "checked", "false") != "false": 
                checked = 1
            else:
                checked = 0

            widgetid = FormCheckbox(self, checked, lambda widgetid, node=node: self._on_input_change(node, widgetid))
            widgetid.set = lambda nodevalue, node=node: self.set_node_attribute(node, "value", nodevalue)
            widgetid.get = lambda node=node: self.get_node_attribute(node, "value")
            stylecmd = lambda node=node, widgetid=widgetid: self.handle_node_style(
                node, widgetid
            )
        elif nodetype == "range":
            widgetid = FormRange(self, 
                nodevalue,
                self.get_node_attribute(node, "min", 0),
                self.get_node_attribute(node, "max", 100),
                self.get_node_attribute(node, "step", 1),
                lambda widgetid, node=node: self._on_input_change(node, widgetid)
            )
            stylecmd = lambda node=node, widgetid=widgetid, widgettype="range": self.handle_node_style(
                node, widgetid, widgettype
            )
        elif nodetype == "radio":
            name = self.get_node_attribute(node, "name", "")
            if self.get_node_attribute(node, "checked", "false") != "false": 
                checked = True
            else:
                checked = False
            
            if name in self.radio_buttons:
                variable = self.radio_buttons[name]
            else:
                variable = None

            widgetid = FormRadioButton(
                self,
                self.radiobutton_token,
                nodevalue,
                checked,
                variable,
                lambda widgetid, node=node: self._on_input_change(node, widgetid)
            )
            widgetid.set = lambda nodevalue, node=node: self.set_node_attribute(node, "value", nodevalue)
            self.radio_buttons[name] = widgetid.variable
            stylecmd = lambda node=node, widgetid=widgetid: self.handle_node_style(
                node, widgetid
            )
        else:
            widgetid = FormEntry(self, nodevalue, nodetype, lambda widgetid, node=node: self._on_input_change(node, widgetid))
            widgetid.bind(
                "<Return>",
                lambda event, node=node: self._handle_form_submission(
                    node=node, event=event
                ),
            )
            stylecmd = lambda node=node, widgetid=widgetid, widgettype="text": self.handle_node_style(
                node, widgetid, widgettype
            )

        self.form_widgets[node] = widgetid
        self.handle_node_replacement(
            node,
            widgetid,
            lambda widgetid=widgetid: self.handle_node_removal(widgetid),
            stylecmd
        )

        if state != "false": 
            widgetid.configure(state="disabled")

    def _on_input_value_change(self, node, attribute, value):
        if node not in self.form_widgets:
            return
        
        nodetype = self.get_node_attribute(node, "type")
        if attribute == "value" and nodetype not in {"checkbox", "radio"}:
            self.form_widgets[node].set(value)
        elif attribute == "checked":
            if nodetype == "checkbox":
                if value != "false": self.form_widgets[node].variable.set(1)
                else: self.form_widgets[node].variable.set(0)
            elif nodetype == "radio":
                nodevalue = self.get_node_attribute(node, "value")
                if value != "false": 
                    self.form_widgets[node].variable.set(nodevalue)

    def _on_body(self, node, index):
        "Wait for style changes on the root node."
        self.tk.call(node,
                    "replace",
                    node,
                    "-stylecmd",
                    self.register(lambda node=node: self._set_overflow(node)))

    def _on_input_change(self, node, widgetid):
        widgetid.event_generate("<<Modified>>")
        self._submit_element_js(node, "onchange")
        return True

    def _crash_prevention(self, data):
        if self._crash_prevention_enabled:
            data = "".join(c for c in data if c <= "\uFFFF")
            data = sub(
                "font-family:[^;']*(;)?",
                self._remove_noto_emoji,
                data,
                flags=IGNORECASE,
            )
            data = sub(r"rgb\([^0-9](.*?)\)", "inherit", data, flags=IGNORECASE)
        return data

    def _begin_download(self):
        thread = get_current_thread()
        self.active_threads.append(thread)
        self.post_event(DOWNLOADING_RESOURCE_EVENT)
        return thread

    def _finish_download(self, thread):
        self.active_threads.remove(thread)
        if len(self.active_threads) == 0:
            self.post_event(DONE_LOADING_EVENT)

    def _submit_deferred_scripts(self):
        if self.pending_scripts:
            for index, script in enumerate(self.pending_scripts):
                # thread safety
                self.after(0, self.on_script, *script)
            self.pending_scripts = []
           
    def _fix_css_urls(self, match, url):
        "Make relative uris in CSS files absolute."
        newurl = match.group()
        newurl = strip_css_url(newurl)
        newurl = urljoin(url, newurl)
        newurl = f"url('{newurl}')"
        return newurl

    def _remove_noto_emoji(self, match):
        "Remove noto color emoji font, which causes Tkinter to crash."
        match = match.group().lower()
        match = match.replace("noto color emoji", "arial")
        return match

    def _handle_link_click(self, node_handle):
        "Handle link clicks."
        href = self.get_node_attribute(node_handle, "href")
        url = self.resolve_url(href)
        self.post_message(f"A link to '{shorten(url)}' was clicked")
        self.visited_links.append(url)
        self.on_link_click(url)

    def _handle_form_reset(self, node):
        "Reset HTML forms."
        if (node not in self.form_nodes) or (not self.forms_enabled):
            return

        form = self.form_nodes[node]

        for formelement in self.loaded_forms[form]:
            if formelement in self.form_widgets:
                nodetype = self.get_node_attribute(formelement, "type")
                nodetag = self.get_node_tag(formelement)
                widget = self.form_widgets[formelement]
                if nodetag == "textarea":
                    nodevalue = self.get_node_text(self.get_node_children(formelement), "-pre")
                    widget.set(nodevalue)
                elif nodetype == "checkbox":
                    if self.get_node_attribute(formelement, "checked", "false") != "false": widget.variable.set(1)
                    else: widget.variable.set(0)
                elif nodetype == "radio":
                    nodevalue = self.get_node_attribute(formelement, "value")
                    if self.get_node_attribute(formelement, "checked", "false") != "false": 
                        widget.variable.set(nodevalue)
                else:
                    nodevalue = self.get_node_attribute(formelement, "value")
                    widget.set(nodevalue)

    def _handle_form_submission(self, node, event=None):
        "Submit HTML forms."
        if (node not in self.form_nodes) or (not self.forms_enabled):
            return

        data = []
        form = self.form_nodes[node]
        action = self.get_node_attribute(form, "action")
        method = self.get_node_attribute(form, "method", "GET").upper()

        for formelement in self.loaded_forms[form]:
            nodeattrname = self.get_node_attribute(formelement, "name")
            if nodeattrname:
                if formelement in self.form_widgets:
                    nodevalue = self.form_widgets[formelement].get()
                elif self.get_node_tag(formelement) == "hidden":
                    nodevalue = self.get_node_attribute(formelement, "value")
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

        self.post_message(f"A form was submitted to {shorten(url)}")
        self.on_form_submit(url, data, method)

    def _handle_overflow_property(self, overflow, overflow_function):
        if overflow != "visible": # visible is the Tkhtml default, so it's largely meaningless
            overflow_map = {"hidden": 0,
                            "auto": 2,
                            "scroll": 1,
                            "clip": 0}
            if overflow in overflow_map:
                overflow = overflow_map[overflow]
                return overflow_function(overflow)
        return None

    def _set_overflow(self, node):
        "Look for and handle the overflow property."
        # Eventually we'll make overflow a composite property of overflow-x and overflow-y
        # But for now it's its own thing and the only one of the three that is actually respected by Tkhtml in rendering
        if self.experimental: 
            overflow_options = ("overflow", "overflow-y")
            overflow = self.get_node_property(node, "overflow-x") 
            self._handle_overflow_property(overflow, self.manage_hsb_func)
        else:
            overflow_options = ("overflow",)
            
        for overflow_type in overflow_options:
            overflow = self.get_node_property(node, overflow_type) 
            overflow = self._handle_overflow_property(overflow, self.manage_vsb_func)
            if overflow != None:
                self.vsb_type = overflow
                break
        
        overflow = self.get_node_attribute(node, BUILTIN_ATTRIBUTES["overflow-x"]) # Tkhtml doesn't support overflow-x
        overflow = self._handle_overflow_property(overflow, self.manage_hsb_func)

        background = self.get_node_property(node, "background-color")
        if background != "transparent" and self.motion_frame_bg != background: # transparent is the Tkhtml default, so it's largely meaningless
            self.motion_frame_bg = background
            self.motion_frame.config(bg=background)

    def _set_cursor(self, cursor):
        "Set the document cursor."
        if self.current_cursor != cursor:
            cursor = CURSOR_MAP[cursor]
            try:
                self.master.config(cursor=cursor, _override=True)
            except tk.TclError:
                self.master.config(cursor=cursor)
            self.current_cursor = cursor
            # I've noticed that the cursor won't always update when the binding is tied to a different widget than the one we are changing the cursor of
            # however, the html widget doesn't support the cursor property so there's not much we can do about this
            # update_idletasks() or update() have no effect, but print() and updating the color or text of another widget does
            # therefore we update the background color of a tiny frame that is barely visible to match the background color of the page whenever we need to change te cursor
            # it's wierd but hey, it works
            self.motion_frame.config(bg=self.motion_frame_bg)

    def _submit_element_js(self, node_handle, attribute):
        if self._javascript_enabled:
            if attribute == "onload":
                if node_handle in self.loaded_elements:
                    # don't run the onload script twice
                    return
                else:
                    self.loaded_elements.append(node_handle)
            mouse = self.get_node_attribute(node_handle, attribute)
            if mouse:
                self.on_element_script(node_handle, attribute, mouse)

    def _handle_recursive_hovering(self, node_handle, prev_hovered_nodes):
        "Set hover flags on the parents of the hovered element."
        self.hovered_nodes.append(node_handle)

        if node_handle not in prev_hovered_nodes:
            self.set_node_flags(node_handle, "hover")

            self._submit_element_js(node_handle, "onmouseover")
        
        self._submit_element_js(node_handle, "onmousemove")

        parent = self.get_current_node_parent(node_handle)
        if parent:
            self._handle_recursive_hovering(parent, prev_hovered_nodes)            

    def _create_iframe(self, node, url, html=None, vertical_scrollbar="auto"):
        if self.embed_obj:
            widgetid = self.embed_obj(self,
                messages_enabled=self.messages_enabled,
                overflow_scroll_frame=self,
                stylesheets_enabled = self.stylesheets_enabled,
                images_enabled = self.images_enabled,
                forms_enabled = self.forms_enabled,
                objects_enabled = self.objects_enabled,
                ignore_invalid_images = self.ignore_invalid_images,
                crash_prevention_enabled = self.crash_prevention_enabled,
                dark_theme_enabled = self._dark_theme_enabled,
                image_inversion_enabled = self._image_inversion_enabled,
                caches_enabled = self._caches_enabled,
                image_alternate_text_enabled = self.image_alternate_text_enabled,
                selection_enabled = self.selection_enabled,
                find_match_highlight_color = self.find_match_highlight_color,
                find_match_text_color = self.find_match_text_color,
                find_current_highlight_color = self.find_current_highlight_color,
                find_current_text_color = self.find_current_text_color,
                selected_text_highlight_color = self.selected_text_highlight_color,
                selected_text_color = self.selected_text_color,
                visited_links = self.visited_links,
                insecure_https = self.insecure_https,
            )

            if html:
                widgetid.load_html(html, url)
            elif url:
                widgetid.load_url(url)

            self.loaded_iframes[node] = widgetid

            self.handle_node_replacement(
                node, widgetid, lambda widgetid=widgetid: self.handle_node_removal(widgetid)
            )
        else:
            self.post_message(f"WARNING: the embedded page {url} could not be shown because no embed widget was provided.")

    def _on_right_click(self, event):
        if not self._javascript_enabled:
            return
        for node_handle in self.hovered_nodes:
            self._submit_element_js(node_handle, "onmousedown")
            self._submit_element_js(node_handle, "oncontextmenu")

    def _on_middle_click(self, event):
        if not self._javascript_enabled:
            return
        for node_handle in self.hovered_nodes:
            self._submit_element_js(node_handle, "onmousedown")
    
    def _on_click(self, event, redirected=False):
        "Set active element flags."
        if not self.current_node:
            # register current node if mouse has never moved
            self._on_mouse_motion(event)

        if not redirected:
            self.selection_type = 0

        self.focus_set()
        self.tag("delete", "selection")

        if self._javascript_enabled:
            for node_handle in self.hovered_nodes:
                self._submit_element_js(node_handle, "onmousedown")

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

    def _on_leave(self, event):
        "Reset cursor and node state when leaving this widget"
        self._set_cursor("default")
        if self.stylesheets_enabled:
            for node in self.hovered_nodes:
                try:
                    self.remove_node_flags(node, "hover")
                    self.remove_node_flags(node, "active")
                except tk.TclError:
                    pass
        self.hovered_nodes = []
        self.current_node = None

    def _on_mouse_motion(self, event):
        "Set hover flags and handle the CSS 'cursor' property."
        if self.is_selecting:
            return
        if self.on_embedded_node:
            node_handle = self.on_embedded_node
        else:
            node_handle = self.get_current_node(event)
            if not node_handle:
                self._on_leave(None)
                return
        try:
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
                        self._set_cursor(cursor)
                    elif is_text_node:
                        self._set_cursor("text")
                    else:
                        self._set_cursor("default")

                    prev_hovered_nodes = set(self.hovered_nodes)
                    self.hovered_nodes = []

                    self._submit_element_js(node_handle, "onmouseenter")

                    self._handle_recursive_hovering(
                        node_handle, prev_hovered_nodes
                    )

                    for node in prev_hovered_nodes - set(self.hovered_nodes):
                        self.remove_node_flags(node, "hover")

                        self._submit_element_js(node_handle, "onmouseout")
                        if node == old_handle:
                            self._submit_element_js(node_handle, "onmouseleave")

        except tk.TclError:
            # sometimes errors are thrown if the mouse is moving while the page is loading
            pass

    def _on_click_release(self, event):
        "Handle click releases on hyperlinks and form elements."
        if self.is_selecting:
            self.is_selecting = False
            self.current_node = None
            self._on_mouse_motion(event)
            return
        
        if self._javascript_enabled:
            for node_handle in self.hovered_nodes:
                self._submit_element_js(node_handle, "onmouseup")
                self._submit_element_js(node_handle, "onclick")

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
                if node_tag == "input" and node_type == "reset":
                    self._handle_form_reset(node_handle)
                elif node_tag == "input" and node_type in {"submit", "image"}:
                    self._handle_form_submission(node_handle)
                else:
                    for node in self.hovered_nodes:
                        if node != node_handle:
                            node_tag = self.get_node_tag(node).lower()
                        if node_tag == "a":
                            self.set_node_flags(node, "visited")
                            self._handle_link_click(node)
                            break
                        elif node_tag == "button":
                            if node != node_handle:
                                node_type = self.get_node_attribute(node, "type").lower()
                            if node_type == "submit":
                                self._handle_form_submission(node)
                                break
        except tk.TclError:
            pass

        self.prev_active_node = None

    def _word_in_node(self, node, offset):
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

    def _on_double_click(self, event):
        "Cycle between normal selection, text selection, and element selection on multi-clicks."
        self._on_click(event, True)

        if self._javascript_enabled:
            for node_handle in self.hovered_nodes:
                self._submit_element_js(node_handle, "ondblclick")

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
                start_offset, end_offset = self._word_in_node(self.selection_start_node, self.selection_start_offset)
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
            self._set_cursor("default")

    def _extend_selection(self, event):
        "Alter selection and HTML element states based on mouse movement."
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
                start_offset, end_offset = self._word_in_node(self.selection_start_node, self.selection_start_offset)
                start_offset2, end_offset2 = self._word_in_node(self.selection_end_node, self.selection_end_offset)
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
                    self._set_cursor("text")
                    if self.stylesheets_enabled:
                        self.remove_node_flags(self.prev_active_node, "active")
                        for node in self.hovered_nodes:
                            self.remove_node_flags(node, "hover")
                    self.prev_active_node = None
                    self.hovered_nodes = []
        except tk.TclError:
            self._set_cursor("default")

    def _on_embedded_mouse_motion(self, event, node_handle):
        self.on_embedded_node = node_handle
        self._on_mouse_motion(event)

    def _add_bindtags(self, widgetid, allowscrolling=True):
        "Add bindtags to allow scrolling and on_embedded_mouse function calls."
        if allowscrolling:
            tags = (
                self.node_tag,
                self.scrollable_node_tag,
            )
        else:
            tags = (self.node_tag,)
        widgetid.bindtags(widgetid.bindtags() + tags)

    def __call__(self):
        "Mark this class as callable so it is accepted as a overflow_scroll_frame by HtmlFrame."
