"""
The core Python bindings to Tkhtml3

Copyright (c) 2021-2025 Andrew Clarke
"""

from re import IGNORECASE, MULTILINE, split, sub, finditer

from urllib.parse import urlencode, urljoin, urlparse

from queue import Queue, Empty

import tkinter as tk
from . import imageutils, extensions, utilities, subwidgets

import tkinterweb_tkhtml


class TkinterWeb(tk.Widget):
    """Bindings for the Tkhtml3 HTML widget.
    
    This object provides the low-level widget that bridges the gap between the underlying Tkhtml3 widget and Tkinter. 

    **Do not use this widget on its own unless absolutely nessessary.** Instead use the :class:`~tkinterweb.HtmlFrame` widget.

    This widget can be accessed through the :attr:`~tkinterweb.HtmlFrame.html` property of the :class:`~tkinterweb.HtmlFrame` and :class:`~tkinterweb.HtmlLabel` widgets to access underlying settings and commands that are not a part of the :class:`~tkinterweb.HtmlFrame` API."""

    def __init__(self, master, tkinterweb_options=None, **kwargs):
        self.master = master
        tkinterweb_options = tkinterweb_options.copy()

        # Setup most variables
        self._setup_status_variables()

        # These settings require the widget to be loaded, so we handle them later
        if "dark_theme_enabled" in tkinterweb_options:
            self._dark_theme_enabled = tkinterweb_options.pop("dark_theme_enabled")

        if "caches_enabled" in tkinterweb_options:
            self._caches_enabled = tkinterweb_options.pop("caches_enabled")

        if "threading_enabled" in tkinterweb_options:
            self._threading_enabled = tkinterweb_options.pop("threading_enabled")

        # Setup the settings variables
        self._setup_settings(tkinterweb_options)

        # Register image loading infrastructure
        if "imagecmd" not in kwargs:
            kwargs["imagecmd"] = master.register(self._on_image_cmd)

        # Get Tkhtml folder and register crash handling
        # Not supported by standard Tkhtml releases
        if "drawcleanupcrashcmd" not in kwargs and self.use_prebuilt_tkhtml:
                kwargs["drawcleanupcrashcmd"] = master.register(self._on_draw_cleanup_crash_cmd)

        # Log everything
        # if "logcmd" not in kwargs:
        #    kwargs["logcmd"] = tkhtml_notifier

        # Set the default style if needed
        if "defaultstyle" not in kwargs:
            if self._dark_theme_enabled:
                self.post_message("WARNING: dark theme is enabled. This feature may cause hangs or crashes on some pages.")
            if self._dark_theme_enabled and self.dark_style:
                kwargs["defaultstyle"] = self.default_style + self.dark_style
            elif self.default_style:
                kwargs["defaultstyle"] = self.default_style

        # Provide OS information for troubleshooting
        self.post_message(f"Starting TkinterWeb for {utilities.PLATFORM.processor} {utilities.PLATFORM.system} with Python {'.'.join(utilities.PYTHON_VERSION)}")

        # Load and initialize the Tkhtml3 widget
        self._load_tkhtml()
        tk.Widget.__init__(self, master, "html", kwargs)

        # Setup threading settings
        try:
            self.allow_threading = bool(self.tk.call("set", "tcl_platform(threaded)"))
        except tk.TclError:
            self.allow_threading = True

        # Set remaining settings
        self.caches_enabled = self._caches_enabled
        self.threading_enabled = self._threading_enabled

        # Create a tiny, blank frame for cursor updating
        self.motion_frame = tk.Frame(self, bg=self.motion_frame_bg, width=1, height=1)
        self.motion_frame.place(x=0, y=0)

        # Setup bindings and node handlers
        self._setup_bindings()
        self._setup_handlers()
        
        self.post_message(f"""Welcome to TkinterWeb!
                                
The API changed in version 4. See https://tkinterweb.readthedocs.io/ for details.

Debugging messages are enabled. Use the parameter `messages_enabled = False` when calling HtmlFrame() or HtmlLabel() to disable these messages.
                                
Load about:tkinterweb for debugging information.
                                
If you benefited from using this package, please consider supporting its development by donating at https://buymeacoffee.com/andereoo - any amount helps!""")
        
        if not tkinterweb_tkhtml.TKHTML_EXTRAS_ROOT_DIR:
            self.post_message("The tkinterweb-tkhtml-extras package is either not installed or does not support your system. Some functionality may be missing.")


    def _setup_settings(self, options):
        "Widget settings."
        settings = {
            "messages_enabled": True,
            "stylesheets_enabled": True,
            "events_enabled": True,
            "images_enabled": True,
            "forms_enabled": True,
            "objects_enabled": True,
            "ignore_invalid_images": True,
            "image_alternate_text_enabled": True,
            "overflow_scroll_frame": None,
            "default_style": "",
            "dark_style": "",

            "use_prebuilt_tkhtml": True,
            "tkhtml_version": "",
            "experimental": False,

            "find_match_highlight_color": "#ef0fff",
            "find_match_text_color": "#fff",
            "find_current_highlight_color": "#38d878",
            "find_current_text_color": "#fff",
            "selected_text_highlight_color": "#3584e4",
            "selected_text_color": "#fff",
            "visited_links": [],

            "image_alternate_text_font": utilities.get_alt_font(),
            "image_alternate_text_size": 14,
            "image_alternate_text_threshold": 10,

            "maximum_thread_count": 20,

            "queue": None,
            "queue_delay": 50,
            "queue_after": None,

            "embed_obj": None,
            "manage_vsb_func": utilities.placeholder,
            "manage_hsb_func": utilities.placeholder,
            "on_link_click": utilities.placeholder,
            "on_form_submit": utilities.placeholder,
            "message_func": utilities.placeholder,
            "on_script": utilities.placeholder,
            "on_element_script": utilities.placeholder,
            "on_resource_setup": utilities.placeholder,

            "insecure_https": False,
            "ssl_cafile": None,
            "request_timeout": 15,
            "headers": {},
            "dark_theme_limit": 280,
            "style_dark_theme_regex": r"([^:;\s{]+)\s?:\s?([^;{!]+)(?=!|;|})",
            "general_dark_theme_regexes": [
                r'(<[^>]+bgcolor=")([^"]*)',
                r'(<[^>]+text=")([^"]*)',
                r'(<[^>]+link=")([^"]*)'
            ],
            "inline_dark_theme_regexes": [
                r'(<[^>]+style=")([^"]*)',
                r'([a-zA-Z-]+:)([^;]*)'
            ],
            "radiobutton_token": "TKWtsvLKac1",

            "node_tag": f"tkinterweb.{id(self)}.nodes",
            "tkinterweb_tag": f"tkinterweb.{id(self)}.tkinterweb",
            "scrollable_node_tag": f"tkinterweb.{id(self)}.scrollablenodes",
            "widget_container_attr": "-tkinterweb-widget-container",
        }
        settings.update(options)
        for key, value in settings.items():
            setattr(self, key, value)

    def _setup_status_variables(self):
        "Widget status variables."
        self.base_url = ""
        self.title = ""
        self.icon = ""

        self.fragment = ""
        self.style_count = 0
        self.active_threads = []
        self.loaded_images = {}
        self.loaded_image_counter = 0
        self.image_directory = {}
        self.image_name_prefix = f"_tkinterweb_img_{id(self)}_"
        self.downloads_have_occured = False
        self.pending_scripts = []
        self.unstoppable = True
        self.on_embedded_node = None
        self.selection_start_node = None
        self.selection_start_offset = None
        self.selection_end_node = None
        self.selection_end_offset = None
        self.current_active_node = None
        self.current_hovered_node = None
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

        self._caches_enabled = True
        self._threading_enabled = True
        self._dark_theme_enabled = False
        self._image_inversion_enabled = False
        self._crash_prevention_enabled = True
        self._javascript_enabled = False
        self._caret_browsing_enabled = False
        self._selection_enabled = True

        # TODO: split the TkinterWeb class into more manager objects
        self._caret_manager_cache = None
        self._event_manager_cache = None

    def _setup_bindings(self):
        "Widget bindtags and bindings."
        self._add_bindtags(self, False, True)

        self.bind_class(self.node_tag, "<Motion>", self._on_mouse_motion, True)
        self.bind_class(self.node_tag, "<FocusIn>", self._on_focusout, True)

        self.bind_class(self.tkinterweb_tag, "<<Copy>>", self.copy_selection, True)
        self.bind_class(self.tkinterweb_tag, "<B1-Motion>", self._extend_selection, True)
        self.bind_class(self.tkinterweb_tag, "<Button-1>", self._on_click, True)
        self.bind_class(self.tkinterweb_tag, "<Button-2>", self._on_middle_click, True)
        self.bind_class(self.tkinterweb_tag, "<Button-3>", self._on_right_click, True)
        self.bind_class(self.tkinterweb_tag, "<Double-Button-1>", self._on_double_click, True)
        self.bind_class(self.tkinterweb_tag, "<ButtonRelease-1>", self._on_click_release, True)
        self.bind_class(self.tkinterweb_tag, "<Destroy>", self._on_destroy)

        for i in {"<Left>", "Control-Left>", "Control-Shift-Left>", "<KP_Left>", "<Control-KP_Left>", "<Control-Shift-KP_Left>", 
                "<Right>", "Control-Right>", "Control-Shift-Right>", "<KP_Right>", "<Control-KP_Right>", "<Control-Shift-KP_Right>",
                "<Up>", "Control-Up>", "Control-Shift-Up>", "<KP_Up>", "<Control-KP_Up>", "<Control-Shift-KP_Up>", 
                "<Down>", "Control-Down>", "Control-Shift-Down>", "<KP_Down>", "<Control-KP_Down>", "<Control-Shift-KP_Down>",
                "<Prior>", "<KP_Prior>", "<Next>", "<KP_Next>", "<Home>", "<KP_Home>", "<End>", "<KP_End>", "<FocusOut>", "<FocusIn>"}:
            method = "_on_" + i.strip("<>").split("-")[-1].split("_")[-1].lower()
            # We use bind and not bind_class here because users may want to override these bindings
            try:
                self.bind(i, getattr(self, method))
            except tk.TclError:
                # KP_ bindings don't work on MacOS
                pass

    def _on_destroy(self, event):
        self._end_queue()
        self.stop()

    def _setup_handlers(self):
        "Register node handlers."
        self.register_handler("script", "script", self._on_script)
        self.register_handler("script", "style", self._on_style)
        self.register_handler("node", "link", self._on_link)
        self.register_handler("node", "title", self._on_title)
        self.register_handler("node", "a", self._on_a)
        self.register_handler("node", "base", self._on_base)
        self.register_handler("node", "meta", self._on_meta)
        self.register_handler("node", "input", self._on_input)
        self.register_handler("node", "textarea", self._on_textarea)
        self.register_handler("node", "select", self._on_select)
        self.register_handler("node", "form", self._on_form)
        self.register_handler("node", "object", self._on_object)
        self.register_handler("node", "iframe", self._on_iframe)
        self.register_handler("node", "table", self._on_table)
        self.register_handler("node", "img", self._on_image)

        # Node handlers don't work on body and html elements. 
        # These elements also cannot be removed without causing a segfault in vanilla Tkhtml. 
        # Weird.
        self.register_handler("parse", "body", self._on_body)
        self.register_handler("parse", "html", self._on_body)

        self.register_handler("attribute", "input", self._on_input_value_change)
        self.register_handler("attribute", "select", self._on_input_value_change)
        self.register_handler("attribute", "a", self._on_a_value_change)
        self.register_handler("attribute", "object", self._on_object_value_change)
        self.register_handler("attribute", "iframe", self._on_iframe_value_change)
        self.register_handler("attribute", "img", self._on_image_value_change)

    def _check_queue(self):
        try:
            while True:
                msg = self.queue.get_nowait()
                msg()
        except Empty:
            pass
        self.queue_after = self.after(self.queue_delay, self._check_queue)

    def _end_queue(self):
        if self.queue_after:
            self.after_cancel(self.queue_after)
            self.queue_after = None
        self.queue = None

    @property
    def caret_manager(self):
        """The widget's corresponding caret manager.
        
        :rtype: :class:`~tkinterweb.extensions.CaretManager`
        
        New in version 4.8."""
        if self._caret_manager_cache is None:
            self._caret_manager_cache = extensions.CaretManager(self)
        return self._caret_manager_cache
    
    @property
    def event_manager(self):
        """The widget's corresponding event manager.
        
        :rtype: :class:`~tkinterweb.extensions.EventManager`
        
        New in version 4.10."""
        if self._event_manager_cache is None:
            self._event_manager_cache = extensions.EventManager(self)
        return self._event_manager_cache

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
                self.post_message("WARNING: JavaScript support is enabled. This feature is a work in progress. Only enable JavaScript support on documents you know and trust.")

    @property
    def crash_prevention_enabled(self):
        return self._crash_prevention_enabled
    
    @crash_prevention_enabled.setter
    def crash_prevention_enabled(self, enabled):
        "Warn the user when disabling crash prevention."
        if self._crash_prevention_enabled != enabled:
            self._crash_prevention_enabled = enabled
            if not enabled:
                self.post_message("WARNING: crash prevention is disabled. You may encounter segmentation faults on some pages.")
    
    @property
    def dark_theme_enabled(self):
        return self._dark_theme_enabled
    
    @dark_theme_enabled.setter
    def dark_theme_enabled(self, enabled):
        "Warn the user when enabling dark mode."
        if self._dark_theme_enabled != enabled:
            self._dark_theme_enabled = enabled    
            if enabled:
                self.post_message("WARNING: dark theme is enabled. This feature may cause hangs or crashes on some pages.")
            if enabled and self.dark_style:
                self.config(defaultstyle=self.default_style + self.dark_style)
            elif self.default_style:
                self.config(defaultstyle=self.default_style)

    @property
    def image_inversion_enabled(self):
        return self._image_inversion_enabled
    
    @image_inversion_enabled.setter
    def image_inversion_enabled(self, enabled):
        "Warn the user when enabling image inversion."
        if self._image_inversion_enabled != enabled:
            self._image_inversion_enabled = enabled
            if enabled:
                self.post_message("WARNING: image inversion is enabled. This feature may cause hangs or crashes on some pages.")

    @property
    def threading_enabled(self):
        return self._threading_enabled
    
    @threading_enabled.setter
    def threading_enabled(self, enabled):
        "Warn the user when disabling threading and ensure that threading is disabled if Tcl/Tk is not built with thread support."
        if self.allow_threading:
            self._threading_enabled = enabled
            if enabled:
                # Initialize the queue
                # The queue evaluates Tcl/Tk commands running in a thread
                # The queue will start or stop when self.maximum_thread_count is set
                if not self.queue:
                    self.queue = Queue()
                self._check_queue()
            else:
                self.post_message("WARNING: threading is disabled. Your app may hang while loading webpages.")
                self._end_queue()
        else:
            self._threading_enabled = False
            self.post_message("WARNING: threading is disabled because your Tcl/Tk library does not support threading. Your app may hang while loading webpages.")
            self._end_queue()

    @property
    def caret_browsing_enabled(self):
        return self._caret_browsing_enabled
    
    @caret_browsing_enabled.setter
    def caret_browsing_enabled(self, enabled):
        "Enable or disable caret browsing."
        self._caret_browsing_enabled = enabled
        if not enabled and self._caret_manager_cache:
            self.caret_manager.reset()

    @property
    def selection_enabled(self):
        return self._selection_enabled
    
    @selection_enabled.setter
    def selection_enabled(self, enabled):
        "Enable or disable text selection."
        self._selection_enabled = enabled
        if not enabled and self.selection_start_node:
            self.clear_selection()

    @property
    def tkhtml_default_style(self):
        return self.tk.call("::tkhtml::htmlstyle")
    
    def post_to_queue(self, callback):
        """Use this method to send a callback to TkinterWeb's thread-safety queue. The callback will be evaluated on the main thread.
        Use this when running Tkinter commands from within a thread. 
        If the queue is not running (i.e. threading is disabled), the callback will be evaluated immediately.
        
        New in version 4.9."""
        if self.queue:
            self.queue.put(callback)
        else:
            callback()

    def post_event(self, event, thread_safe=False):
        "Generate a virtual event."
        # NOTE: when thread_safe=True, this method is thread-safe

        if thread_safe and self.queue:
            self.post_to_queue(lambda event=event: self._post_event(event))
        else:
            self._post_event(event)

    def _post_event(self, event):
        "Generate a virtual event."
        if self.events_enabled: # and self.unstoppable
            try:
                self.event_generate(event)
            except tk.TclError:
                # The widget doesn't exist anymore
                pass

    def post_message(self, message, thread_safe=False):
        "Post a message."
        # NOTE: when thread_safe=True, this method is thread-safe

        if thread_safe and self.queue:
            self.post_to_queue(lambda message=message: self._post_message(message))
        else:
            self._post_message(message)

    def _post_message(self, message):
        "Post a message."
        if self.overflow_scroll_frame:
            message = "[EMBEDDED DOCUMENT] " + message
        if self.messages_enabled:
            self.message_func(message)

    def parse(self, html, thread_safe=False):
        "Parse HTML code."
        # NOTE: when thread_safe=True, this method is thread-safe

        self.downloads_have_occured = False
        self.unstoppable = True
        html = self._crash_prevention(html)
        html = self._dark_mode(html)

        # By default Tkhtml won't display plain text
        if "<" not in html and ">" not in html:
            html = f"<p>{html}</p>"

        # Send the HTML code to the queue if needed
        # Otherwise, evaluate directly so that the document can be manipulated as soon as parse() returns
        if thread_safe:
            self.post_to_queue(lambda html=html: self._parse(html))
        else:
            self._parse(html)
    
    def _parse(self, html):
        "Parse HTML code."
        # NOTE: this must run in the main thread

        self.tk.call(self._w, "parse", html)
        self.post_event(utilities.DOM_CONTENT_LOADED_EVENT)

        # We assume that if no downloads have been made by now the document has finished loading, so we send the done loading signal
        if not self.downloads_have_occured:
            self._handle_load_finish()
        else:
            # Scroll to the fragment if given but do not issue a done loading event
            self._handle_load_finish(False)

        self._submit_deferred_scripts()
        self.send_onload()

    def send_onload(self, root=None, children=None):
        """Send the onload signal for nodes that aren't handled at runtime.
        We keep this a seperate command so that it can be run after inserting elements or changing the innerHTML.
        
        New in version 4.1."""
        # Don't bother worring about element bindings...they can't be set if the element doesn't exist
        if not self._javascript_enabled:
            return
        if children:
            for node in children:
                if self.get_node_tag(node) not in {"img", "object", "link"}:
                    self._post_element_event(node, "onload")
        else:
            for node in self.search("[onload]", root=root):
                if self.get_node_tag(node) not in {"img", "object", "link"}:
                    self._post_element_event(node, "onload")
                

    def parse_css(self, sheetid=None, data="", url=None, override=False):
        "Parse CSS code."
        if not url:
            url = self.base_url
        data = self._crash_prevention(data)
        if self._dark_theme_enabled:
            data = sub(self.style_dark_theme_regex, lambda match, matchtype=0: self._generate_altered_colour(match, matchtype), data)
        try:
            # urlcmd = self.register(self.resolve_url)
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
            # The widget doesn't exist anymore
            pass

    def reset(self, thread_safe=False):
        "Reset the widget."
        # NOTE: when thread_safe=True, this method is thread-safe. Imagine that!

        self.stop()
        self.image_directory = {}
        self.form_get_commands = {}
        self.form_nodes = {}
        self.form_widgets = {}
        self.loaded_forms = {}
        self.waiting_forms = 0
        self.radio_buttons = {}
        self.loaded_iframes = {}
        self.loaded_elements = []
        self.title = ""
        self.icon = ""
        self.fragment = ""
        
        if self._event_manager_cache:
            self._event_manager_cache.reset()

        if thread_safe:
            self.post_to_queue(self._reset)
        else:
            self._reset()

    def _reset(self):
        # NOTE: this must run in the main thread
        
        self.vsb_type = self.manage_vsb_func()
        self.manage_hsb_func()

        # Note to self: these need to be here
        # Or very strange errors will magically appear,
        # Usually when switching between pages quickly
        self.selection_start_node = None
        self.selection_end_node = None
        self.on_embedded_node = None
        self.hovered_nodes = []
        self.current_hovered_node = None

        self._set_cursor("default")
        self.tk.call(self._w, "reset")
        if self._caret_browsing_enabled:
            self.caret_manager.reset()

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

    def search(self, selector, *a, cnf={}, **kw):
        """Search the document for the specified CSS selector; return a Tkhtml3 node if found."""
        return self.tk.call((self._w, "search", selector)+utilities.TclOpt(a)+self._options(cnf, kw))

    def xview(self, *args, auto_scroll=False):
        "Used to control horizontal scrolling."
        #if args:
        #    return self.tk.call(self._w, "xview", *args)
        #coords = map(float, self.tk.call(self._w, "xview").split()) #raises an error
        #return tuple(coords)
        xview = self.tk.call(self._w, "xview", *args)
        if args and self._caret_browsing_enabled:
            self.caret_manager.update(auto_scroll=auto_scroll)
        return xview

    def xview_scroll(self, number, what, auto_scroll=False):
        """Shifts the view in the window left or right, according to number and what.
        "number" is an integer, and "what" is either "units" or "pages"."""
        return self.xview("scroll", number, what, auto_scroll=auto_scroll)

    def xview_moveto(self, number, auto_scroll=False):
        "Shifts the view horizontally to the specified position"
        return self.xview("moveto", number, auto_scroll=auto_scroll)

    def yview(self, *args, auto_scroll=False):
        """Used to control vertical scrolling."""
        yview = self.tk.call(self._w, "yview", *args)
        if args and self._caret_browsing_enabled:
            self.caret_manager.update(auto_scroll=auto_scroll)
        return yview

    def yview_scroll(self, number, what, auto_scroll=False):
        """Shifts the view in the window left or right, according to number and what.
        "number" is an integer, and "what" is either "units" or "pages"."""
        return self.yview("scroll", number, what, auto_scroll=auto_scroll)

    def yview_moveto(self, number, auto_scroll=False):
        "Moves the view vertically to the specified position."
        return self.yview("moveto", number, auto_scroll=auto_scroll)

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
            self.post_event(utilities.DONE_LOADING_EVENT)
        self._submit_deferred_scripts()
        return fragment
    
    def enable_imagecache(self, enabled):
        "Enable or disable the Tkhtml imagecache."
        self.tk.call(self._w, "configure", "-imagecache", enabled)

    def get_node_text(self, node_handle, *args):
        "Get the text content of the given node."
        return self.tk.call(node_handle, "text", *utilities.TclOpt(args))

    def set_node_text(self, node_handle, new):
        "Set the text content of the given node."
        self.tk.call(node_handle, "text", "set", new)
        self.tk.call(self._w, "_relayout") # needed for pathName text text to return the updated string

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
        if value:  # Backwards compatability
            return self.tk.call(node_handle, "attribute", attribute, value)
        else:
            return self.tk.call(node_handle, "attribute", "-default", default, attribute)

    def set_node_attribute(self, node_handle, attribute, value):
        "Set the specified attribute of the given node."
        return self.tk.call(node_handle, "attribute", attribute, value)

    def get_node_attributes(self, node_handle):
        "Get the attributes of the given node."
        attr = self.tk.call(node_handle, "attribute")
        return dict(zip(attr[0::2], attr[1::2]))

    def get_node_property(self, node_handle, node_property, *args):
        "Get the specified CSS property of the given node."
        return self.tk.call(node_handle, "property", *utilities.TclOpt(args), node_property)

    def get_node_properties(self, node_handle, *args):
        "Get the CSS properties of the given node."
        prop = self.tk.call(node_handle, "property", *utilities.TclOpt(args))
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
    
    def replace_node_contents(self, node_handle, contents, *args):
        """Fill a node with either a Tk widget or with Tkhtml nodes.
        
        New in version 4.2."""
        if not contents:
            # Calling replace on an empty node causes Tkhtml to segfault
            contents = self.tk.call(self._w, "fragment", " ")
        return self.tk.call(node_handle, "replace", contents, *args)

    def delete_node(self, node_handle):
        "Delete the given node."
        if self.experimental:
            node_parent = self.get_node_parent(node_handle)
            if node_parent:
                self.tk.call(node_parent, "remove", node_handle)
            else:
                raise RuntimeError(f"root elements cannot be removed")
        else:
            node_parent = self.get_node_parent(node_handle)
            node_tag = self.get_node_tag(node_handle)
            # Removing the body element causes a segfault
            if node_parent:
                if node_tag != "body":
                    self.tk.call(node_parent, "remove", node_handle)
                else:
                    raise RuntimeError(f"{node_tag} elements cannot be removed")
            elif node_tag:
                raise RuntimeError(f"{node_tag} elements cannot be removed")
            else:
                raise RuntimeError(f"element is invalid or has already been removed")

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
        "Get the path name of node."
        return self.tk.call(node_handle, "html")

    def get_node_stacking(self, node_handle):
        """Return the node-handle that forms the stacking context this node is located in.
        Return "" for the root-element or any element that is part of an orphan subtree.
        
        New in version 4.2."""
        return self.tk.call(node_handle, "stacking")

    def get_current_hovered_node(self, event):
        "Get current node."
        return self.tk.eval(
            f"""set node [lindex [lindex [{self} node {event.x} {event.y}] end] end]"""
        )

    def get_current_hovered_node_parent(self, node):
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
        data = self.tk.call(name, "data")
        self.tk.call("image", "delete", name)
        return data

    def postscript(self, cnf={}, **kwargs):
        """Print the contents of the canvas to a postscript file.
        Valid options: colormap, colormode, file, fontmap, height, 
        pageanchor, pageheight, pagesize, pagewidth, pagex, pagey, 
        nobg, noimages, rotate, width, x, and y.
        Does not work unless experimental Tkhtml is used."""
        return self.tk.call((self._w, "postscript")+self._options(cnf, kwargs))

    def preload_image(self, url):
        """Preload an image for use later. 
        Only useful if caches are enabled and reset() is not called after preloading."""
        return self.tk.call(self._w, "preload", url)
    
    def get_computed_styles(self):
        "Get a tuple containing the computed CSS rules for each CSS selector."
        return self.tk.call(self._w, "_styleconfig")

    def override_node_CSS(self, node, *props):
        """Overrides the node's properties; if it is a text node, it overrides the parent's properties.
        
        New in version 4.4."""
        if not self.get_node_tag(node): node = self.get_node_parent(node)
        return self.override_node_properties(node, *props)

    def write(self, *arg, cnf={}, **kw):
        """Write directly to an open HTML document stream, may be used when parsing.
        
        New in version 4.4."""
        return self.tk.call(self._w, "write", *arg+self._options(cnf, kw))
    
    def allocate_image_name(self):
        """Get a unique image name. 
        
        New in version 4.9."""
        name = self.image_name_prefix + str(self.loaded_image_counter)
        self.loaded_image_counter += 1
        return name

    def fetch_scripts(self, attributes, url=None, data=None):
        "Fetch and run scripts"
        # NOTE: this method is thread-safe and is designed to run in a thread

        thread = self._begin_download()

        if url and thread.isrunning:
            self.post_message(f"Fetching script from {utilities.shorten(url)}", True)
            try:
                data = self._download_url(url)[0]
            except Exception as error:
                self.post_to_queue(lambda message=f"ERROR: could not load script {url}: {error}",
                               url=url: self._finish_resource_load(message, url, "script", False))

        if data and thread.isrunning:
            if "defer" in attributes:
                self.pending_scripts.append((attributes, data))
            else:
                self.post_to_queue(lambda attributes=attributes, data=data: self.on_script(attributes, data))
                
            if url:
                self.post_to_queue(lambda message=f"Successfully loaded {utilities.shorten(url)}", 
                               url=url: self._finish_resource_load(message, url, "script", True))

        self._finish_download(thread)

    def fetch_styles(self, node=None, url=None, data=None):
        "Fetch stylesheets and parse the CSS code they contain"
        # NOTE: this method is thread-safe and is designed to run in a thread

        thread = self._begin_download()

        if url and thread.isrunning:
            self.post_message(f"Fetching stylesheet from {utilities.shorten(url)}", True)
            try:
                data = sub(r"url\((.*?)\)", 
                           lambda match, url=url: self._fix_css_urls(match, url), 
                           self._download_url(url)[0]
                           )
            except Exception as error:
                self.post_to_queue(lambda message=f"ERROR: could not load stylesheet {url}: {error}",
                    url=url: self._finish_resource_load(message, url, "stylesheet", False))

        if data and thread.isrunning:
            self.post_to_queue(lambda node=node, url=url, data=data: self._finish_fetching_styles(node, url, data))
                    
        self._finish_download(thread)

    def _finish_fetching_styles(self, node, url, data):
        # NOTE: this must run in the main thread

        self.style_count += 1
        sheetid = "user." + str(self.style_count).zfill(4)

        self.parse_css(f"{sheetid}.9999", data, url)
        if node:
            self._post_element_event(node, "onload", None, utilities.ELEMENT_LOADED_EVENT)
        if url:
            self.post_message(f"Successfully loaded {utilities.shorten(url)}")
            self.on_resource_setup(url, "stylesheet", True)
    
    def _finish_resource_load(self, message, url, resource, success):
        # NOTE: this must run in the main thread

        self.post_message(message)
        self.on_resource_setup(url, resource, success)

    def fetch_objects(self, node, url):
        # NOTE: this method is thread-safe and is designed to run in a thread

        thread = self._begin_download()

        try:
            data, url, filetype, code = self._download_url(url)

            if data and filetype.startswith("image"):
                name = self.allocate_image_name()
                data, data_is_image = self.check_images(data, name, url, filetype)
                self.post_to_queue(lambda node=node, data=data, name=name, url=url, filetype=filetype, data_is_image=data_is_image: self._finish_fetching_image_objects(node, data, name, url, filetype, data_is_image))
            elif data and filetype == "text/html":
                self.post_to_queue(lambda node=node, data=data, name=name, url=url, filetype=filetype: self._finish_fetching_HTML_objects(node, data, name, url, filetype))

        except Exception as error:
            self.post_message(f"ERROR: could not load object element with data {url}: {error}", True)
        
        self._finish_download(thread)

    def _finish_fetching_image_objects(self, node, data, name, url, filetype, data_is_image):
        # NOTE: this must run in the main thread

        image = self.finish_fetching_images(None, data, name, filetype, url, data_is_image)
        self.override_node_properties(node, "-tkhtml-replacement-image", f"url({image})")
        self._post_element_event(node, "onload", None, utilities.ELEMENT_LOADED_EVENT)

    def _finish_fetching_HTML_objects(self, node, data, url, filetype):
        # NOTE: this must run in the main thread

        self._create_iframe(node, url, data)
        self._post_element_event(node, "onload", None, utilities.ELEMENT_LOADED_EVENT)

    def load_alt_text(self, url, name):
        # NOTE: this must run in the main thread

        if (url in self.image_directory):
            node = self.image_directory[url]
            if not self.ignore_invalid_images:
                image = imageutils.data_to_image(utilities.BROKEN_IMAGE, name, "image/png", self._image_inversion_enabled, self.dark_theme_limit)
            elif self.image_alternate_text_enabled:
                try:  # Ensure thread safety when closing
                    alt = self.get_node_attribute(node, "alt")
                    if alt:
                        ### Should work, but doesn't
                        #if self.experimental: 
                        #    # Insert the parsed fragment directly if in experimental mode
                        #    self.insert_node(node, self.parse_fragment(alt))
                        #else:

                        # Generate an image with alternate text if not in experimental mode
                        try:
                            image = imageutils.text_to_image(
                                name, alt, self.bbox(node),
                                self.image_alternate_text_font,
                                self.image_alternate_text_size,
                                self.image_alternate_text_threshold,
                            )
                        except (ImportError, ModuleNotFoundError,):
                            self.post_message(f"ERROR: could not display alternate text for the image {url}: PIL and PIL.ImageTk must be installed")
                            return
                    else:
                        return
                except (RuntimeError, tk.TclError): 
                    return  # Widget no longer exists
        elif not self.ignore_invalid_images:
            image = imageutils.data_to_image(utilities.BROKEN_IMAGE, name, "image/png", self._image_inversion_enabled, self.dark_theme_limit)
        else:
            return
        
        if name in self.loaded_images:
            self.loaded_images[name] = (self.loaded_images[name], image)
        else:
            self.loaded_images[name] = image

    def fetch_images(self, node, url, name):
        "Fetch images and display them in the document."
        # NOTE: this method is thread-safe and is designed to run in a thread

        thread = self._begin_download()

        self.post_message(f"Fetching image from {utilities.shorten(url)}", True)

        if url == self.base_url:
            self.post_to_queue(lambda url=url, name=name, error="ERROR: image url not specified": self._on_image_error(url, name, error))
        else:
            try:
                data, url, filetype, code = self._download_url(url)
                data, data_is_image = self.check_images(data, name, url, filetype)                
                    
                if thread.isrunning:
                    self.post_to_queue(lambda node=node, data=data, name=name, url=url, filetype=filetype, data_is_image=data_is_image: self.finish_fetching_images(node, data, name, url, filetype, data_is_image))
            except Exception as error:
                self.post_to_queue(lambda url=url, name=name, error=f"ERROR: {error}": self._on_image_error(url, name, error))

        self._finish_download(thread)

    def check_images(self, data, name, url, filetype):
        """Invert images if needed and convert SVG images to PNGs.
        
        New in version 4.9."""
        # NOTE: this method is thread-safe and is designed to run in a thread

        data_is_image = False
        if "svg" in filetype:
            try:
                data = imageutils.svg_to_png(data)
            except (ValueError, ImportError, ModuleNotFoundError,):
                raise RuntimeError(f"could not display the image {url}: either PyGObject, CairoSVG, or both PyCairo and Rsvg must be installed to parse .svg files.")
            
        if self._image_inversion_enabled:
            try:
                data = imageutils.invert_image(data, self.dark_theme_limit)
                data_is_image = True
            except (ImportError, ModuleNotFoundError,):
                error = f"ERROR: could not invert the image {url}: PIL and PIL.ImageTk must be installed."
                self.post_to_queue(lambda url=url, name=name, error=error: self._on_image_error(url, name, error))
            
        return data, data_is_image

    def finish_fetching_images(self, node, data, name, url, filetype, data_is_image=False):
        # NOTE: this must run in the main thread

        try:
            image = imageutils.data_to_image(data, name, filetype, data_is_image)
            
            self.post_message(f"Successfully loaded {utilities.shorten(url)}")
            self.on_resource_setup(url, "image", True)
            if node:
                self._post_element_event(node, "onload", None, utilities.ELEMENT_LOADED_EVENT)
            #if self.experimental:
            #    node = self.search(f'img[src="{url}"]')
            #    if node:
            #        if self.get_node_children(node): self.delete_node(self.get_node_children(node))
            if name in self.loaded_images:
                self.loaded_images[name] = (self.loaded_images[name], image)
            else:
                self.loaded_images[name] = image

            return image
        except (ImportError, ModuleNotFoundError,):
            error = f"ERROR: could not display image {url}: PIL and PIL.ImageTk must be installed"
            self._on_image_error(url, name, error)
        except Exception as error:
            self._on_image_error(url, name, f"ERROR: could not display image {url}: {error}")

    def _on_image_error(self, url, name, error):
        # NOTE: this must run in the main thread
        self.post_message(error)
        self.load_alt_text(url, name)
        self.on_resource_setup(url, "image", False)

    def handle_node_replacement(self, node, widgetid, deletecmd, stylecmd=None, allowscrolling=True, handledelete=True):
        "Replace a Tkhtml3 node with a Tkinter widget."
        if stylecmd:
            if handledelete:
                self.replace_node_contents(
                    node, widgetid,
                    "-deletecmd", self.register(deletecmd),
                    "-stylecmd", self.register(stylecmd),
                )
            else:
                self.replace_node_contents(
                    node, widgetid, "-stylecmd", self.register(stylecmd)
                )
        else:
            if handledelete:
                self.replace_node_contents(
                    node, widgetid, "-deletecmd", self.register(deletecmd)
                )
            else:
                self.replace_node_contents(node, widgetid)

        self._add_bindtags(widgetid, allowscrolling)
        for child in widgetid.winfo_children():
            self._add_bindtags(child, allowscrolling)
            
        widgetid.bind(
            "<Enter>",
            lambda event, node_handle=node: self._on_embedded_mouse_enter(
                event, node_handle=node_handle
            ),
        )
        widgetid.bind(
            "<Leave>",
            lambda event, node_handle=None: self._on_embedded_mouse_leave(
                event, node_handle=node_handle
            ),
        )

    def _handle_node_removal(self, widgetid):
        widgetid.destroy()

    def _handle_node_style(self, node, widgetid, widgettype="button"):
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
            widgetid.configure(background=bg)
        elif widgettype == "text":
            bg = self.get_node_property(node, "background-color")
            fg = self.get_node_property(node, "color")
            font = self.get_node_property(node, "font")
            if bg == "transparent":
                bg = "white"
            if fg == "transparent":
                fg = "white"
            widgetid.configure(background=bg)
            try:
                widgetid.configure(foreground=fg, font=font)
            except tk.TclError:
                pass
        elif widgettype == "auto":
            bg = self.get_node_property(node, "background-color")
            fg = self.get_node_property(node, "color")
            font = self.get_node_property(node, "font")
            if bg == "transparent":
                bg = "white"
            if fg == "transparent":
                fg = "white"
            widgets = [widgetid] + [widget for widget in widgetid.winfo_children()]
            for widget in widgets:
                widget.configure(background=bg)
                try:
                    widget.configure(foreground=fg, font=font)
                except tk.TclError:
                    pass

    def map_node(self, node, force=False):
        """Redraw a node if it currently contains a Tk widget.
        
        New in version 4.2."""
        if force or (self.get_node_attribute(node, self.widget_container_attr) != ""):
            self.set_node_attribute(node, self.widget_container_attr, "")
            self.replace_node_contents(node, node)

    def replace_node_with_widget(self, node, widgetid):
        """Replace a node with a Tk widget.
        
        New in version 4.2."""
        if not widgetid:
            # Reset the node if a widget is not supplied
            self.map_node(node)
            return
            
        manager = widgetid.winfo_manager()
        if manager == "Tkhtml":  # Don't display the same widget twice
            for old_node in self.search(f"[{self.widget_container_attr}]"):
                if self.get_node_attribute(old_node, self.widget_container_attr) == str(widgetid):
                    # If we know where the widget is, 
                    # Replace the old node with its original contents so we can redraw the widget here
                    self.map_node(old_node)
                    break
            else:
                raise tk.TclError(f"cannot embed widget already managed by {manager}")
        # Tkhtml seems to remove the widget from the previous geometry manager if it is not Tkhtml so I think we are fine

        handleremoval = self.get_node_attribute(node, "handleremoval", "false") != "false"

        # Handle scrolling
        # If set to "auto" (default), scrolling will work on the widget as long as no bindings are already set on it
        allowscrolling = self.get_node_attribute(node, "allowscrolling", "auto")
        if allowscrolling == "auto":
            widgets = [widgetid] + [widget for widget in widgetid.winfo_children()]
            allowscrolling = True
            events = ("<MouseWheel>", "<Button-4>", "<Button-5>")
            ignore = {".", "all"}
            def check_scrolling():
                for widget in widgets:
                    for tag in widget.bindtags():
                        if tag in ignore: continue
                        for event in events:
                            if widget.bind_class(tag, event):
                                return False
                return True
            allowscrolling = check_scrolling()
        elif allowscrolling in {"", "true"}:
            allowscrolling = True
        else:
            allowscrolling = False

        # Handle styling
        # If set to "false" (default), nothing will be done
        # If set to "deep", the widget and any children are styled
        # If set to "true" or "auto", only the widget will be styled
        allowstyling = self.get_node_attribute(node, "allowstyling", "false")
        if allowstyling == "deep":
            allowstyling = lambda node=node, widgetid=widgetid, widgettype="auto": self._handle_node_style(node, widgetid, widgettype)
        elif allowstyling in {"", "true", "auto"}:
            allowstyling = lambda node=node, widgetid=widgetid, widgettype="text": self._handle_node_style(node, widgetid, widgettype)
        else:
            allowstyling = None

        if handleremoval:
            # Tkhtml's -deletecmd handler is quite broken
            # I would instead give the widget an extra class and bind to <Unmap>
            # But apparently that doesn't fire at all. Oh well.
            handleremoval = lambda widgetid=widgetid: self._handle_node_removal(widgetid)
        else:
            handleremoval = None
        
        # We used to add the node to a dict but we need to be able to delete it when destroy is called on any of its parents
        # By setting an attribute we can use Tkhtml's search function to check if the widget exists elsewhere without having to invert a dict
        # I'll probably change that eventually
        self.set_node_attribute(node, self.widget_container_attr, widgetid)
        self.handle_node_replacement(
            node,
            widgetid,
            handleremoval,
            allowstyling,
            allowscrolling,
            False,
        )
        self._post_element_event(node, "onload", None, utilities.ELEMENT_LOADED_EVENT)

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
            # Find matches
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
                # Highlight matches
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

                # Scroll to node if selected match is not visible
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

    def get_child_text(self, node):
        """Get text of node and all its descendants recursively.
        
        New in version 4.4."""
        text = self.get_node_text(node, "-pre")
        for child in self.get_node_children(node):
            text += self.get_child_text(child)
        return text
    
    def resolve_url(self, url):
        "Generate a full url from the specified url."
        return urljoin(self.base_url, url)
    
    def update_tags(self):
        "Update selection and find tag colours."
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
        self.update_selection()

    def clear_selection(self):
        "Clear the current selection."
        self.tag("delete", "selection")
        self.selection_start_node = None
    
    def update_selection(self):
        """Update the current selection.

        New in version 4.8."""
        self.tag("delete", "selection")
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

        # If the user scrolls on the page while its resources are loading, stop scrolling to the fragment
        if isinstance(widget.fragment, tuple):
            widget.fragment = None
            
        yview = widget.yview()

        if event.num == 4:
            for node_handle in widget.hovered_nodes:
                widget._post_element_event(node_handle, "onscrollup", event)
            if widget.overflow_scroll_frame and (yview[0] == 0 or widget.vsb_type == 0):
                widget.overflow_scroll_frame.scroll_x11(event, widget.overflow_scroll_frame)
            else:
                if widget.vsb_type == 0:
                    return
                widget.yview_scroll(-4, "units")
        else:
            for node_handle in widget.hovered_nodes:
                widget._post_element_event(node_handle, "onscrolldown", event)
            if widget.overflow_scroll_frame and (yview[1] == 1 or widget.vsb_type == 0):
                widget.overflow_scroll_frame.scroll_x11(event, widget.overflow_scroll_frame)
            else:
                if widget.vsb_type == 0:
                    return
                widget.yview_scroll(4, "units")

    def scroll(self, event):
        "Manage scrolling on Windows/MacOS."

        # If the user scrolls on the page while it is loading, stop scrolling to the fragment
        if isinstance(self.fragment, tuple):
            self.fragment = None

        yview = self.yview() 

        for node_handle in self.hovered_nodes:
            self._post_element_event(node_handle, "onscroll", event)     

        if self.overflow_scroll_frame and event.delta > 0 and (yview[0] == 0 or self.vsb_type == 0):
            self.overflow_scroll_frame.scroll(event)
        elif self.overflow_scroll_frame and event.delta < 0 and (yview[1] == 1 or self.vsb_type == 0):
            self.overflow_scroll_frame.scroll(event)
        elif utilities.PLATFORM.system == "Darwin":
            if self.vsb_type == 0:
                return
            self.yview_scroll(int(-1*event.delta), "units")
        else:
            if self.vsb_type == 0:
                return
            self.yview_scroll(int(-1*event.delta/30), "units")

    def safe_tk_eval(self, expr):
        """Always evaluate the given expression on the main thread.

        Since version 4.9 all callbacks are evaluated on the main thread. Except for niche cases this command should not need to be used.

        This command may be moved or removed at any time.
        
        New in version 4.4."""
        return utilities.safe_tk_eval(self, expr)

    def serialize_node(self, ib=3):
        """Pretty-print a node's contents. Similar to innerHTML, but formatted.

        New in version 4.4."""
        return utilities.safe_tk_eval(r"""
            proc indent {d} {return [string repeat { } $d]}
            proc prettify {node} {
                set depth [expr {([info level] - 1) * %d}]
                set tag [$node tag]
                if {$tag eq ""} {
                if {[string trim [$node text]] eq ""} return
                set z [string map {< &lt; > &gt;} [$node text -pre]]
                if {[[$node parent] tag] ne "pre"} {
                        return [indent $depth][regsub -all {\s+} $z " "]\n
                } else {
                        return [indent $depth]$z\n
                }
                }
                set ret [indent $depth]<$tag
                foreach {zKey zVal} [$node attribute] {
                    append ret " $zKey=\"[string map [list \x22 \x5C\x22] $zVal]\""
                }
                append ret >\n
                set void {area base br col embed hr img input keygen link meta param source track wbr}
                if {[lsearch -exact $void $tag] != -1} {
                    return $ret
                }
                foreach child [$node children] {
                append ret [prettify $child]
                }
                return $ret[indent $depth]</$tag>\n
            }
                prettify [%s node] """ % (ib, self)
        )

    def serialize_node_style(self, ib=3, return_as_dict=False):
        """Pretty-print a node's style.

        New in version 4.4."""
        style = {
            i[0]: dict(j.split(":", 1) for j in i[1].split("; ") if j.strip())
            for i in self.get_computed_styles()
            if "agent" != i[2]
        }

        if return_as_dict:
            return style
        else:
            text = ""
            for i in style:
                text += i + " {\n"
                for j in style[i]:
                    text += " "*ib + style[i][j] + ";\n"
                text += "}\n"
            return text
        
    def tkhtml_offset_to_text_index(self, node, offset, invert=False):
        """Translate a Tkhtml node offset to a node text index or back.

        New in version 4.8."""
        # Ideally we would use the pathName text offset/index commands,
        # but for the end user I think it is more useful to get an index within a Tkhtml node rather than in the entire document
        text = self.get_node_text(node)
        pre_text = self.get_node_text(node, "-pre")

        # Tkhtml offsets consider \xa0 as occupying two spaces, so we double each instance of \xa0
        doubles = text.replace("\xa0", "\xa0\xa0")[:offset].count("\xa0\xa0")

        # Tkhtml offsets start from the first non-space character
        # Tkhtml offsets also ignore multiple spaces when they are visually collapsed
        # Meanwhile, textContent includes extra spaces
        # So, we have to add/subtract the number of extra characters
        if invert:
            offset += doubles
            skew = 0
            for index in range(offset):
                while index < len(text) and pre_text[index + skew] != text[index]:
                    skew += 1
            return text, pre_text, offset - skew
        else:
            offset -= doubles
            skew = 0
            for index, letter in enumerate(text[:offset]):
                while pre_text[index + skew] != letter:
                    skew += 1
            return text, pre_text, offset + skew
    
    def _load_tkhtml(self):
        "Load Tkhtml"
        if self.tkhtml_version == "auto":
            self.tkhtml_version = None

        try:
            loaded_version = tkinterweb_tkhtml.get_loaded_tkhtml_version(self.master)
            self.post_message(f"Using Tkhtml {loaded_version} because it is already loaded")
        except tk.TclError:
            if self.use_prebuilt_tkhtml:
                try:
                    file, loaded_version, self.experimental = tkinterweb_tkhtml.get_tkhtml_file(self.tkhtml_version, experimental=self.experimental)
                    tkinterweb_tkhtml.load_tkhtml_file(self.master, file)
                    self.post_message(f"Tkhtml {loaded_version} successfully loaded from {tkinterweb_tkhtml.TKHTML_ROOT_DIR}")
                except tk.TclError as error: # If something goes wrong, try again with version 3.0 in case it is a Cairo issue
                    self.post_message(f"WARNING: An error occured while loading Tkhtml {loaded_version}: {error}\n\n\
It is likely that not all dependencies are installed. Make sure Cairo is installed on your system. Some features may be missing.")
                    file, loaded_version, self.experimental = tkinterweb_tkhtml.get_tkhtml_file(index=0, experimental=self.experimental)
                    try:
                        tkinterweb_tkhtml.load_tkhtml_file(self.master, file)
                        self.post_message(f"Tkhtml {loaded_version} successfully loaded from {tkinterweb_tkhtml.TKHTML_ROOT_DIR}")
                    except tk.TclError as error: # If it still won't load it never will. It is most likely that the system is not supported. The user needs to compile and install Tkhtml.
                        raise tk.TclError(f"{error} It is likely that your system is not supported out of the box. {tkinterweb_tkhtml.HELP_MESSAGE}") from error
            else:
                tkinterweb_tkhtml.load_tkhtml(self.master)
                loaded_version = tkinterweb_tkhtml.get_loaded_tkhtml_version(self.master)
                self.post_message(f"Tkhtml {loaded_version} successfully loaded")

    def _handle_load_finish(self, post_event=True):
        if self.fragment:
            try:
                if isinstance(self.fragment, tuple):
                    self.yview(self.fragment)
                else:
                    node = self.search(f"[id='{self.fragment}']")
                    if not node: 
                        node = self.search(f"[name={self.fragment}]")
                    if node:
                        self.fragment = node
                        self.yview(node)
            except tk.TclError:
                pass
        
        if post_event:
            self.post_event(utilities.DONE_LOADING_EVENT)

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
                    colors[count] = utilities.invert_color(
                        list(
                            int(color[i : i + lv // 3], 16)
                            for i in range(0, lv, lv // 3)
                        ),
                        match.group(1), self.dark_theme_limit
                    )
                    changed = True
                elif color.startswith("rgb(") or color.startswith("rgba("):
                    colors_list = (list(
                            map(
                                int,
                                color.lstrip("rgba(")
                                .lstrip("rgb(")
                                .rstrip(")")
                                .strip(" ")
                                .split(","),
                            )
                        ),)
                    if len(colors_list) == 3:
                        colors[count] = utilities.invert_color(
                            colors_list,
                            match.group(1), self.dark_theme_limit
                        )
                        changed = True
                else:
                    try:
                        color = list(self.winfo_rgb(color))
                        colors[count] = utilities.invert_color(color, match.group(1), self.dark_theme_limit)
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
            return utilities.download(url, insecure=self.insecure_https, cafile=self.ssl_cafile, headers=tuple(self.headers.items()), timeout=self.request_timeout)
        else:
            return utilities.cache_download(url, insecure=self.insecure_https, cafile=self.ssl_cafile, headers=tuple(self.headers.items()), timeout=self.request_timeout)
    
    def _thread_check(self, callback, *args, **kwargs):
        if not self.downloads_have_occured:
            self.downloads_have_occured = True
            
        if not self.threading_enabled:
            callback(*args, **kwargs)
        elif len(self.active_threads) >= self.maximum_thread_count:
            self.after(500, lambda callback=callback, args=args: self._thread_check(callback, *args, **kwargs))
        else:
            thread = utilities.StoppableThread(target=callback, args=args, kwargs=kwargs)
            thread.start()

    def _on_script(self, attributes, tag_contents):
        """A JavaScript engine could be used here to parse the script.
        Returning any HTMl code here (should) cause it to be parsed in place of the script tag."""
        if not self._javascript_enabled or not self.unstoppable:
            return

        attributes = attributes.split()
        attributes = dict(zip(attributes[::2], attributes[1::2])) # Make attributes a dict

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
            # Onload is fired if and when the stylesheet is parsed
        elif "icon" in rel:
            self.icon = url
            self.post_event(utilities.ICON_CHANGED_EVENT)
            self._post_element_event(node, "onload", None, utilities.ELEMENT_LOADED_EVENT)
        else:
            self._post_element_event(node, "onload", None, utilities.ELEMENT_LOADED_EVENT)

    def _on_atimport(self, parent_url, new_url):
        "Load @import scripts."
        if not self.stylesheets_enabled or not self.unstoppable:
            return
        try:
            new_url = urljoin(parent_url, new_url)
            self.post_message(f"Loading stylesheet from {utilities.shorten(new_url)}")

            self._thread_check(self.fetch_styles, url=new_url)

        except Exception as error:
            self.post_message(f"ERROR: could not load stylesheet {new_url}: {error}")

    def _on_title(self, node):
        "Handle <title> elements. We could use a script handler but then the node is no longer visible to the DOM."
        children = self.get_node_children(node)
        if children: # Fix for Bug #136, where an empty title tag raises an exception
            self.title = self.get_node_text(self.get_node_children(node), "-pre")
            self.post_event(utilities.TITLE_CHANGED_EVENT)

    def _on_base(self, node):
        "Handle <base> elements."
        href = self.get_node_attribute(node, "href", "")
        if href:
            self.base_url = self.resolve_url(href)
    
    def _on_meta(self, node):
        "Partly handle <meta> elements."
        if self.get_node_attribute(node, "http-equiv") == "refresh":
            content = self.get_node_attribute(node, "content").split(";")
            if len(content) == 2:
                if content[1].startswith("url="):
                    url = self.resolve_url(content[1].lstrip("url="))
                    self.post_message(f"Redirecting to '{utilities.shorten(url)}'")
                    self.visited_links.append(url)
                    self.on_link_click(url)

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
            self.post_message(f"Creating iframe from {utilities.shorten(src)}")
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
            # This doesn't work when in an attribute handler
            data = self.get_node_attribute(node, "data")

        if data != "":
            try:
                # Load widgets presented in <object> elements
                widgetid = self.nametowidget(data)
                self.replace_node_with_widget(node, widgetid)
            except KeyError:
                data = self.resolve_url(data)
                if data == self.base_url:
                    # Don't load the object if it is the same as the current file
                    # Otherwise the page will load the same object indefinitely and freeze the GUI forever
                    return

                self.post_message(f"Creating object from {utilities.shorten(data)}")
                self._thread_check(self.fetch_objects, node, data)

    def _on_object_value_change(self, node, attribute, value):
        if attribute == "data":
            if value:
                self._on_object(node, value)
            else:
                # Reset the element if data is not supplied
                # Force reset because it might contain widgets that are added internally
                self.map_node(node, True)
                
    def _on_draw_cleanup_crash_cmd(self):
        if self._crash_prevention_enabled:
            self.post_message("WARNING: HtmlDrawCleanup has encountered a critical error. This is being ignored because crash prevention is enabled.")
        else:
            self.destroy()

    def _on_image(self, node):
        url = self.resolve_url(self.get_node_attribute(node, "src"))
        self.image_directory[url] = node
    
    def _on_image_value_change(self, node, attribute, value):
        if attribute == "src":
            url = self.resolve_url(value)
            if node in self.image_directory.values():
                for k, v in frozenset(self.image_directory.items()):
                    if v == node:
                        del self.image_directory[k]
                        break
            self.image_directory[url] = node
            # if self.experimental:
            #     c = self.get_node_children(node)
            #     if c: self.destroy_node(c)

    def _on_image_cmd(self, url):
        "Handle images."
        if not self.images_enabled or not self.unstoppable:
            return

        name = self.allocate_image_name()

        if url.startswith(self.image_name_prefix):
            name = url
        else:
            image = imageutils.blank_image(name)
            self.loaded_images[name] = image

            if any({
                    url.startswith("linear-gradient("),
                    url.startswith("radial-gradient("),
                    url.startswith("repeating-linear-gradient("),
                    url.startswith("repeating-radial-gradient("),
                }):
                self.post_message(f"Fetching image: {utilities.shorten(url)}")
                self.load_alt_text(url, name)
                for image in url.split(","):
                    self.post_message(f"ERROR: could not display the image {utilities.shorten(url)} because it is not supported yet")
                self.on_resource_setup(url, "image", False)
            else:
                url = url.split("), url(", 1)[0].replace("'", "").replace('"', "")
                url = self.resolve_url(url)
                if url in self.image_directory:
                    node = self.image_directory[url]
                else:
                    node = None
                self._thread_check(self.fetch_images, node, url, name)

        return list((name, self.register(self._on_image_delete)))
    
    def _on_image_delete(self, name):
        # Remove the reference to the image in the main thread
        self.post_to_queue(lambda name=name: self._finish_image_delete(name))

    def _finish_image_delete(self, name):
        # NOTE: this must run in the main thread
        try:
            del self.loaded_images[name]
        except AttributeError:
            pass

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
            #self.post_message(f"Successfully setup form element {node}")

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
                self.waiting_forms -= 1
                self.post_message("Successfully setup table form")
                #self.post_message(f"Successfully setup table form element {node}")

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
        widgetid = subwidgets.Combobox(self)
        widgetid.insert(text, values, selected)
        widgetid.configure(onchangecommand=lambda *_, widgetid=widgetid: self._on_input_change(node, widgetid))
        self.form_widgets[node] = widgetid
        state = self.get_node_attribute(node, "disabled", False) != "0"
        if state:
            widgetid.configure(state="disabled")
        self.set_node_attribute(node, self.widget_container_attr, widgetid)
        self.handle_node_replacement(
            node,
            widgetid,
            lambda widgetid=widgetid: self._handle_node_removal(widgetid),
            lambda node=node, widgetid=widgetid, widgettype="text": self._handle_node_style(
                node, widgetid, widgettype
            ),
        )
        #self.post_message(f"Successfully setup select element {node}")

    def _on_textarea(self, node):
        "Handle <textarea> elements."
        if not self.forms_enabled:
            return
        widgetid = subwidgets.ScrolledTextBox(self, self.get_node_text(self.get_node_children(node), "-pre"), lambda widgetid, node=node: self._on_input_change(node, widgetid))

        self.form_widgets[node] = widgetid
        state = self.get_node_attribute(node, "disabled", False) != "0"
        if state:
            widgetid.configure(state="disabled")
        self.set_node_attribute(node, self.widget_container_attr, widgetid)
        self.handle_node_replacement(
            node,
            widgetid,
            lambda widgetid=widgetid: self._handle_node_removal(widgetid),
            lambda node=node, widgetid=widgetid, widgettype="text": self._handle_node_style(
                node, widgetid, widgettype
            ),
        )
        #self.post_message(f"Successfully setup select element {node}")

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
            widgetid = subwidgets.FileSelector(self, accept, multiple, lambda widgetid, node=node: self._on_input_change(node, widgetid))
            stylecmd = lambda node=node, widgetid=widgetid: self._handle_node_style(
                node, widgetid
            )
        elif nodetype == "color":
            widgetid = subwidgets.ColourSelector(self, nodevalue, lambda widgetid, node=node: self._on_input_change(node, widgetid))
            stylecmd = utilities.placeholder
        elif nodetype == "checkbox":
            if self.get_node_attribute(node, "checked", "false") != "false": 
                checked = 1
            else:
                checked = 0

            widgetid = subwidgets.FormCheckbox(self, checked, lambda widgetid, node=node: self._on_input_change(node, widgetid))
            widgetid.set = lambda nodevalue, node=node: self.set_node_attribute(node, "value", nodevalue)
            widgetid.get = lambda node=node: self.get_node_attribute(node, "value")
            stylecmd = lambda node=node, widgetid=widgetid: self._handle_node_style(
                node, widgetid
            )
        elif nodetype == "range":
            widgetid = subwidgets.FormRange(self, 
                nodevalue,
                self.get_node_attribute(node, "min", 0),
                self.get_node_attribute(node, "max", 100),
                self.get_node_attribute(node, "step", 1),
                lambda widgetid, node=node: self._on_input_change(node, widgetid)
            )
            stylecmd = lambda node=node, widgetid=widgetid, widgettype="range": self._handle_node_style(
                node, widgetid, widgettype
            )
        elif nodetype == "number":
            widgetid = subwidgets.FormNumber(self, 
                nodevalue,
                self.get_node_attribute(node, "min", 0),
                self.get_node_attribute(node, "max", 100),
                self.get_node_attribute(node, "step", 1),
                lambda widgetid, node=node: self._on_input_change(node, widgetid)
            )
            stylecmd = lambda node=node, widgetid=widgetid: self._handle_node_style(
                node, widgetid
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

            widgetid = subwidgets.FormRadioButton(
                self,
                self.radiobutton_token,
                nodevalue,
                checked,
                variable,
                lambda widgetid, node=node: self._on_input_change(node, widgetid)
            )
            widgetid.set = lambda nodevalue, node=node: self.set_node_attribute(node, "value", nodevalue)
            self.radio_buttons[name] = widgetid.variable
            stylecmd = lambda node=node, widgetid=widgetid: self._handle_node_style(
                node, widgetid
            )
        else:
            widgetid = subwidgets.FormEntry(self, nodevalue, nodetype, lambda widgetid, node=node: self._on_input_change(node, widgetid))
            widgetid.bind(
                "<Return>",
                lambda event, node=node: self._handle_form_submission(
                    node=node, event=event
                ),
            )
            stylecmd = lambda node=node, widgetid=widgetid, widgettype="text": self._handle_node_style(
                node, widgetid, widgettype
            )

        self.form_widgets[node] = widgetid
        self.set_node_attribute(node, self.widget_container_attr, widgetid)
        self.handle_node_replacement(
            node,
            widgetid,
            lambda widgetid=widgetid: self._handle_node_removal(widgetid),
            stylecmd
        )

        if state != "false": 
            widgetid.configure(state="disabled")
        #self.post_message(f"Successfully setup {nodetype if nodetype else "text"} input element {node}")

    def _on_input_value_change(self, node, attribute, value):
        if node not in self.form_widgets:
            return

        nodetype = self.get_node_attribute(node, "type")
        widget = self.form_widgets[node]
        if attribute == "value" and nodetype not in {"checkbox", "radio"}:
            widget.set(value)
        elif attribute in {"min", "max", "step"} and nodetype in {"range", "number"}:
            CONFIG_MAP = {"min": "from_", "max": "to", "step": "step"}
            widget.configure(**{CONFIG_MAP[attribute]: value})
        elif attribute == "checked":
            if nodetype == "checkbox":
                widget.variable.set(1 if value != "false" else 0)
            elif nodetype == "radio":
                nodevalue = self.get_node_attribute(node, "value")
                if value != "false":
                    widget.variable.set(nodevalue)

    def _on_body(self, node, index):
        "Wait for style changes on the root node."
        self.replace_node_contents(node,
                    node,
                    "-stylecmd",
                    self.register(lambda node=node: self._set_overflow(node)))

    def _on_input_change(self, node, widgetid):
        widgetid.event_generate(utilities.FIELD_CHANGED_EVENT)
        self._post_element_event(node, "onchange", None, utilities.FIELD_CHANGED_EVENT)
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
        # NOTE: this method is thread-safe and is designed to run in a thread

        thread = utilities.get_current_thread()
        self.active_threads.append(thread)
        self.post_event(utilities.DOWNLOADING_RESOURCE_EVENT, True)
        return thread

    def _finish_download(self, thread):
        # NOTE: this method is thread-safe and is designed to run in a thread

        self.active_threads.remove(thread)
        if len(self.active_threads) == 0:
            self.post_to_queue(self._handle_load_finish)
        else:
            self.post_to_queue(lambda: self._handle_load_finish(False))

    def _submit_deferred_scripts(self):
        if self.pending_scripts:
            for index, script in enumerate(self.pending_scripts):
                self.on_script(*script)
            self.pending_scripts = []
           
    def _fix_css_urls(self, match, url):
        "Make relative uris in CSS files absolute."
        newurl = match.group()
        newurl = utilities.strip_css_url(newurl)
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
        self.post_message(f"A link to '{utilities.shorten(url)}' was clicked")
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
                nodetype = self.get_node_attribute(formelement, "type")

                if formelement in self.form_widgets:
                    nodevalue = self.form_widgets[formelement].get()
                    if nodetype == "number":
                        if not self.form_widgets[formelement].check():
                            return
                elif self.get_node_tag(formelement) == "hidden":
                    nodevalue = self.get_node_attribute(formelement, "value")
                    
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

        self.post_message(f"A form was submitted to {utilities.shorten(url)}")
        self.on_form_submit(url, data, method)

    def _handle_overflow_property(self, overflow, overflow_function):
        if overflow != "visible": # Visible is the Tkhtml default, so it's largely meaningless
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
        
        overflow = self.get_node_attribute(node, utilities.BUILTIN_ATTRIBUTES["overflow-x"]) # Tkhtml doesn't support overflow-x
        overflow = self._handle_overflow_property(overflow, self.manage_hsb_func)

        background = self.get_node_property(node, "background-color")
        if background != "transparent" and self.motion_frame_bg != background: # Transparent is the Tkhtml default, so it's largely meaningless
            self.motion_frame_bg = background
            self.motion_frame.config(bg=background)

    def _set_cursor(self, cursor):
        "Set the document cursor."
        if self.current_cursor != cursor:
            cursor = utilities.CURSOR_MAP[cursor]
            try:
                self.master.config(cursor=cursor, _override=True)
            except tk.TclError:
                self.master.config(cursor=cursor)
            self.current_cursor = cursor
            # I've noticed that the cursor won't always update when the binding is tied to a different widget than the one we are changing the cursor of
            # However, the html widget doesn't support the cursor property so there's not much we can do about this
            # update_idletasks() or update() have no effect, but print() and updating the color or text of another widget does
            # Therefore we update the background color of a tiny frame that is barely visible to match the background color of the page whenever we need to change te cursor
            # It's weird but hey, it works
            self.motion_frame.config(bg=self.motion_frame_bg)

    def _post_element_event(self, node_handle, attribute, event=None, event_name=None):
        "Post an element event"
        
        # Post the JavaScript event first if needed
        if self._javascript_enabled:
            if attribute == "onload":
                if node_handle in self.loaded_elements:
                    # Don't run the onload script twice
                    return
                else:
                    self.loaded_elements.append(node_handle)
            if attribute in utilities.JS_EVENT_MAP:
                # If the event is a non-standard event (i.e. onscrollup), convert it
                attribute = utilities.JS_EVENT_MAP[attribute]
            if attribute:
                mouse = self.get_node_attribute(node_handle, attribute)
                if mouse:
                    self.on_element_script(node_handle, attribute, mouse)
        
        # Then post the Tkinter event
        if self.events_enabled and (event or event_name):
            self.event_manager.post_event(node_handle, attribute, event, event_name)

    def _create_iframe(self, node, url, html=None, vertical_scrollbar="auto"):
        if self.embed_obj:
            widgetid = self.embed_obj(self,
                messages_enabled=self.messages_enabled,
                message_func=self.message_func,
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
                ssl_cafile = self.ssl_cafile,
                request_timeout = self.request_timeout,
                caret_browsing_enabled = self._caret_browsing_enabled
            )

            if html:
                widgetid.load_html(html, url)
            elif url:
                widgetid.load_url(url)

            self.loaded_iframes[node] = widgetid

            self.handle_node_replacement(
                node, widgetid, lambda widgetid=widgetid: self._handle_node_removal(widgetid)
            )
        else:
            self.post_message(f"WARNING: the embedded page {url} could not be shown because no embed widget was provided.")

    def _on_right_click(self, event):
        for node_handle in self.hovered_nodes:
            self._post_element_event(node_handle, "onmousedown")
            self._post_element_event(node_handle, "oncontextmenu", event)

    def _on_middle_click(self, event):
        for node_handle in self.hovered_nodes:
            self._post_element_event(node_handle, "onmiddlemouse", event)

    def _on_focusout(self, event):
        if self._caret_browsing_enabled:
            if (self.winfo_toplevel().focus_displayof() not in {None, self}):
                self.caret_manager.hide()

    def _on_focusin(self, event):
        if self._caret_browsing_enabled:
            self.caret_manager.update()

    def _on_up(self, event):
        if self._caret_browsing_enabled and self.caret_manager.is_placed():
            self.caret_manager.shift_up(event)
        else:
            self.yview_scroll(-5, "units")

    def _on_down(self, event):
        if self._caret_browsing_enabled and self.caret_manager.is_placed():
            self.caret_manager.shift_down(event)
        else:
            self.yview_scroll(5, "units")

    def _on_left(self, event): 
        if self._caret_browsing_enabled: 
            self.caret_manager.shift_left(event)

    def _on_right(self, event): 
        if self._caret_browsing_enabled: 
            self.caret_manager.shift_right(event)
    
    def _on_prior(self, event): self.yview_scroll(-1, "pages")

    def _on_next(self, event): self.yview_scroll(1, "pages")

    def _on_home(self, event): self.yview_moveto(0)

    def _on_end(self, event): self.yview_moveto(1)

    def _on_click(self, event, redirected=False):
        "Set active element flags."
        if not self.current_hovered_node:
            # Register current node if mouse has never moved
            self._on_mouse_motion(event)

        if not redirected:
            self.selection_type = 0

        self.focus_set()
        self.tag("delete", "selection")

        if self._javascript_enabled or self.events_enabled:
            for node_handle in self.hovered_nodes:
                self._post_element_event(node_handle, "onmousedown", event)

        if self.hovered_nodes:
            self.selection_start_node, self.selection_start_offset = self.node(
                True, event.x, event.y
            )
            self.selection_end_node = None
            self.selection_end_offset = None

            if self._caret_browsing_enabled:
                self.caret_manager.set(self.selection_start_node, self.selection_start_offset)

            if self.stylesheets_enabled:
                self.set_node_flags(self.hovered_nodes[0], "active")
                self.current_active_node = self.hovered_nodes[0]

    def _on_leave(self, event=None):
        "Reset cursor and node state when leaving this widget"
        self._set_cursor("default")
        if self.stylesheets_enabled:
            for node in self.hovered_nodes:
                try:
                    self.remove_node_flags(node, "hover")
                    self.remove_node_flags(node, "active")
                    self._post_element_event(node, "onmouseout", event)
                except tk.TclError:
                    pass
        self.hovered_nodes = []
        self.current_hovered_node = None

    def _handle_recursive_hovering(self, event, node_handle, prev_hovered_nodes):
        "Set hover flags on the parents of the hovered element."
        if node_handle not in self.hovered_nodes:
            self.hovered_nodes.append(node_handle)

        if node_handle not in prev_hovered_nodes:
            self.set_node_flags(node_handle, "hover")
            self._post_element_event(node_handle, "onmouseover", event, "Enter")

        self._post_element_event(node_handle, "onmousemove", event)
        if event.state == 256:
            self._post_element_event(node_handle, "onmouseb1move", event)

        parent = self.get_current_hovered_node_parent(node_handle)
        if parent:
            self._handle_recursive_hovering(event, parent, prev_hovered_nodes)            

    def _on_mouse_motion(self, event):
        "Set hover flags, motion events, and handle the CSS 'cursor' property."        
        if self.on_embedded_node:
            node_handle = self.on_embedded_node
        else:
            node_handle = self.get_current_hovered_node(event)
            if not node_handle:
                self._on_leave(None)
                return

        try:
            # If we are in the same node, sumbit motion events
            # If event.state == 256, the mouse is being pressed
            # If event.type == 5, it's coming from self._on_click_release()
            if node_handle == self.current_hovered_node and event.type != "5":
                for node_handle in self.hovered_nodes:
                    self._post_element_event(node_handle, "onmousemove", event)
                    if event.state == 256:
                        self._post_element_event(node_handle, "onmouseb1move", event)
                return
            
            # If not we have some work to do
            if self.hovered_nodes:
                self._post_element_event(self.hovered_nodes[0], "onmouseleave")

            prev_hovered_nodes = set(self.hovered_nodes)
            
            if not self.get_node_tag(node_handle):
                useful_node_handle = self.get_current_hovered_node_parent(node_handle)
            else:
                useful_node_handle = node_handle
            self.hovered_nodes = []
            self._handle_recursive_hovering(event, useful_node_handle, prev_hovered_nodes)

            cursor = self.get_node_property(useful_node_handle, "cursor")
            if (event.state != 256 or event.type == "5") and cursor in utilities.CURSOR_MAP: # if cursor is set
                self._set_cursor(cursor)
            elif useful_node_handle != node_handle: # if on a text node
                self._set_cursor("text")
            else:
                self._set_cursor("default")

            # self.current_hovered_node can be a text node
            # self.hovered nodes will never hold text nodes
            self.current_hovered_node = node_handle

            self._post_element_event(useful_node_handle, "onmouseenter")

            for node in prev_hovered_nodes - set(self.hovered_nodes):
                self.remove_node_flags(node, "hover")
                self._post_element_event(node, "onmouseout", event, "Leave")

        except tk.TclError:
            # Sometimes errors are thrown if the mouse is moving while the page is loading
            pass

    def _on_click_release(self, event):
        "Handle click releases on hyperlinks and form elements."
        if self.get_selection():
            return self._on_mouse_motion(event)
        
        if not self.hovered_nodes:
            return
        
        for node_handle in self.hovered_nodes:
            self._post_element_event(node_handle, "onmouseup", event)
            self._post_element_event(node_handle, "onclick")

        node_handle = self.hovered_nodes[0]

        try:
            node_tag = self.get_node_tag(node_handle).lower()

            if not node_tag:
                node_handle = self.get_node_parent(node_handle)
                node_tag = self.get_node_tag(node_handle).lower()

            node_type = self.get_node_attribute(node_handle, "type").lower()

            if self.current_active_node and self.stylesheets_enabled:
                self.remove_node_flags(self.current_active_node, "active")
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

        self.current_active_node = None

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

        for node_handle in self.hovered_nodes:
            self._post_element_event(node_handle, "ondblclick", event)

        if not self.selection_enabled or not self.selection_start_node:
            return

        try:
            if self.selection_type == 1:
                text = self.get_node_text(self.selection_start_node)
                self.selection_start_offset = 0
                self.selection_end_node = self.selection_start_node
                self.selection_end_offset = len(text)
                self.update_selection()
                self.selection_type = 2

            elif self.selection_type == 2:
                self.clear_selection()
                self.selection_type = 0

            else:
                start_offset, end_offset = self._word_in_node(self.selection_start_node, self.selection_start_offset)
                self.selection_end_node = self.selection_start_node
                self.selection_start_offset = start_offset
                self.selection_end_offset = end_offset
                self.update_selection()
                self.selection_type = 1
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
            new_node, new_offset = self.node(True, event.x, event.y)

            if new_node is None:
                return

            self.selection_end_node, self.selection_end_offset = new_node, new_offset

            if self.selection_type == 1:
                start_offset, end_offset = self._word_in_node(self.selection_start_node, self.selection_start_offset)
                start_offset2, end_offset2 = self._word_in_node(self.selection_end_node, self.selection_end_offset)
                start_index = self.text("offset", self.selection_start_node, self.selection_start_offset)
                end_index = self.text("offset", self.selection_end_node, self.selection_end_offset)
                if start_index > end_index:
                    self.selection_start_offset = end_offset
                    self.selection_end_offset = start_offset2
                else:
                    self.selection_start_offset = start_offset
                    self.selection_end_offset = end_offset2

            elif self.selection_type == 2:
                start_index = self.text("offset", self.selection_start_node, self.selection_start_offset)
                end_index = self.text("offset", self.selection_end_node, self.selection_end_offset)
                if start_index > end_index:
                    text = self.get_node_text(self.selection_start_node)
                    self.selection_start_offset = len(text)
                    self.selection_end_offset = 0
                else:
                    text = self.get_node_text(self.selection_end_node)
                    self.selection_start_offset = 0
                    self.selection_end_offset = len(text)
                
            self.update_selection()

            if self.current_active_node:
                if self.stylesheets_enabled:
                    self.remove_node_flags(self.current_active_node, "active")
                self.current_active_node = None

                if self.get_node_tag(self.current_hovered_node):
                    self._set_cursor("default")
                else:
                    self._set_cursor("text")

            if self._caret_browsing_enabled:
                self.caret_manager.set(self.selection_end_node, self.selection_end_offset)
        except tk.TclError:
            self._set_cursor("default")

    def _on_embedded_mouse_enter(self, event, node_handle):
        self.on_embedded_node = node_handle
        self._on_mouse_motion(event)
    
    def _on_embedded_mouse_leave(self, event, node_handle):
        self.on_embedded_node = node_handle
        # Calling self._on_mouse_motion here seems so cause some flickering
        # event.x and event.y are relative to this node and not self
        # We could fix this but I can't find any noticeable side effects of not including it
        # Not too sure why it was originally here?

    def _add_bindtags(self, widgetid, allowscrolling=True, master=False):
        "Add bindtags to allow scrolling and on_embedded_mouse function calls."
        if allowscrolling:
            tags = (
                self.node_tag,
                self.scrollable_node_tag,
            )
        else:
            tags = (self.node_tag,)

        if master:
            tags = (self.node_tag, self.tkinterweb_tag)

        widgetid.bindtags(widgetid.bindtags() + tags)

class TkHtmlParsedURI:
    """Bindings for the Tkhtml URI parsing system. 
    
    The underlying commands are largely unmaintained. Consider using the methods provided by the :class:`.HtmlFrame` widget and by Python's :py:mod:`urllib` library.
    
    New in version 4.4."""

    def __init__(self, uri, html):
        self._html = html
        self.parsed = self.uri(uri)

    def __repr__(self):
        return f"{self._html._w}::{self.__class__.__name__.lower()}"

    def __str__(self):
        return self.uri_get(self.parsed)

    def __del__(self):
        self.uri_destroy(self.parsed)

    def uri(self, uri):
        "Returns name of parsed uri to be used in methods below."
        return self._html.tk.call("::tkhtml::uri", uri)

    def tkhtml_uri_decode(self, uri, base64=False):
        "Decode the uri."
        return self._html.tk.call("::tkhtml::decode", "-base64" if base64 else "", uri)

    def tkhtml_uri_encode(self, uri):
        "Encodes the uri."
        return self._html.tk.call("::tkhtml::encode", uri)

    def tkhtml_uri_escape(self, uri, query=False):
        "Returns the decoded data."
        a = "-query" if query else ""
        return self._html.tk.call("::tkhtml::escape_uri", a, uri)

    def uri_resolve(self, uri):
        "Resolve a uri."
        return self._html.tk.call(self.parsed, "resolve", uri)

    def uri_load(self, uri):
        "Load a uri."
        return self._html.tk.call(self.parsed, "load", uri)

    def uri_get(self):
        "Get the uri."
        return self._html.tk.call(self.parsed, "get")

    def uri_defrag(self):
        "Defrag the uri."
        return self._html.tk.call(self.parsed, "get_no_fragment")

    def uri_scheme(self):
        "Return the uri scheme."
        return self._html.tk.call(self.parsed, "scheme")

    def uri_authority(self):
        "Return the uri authority."
        return self._html.tk.call(self.parsed, "authority")

    def uri_path(self):
        "Return the uri path."
        return self._html.tk.call(self.parsed, "path")

    def uri_query(self):
        "Return the uri query."
        return self._html.tk.call(self.parsed, "query")

    def uri_fragment(self):
        "Return the uri fragment."
        return self._html.tk.call(self.parsed, "fragment")

    def uri_destroy(self):
        "Destroy this uri."
        self._html.tk.call(self.parsed, "destroy")
