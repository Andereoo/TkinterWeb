"""
The core Python bindings to Tkhtml3

Copyright (c) 2021-2025 Andrew Clarke
"""

from re import IGNORECASE, split, sub

from urllib.parse import urljoin

from queue import Queue, Empty

import tkinter as tk
from . import extensions, utilities, handlers

import tkinterweb_tkhtml


class TkinterWeb(tk.Widget):
    """This object provides the low-level widget that bridges the gap between the underlying Tkhtml3 widget and Tkinter. 

    **Do not use this widget on its own unless absolutely nessessary.** Instead use the :class:`~tkinterweb.HtmlFrame` widget.

    This widget can be accessed through the :attr:`~tkinterweb.HtmlFrame.html` property of the :class:`~tkinterweb.HtmlFrame` and :class:`~tkinterweb.HtmlLabel` widgets to access underlying settings and commands that are not a part of the :class:`~tkinterweb.HtmlFrame` API.
    
    This widget stores many useful instance variables and configuration flags. Some are exposed through the main API, others are not. Please see the source code for more details."""

    def __init__(self, master, tkinterweb_options=None, **kwargs):
        self.master = master
        tkinterweb_options = tkinterweb_options.copy()

        # Setup most variables
        self._setup_status_variables()

        # Setup the settings variables
        _delayed_options = {"dark_theme_enabled", "caches_enabled", "threading_enabled"}
        tkinterweb_options = self._setup_settings(tkinterweb_options, _delayed_options)

        # Load Tkhtml3
        self._load_tkhtml()

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

        shrink = bool(kwargs.get("shrink"))
        textwrap = kwargs.get("textwrap")

        # Set the textwrap value if needed
        if self.using_tkhtml30:
            if self.default_style:
                # For Tkhtml 3.0, we do our best by applying CSS to block word wrapping
                if textwrap == "auto" and shrink:
                    self.default_style += utilities.TEXTWRAP_STYLE
                elif not textwrap:
                    self.default_style += utilities.TEXTWRAP_STYLE
            # Version 3.0 doesn't support textwrap
            kwargs.pop("textwrap", None)
        elif textwrap == "auto":
            kwargs["textwrap"] = not(shrink)

        # Set the default style if needed
        if not kwargs.get("defaultstyle", "") and self.default_style:
            kwargs["defaultstyle"] = self.default_style

        # Unset width and height if null
        if kwargs.get("width") == 0: 
            del kwargs["width"]
        if kwargs.get("height") == 0: 
            del kwargs["height"]

        # Provide OS information for troubleshooting
        self.post_message(f"Starting TkinterWeb for {utilities.PLATFORM.processor} {utilities.PLATFORM.system} with Python {'.'.join(utilities.PYTHON_VERSION)}")

        # Initialize the Tkhtml3 widget
        tk.Widget.__init__(self, master, "html", kwargs)

        # Setup threading settings
        try:
            self.allow_threading = bool(self.tk.call("set", "tcl_platform(threaded)"))
        except tk.TclError:
            self.allow_threading = True

        # Set remaining settings
        for key in _delayed_options:
            setattr(self, key, tkinterweb_options[key])

        # Create a tiny, blank frame for cursor updating
        self.motion_frame_bg = "white"
        self.motion_frame = tk.Frame(self, bg=self.motion_frame_bg, width=1, height=1)
        self.motion_frame.place(x=0, y=0)

        # Setup bindings        
        self._setup_bindings()
        self._setup_handlers()
        
        self.post_message(f"""Welcome to TkinterWeb!
                                
The API changed in version 4. See https://tkinterweb.readthedocs.io/ for details.

Debugging messages are enabled. Use the parameter `messages_enabled = False` when calling HtmlFrame() or HtmlLabel() to disable these messages.
                                
Load about:tkinterweb for debugging information.
                                
If you benefited from using this package, please consider supporting its development by donating at https://buymeacoffee.com/andereoo - any amount helps!""")
        
        if not tkinterweb_tkhtml.TKHTML_EXTRAS_ROOT_DIR:
            self.post_message("The tkinterweb-tkhtml-extras package is either not installed or does not support your system. Some functionality may be missing.")

    # --- Widget setup --------------------------------------------------------

    def _setup_settings(self, options, delayed_options):
        """Widget settings. 
        Some settings have extra logic that needs to run when changing them, so they're defined elsewhere as properties.
        They are set when needed. If the settings are set through the options attribute, they will be added here."""
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
            "text_mode": False,

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

            "request_func": None,
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

            "node_tag": f"tkinterweb.{id(self)}.nodes",
            "tkinterweb_tag": f"tkinterweb.{id(self)}.tkinterweb",
            "scrollable_node_tag": f"tkinterweb.{id(self)}.scrollablenodes",
        }
        settings.update(options)
        for key, value in settings.items():
            if key not in delayed_options:
                setattr(self, key, value)

        return settings

    def _setup_status_variables(self):
        "Widget status variables."
        self.base_url = ""
        self.title = ""
        self.icon = ""

        self.fragment = ""
        self.active_threads = []
        self.downloads_have_occured = False
        self.current_active_node = None
        self.clicked_node = None
        self.current_hovered_node = None
        self.hovered_nodes = []

        self._style_count = 0
        self._current_cursor = ""

        # This set is used when resetting the widget and contains a reference to all loaded managers
        # Managers automatically add themselves to this set as they are created
        self._managers = set()

    def _setup_bindings(self):
        "Widget bindtags and bindings."
        self._add_bindtags(self, False, True)

        self.bind_class(self.node_tag, "<Motion>", self._on_mouse_motion, True)
        self.bind_class(self.node_tag, "<FocusIn>", self._on_focusout, True)

        self.bind_class(self.tkinterweb_tag, "<<Copy>>", self._copy_selection, True)
        self.bind_class(self.tkinterweb_tag, "<Control-a>", self._select_all, True)
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

    def _on_destroy(self, event):
        self._end_queue()
        self.stop()

    def _setup_handlers(self):
        "Setup node handlers"
        # Node handlers don't work on body and html elements. 
        # Body and html elements also cannot be removed without causing a segfault in vanilla Tkhtml. 
        # Weird.
        self.register_lazy_handler("parse", "body", "node_manager")
        self.register_lazy_handler("parse", "html", "node_manager")

        self.register_lazy_handler("node", "meta", "node_manager")
        self.register_lazy_handler("node", "title", "node_manager")
        self.register_lazy_handler("node", "a", "node_manager")
        self.register_lazy_handler("node", "base", "node_manager")
        self.register_lazy_handler("attribute", "a", "node_manager")
        
        self.register_lazy_handler("node", "form", "form_manager")
        self.register_lazy_handler("node", "table", "form_manager")
        self.register_lazy_handler("node", "select", "form_manager")
        self.register_lazy_handler("attribute", "select", "form_manager")
        self.register_lazy_handler("node", "textarea", "form_manager")
        self.register_lazy_handler("node", "input", "form_manager")
        self.register_lazy_handler("attribute", "input", "form_manager")

        self.register_lazy_handler("script", "script", "script_manager")

        self.register_lazy_handler("script", "style", "style_manager")
        self.register_lazy_handler("node", "link", "style_manager")

        self.register_lazy_handler("node", "img", "image_manager")
        self.register_lazy_handler("attribute", "img", "image_manager")

        self.register_lazy_handler("node", "iframe", "object_manager")
        self.register_lazy_handler("attribute", "iframe", "object_manager")
        self.register_lazy_handler("node", "object", "object_manager")
        self.register_lazy_handler("attribute", "object", "object_manager")

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

        self.tkhtml_version = loaded_version
        self.using_tkhtml30 = loaded_version == "3.0"

    # --- Extensions ----------------------------------------------------------

    # The following 'managers' each offer extra functionality. 
    # The ones in handlers.py are primarily node handlers.
    # These objects are created when needed, if enabled
    # Most can be disabled, except search_manager and widget_manager, which run at the user's request or via other managers that can be disabled
    # Any calls to a disabled manager will be ignored and return 'None'

    # There's probably a lot more re-organization that should be done here,
    # But for now this is a lot better
    
    @utilities.lazy_manager("selection_enabled")
    def selection_manager(self):
        """The widget's selection manager.
        
        :rtype: :class:`~tkinterweb.extensions.SelectionManager`
        
        New in version 4.11."""
        return extensions.SelectionManager(self)
        
    @utilities.lazy_manager("caret_browsing_enabled")
    def caret_manager(self):
        """The widget's caret manager.
        
        :rtype: :class:`~tkinterweb.extensions.CaretManager`
        
        New in version 4.8."""
        return extensions.CaretManager(self)
    
    @utilities.lazy_manager("events_enabled")
    def event_manager(self):
        """The widget's event manager.
        
        :rtype: :class:`~tkinterweb.extensions.EventManager`
        
        New in version 4.10."""
        return extensions.EventManager(self)

    @utilities.lazy_manager(None)
    def widget_manager(self):
        """The widget's widget manager.
        
        :rtype: :class:`~tkinterweb.extensions.WidgetManager`
        
        New in version 4.11."""
        return extensions.WidgetManager(self)
    
    @utilities.lazy_manager(None)
    def search_manager(self):
        """The widget's document search manager.
        
        :rtype: :class:`~tkinterweb.extensions.SearchManager`
        
        New in version 4.11."""
        return extensions.SearchManager(self)

    @utilities.lazy_manager("javascript_enabled")
    def script_manager(self):
        """The widget's script manager.
        
        :rtype: :class:`~tkinterweb.handlers.ScriptManager`
        
        New in version 4.11."""
        return handlers.ScriptManager(self)

    @utilities.lazy_manager("stylesheets_enabled")
    def style_manager(self):
        """The widget's style manager.
        
        :rtype: :class:`~tkinterweb.handlers.StyleManager`
        
        New in version 4.11."""
        return handlers.StyleManager(self)

    @utilities.lazy_manager("images_enabled")
    def image_manager(self):
        """The widget's image manager.
        
        :rtype: :class:`~tkinterweb.handlers.ImageManager`
        
        New in version 4.11."""
        return handlers.ImageManager(self)

    @utilities.lazy_manager("objects_enabled")
    def object_manager(self):
        """The widget's object manager.
        
        :rtype: :class:`~tkinterweb.handlers.ObjectManager`
        
        New in version 4.11."""
        return handlers.ObjectManager(self)

    @utilities.lazy_manager("forms_enabled")
    def form_manager(self):
        """The widget's form manager.
        
        :rtype: :class:`~tkinterweb.handlers.FormManager`
        
        New in version 4.11."""
        return handlers.FormManager(self)

    @utilities.lazy_manager(None)
    def node_manager(self):
        """The widget's node handler manager.
        
        :rtype: :class:`~tkinterweb.extensions.NodeManager`
        
        New in version 4.11."""
        return handlers.NodeManager(self)

    # --- Properties ----------------------------------------------------------

    @utilities.special_setting(True)
    def caches_enabled(self, prev_enabled, enabled):
        "Disable the Tkhtml image cache when disabling caches."
        if prev_enabled != enabled:
            self._enable_imagecache(enabled)
    
    @utilities.special_setting(False)
    def javascript_enabled(self, prev_enabled, enabled):
        "Warn the user when enabling JavaScript."
        if prev_enabled != enabled:
            if enabled:
                self.post_message("WARNING: JavaScript support is enabled. This feature is a work in progress. Only enable JavaScript support on documents you know and trust.")

    @utilities.special_setting(True)
    def crash_prevention_enabled(self, prev_enabled, enabled):
        "Warn the user when disabling crash prevention."
        if prev_enabled != enabled:
            if not enabled:
                self.post_message("WARNING: crash prevention is disabled. You may encounter segmentation faults on some pages.")
    
    @utilities.special_setting(False)
    def dark_theme_enabled(self, prev_enabled, enabled):
        "Warn the user when enabling dark mode."
        if prev_enabled != enabled:
            if enabled:
                self.post_message("WARNING: dark theme is enabled. This feature may cause hangs or crashes on some pages.")
            if enabled and self.dark_style:
                self.config(defaultstyle=self.default_style + self.dark_style)
            elif self.default_style:
                self.config(defaultstyle=self.default_style)

    @utilities.special_setting(False)
    def image_inversion_enabled(self, prev_enabled, enabled):
        "Warn the user when enabling image inversion."
        if prev_enabled != enabled:
            prev_enabled = enabled
            if enabled:
                self.post_message("WARNING: image inversion is enabled. This feature may cause hangs or crashes on some pages.")

    @utilities.special_setting(True)
    def threading_enabled(self, prev_enabled, enabled):
        "Warn the user when disabling threading and ensure that threading is disabled if Tcl/Tk is not built with thread support."
        if self.allow_threading:
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

    @utilities.special_setting(False)
    def caret_browsing_enabled(self, prev_enabled, enabled):
        "Enable or disable caret browsing."
        if getattr(self, "_caret_manager", False) and not enabled:
            self._caret_manager.reset()

    @utilities.special_setting(True)
    def selection_enabled(self, prev_enabled, enabled):
        "Enable or disable text selection."
        if getattr(self, "_selection_manager", False) and not enabled:
            self._selection_manager.clear_selection()

    @property
    def tkhtml_default_style(self):
        return self.tk.call("::tkhtml::htmlstyle")

    # --- Queuing, messaging, and events --------------------------------------

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

    def post_to_queue(self, callback, thread_safe=True):
        """Use this method to send a callback to TkinterWeb's thread-safety queue. The callback will be evaluated on the main thread.
        Use this when running Tkinter commands from within a thread. 
        If the queue is not running (i.e. threading is disabled), the callback will be evaluated immediately.
        
        New in version 4.9."""
        if thread_safe and self.queue:
            self.queue.put(callback)
        else:
            callback()

    def post_event(self, event, thread_safe=False):
        "Generate a virtual event."
        # NOTE: when thread_safe=True, this method is thread-safe
        # Would you believe that?
        if not self.events_enabled:
            return

        if thread_safe and self.queue:
            self.post_to_queue(lambda event=event: self._post_event(event))
        else:
            self._post_event(event)

    def _post_event(self, event):
        "Generate a virtual event."
        try:
            self.event_generate(event)
        except tk.TclError:
            # The widget doesn't exist anymore
            pass

    def post_message(self, message, thread_safe=False):
        "Post a message."
        # NOTE: when thread_safe=True, this method is thread-safe
        # Amazing stuff, eh?
        if not self.messages_enabled:
            return
        
        if thread_safe and self.queue:
            self.post_to_queue(lambda message=message: self._post_message(message))
        else:
            self._post_message(message)

    def _post_message(self, message):
        "Post a message."
        if self.overflow_scroll_frame:
            message = "[EMBEDDED DOCUMENT] " + message
        self.message_func(message)

    # --- HTML/CSS parsing ----------------------------------------------------

    def parse(self, html, thread_safe=False):
        "Parse HTML code. Call :meth:`TkinterWeb.reset` before calling this method for the first time."
        # NOTE: when thread_safe=True, this method is thread-safe

        self.downloads_have_occured = False
        html = self._crash_prevention(html)
        html = self._dark_mode(html)

        # By default Tkhtml won't display plain text
        if "<" not in html and ">" not in html:
            html = f"<body><div>{html}</div></body>"

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

        self.script_manager._submit_deferred_scripts()
        self.event_manager.send_onload()

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

    def parse_css(self, sheetid=None, data="", url=None, fallback_priority="author"):
        "Parse CSS code."
        if not url:
            url = self.base_url
        data = self._crash_prevention(data)
        data = self._css_dark_mode(data)
        
        try:
            importcmd = self.register(
                lambda new_url, parent_url=url: self.style_manager._on_atimport(
                    parent_url, new_url
                )
            )
            urlcmd = self.register(
                lambda new_url, url=url: self.resolve_url(
                    new_url, url
                )
            )
            
            if sheetid:
                self.tk.call(
                    self._w, "style", "-id", sheetid, "-importcmd", importcmd, "-urlcmd", urlcmd, data
                )
            else:
                self._style_count += 1
                self.tk.call(
                    self._w, "style", "-id", fallback_priority + str(self._style_count).zfill(4), "-importcmd", importcmd, "-urlcmd", urlcmd, data
                )
        except tk.TclError:
            # The widget doesn't exist anymore
            pass

    def reset(self, thread_safe=False):
        "Reset the widget."
        # NOTE: when thread_safe=True, this method is thread-safe. Imagine that!

        self.stop()

        self.title = ""
        self.icon = ""
        self.fragment = ""

        if thread_safe:
            self.post_to_queue(self._reset)
        else:
            self._reset()

    def _reset(self):
        # NOTE: this must run in the main thread
        
        # Reset the scrollbars to the default setting
        self.manage_vsb_func()
        self.manage_hsb_func()

        # Note to self: these need to be here
        # Or very strange errors will magically appear,
        # Usually when switching between pages quickly
        self.hovered_nodes.clear()
        self.current_hovered_node = None

        self._set_cursor("default")
        self.tk.call(self._w, "reset")

        for manager in self._managers:
            manager.reset()

    def stop(self):
        "Stop loading resources."
        for thread in self.active_threads:
            thread.stop()
    
    def resolve_url(self, url, base=None):
        "Generate a full url from the specified url."
        if not base: base = self.base_url
        return urljoin(base, url)
    
    # --- Resource loading ----------------------------------------------------

    def download_url(self, url, *args):
        if self.request_func:
            return self.request_func(url, *args)
        
        if url.startswith("file://") or (not self.caches_enabled):
            return utilities.download(url, *args, insecure=self.insecure_https, cafile=self.ssl_cafile, headers=tuple(self.headers.items()), timeout=self.request_timeout)
        else:
            return utilities.cache_download(url, *args, insecure=self.insecure_https, cafile=self.ssl_cafile, headers=tuple(self.headers.items()), timeout=self.request_timeout)
    
    def _thread_check(self, callback, url, *args, **kwargs):
        if not self.downloads_have_occured:
            self.downloads_have_occured = True
            
        if not self.threading_enabled or url.startswith("file://"):
            callback(url, *args, **kwargs)
        elif len(self.active_threads) >= self.maximum_thread_count:
            self.after(500, lambda callback=callback, url=url, args=args: self._thread_check(callback, url, *args, **kwargs))
        else:
            thread = utilities.StoppableThread(target=callback, args=(url, *args,), kwargs=kwargs)
            thread.start()

    def _begin_download(self):
        # NOTE: this may run in a thread

        thread = utilities.get_current_thread()
        self.active_threads.append(thread)
        self.post_event(utilities.DOWNLOADING_RESOURCE_EVENT, thread.is_subthread)
        return thread

    def _finish_download(self, thread):
        # NOTE: this may run in a thread

        self.active_threads.remove(thread)
        if len(self.active_threads) == 0:
            self.post_to_queue(self._handle_load_finish, thread.is_subthread)
        else:
            self.post_to_queue(lambda: self._handle_load_finish(False), thread.is_subthread)

    def _finish_resource_load(self, message, url, resource, success):
        # NOTE: this must run in the main thread

        self.post_message(message)
        self.on_resource_setup(url, resource, success)

    # --- Bindings ------------------------------------------------------------

    def node(self, *args):
        "Retrieve one or more document node handles from the current document."
        nodes = self.tk.call(self._w, "node", *args)
        if nodes:
            return nodes
        else:
            return None, None

    def text(self, subcommand, *args):
        "Interact with the text of the HTML document. Valid subcommands are bbox, index, offset, and text."
        return self.tk.call(self._w, "text", subcommand, *args)

    def tag(self, subcommand, tag_name, *args):
        "Highlight regions of text displayed by the widget. Valid subcommands are add, remove, configure, and delete."
        return self.tk.call(self._w, "tag", subcommand, tag_name, *args)

    def search(self, selector, *a, cnf={}, **kw):
        """Search the document for the specified CSS selector; return a Tkhtml node if found."""
        return self.tk.call((self._w, "search", selector)+utilities.TclOpt(a)+self._options(cnf, kw))

    def xview(self, *args, auto_scroll=False):
        "Control horizontal scrolling."
        #if args:
        #    return self.tk.call(self._w, "xview", *args)
        #coords = map(float, self.tk.call(self._w, "xview").split()) #raises an error
        #return tuple(coords)
        xview = self.tk.call(self._w, "xview", *args)
        if args:
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
        """Control vertical scrolling."""
        yview = self.tk.call(self._w, "yview", *args)
        if args:
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
    
    def parse_fragment_simple(self, html):
        return self.tk.call(self._w, "fragment", html)

    def parse_fragment(self, html):
        """Parse a document fragment.
        A document fragment isn't part of the active document but is comprised of nodes like the active document.
        Changes made to the fragment don't affect the document.
        Returns a root node."""
        self.downloads_have_occured = False
        html = self._crash_prevention(html)
        html = self._dark_mode(html)
        fragment = self.tk.call(self._w, "fragment", html)
        # We assume that if no downloads have been made by now the document has finished loading, so we send the done loading signal
        if not self.downloads_have_occured:
            self.post_event(utilities.DONE_LOADING_EVENT)
        self.script_manager._submit_deferred_scripts()
        return fragment
    
    def _enable_imagecache(self, enabled):
        "Enable or disable the Tkhtml image cache."
        self.tk.call(self._w, "configure", "-imagecache", enabled)

    def get_node_text(self, node_handle, *args):
        "Get the text content of the given node."
        return self.tk.call(node_handle, "text", *utilities.TclOpt(args))

    def set_node_text(self, node_handle, new):
        "Set the text content of the given node."
        self.tk.call(node_handle, "text", "set", new)
        self.relayout() # needed for pathName text text to return the updated string

    def relayout(self):
        self.tk.call(self._w, "_relayout")

    def get_child_text(self, node):
        """Get text of node and all its descendants recursively.
        
        New in version 4.4."""
        text = self.get_node_text(node, "-pre")
        for child in self.get_node_children(node):
            text += self.get_child_text(child)
        return text
    
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

    def set_node_property(self, node_handle, node_property, new_value, *args):
        "Set the specified CSS property of the given node."
        current = self.get_node_properties(node_handle, "-inline")
        current[node_property] = new_value
        style = " ".join(f"{p}: {v};" for p, v in current.items())
        self.set_node_attribute(node_handle, "style", style)

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
        if (node_handle != contents) and not self.get_node_parent(node_handle):
            raise RuntimeError(f"root elements cannot be replaced")

        if not contents:
            # Calling replace with empty text causes Tkhtml to segfault
            contents = self.tk.call(self._w, "fragment", " ")
        return self.tk.call(node_handle, "replace", contents, *args)
    
    def get_node_replacement(self, node_handle):
        """Return the Tk widget contained by the given node.
        
        New in version 4.13."""
        return self.tk.call(node_handle, "replace")

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
        "remove dynamic flags on the given node."
        self.tk.call(node, "dynamic", "clear", name)

    def get_node_tkhtml(self, node_handle):
        "Get the path name of the node's corresponding Tkhtml instance."
        return self.tk.call(node_handle, "html")

    def get_node_stacking(self, node_handle):
        """Return the node-handle that forms the stacking context this node is located in.
        Return "" for the root-element or any element that is part of an orphan subtree.
        
        New in version 4.2."""
        return self.tk.call(node_handle, "stacking")

    def get_current_hovered_node(self, event):
        "Get the current node."
        if self.widget_manager.hovered_embedded_node:
            return self.widget_manager.hovered_embedded_node

        return self.tk.eval(
            f"""set node [lindex [lindex [{self} node {event.x} {event.y}] end] end]"""
        )

    def get_current_hovered_node_parent(self, node):
        "Get the parent of the node returned by :meth:`TkinterWeb.get_current_hovered_node`."
        return self.tk.eval(f"""set node [lindex [lindex [{node} parent] end] end]""")

    def register_handler(self, handler_type, node_tag, callback):
        "Register a node handler."
        self.tk.call(self._w, "handler", handler_type, node_tag, self.register(callback))

    def _lazy_handler(self, manager, method):
        def callback(*args, **kwargs):
            manager_obj = getattr(self, manager)
            return getattr(manager_obj, method)(*args, **kwargs)
        return callback
    
    def register_lazy_handler(self, handler_type, node_tag, manager_name):
        "Register a node handler to run lazily in the given manager."
        if handler_type == "attribute":
            callback_name = f"_on_{node_tag}_value_change"
        else:
            callback_name = f"_on_{node_tag}"

        self.tk.call(self._w, "handler", handler_type, node_tag, 
                     self.register(
                         self._lazy_handler(manager_name, callback_name)
                         )
                     )
        
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
 
    # --- Cmds & crash prevention ---------------------------------------------

    def _on_image_cmd(self, url):
        "Handle images."
        return self.image_manager._on_image_cmd(url)
       
    def _on_draw_cleanup_crash_cmd(self):
        if self.crash_prevention_enabled:
            self.post_message("WARNING: HtmlDrawCleanup has encountered a critical error. This is being ignored because crash prevention is enabled.")
        else:
            self.post_message("WARNING: HtmlDrawCleanup has encountered a critical error.")
            self.destroy()

    def _crash_prevention(self, data):
        if self.crash_prevention_enabled:
            ### TODO: enable emojis & noto colo emoji font in Tcl/Tk 9

            # From Bug #11
            data = "".join(c for c in data if c <= "\uFFFF")

            # I moved these workarounds to Tkhtml in version 3.1
            if self.using_tkhtml30:
                data = sub(
                    "font-family:[^;']*(;)?",
                    self._remove_noto_emoji,
                    data,
                    flags=IGNORECASE,
                )
                data = sub(r"rgb\([^0-9](.*?)\)", "inherit", data, flags=IGNORECASE)
        return data

    def _remove_noto_emoji(self, match):
        "Remove noto color emoji font, which causes Tkinter to crash."
        match = match.group().lower()
        match = match.replace("noto color emoji", "arial")
        return match

    # --- Dark mode -----------------------------------------------------------

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
        if self.dark_theme_enabled:
            html = sub(self.inline_dark_theme_regexes[0], lambda match: match.group(1) + sub(self.inline_dark_theme_regexes[1], self._generate_altered_colour, match.group(2)), html)
            for regex in self.general_dark_theme_regexes:
                html = sub(regex, self._generate_altered_colour, html, flags=IGNORECASE)
        return html
    
    def _css_dark_mode(self, data):
        if self.dark_theme_enabled:
            return sub(self.style_dark_theme_regex, lambda match, matchtype=0: self._generate_altered_colour(match, matchtype), data)
        return data
    
    # --- Miscellaneous -------------------------------------------------------

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

        text = self.get_node_text(node, "-pre")

        ws = len(text) - len(text.lstrip())

        if invert:
            #index = self.text("offset", node, 0) + offset
            #node, offset = self.text("index", index)
            return text, max(offset - ws, 0)
        else:
            try:
                offset = self.text("offset", node, offset + ws) - self.text("offset", node, 0)
            except TypeError:
                pass
            return text, offset
        
    def _set_cursor(self, cursor):
        "Set the document cursor."
        if self._current_cursor != cursor:
            cursor = utilities.CURSOR_MAP[cursor]
            try:
                self.master.config(cursor=cursor, _override=True)
            except tk.TclError:
                self.master.config(cursor=cursor)
            self._current_cursor = cursor
            # I've noticed that the cursor won't always update when the binding is tied to a different widget than the one we are changing the cursor of
            # However, the html widget doesn't support the cursor property so there's not much we can do about this
            # update_idletasks() or update() have no effect, but updating the color or text of another widget does
            # print() also works. Don't ask me why.
            # Therefore we update the background color of a tiny frame that is barely visible whenever we need to change the cursor
            # I might as well match the background color of the page but it doesn't really matter
            # It's weird but hey, it works
            self.motion_frame.config(bg=self.motion_frame_bg)

    # --- Widget-user interaction ---------------------------------------------

    def _scroll_x11(self, event, widget=None):
        "Manage scrolling on Linux."
        if not widget:
            widget = event.widget

        # If the user scrolls on the page while its resources are loading, stop scrolling to the fragment
        if isinstance(widget.fragment, tuple):
            widget.fragment = None
            
        yview = widget.yview()

        if event.num == 4:
            for node_handle in widget.hovered_nodes:
                widget.event_manager.post_element_event(node_handle, "onscrollup", event)
            if widget.overflow_scroll_frame and (yview[0] == 0 or widget.manage_vsb_func(check=True) == 0):
                widget.overflow_scroll_frame._scroll_x11(event, widget.overflow_scroll_frame)
            else:
                if widget.manage_vsb_func(check=True) == 0:
                    return
                widget.yview_scroll(-4, "units")
        else:
            for node_handle in widget.hovered_nodes:
                widget.event_manager.post_element_event(node_handle, "onscrolldown", event)
            if widget.overflow_scroll_frame and (yview[1] == 1 or widget.manage_vsb_func(check=True) == 0):
                widget.overflow_scroll_frame._scroll_x11(event, widget.overflow_scroll_frame)
            else:
                if widget.manage_vsb_func(check=True) == 0:
                    return
                widget.yview_scroll(4, "units")

    def _xscroll_x11(self, event, widget=None):
        "Manage scrolling on Linux."
        if not widget:
            widget = event.widget

        xview = widget.xview()

        if event.num == 4:
            if widget.overflow_scroll_frame and (xview[0] == 0 or widget.manage_hsb_func(check=True) == 0):
                widget.overflow_scroll_frame._xscroll_x11(event, widget.overflow_scroll_frame)
            else:
                if widget.manage_hsb_func(check=True) == 0:
                    return
                widget.xview_scroll(-4, "units")
        else:
            if widget.overflow_scroll_frame and (xview[1] == 1 or widget.manage_hsb_func(check=True) == 0):
                widget.overflow_scroll_frame._xscroll_x11(event, widget.overflow_scroll_frame)
            else:
                if widget.manage_hsb_func(check=True) == 0:
                    return
                widget.xview_scroll(4, "units")

    def _scroll(self, event):
        "Manage scrolling on Windows/MacOS."

        # If the user scrolls on the page while it is loading, stop scrolling to the fragment
        if isinstance(self.fragment, tuple):
            self.fragment = None

        yview = self.yview() 

        for node_handle in self.hovered_nodes:
            self.event_manager.post_element_event(node_handle, "onscroll", event)     

        if self.overflow_scroll_frame and event.delta > 0 and (yview[0] == 0 or self.manage_vsb_func(check=True)  == 0):
            self.overflow_scroll_frame._scroll(event)
        elif self.overflow_scroll_frame and event.delta < 0 and (yview[1] == 1 or self.manage_vsb_func(check=True) == 0):
            self.overflow_scroll_frame._scroll(event)
        elif utilities.PLATFORM.system == "Darwin":
            if self.manage_vsb_func(check=True) == 0:
                return
            self.yview_scroll(int(-1*event.delta), "units")
        else:
            if self.manage_vsb_func(check=True) == 0:
                return
            self.yview_scroll(int(-1*event.delta/30), "units")      
          
    def _xscroll(self, event):
        "Manage scrolling on Windows/MacOS."

        xview = self.xview() 

        if self.overflow_scroll_frame and event.delta > 0 and (xview[0] == 0 or self.manage_hsb_func(check=True) == 0):
            self.overflow_scroll_frame._xscroll(event)
        elif self.overflow_scroll_frame and event.delta < 0 and (xview[1] == 1 or self.manage_hsb_func(check=True) == 0):
            self.overflow_scroll_frame._xscroll(event)
        elif utilities.PLATFORM.system == "Darwin":
            if self.manage_hsb_func(check=True) == 0:
                return
            self.xview_scroll(int(-1*event.delta), "units")
        else:
            if self.manage_hsb_func(check=True) == 0:
                return
            self.xview_scroll(int(-1*event.delta/30), "units")      

    def _on_right_click(self, event):
        for node_handle in self.hovered_nodes:
            self.event_manager.post_element_event(node_handle, "onmousedown")
            self.event_manager.post_element_event(node_handle, "oncontextmenu", event)

    def _on_middle_click(self, event):
        for node_handle in self.hovered_nodes:
            self.event_manager.post_element_event(node_handle, "onmiddlemouse", event)

    def _on_focusout(self, event):
        if self.caret_browsing_enabled:
            if (self.winfo_toplevel().focus_displayof() not in {None, self}):
                self.caret_manager.hide()

    def _on_focusin(self, event):
        self.caret_manager.update()

    def _on_up(self, event):
        if self.caret_manager.is_placed():
            self.caret_manager.shift_up(event)
        else:
            self.yview_scroll(-5, "units")

    def _on_down(self, event):
        if self.caret_manager.is_placed():
            self.caret_manager.shift_down(event)
        else:
            self.yview_scroll(5, "units")

    def _on_left(self, event): 
        self.caret_manager.shift_left(event)

    def _on_right(self, event): 
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
            self.selection_manager.reset_selection_type()

        self.focus_set()
        self.selection_manager.clear_selection()

        if self.javascript_enabled or self.events_enabled:
            for node_handle in self.hovered_nodes:
                self.event_manager.post_element_event(node_handle, "onmousedown", event)

        if self.hovered_nodes:
            node, offset = self.node(
                True, event.x, event.y
            )
            self.clicked_node = self.hovered_nodes[0]

            self.selection_manager.begin_selection(node, offset)

            self.caret_manager.set(node, offset)

            if self.stylesheets_enabled and (not self.text_mode or (event.state & 0x4) != 0):
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
                    self.event_manager.post_element_event(node, "onmouseout", event)
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
            self.event_manager.post_element_event(node_handle, "onmouseover", event, "Enter")

        self.event_manager.post_element_event(node_handle, "onmousemove", event)
        if event.state & 0x0100:
            self.event_manager.post_element_event(node_handle, "onmouseb1move", event)

        parent = self.get_current_hovered_node_parent(node_handle)
        if parent:
            self._handle_recursive_hovering(event, parent, prev_hovered_nodes)            

    def _on_mouse_motion(self, event):
        "Set hover flags, motion events, and handle the CSS 'cursor' property."

        node_handle = self.get_current_hovered_node(event)

        if not node_handle:
            if self.text_mode:
                try:
                    node_handle, index = self.text("index", "-1")    
                except ValueError:
                    return
            else:
                self._on_leave(None)
                return

        try:
            # If we are in the same node, sumbit motion events
            # If event.state & 0x0100, the mouse is being pressed
            # If event.type == 5, it's coming from self._on_click_release()
            if node_handle == self.current_hovered_node and event.type != "5":
                for node_handle in self.hovered_nodes:
                    self.event_manager.post_element_event(node_handle, "onmousemove", event)
                    if event.state & 0x0100:
                        self.event_manager.post_element_event(node_handle, "onmouseb1move", event)
                return
            
            # If not we have some work to do
            if self.hovered_nodes:
                self.event_manager.post_element_event(self.hovered_nodes[0], "onmouseleave")
                

            prev_hovered_nodes = set(self.hovered_nodes)
            
            if not self.get_node_tag(node_handle):
                useful_node_handle = self.get_current_hovered_node_parent(node_handle)
            else:
                useful_node_handle = node_handle
            self.hovered_nodes = []
            self._handle_recursive_hovering(event, useful_node_handle, prev_hovered_nodes)

            cursor = self.get_node_property(useful_node_handle, "cursor")
            if self.text_mode and not (event.state & 0x4):
                self._set_cursor("text")
            elif (not (event.state & 0x0100) or event.type == "5" or 
                (not self.selection_enabled and 
                 (self.clicked_node == useful_node_handle or not self.clicked_node)
                 )) and cursor in utilities.CURSOR_MAP: # if cursor is set
                self._set_cursor(cursor)
            elif ((useful_node_handle != node_handle) and self.selection_enabled) : # if on a text node
                self._set_cursor("text")
            else:
                self._set_cursor("default")

            # self.current_hovered_node can be a text node
            # self.hovered nodes will never hold text nodes
            self.current_hovered_node = node_handle

            self.event_manager.post_element_event(useful_node_handle, "onmouseenter")

            for node in prev_hovered_nodes - set(self.hovered_nodes):
                self.remove_node_flags(node, "hover")
                self.event_manager.post_element_event(node, "onmouseout", event, "Leave")

        except tk.TclError:
            # Sometimes errors are thrown if the mouse is moving while the page is loading
            pass

    def _handle_link_click(self, node_handle):
        "Handle link clicks."
        href = self.get_node_attribute(node_handle, "href")
        url = self.resolve_url(href)
        self.post_message(f"A link to '{utilities.shorten(url)}' was clicked")
        self.visited_links.append(url)
        self.on_link_click(url)

    def _on_click_release(self, event):
        "Handle click releases on hyperlinks and form elements."
        if self.selection_manager.get_selection():
            return self._on_mouse_motion(event)
    
        if not self.hovered_nodes:
            return
        
        for node_handle in self.hovered_nodes:
            self.event_manager.post_element_event(node_handle, "onmouseup", event)
            self.event_manager.post_element_event(node_handle, "onclick")

        node_handle = self.hovered_nodes[0]

        if self.clicked_node != node_handle:
            return

        try:
            node_tag = self.get_node_tag(node_handle).lower()

            if not node_tag:
                node_handle = self.get_node_parent(node_handle)
                node_tag = self.get_node_tag(node_handle).lower()

            node_type = self.get_node_attribute(node_handle, "type").lower()

            if self.current_active_node and self.stylesheets_enabled:
                self.remove_node_flags(self.current_active_node, "active")

            if self.text_mode and not (event.state & 0x4):
                return
            
            if node_tag == "input" and node_type == "reset":
                self.form_manager._handle_form_reset(node_handle)
            elif node_tag == "input" and node_type in {"submit", "image"}:
                self.form_manager._handle_form_submission(node_handle)
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
                            self.form_manager._handle_form_submission(node)
                            break
        except tk.TclError:
            pass

        self.current_active_node = None

    def _on_double_click(self, event):
        "Cycle between normal selection, text selection, and element selection on multi-clicks."
        self._on_click(event, True)

        for node_handle in self.hovered_nodes:
            self.event_manager.post_element_event(node_handle, "ondblclick", event)

        try:
            self.selection_manager.double_click_selection()
        except tk.TclError:
            self._set_cursor("default")

    def _extend_selection(self, event):
        "Alter selection and HTML element states based on mouse movement."
        if self.selection_manager.selection_start_node is None:
            return

        try:
            new_node, new_offset = self.node(True, event.x, event.y)

            if new_node is None:
                return

            self.selection_manager.extend_selection(new_node, new_offset)

            if self.current_active_node:
                if self.stylesheets_enabled:
                    self.remove_node_flags(self.current_active_node, "active")
                self.current_active_node = None

                if self.selection_enabled and not self.text_mode:
                    self._set_cursor("default")

            self.caret_manager.set(new_node, new_offset)
        except tk.TclError:
            if not self.text_mode:
                self._set_cursor("default")

    def _copy_selection(self, event):
        self.selection_manager.copy_selection()

    def _select_all(self, event):
        self.selection_manager.select_all()

    # --- Backwards-compatibility ---------------------------------------------

    def update_tags(self):
        utilities.deprecate("update_tags", "selection_manager")
        return self.selection_manager.update_tags()

    def select_all(self):
        utilities.deprecate("select_all", "selection_manager")
        return self.selection_manager.select_all()

    def clear_selection(self):
        utilities.deprecate("clear_selection", "selection_manager")
        return self.selection_manager.clear_selection()
    
    def update_selection(self):
        utilities.deprecate("update_selection", "selection_manager")
        return self.selection_manager.update_selection()
    
    def get_selection(self):
        utilities.deprecate("get_selection", "selection_manager")
        return self.selection_manager.get_selection()

    def copy_selection(self, event=None):
        utilities.deprecate("copy_selection", "selection_manager")
        return self.selection_manager.copy_selection()

    def allocate_image_name(self):
        utilities.deprecate("allocate_image_name", "image_manager")
        return self.image_manager.allocate_image_name()

    def handle_node_replacement(self, node, widgetid, deletecmd, stylecmd=None, allowscrolling=True, handledelete=True):
        utilities.deprecate("handle_node_replacement", "widget_manager")
        return self.widget_manager.handle_node_replacement(node, widgetid, deletecmd, stylecmd, allowscrolling, handledelete)

    def map_node(self, node, force=False):
        utilities.deprecate("map_node", "widget_manager")
        return self.widget_manager.map_node(node, force)

    def replace_node_with_widget(self, node, widgetid):
        utilities.deprecate("replace_node_with_widget", "widget_manager")
        return self.widget_manager.set_node_widget(node, widgetid)
    
    def find_text(self, searchtext, select, ignore_case, highlight_all):
        utilities.deprecate("find_text", "search_manager")
        return self.search_manager.find_text(searchtext, select, ignore_case, highlight_all)
    
    def send_onload(self, root=None, children=None):
        utilities.deprecate("send_onload", "event_manager")
        return self.event_manager.send_onload(root, children)


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
