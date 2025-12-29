"""
Widgets that expand on the functionality of the basic bindings
by adding scrolling, file loading, and many other convenience functions

Copyright (c) 2021-2025 Andrew Clarke
"""

from . import bindings, dom, js, utilities, subwidgets, imageutils

from urllib.parse import urldefrag, urlparse, urlunparse

import tkinter as tk
from tkinter.ttk import Frame, Style


### TODO: consider better matching the parameters used in stock Tkinter widgets
### And add better support for others (i.e. we could do more with the background/bg keyword)

class HtmlFrame(Frame):
    """TkinterWeb's flagship HTML widget.

    :param master: The parent widget.
    :type master: :py:class:`tkinter.Widget`

    Callbacks:

    :param on_navigate_fail: The function to be called when a url cannot be loaded. The target url, error, and code will be passed as arguments. By default the TkinterWeb error page is shown.
    :type on_navigate_fail: function
    :param on_link_click: The function to be called when a hyperlink is clicked. The target url will be passed as an argument. By default the url is navigated to.
    :type on_link_click: function
    :param on_form_submit: The function to be called when a form is submitted. The target url, data, and method ("GET" or "POST") will be passed as arguments. By default the response is loaded.
    :type on_form_submit: function
    :param on_script: The function to be called when a ``<script>`` element is encountered. This can be used to connect a script handler, such as a JavaScript engine. The script element's attributes and contents will be passed as arguments.
    :type on_script: function
    :param on_element_script: The function to be called when a JavaScript event attribute on an element is encountered. This can be used to connect a script handler, such as a JavaScript engine, or even to run your own Python code. The element's corresponding Tkhtml3 node, relevant attribute, and attribute contents will be passed as arguments. New in version 4.1.
    :type on_element_script: function
    :param on_resource_setup: The function to be called when an image, stylesheet, or script load finishes. The resource's url, type ("image", "stylesheet", or "script"), and whether setup was successful or not (True or False) will be passed as arguments.
    :type on_resource_setup: function
    :param message_func: The function to be called when a debug message is issued. This only works if :attr:`messages_enabled` is set to True. The message will be passed as an argument. By default the message is printed.
    :type message_func: function

    Widget appearance:

    :param visited_links: The list used to determine if a hyperlink should be given the CSS ``:visited`` flag.
    :type visited_links: list
    :param zoom: The page zoom multiplier.
    :type zoom: float
    :param fontscale: The page fontscale multiplier.
    :type fontscale: float
    :param vertical_scrollbar: Show the vertical scrollbar. Consider using the CSS ``overflow`` property on the ``<html>`` or ``<body>`` element instead.
    :type vertical_scrollbar: bool or "auto"
    :param horizontal_scrollbar: Show the horizontal scrollbar. It is usually best to leave this hidden. Consider adding the ``tkinterweb-overflow-x="scroll" | "auto" | "hidden"`` attribute on the ``<html>`` or ``<body>`` element instead.
    :type horizontal_scrollbar: bool or "auto"
    :param shrink: If False, the widget's width and height are set by the width and height options as per usual. You may still need to call ``grid_propagate(0)`` or ``pack_propagate(0)`` for Tkinter to respect the set width and height. If this option is set to True, the widget's requested width and height are determined by the current document.
    :type shrink: bool

    Features:

    :param messages_enabled: Enable/disable messages. This is enabled by default.
    :type messages_enabled: bool
    :param selection_enabled: Enable/disable selection. This is enabled by default.
    :type selection_enabled: bool
    :param caret_browsing_enabled: Enable/disable caret browsing. This is disabled by default. New in version 4.8.
    :type caret_browsing_enabled: bool
    :param stylesheets_enabled: Enable/disable stylesheets. This is enabled by default.
    :type stylesheets_enabled: bool
    :param images_enabled: Enable/disable images. This is enabled by default.
    :type images_enabled: bool
    :param forms_enabled: Enable/disable forms and form elements. This is enabled by default.
    :type forms_enabled: bool
    :param objects_enabled: Enable/disable embedding of ``<object>`` and ``<iframe>`` elements. This is enabled by default.
    :type objects_enabled: bool
    :param caches_enabled: Enable/disable caching. Disabling this option will conserve memory, but will also result in longer page and image reload times. This is enabled by default.
    :type caches_enabled: bool
    :param crash_prevention_enabled: Enable/disable crash prevention. Disabling this option may improve page load speed, but crashes will occur on some websites. This is enabled by default.
    :type crash_prevention_enabled: bool
    :param events_enabled: Enable/disable generation of Tk events. This is enabled by default.
    :type events_enabled: bool
    :param threading_enabled: Enable/disable threading. Has no effect if the Tcl/Tk build does not support threading. This is enabled by default.
    :type threading_enabled: bool
    :param javascript_enabled: Enable/disable JavaScript support. This is disabled by default. Highly experimental. New in version 4.1.
    :type javascript_enabled: bool
    :param image_alternate_text_enabled: Enable/disable the display of alt text for broken images. This is enabled by default.
    :type image_alternate_text_enabled: bool
    :param dark_theme_enabled: Enable/disable dark mode. This feature is a work-in-progress and may cause hangs or crashes on more complex websites.
    :type dark_theme_enabled: bool
    :param image_inversion_enabled: Enable/disable image inversion. If enabled, an algorithm will attempt to detect and invert images with a predominantly light-coloured background. Photographs and dark-coloured images should be left as is. This feature is a work-in-progress and may cause hangs or crashes on more complex websites.
    :type image_inversion_enabled: bool
    :param ignore_invalid_images: If enabled and alt text is disabled or the image has no alt text, a broken image icon will be displayed in place of the image.
    :type ignore_invalid_images: bool

    Widget colors and styling:

    :param about_page_background: The default background color of built-in pages. By default this matches the :py:class:`ttk.Frame` background color to better integrate custom documents with Tkinter.
    :type about_page_background: str
    :param about_page_foreground: The default text color of built-in pages.
    :type about_page_foreground: str
    :param find_match_highlight_color: The highlight color of matches found by :py:func:`find_text()`. 
    :type find_match_highlight_color: str
    :param find_match_text_color: The text color of matches found by :py:func:`find_text()`. 
    :type find_match_text_color: str
    :param find_current_highlight_color: The highlight color of the current match selected by :py:func:`find_text()`. 
    :type find_current_highlight_color: str
    :param find_current_text_color: The text color of the current match selected by :py:func:`find_text()`. 
    :type find_current_text_color: str
    :param selected_text_highlight_color: The highlight color of selected text. 
    :type selected_text_highlight_color: str
    :param selected_text_color: The text color of selected text. 
    :type selected_text_color: str
    :param default_style: The stylesheet used to set the default appearance of HTML elements. It is generally best to leave this setting alone.
    :type default_style: str
    :param dark_style: The additional stylesheet used to set the default appearance of HTML elements when dark mode is enabled. It is generally best to leave this setting alone.
    :type dark_style: str

    Download behaviour:

    :param insecure_https: If True, website certificate errors are ignored. This can be used to work around issues where :py:mod:`ssl` is unable to get a page's certificate on some older Mac systems.
    :type insecure_https: bool
    :param ssl_cafile: Path to a file containing CA certificates. This can be used to work around issues where :py:mod:`ssl` is unable to get a page's certificate on some older Mac systems. New in version 4.5.
    :type ssl_cafile: bool or str
    :param headers: The headers used by urllib's :py:class:`~urllib.request.Request` when fetching a resource.
    :type headers: dict
    :param request_timeout: The number of seconds to wait when fetching a resource before timing out. New in version 4.6.
    :type request_timeout: int

    HTML rendering behaviour:

    :param experimental: If True, experimental features will be enabled. If "auto", experimental features will be enabled if the loaded Tkhtml version supports experimental features. You will need to compile the cutting-edge Tkhtml widget from https://github.com/Andereoo/TkinterWeb-Tkhtml/tree/experimental and replace the default Tkhtml binary for your system with the experimental version. Unless you need to screenshot the full page on Windows or print your page for now it is likely best to use the default Tkhtml binary and leave this setting alone.
    :type experimental: bool or "auto"
    :param use_prebuilt_tkhtml: If True (the default), the Tkhtml binary for your system supplied by TkinterWeb will be used. If your system isn't supported and you don't want to compile the Tkhtml widget from https://github.com/Andereoo/TkinterWeb-Tkhtml yourself, you could try installing Tkhtml3 system-wide and set :attr:`use_prebuilt_tkhtml` to False. Note that some crash prevention features will no longer work.
    :type use_prebuilt_tkhtml: bool
    :param tkhtml_version: The Tkhtml version to use. If the requested version is not found, TkinterWeb will fallback to Tkhtml 3.0. Only one Tkhtml version can be loaded at a time. New in version 4.4.
    :type tkhtml_version: float or "auto"
    :param parsemode: The parse mode. In "html" mode, explicit XML-style self-closing tags are not handled specially and unknown tags are ignored. "xhtml" mode is similar to "html" mode except that explicit self-closing tags are recognized. "xml" mode is similar to "xhtml" mode except that XML CDATA sections and unknown tag names are recognized. It is usually best to leave this setting alone.
    :type parsemode: "xml", "xhtml", or "html"
    :param mode: The rendering engine mode. It is usually best to leave this setting alone.
    :type mode: "standards", "almost standards", or "quirks"

    Other ttk.Frame arguments are also supported.
    
    :raise TypeError: If the value type is wrong and cannot be converted to the correct type."""

    def __init__(self, master, **kwargs):
        # State and settings variables
        self._current_url = ""
        self._previous_url = ""
        self._accumulated_styles = []
        self._waiting_for_reset = False
        self._thread_in_progress = None
        self._prev_height = 0
        self._button = None
        self._style = None

        ### TODO: switch to a TypedDict or something
        self._htmlframe_options = {
            "on_navigate_fail": self.show_error_page,
            "vertical_scrollbar": "auto",
            "horizontal_scrollbar": False,
            "about_page_background": "",
            "about_page_foreground": "",
        }
        self._tkinterweb_options = {
            "on_link_click": self.load_url,
            "on_form_submit": self.load_form_data,
            "on_script": self._on_script,
            "on_element_script": self._on_element_script,
            "on_resource_setup": utilities.placeholder,
            "message_func": utilities.notifier,
            "messages_enabled": True,
            "caret_browsing_enabled": False,
            "selection_enabled": True,
            "stylesheets_enabled": True,
            "images_enabled": True,
            "forms_enabled": True,
            "objects_enabled": True,
            "caches_enabled": True,
            "dark_theme_enabled": False,
            "image_inversion_enabled": False,
            "crash_prevention_enabled": True,
            "events_enabled": True,
            "threading_enabled": True,
            "javascript_enabled": False,
            "image_alternate_text_enabled": True,
            "ignore_invalid_images": True,
            "visited_links": [],
            "find_match_highlight_color": "#f1a1f7",
            "find_match_text_color": "#000",
            "find_current_highlight_color": "#8bf0b3",
            "find_current_text_color": "#000",
            "selected_text_highlight_color": "#9bc6fa",
            "selected_text_color": "#000",
            "default_style": utilities.DEFAULT_STYLE,
            "dark_style": utilities.DARK_STYLE,
            "insecure_https": False,
            "ssl_cafile": None,
            "request_timeout": 15,
            "headers": utilities.HEADERS,
            "experimental": False,
            # No impact after loading
            "use_prebuilt_tkhtml": True,
            "tkhtml_version": "auto",
            # Internal
            "overflow_scroll_frame": None,
            "embed_obj": HtmlFrame,
            "manage_vsb_func": self._manage_vsb,
            "manage_hsb_func": self._manage_hsb,
        }
        self._tkhtml_options = {
            "zoom": 1.0,
            "fontscale": 1.0,
            "parsemode": utilities.DEFAULT_PARSE_MODE,
            "shrink": False,
            "mode": utilities.DEFAULT_ENGINE_MODE,
        }
                            
        for key, value in self._htmlframe_options.items():
            if key in kwargs:
                value = self._check_value(self._htmlframe_options[key], kwargs.pop(key))
                self._htmlframe_options[key] = value
            setattr(self, key, value)

        for key in list(kwargs.keys()):
            if key in self._tkinterweb_options:
                value = self._check_value(self._tkinterweb_options[key], kwargs.pop(key))
                self._tkinterweb_options[key] = value
            elif key in self._tkhtml_options:
                self._tkhtml_options[key] = kwargs.pop(key)

        super().__init__(master, **kwargs)

        # Setup sub-widgets
        self._html = html = bindings.TkinterWeb(self, self._tkinterweb_options, **self._tkhtml_options)
        self._hsb = hsb = subwidgets.AutoScrollbar(self, orient="horizontal", command=html.xview)
        self._vsb = vsb = subwidgets.AutoScrollbar(self, orient="vertical", command=html.yview)

        html.configure(xscrollcommand=hsb.set, yscrollcommand=vsb.set)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        html.grid(row=0, column=0, sticky="nsew")
        hsb.grid(row=1, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="nsew")

        self._manage_hsb()
        self._manage_vsb()

        # html.document only applies to the document it is bound to (which makes things easy)
        # Html applies to all html widgets
        # For some reason, binding to Html only works on Linux/Unix and binding to html.document only works on Windows
        # Html fires on all documents (i.e. <iframe> elements), so it has to be handled slightly differently
        if not self._html.overflow_scroll_frame:
            self.bind_class("Html", "<Button-4>", html.scroll_x11)
            self.bind_class("Html", "<Button-5>", html.scroll_x11)
            self.bind_class("Html", "<Shift-Button-4>", html.xscroll_x11)
            self.bind_class("Html", "<Shift-Button-5>", html.xscroll_x11)

        for i in (f"{html}.document", html.scrollable_node_tag):
            self.bind_class(i, "<MouseWheel>", html.scroll)
            self.bind_class(i, "<Shift-MouseWheel>", html.xscroll)

        self.bind_class(html.scrollable_node_tag, "<Button-4>", lambda event, widget=html: html.scroll_x11(event, widget))
        self.bind_class(html.scrollable_node_tag, "<Button-5>", lambda event, widget=html: html.scroll_x11(event, widget))
        self.bind_class(html.scrollable_node_tag, "<Shift-Button-4>", lambda event, widget=html: html.xscroll_x11(event, widget))
        self.bind_class(html.scrollable_node_tag, "<Shift-Button-5>", lambda event, widget=html: html.xscroll_x11(event, widget))

        # Overwrite the default bindings for scrollbars so that:
        # A) scrolling on the page while loading stops it from tracking the fragment
        # B) scrolling horizontally on a vertical scrollbar scrolls horizontally (the default is to scroll vertically)
        # C) scrolling vertically on a horizontal scrollbar scrolls vertically (the default is to block scrolling)
        for i in (vsb, hsb):
            i.bind("<Button-4>", lambda event, widget=html: html.scroll_x11(event, widget))
            i.bind("<Button-5>", lambda event, widget=html: html.scroll_x11(event, widget))
            i.bind("<MouseWheel>", html.scroll)
            i.bind("<Shift-Button-4>", lambda event, widget=html: html.xscroll_x11(event, widget))
            i.bind("<Shift-Button-5>", lambda event, widget=html: html.xscroll_x11(event, widget))
            i.bind("<Shift-MouseWheel>", html.xscroll)
            i.bind("<Enter>", html._on_leave)

        self.bind("<Leave>", html._on_leave)
        self.bind("<Enter>", html._on_mouse_motion)
        self.bind_class(html.tkinterweb_tag, "<Configure>", self._handle_resize)

    @property
    def title(self):
        """The document's title.

        :rtype: str"""
        return self._html.title
    
    @property
    def icon(self):
        """The document icon's url.
        
        :rtype: str"""
        return self._html.icon
    
    @property
    def current_url(self):
        """The document's url.
        
        :rtype: str"""
        return self._current_url
    
    @property
    def base_url(self):
        """The documents's base url. This is automatically generated from :attr:`~tkinterweb.HtmlFrame.current_url` but will also change if explicitly specified by the document.
        
        :rtype: str"""
        return self._html.base_url
    
    @utilities.lazy_manager(None)
    def document(self):
        """The DOM manager. Use this to access :class:`~tkinterweb.dom.HTMLDocument` methods to manupulate the DOM.
        
        :rtype: :class:`~tkinterweb.dom.HTMLDocument`"""
        return dom.HTMLDocument(self._html)

    @utilities.lazy_manager(None)
    def javascript(self):
        """The JavaScript manager. Use this to access :class:`~tkinterweb.js.JSEngine` methods.
        
        :rtype: :class:`~tkinterweb.js.JSEngine`"""
        return js.JSEngine(self._html, self.document)

    @property
    def html(self):
        """The underlying html widget. Use this to access internal :class:`~tkinterweb.TkinterWeb` methods.
        
        :rtype: :class:`~tkinterweb.TkinterWeb`"""
        return self._html

    def configure(self, **kwargs):
        """
        Change the widget's configuration options. See above for options.
        """
        for key in list(kwargs.keys()):
            if key in self._htmlframe_options:
                value = self._check_value(self._htmlframe_options[key], kwargs.pop(key))
                setattr(self, key, value)
                if key == "vertical_scrollbar":
                    self._manage_vsb(value)
                elif key == "horizontal_scrollbar":
                    self._manage_hsb(value)
            elif key in self._tkinterweb_options:
                value = self._check_value(self._tkinterweb_options[key], kwargs.pop(key))
                setattr(self._html, key, value)
                if key in {"find_match_highlight_color", "find_match_text_color", "find_current_highlight_color",
                           "find_current_text_color", "selected_text_highlight_color", "selected_text_color"}:
                    self._html.selection_manager.update_tags()
            elif key in self._tkhtml_options:
                self._html[key] = kwargs.pop(key)
                if key == "zoom":
                    self._handle_resize(force=True)
                    self._html.caret_manager.update()
                elif key == "fontscale":
                    self._html.caret_manager.update()
        super().configure(**kwargs)

    def config(self, _override=False, **kwargs):
        """
        Change the widget's configuration options. See above for options.
        """
        if _override:
            super().configure(**kwargs)
        else:
            self.configure(**kwargs)

    def cget(self, key):
        """
        Return the value of a given configuration option. See above for options.

        :param key: The configuration option to search for.
        :return: The value of the specified configuration option.
        """
        if key in self._htmlframe_options:
            return getattr(self, key)
        elif key in self._tkinterweb_options.keys():
            return getattr(self._html, key)
        elif key in self._tkhtml_options.keys():
            return self._html.cget(key)
        return super().cget(key)
    
    def bind(self, sequence, *args, **kwargs):
        "Add an event binding. For convenience, some bindings will be bound to this widget and others will be bound to its associated :class:`~tkinterweb.TkinterWeb` instance."
        if sequence in {"<Leave>", "<Enter>"}:
            super().bind(sequence, *args, **kwargs)
        else:
            self._html.bind(sequence, *args, **kwargs)

    def unbind(self, sequence, *args, **kwargs):
        ""
        if sequence in {"<Leave>", "<Enter>"}:
            super().unbind(sequence, *args, **kwargs)
        else:
            self._html.unbind(sequence, *args, **kwargs)
    
    def __getitem__(self, key):
        return self.cget(key)

    def __setitem__(self, key, value):
        self.configure(**{key: value})

    def load_html(self, html_source, base_url=None, fragment=None, _thread_safe=False):
        """Clear the current page and parse the given HTML code.
        
        :param html_source: The HTML code to render.
        :type html_source: str
        :param base_url: The base url to use when parsing stylesheets and images. If this argument is not supplied, it will be set to the current working directory.
        :type base_url: str, optional
        :param fragment: The url fragment to scroll to after the document loads.
        :type fragment: str, optional"""
        self._html.reset(_thread_safe)

        if fragment: fragment = "".join(char for char in fragment if char.isalnum() or char in ("-", "_", ".")).replace(".", r"\.")

        if base_url == None:
            path = utilities.WORKING_DIR
            if not path.startswith("/"):
                path = f"/{path}"
            base_url = f"file://{path}/"
        self._html.base_url = self._current_url = base_url
        self._html.fragment = fragment
        self._html.parse(html_source, _thread_safe)

        if _thread_safe:
            self._html.post_to_queue(self._load_html)
        else:
            self._load_html()
    
    def _load_html(self):
        # NOTE: must be run from main thread
        
        self._finish_css()
        self._handle_resize(force=True)

    def load_file(self, file_url, decode=None, force=False):
        """Convenience method to load a local HTML file.

        This method will always load the file in the main thread. If you want to load the file in a seperate thread, use :meth:`HtmlFrame.load_url`.
        
        :param file_url: The HTML file to render.
        :type file_url: str
        :param decode: The decoding to use when loading the file.
        :type decode: str or None, optional
        :param force: Force the page to reload all elements.
        :type force: bool, optional"""
        self._previous_url = self._current_url
        if not file_url.startswith("file://"):
            file_url = "file://" + str(file_url)
            self._current_url = file_url
            self._html.post_event(utilities.URL_CHANGED_EVENT)
        self._continue_loading(file_url, decode=decode, force=force)

    def load_website(self, website_url, decode=None, force=False):
        """Convenience method to load a website.
        
        :param website_url: The url to load.
        :type website_url: str
        :param decode: The decoding to use when loading the website.
        :type decode: str or None, optional
        :param force: Force the page to reload all elements.
        :type force: bool, optional"""
        self._previous_url = self._current_url
        if (not website_url.startswith("https://")) and (not website_url.startswith("http://")) and (not website_url.startswith("about:")):
            website_url = "http://" + str(website_url)
            self._current_url = website_url
            self._html.post_event(utilities.URL_CHANGED_EVENT)
        self.load_url(website_url, decode, force)

    def load_url(self, url, decode=None, force=False):
        """Loads and renders HTML from the given url. 
        
        A local file will be loaded if the url begins with "file://". 
        A website will be loaded if the url begins with "https://" or "http://". 
        If the url begins with "view-source:", the source code of the webpage will be displayed. 
        Loading "about:tkinterweb" will open a page with debugging information.
        
        :param url: The url to load.
        :type url: str
        :param decode: The decoding to use when loading the url.
        :type decode: str or None, optional
        :param force: Force the page to reload all elements.
        :type force: bool, optional"""
        if not self._current_url == url:
            self._previous_url = self._current_url
        if url in utilities.BUILTIN_PAGES:
            utilities.BUILTIN_PAGES._html = self._html
            return self.load_html(self._get_about_page(url), url)

        self._waiting_for_reset = True

        # Set the base url now in case it takes a while for the website to download
        self._html.base_url = url

        if self._thread_in_progress:
            self._thread_in_progress.stop()
        if self._html.threading_enabled:
            thread = utilities.StoppableThread(target=self._continue_loading, args=(
                url,), kwargs={"decode": decode, "force": force, "thread_safe": True})
            self._thread_in_progress = thread
            thread.start()
        else:
            self._continue_loading(url, decode=decode, force=force)

    def load_form_data(self, url, data, method="GET", decode=None):
        """Submit form data to a server and load the response.
        
        :param url: The url to load.
        :type url: str
        :param data: The data to pass to the server.
        :type data: str
        :param method: The form submission method.
        :type method: "GET" or "POST", optional
        :param decode: The decoding to use when loading the file.
        :type decode: str or None, optional"""
        self._previous_url = self._current_url
        if self._thread_in_progress:
            self._thread_in_progress.stop()
        if self._html.threading_enabled:
            thread = utilities.StoppableThread(
                target=self._continue_loading, args=(url, data, method, decode, True))
            self._thread_in_progress = thread
            thread.start()
        else:
            self._continue_loading(url, data, method, decode)

    def add_html(self, html_source, return_element=False):
        """Parse HTML and add it to the end of the current document. Unlike :meth:`HtmlFrame.load_html`, :meth:`HtmlFrame.add_html` adds rendered HTML code without clearing the original document.
        
        :param html_source: The HTML code to render.
        :type html_source: str
        :param return_element: If True, return the root element of the added HTML.
        :type return_element: :class:`~tkinterweb.dom.HTMLElement`
        :return: :class:`~tkinterweb.dom.HTMLElement` or None"""

        self._previous_url = ""
        #if not self._html.base_url:
        #    path = WORKING_DIR
        #    if not path.startswith("/"):
        #        path = f"/{path}"
        #    base_url = f"file://{path}/"
        #    self._html.base_url = self._current_url = base_url

        if return_element:
            node = self._html.parse_fragment(html_source)
            body = self.document.body.node
            self._html.insert_node(body, node)
            node = dom.HTMLElement(self.document, node)
        else:
            self._html.parse(html_source)
            node = None

        self._finish_css()
        self._handle_resize(force=True)

        return node
    
    def insert_html(self, html_source, index=0, return_element=False):
        """Parse HTML and insert it into the current document.
        
        :param html_source: The HTML code to render.
        :type html_source: str
        :param index: The index of the element to insert before.
        :type index: int
        :param return_element: If True, return the root element of the inserted HTML.
        :type return_element: :class:`~tkinterweb.dom.HTMLElement`
        :return: :class:`~tkinterweb.dom.HTMLElement` or None
        
        New in version 4.4."""

        self._previous_url = ""
        #if not self._html.base_url:
        #    path = WORKING_DIR
        #    if not path.startswith("/"):
        #        path = f"/{path}"
        #    base_url = f"file://{path}/"
        #    self._html.base_url = self._current_url = base_url

        node = self._html.parse_fragment(html_source)
        body = self.document.body.node
        child = self._html.get_node_children(body)[index]
        self._html.insert_node_before(body, node, child)
 
        self._finish_css()
        self._handle_resize(force=True)

        if return_element:
            return dom.HTMLElement(self.document, node)
    
    def add_css(self, css_source):
        """Send CSS stylesheets to the parser. This can be used to alter the appearance of already-loaded documents.
        
        :param css_source: The CSS code to parse.
        :type css_source: str"""
        if self._waiting_for_reset:
            self._accumulated_styles.append(css_source)
        else:
            self._html.parse_css(data=css_source)

    def stop(self):
        """Stop loading this page and abandon all pending requests."""
        if self._thread_in_progress:
            self._thread_in_progress.stop()
        self._html.stop()
        self._current_url = self._previous_url
        self._html.post_event(utilities.URL_CHANGED_EVENT)
        self._html.post_event(utilities.DONE_LOADING_EVENT)

    def find_text(self, text, select=1, ignore_case=True, highlight_all=True, detailed=False):
        """Search the document for text and highlight matches. 
        
        :param text: The Regex expression to use to find text. If this is set to a blank string (""), all highlighted text will be cleared.
        :type text: str
        :param select: The index of the match to select and scroll to.
        :type select: int, optional
        :param ignore_case: If True, uppercase and lowercase letters will be treated as the same character.
        :type ignore_case: bool, optional
        :param highlight_all: If True, all matches will be highlighted.
        :type highlight_all: bool, optional
        :param detailed: If True, this method will also return information on the nodes that were found. See `bug #93 <https://github.com/Andereoo/TkinterWeb/issues/93#issuecomment-2052516492>`_ for more details.
        :type detailed: bool, optional
        :return: The number of matches. If `detailed` is True, also returns selected match's Tkhtml3 node and a list of matching Tkhtml3 nodes.
        :rtype: int | int, Tkhtml3 node, list(Tkhtml3 node)"""
        nmatches, selected, matches = self._html.search_manager.find_text(text, select, ignore_case, highlight_all)
        if detailed:
            return nmatches, selected, matches
        else:
            return nmatches
    
    def widget_to_element(self, widget):
        """Get the HTML element containing the given widget.
        
        :param widget: The widget to search for.
        :type widget: :py:class:`tkinter.Widget`
        :return: The element containing the given widget.
        :rtype: :class:`~tkinterweb.dom.HTMLElement`
        :raise KeyError: If the given widget is not in the document.
        
        New in version 4.2."""
        for node in self._html.search(f"[{self._html.widget_manager.widget_container_attr}]"):
            if self._html.get_node_attribute(node, self._html.widget_manager.widget_container_attr) == str(widget):
                return dom.HTMLElement(self.document, node)
        raise KeyError("the specified widget is not in the document")

    def screenshot_page(self, filename=None, full=False, show=False):
        """Take a screenshot. 
        
        This command should be used with care on large documents if :attr:`full` is set to True, as it may generate very large images that take a long time to create and consume large amounts of memory.

        On Windows, if experimental mode is not enabled, ensure you run ``ctypes.windll.shcore.SetProcessDpiAwareness(1)`` before creating your Tkinter window or else the screenshot may be badly offset. On Windows it's good practice to run this anyway.
        
        :param filename: The file path to save the screenshot to. If None, the image is not saved to the disk.
        :type filename: str or None, optional
        :param full: If True, the entire page is captured. On Windows, experimental mode must be enabled. If False, only the visible content is captured.
        :type full: bool, optional
        :param show: Display the screenshot in the default system handler.
        :type show: bool, optional
        :return: A PIL Image containing the rendered document.
        :rtype: :py:class:`PIL.Image`
        :raise NotImplementedError: If experimental mode is not enabled, :attr:`full` is set to True, and TkinterWeb is running on Windows."""
        if self._html.experimental or utilities.PLATFORM.system != "Windows":
            self._html.post_message(f"Taking a screenshot of {self._current_url}...")
            data = self._html.image(full=full)
            height = len(data)
            width = len(data[0].split())
            image = imageutils.create_RGB_image(data, width, height)
        elif not full:
            # Vanilla Tkhtml image does not work on Windows
            # We use PIL's ImageGrab instead for visible content
            # We could also use this for visible content on other systems
            # It's faster than Tkhtml image, but it does not work on Wayland and is less foolproof
            from PIL import ImageGrab

            x = self.winfo_rootx()
            y = self.winfo_rooty()
            width = self.winfo_width()
            height = self.winfo_height()
            
            image = ImageGrab.grab(bbox=(x, y, x+width, y+height))
        else:
            self._html.post_message("ERROR: A screenshot could not be taken because screenshot_page(full=True) is an experimental feature on Windows")
            raise NotImplementedError("a screenshot could not be taken because screenshot_page(full=True) is an experimental feature on Windows")
        
        if filename:
            image.save(filename)
            self._html.post_message(f"Screenshot taken: {width}px by {height}px!")
        if show:
            image.show()
        return image

    def print_page(self, filename=None, cnf={}, **kwargs):
        """Print the document to a PostScript file. 
        
        This method is experimental and requires experimental mode to be enabled.

        :param filename: The file path to print the page to. If None, the image is not saved to the disk.
        :type filename: str or None, optional
        :param kwargs: Other valid options are colormap, colormode, file, fontmap, height, pageanchor, pageheight, pagesize (can be A3, A4, A5, LEGAL, and LETTER), pagewidth, pagex, pagey, nobg, noimages, rotate, width, x, and y.
        :return: A string containing the PostScript code.
        :rtype: str
        :raise NotImplementedError: If experimental mode is not enabled."""
        if self._html.experimental:
            cnf |= kwargs
            self._html.post_message(f"Printing {self._current_url}...")
            if filename:
                cnf["file"] = filename
            if "pagesize" in cnf:
                pagesizes = {
                    "A3": "842x1191", "A4": "595x842", "A5": "420x595",
                    "Legal": "612x792", "Letter": "612x1008"
                }
                try:
                    cnf["pagesize"] = pagesizes[cnf["pagesize"].upper()]
                    self._html.post_message(f"Setting printer page size to {cnf['pagesize']} PostScript points.")
                except KeyError:
                    raise KeyError("Parameter 'pagesize' must be A3, A4, A5, Legal, or Letter")

            self._html.update() # Update the root window to ensure HTML is rendered
            file = self._html.postscript(cnf)
            
            # No need to save - Tkhtml handles that for us
            if filename:
                self._html.post_message("Printed!")
            if file: return file
        else:
            self._html.post_message("ERROR: The page could not be printed because print_page is an experimental feature")
            raise NotImplementedError("the page could not be printed because print_page is an experimental feature")

    def save_page(self, filename=None):
        """Save the page as an HTML file.
                
        :param filename: The file path to save the page to. If None, the image is not saved to the disk.
        :type filename: str or None, optional
        :return: A string containing the page's HTML/CSS code.
        :rtype: str"""
        self._html.post_message(f"Saving {self._current_url}...")
        html = self.document.documentElement.innerHTML
        if filename:
            with open(filename, "w+") as handle:
                handle.write(html)
            self._html.post_message("Saved!")
        return html
    
    def snapshot_page(self, filename=None, allow_agent=False):
        """Save a snapshot of the document. 
        
        Unlike :py:func:`save_page`, which returns the original document, :py:func:`snapshot_page` returns the page as rendered. ``<link>`` elements are ignored and instead one ``<style>`` element contains all of the necessary CSS information for the document. This can be useful for saving documents for offline use.
                
        :param filename: The file path to save the page to. If None, the image is not saved to the disk.
        :type filename: str or None, optional
        :param allow_agent: If True, CSS properties added by the rendering engine (eg. those affected by the widget's :attr:`default_style` option) are also included.
        :type allow_agent: bool, optional
        :return: A string containing the page's rendered HTML/CSS code.
        :rtype: str"""
        self._html.post_message(f"Snapshotting {self._current_url}...")
        title = ""
        icon = ""
        base = ""
        style = "\n"
        
        for rule in self._html.get_computed_styles():
            selector, prop, origin = rule
            if origin == "agent" and not allow_agent: continue
            style += f"\t\t\t{selector} {{{prop.replace('-tkhtml-no-color', 'transparent')}}}\n"

        if self._html.title: title = f"\n\t\t<title>{self._html.title}</title>"
        if self._html.icon: icon = f"\n\t\t<link rel=\"icon\" type=\"image/x-icon\" href=\"/{self._html.icon}\">"
        if self._html.base_url: base = f"\n\t\t<base href=\"{self._html.base_url}\"></base>"
        if style.strip(): style = f"\n\t\t<style>{style}\t\t</style>"
        body = self.document.body.innerHTML

        html = f"""<html>\n\t<head>{title}{icon}{base}{style}\n\t</head>\n\t<body>\n\t{body}\n\t</body>\n</html>"""
        if filename:
            with open(filename, "w+") as handle:
                handle.write(html)
            self._html.post_message("Saved!")
        return html
    
    def get_page_text(self):
        """Return the page's text content.
        
        :return: A string containing the page's text content.
        :rtype: str
        
        New in version 4.8."""
        return self._html.text("text")
    
    def show_error_page(self, url, error, code):
        """Show the error page.
        
        :param url: The url of the broken page.
        :type url: str
        :param error: The error message.
        :type error: str
        :param code: The HTTP error code.
        :type code: str
        """
        if self.winfo_exists():
            if not self._button:
                self._button = tk.Button(self, text="Try Again")
            self._button.configure(command=lambda url=self._current_url: self.load_url(url, None, True))
            self.load_html(self._get_about_page("about:error", code, self._button), url)

    def resolve_url(self, url):
        """Generate a full url from the specified url. This can be used to generate full urls when given a relative url.

        :param url: The url to modify if needed.
        :type url: str
        :return: The full, resolved url.
        :rtype: str"""
        return self._html.resolve_url(url)

    def yview(self, *args):
        """Adjust the viewport. 
        
        This method uses the standard interface copied from other built-in scrollable Tkinter widgets. Additionally, if a Tkhtml3 node is supplied as an argument, the document will scroll to the top of the given node."""
        self._html.yview(*args)

    def yview_moveto(self, number):
        """Moves the view vertically to the specified position.
        
        :param number: The position to scroll to.
        :type number: float"""
        self._html.yview_moveto(number)

    def yview_scroll(self, number, what):
        """Shifts the view in up or down.
        
        :param number: Specifies the number of 'whats' to scroll by; make positive to scroll down or negative to scroll up.
        :type number: int
        :param what: Either "units" or "pages"
        :type what: str"""
        self._html.yview_scroll(number, what)
        
    def get_currently_hovered_element(self, ignore_text_nodes=True):
        """Get the element under the mouse. Particularly useful for creating right-click menus or displaying hints when the mouse moves.
        
        :param ignore_text_nodes: If True, text nodes (i.e. the contents of a ``<p>`` element) will be ignored and their parent node returned. It is generally best to leave leave this at the default.
        :type ignore_text_nodes: bool, optional
        :return: The element under the mouse.
        :rtype: :class:`~tkinterweb.dom.HTMLElement`"""
        node = self._html.current_hovered_node
        if ignore_text_nodes:
            if not self._html.get_node_tag(self._html.current_hovered_node):
                node = self._html.get_node_parent(self._html.current_hovered_node)
        return dom.HTMLElement(self.document, node)
    
    def get_caret_position(self):
        """Get the position of the caret. This can be used to modify the document's text when the user types. 
        
        :return: The :class:`~tkinterweb.dom.HTMLElement` under the caret, the text content of that element, and an index representing the position in that string that the caret is at. If the caret is not visible, this method will return None
        :rtype: :class:`~tkinterweb.dom.HTMLElement`, str, int or None
        
        The element returned will always be a text node. If you need to change the style or HTML content of a text node you will first need to get its parent.
        
        New in version 4.8."""
        if self._html.caret_manager.node:
            _, pre_text, index = self._html.tkhtml_offset_to_text_index(self._html.caret_manager.node, self._html.caret_manager.offset)
            return dom.HTMLElement(self.document, self._html.caret_manager.node), pre_text, index
        else:
            return None
        
    def get_caret_page_position(self):
        """Get the position of the caret, as an index relative to the page text content. Get the page's text content via :meth:`HtmlFrame.get_page_text`.

        :return: An index representing the position in the page’s text content that the caret is at. If the caret is not visible, this method will return None
        :rtype: int or None
        
        New in version 4.8."""
        if self._html.caret_manager.node:
            return self._html.text("text"), self._html.text("offset", self._html.caret_manager.node, self._html.caret_manager.offset)
        else:
            return None
        
    def set_caret_position(self, element, index):
        """Set the position of the caret, given an HTML element and text index. The given element must contain text and be visible.
        
        If the given index extends out of the bounds of the given element, the caret will be moved into the preceeding or following elements.
        
        :param element: Specifies the element to place the caret over.
        :type element: :class:`~tkinterweb.dom.HTMLElement`
        :param index: The index in the element's text content to place the caret at.
        :type index: int

        :raise RuntimeError: If caret browsing is disabled or the given element is empty or has been removed.
        
        New in version 4.8."""
        if not self._html.caret_browsing_enabled:
            # This is here not because things break when caret browsing is disabled,
            # But because I bet someone somewhere is trying to set the caret's position
            # With caret browsing disabled and pulling their hair out over it
            raise RuntimeError("cannot modify the caret when caret browsing is disabled")

        text, pre_text, offset = self._html.tkhtml_offset_to_text_index(element.node, index, True)
        if not self._html.bbox(element.node):
            raise RuntimeError(f"the element {element} is not visible.")
        if text == "":
            raise RuntimeError(f"the element {element} is empty. Either provide a different element or set the caret's position using set_caret_page_position.")
        self._html.caret_manager.set(element.node, offset, recalculate=True)

    def set_caret_page_position(self, index):
        """Set the position of the caret given a text index. This can be useful if a specific HTML element is not known (i.e. if known HTML elements have been removed).

        :param index: The index in the page's text content to place the caret at.
        :type index: int

        :raise RuntimeError: If caret browsing is disabled.
        
        New in version 4.8."""
        if not self._html.caret_browsing_enabled:
            raise RuntimeError("cannot modify the caret when caret browsing is disabled")

        if self._html.caret_manager.node:
            self._html.caret_manager.set(None, index, recalculate=True)

    def shift_caret_left(self):
        """Shift the caret left. 
        If the caret is at the beginning of a node, this method will move the caret to the end of the previous text node.

        :raise RuntimeError: If caret browsing is disabled.
        
        New in version 4.8."""
        if not self._html.caret_browsing_enabled:
            raise RuntimeError("cannot shift the caret when caret browsing is disabled")
        
        self._html.caret_manager.shift_left()

    def shift_caret_right(self):
        """Shift the caret right. 
        If the caret is at the end of a node, this method will move the caret to the beginning of the next text node.

        :raise RuntimeError: If caret browsing is disabled.
        
        New in version 4.8."""
        if not self._html.caret_browsing_enabled:
            raise RuntimeError("cannot shift the caret when caret browsing is disabled")
        
        self._html.caret_manager.shift_right()

    def get_selection_position(self):
        """Get the start position, end position, and contained elements of selected text.
        
        :return: 
            - A tuple containing:
                - The :class:`~tkinterweb.dom.HTMLElement` containing the start of the selection
                - The text content of that element
                - An index representing the position in that string that the selection begins at
            - A second tuple containing:
                - The :class:`~tkinterweb.dom.HTMLElement` containing the end of the selection
                - The text content of that element
                - An index representing the position in that string that the selection ends at
            - A list containing an :class:`~tkinterweb.dom.HTMLElement` for each other element under the selection, in sequencial order.

            If no selection is found, this method will return None
            
        :rtype: A pair of (:class:`~tkinterweb.dom.HTMLElement`, str, int) tuples and a list of :class:`~tkinterweb.dom.HTMLElement` objects, or None

        The elements returned will always be text nodes. If you need to change the style or HTML content of a text node you will first need to get its parent.
        
        New in version 4.8."""

        if self._html.selection_manager.selection_start_node and self._html.selection_manager.selection_end_node:
            if self._html.selection_manager.selection_start_node != self._html.selection_manager.selection_end_node:
                start_index = self._html.text("offset", self._html.selection_manager.selection_start_node, self._html.selection_manager.selection_start_offset)
                end_index = self._html.text("offset", self._html.selection_manager.selection_end_node, self._html.selection_manager.selection_end_offset)
                true_start_index, true_end_index = sorted([start_index, end_index])

                if start_index == true_start_index: # ensure that the output is independent of selection direction
                    start_node, end_node = self._html.selection_manager.selection_start_node, self._html.selection_manager.selection_end_node
                    start_offset, end_offset = self._html.selection_manager.selection_start_offset, self._html.selection_manager.selection_end_offset
                else:
                    start_node, end_node = self._html.selection_manager.selection_end_node, self._html.selection_manager.selection_start_node
                    start_offset, end_offset = self._html.selection_manager.selection_end_offset, self._html.selection_manager.selection_start_offset
                
                _, pre_text, index = self._html.tkhtml_offset_to_text_index(start_node, start_offset)
                _, pre_text2, index2 = self._html.tkhtml_offset_to_text_index(end_node, end_offset)

                contained_nodes = []
                excluded_nodes = {dom.extract_nested(start_node), dom.extract_nested(end_node)}
                page_index = true_start_index
                for page_index in range(true_start_index, true_end_index + 1):
                    node, offset = self._html.text("index", page_index)
                    if node not in contained_nodes and dom.extract_nested(node) not in excluded_nodes:
                        contained_nodes.append(node)

                return (
                    (dom.HTMLElement(self.document, start_node), pre_text, index),
                    (dom.HTMLElement(self.document, end_node), pre_text2, index2),
                    list(dom.HTMLElement(self.document, node) for node in contained_nodes),
                )
            else:
                element = dom.HTMLElement(self.document, self._html.selection_manager.selection_start_node)
                start_offset, end_offset = sorted([self._html.selection_manager.selection_start_offset, self._html.selection_manager.selection_end_offset])
                _, pre_text, index = self._html.tkhtml_offset_to_text_index(self._html.selection_manager.selection_start_node, start_offset)
                _, pre_text2, index2 = self._html.tkhtml_offset_to_text_index(self._html.selection_manager.selection_start_node, end_offset)
                return (
                    (element, pre_text, index),
                    (element, pre_text2, index2),
                    [],
                ) 
        else:
            return None
        
    def get_selection_page_position(self):
        """Get the start and end position of selected text, as indexes relative to the page's text content.

        :return: Two indexes representing the selection's start and end positions in that string. If no selection is found, this method will return None.
        :rtype: int, int or None
        
        New in version 4.8."""
        if self._html.selection_manager.selection_start_node and self._html.selection_manager.selection_end_node:
            start_index = self._html.text("offset", self._html.selection_manager.selection_start_node, self._html.selection_manager.selection_start_offset)
            end_index = self._html.text("offset", self._html.selection_manager.selection_end_node, self._html.selection_manager.selection_end_offset)
            start_index, end_index = tuple(sorted([start_index, end_index]))
            return start_index, end_index
        else:
            return None
        
    def set_selection_position(self, start_element, start_index, end_element, end_index):
        """Set the current selection, given a starting and ending HTML element and text index. The given elements must contain text and be visible.
        
        :param start_element: Specifies the element to begin the selection in.
        :type start_element: :class:`~tkinterweb.dom.HTMLElement`
        :param start_index: The index in the element's text content to begin the selection at.
        :type start_index: int
        :param end_element: Specifies the element to end the selection in.
        :type end_element: :class:`~tkinterweb.dom.HTMLElement`
        :param end_index: The index in the element's text content to end the selection at.
        :type end_index: int

        :raise RuntimeError: If selection is disabled or the given elements are empty or have been removed.
        
        New in version 4.8."""
        if not self._html.selection_enabled:
            raise RuntimeError("cannot modify the selection when selection is disabled")

        text, _, start_offset = self._html.tkhtml_offset_to_text_index(start_element.node, start_index, True)
        text2, _, end_offset = self._html.tkhtml_offset_to_text_index(end_element.node, end_index, True)

        texts = {start_element: text, end_element: text2}

        for element in {start_element, end_element}:
            if not self._html.bbox(element.node):
                raise RuntimeError(f"the element {element} is not visible.")
            if texts[element] == "":
                raise RuntimeError(f"the element {element} is empty. Either provide a different element or set the selection using set_selection_page_position.")

        self._html.selection_manager.reset_selection_type()
        self._html.selection_manager.begin_selection(start_element.node, start_offset)
        self._html.selection_manager.extend_selection(end_element.node, end_offset)

    def set_selection_page_position(self, start_index, end_index):
        """Set the current selection, given two text indexes. This can be useful if specific HTML elements are not known (i.e. if known HTML elements have been removed).
        
        :param start_index: The index in the pages's text content to begin the selection at.
        :type start_index: int
        :param end_index: The index in the page's text content to end the selection at.
        :type end_index: int

        :raise RuntimeError: If selection is disabled.
        
        New in version 4.8."""
        if not self._html.selection_enabled:
            raise RuntimeError("cannot modify the selection when selection is disabled")

        start_node, start_offset = self._html.text("index", start_index)
        end_node, end_offset = self._html.text("index", end_index)
        self._html.selection_manager.reset_selection_type()
        self._html.selection_manager.begin_selection(start_node, start_offset)
        self._html.selection_manager.extend_selection(end_node, end_offset)

    def get_selection(self):
        """Return any selected text.

        :return: The current selection.
        :rtype: str"""
        return self._html.selection_manager.get_selection()

    def clear_selection(self):
        """Clear the current selection."""
        self._html.selection_manager.clear_selection()

    def select_all(self):
        """Select all text in the document."""
        if not self._html.selection_enabled:
            raise RuntimeError("cannot set the selection when selection is disabled")

        self._html.selection_manager.select_all()

    # --- Internals -----------------------------------------------------------

    def _check_value(self, old, new):
        """Ensure new configuration option values are a valid type."""
        expected_type = type(old)
        if old == None and isinstance(new, tk.Widget):
            return new
        elif old == None:
            if (not callable(new)) and (new != None):
                raise TypeError(f"expected callable object, got \"{new}\"")
        elif callable(old):
            if not callable(new):
                raise TypeError(f"expected callable object, got \"{new}\"")
        elif not isinstance(new, expected_type) and old != "auto" and new != "auto":
            try:
                new = expected_type(new)
            except (TypeError, ValueError,):
                raise TypeError(f"expected {expected_type.__name__}, got \"{new}\"")
        return new
    
    def _handle_resize(self, event=None, force=False):
        """Make all elements with the 'tkinterweb-full-page' attribute the same height as the html widget.
        This can be used in conjunction with table elements to vertical align pages,
        which is otherwise not possible with Tkhtml. Hopefully we won't need this forever."""
        if event:
            height = event.height
        else:
            height = self._html.winfo_height()
        if self._prev_height != height or force:
            resizeable_elements = self._html.search(f"[{utilities.BUILTIN_ATTRIBUTES['vertical-align']}]")
            for node in resizeable_elements:
                self._html.set_node_property(node, "height", f"{height/self['zoom']}px")
        self._prev_height = height

        if self._html.caret_browsing_enabled:
            self._html.caret_manager.update()

    def _manage_vsb(self, allow=None, check=False):
        "Show or hide the scrollbars."
        if check:
            return self._vsb.scroll
        
        if allow == None:
            allow = self.vertical_scrollbar
        if allow == "auto":
            allow = 2
        self._vsb.set_type(allow, *self._html.yview())
        return allow
    
    def _manage_hsb(self, allow=None, check=False):
        "Show or hide the scrollbars."
        if check:
            return self._hsb.scroll

        if allow == None:
            allow = self.horizontal_scrollbar
        if allow == "auto":
            allow = 2
        self._hsb.set_type(allow, *self._html.xview())
        return allow

    def _get_about_page(self, url, i1="", i2=""):
        if not self.about_page_background: 
            if not self._style: self._style = Style()
            self.about_page_background = self._style.lookup('TFrame', 'background')
        if not self.about_page_foreground: 
            if not self._style: self._style = Style()
            self.about_page_foreground = self._style.lookup('TFrame', 'foreground')

        return utilities.BUILTIN_PAGES[url].format(bg=self.about_page_background, fg=self.about_page_foreground, i1=i1, i2=i2)

    def _continue_loading(self, url, data="", method="GET", decode=None, force=False, thread_safe=False):
        "Finish loading urls and handle URI fragments."
        # NOTE: this method is thread-safe and is designed to run in a thread

        code = 404
        self._current_url = url

        self._html.post_event(utilities.DOWNLOADING_RESOURCE_EVENT, True)
        
        try:
            method = method.upper()
            parsed = urlparse(url)

            if method == "GET":
                url = str(url) + str(data)

            fragment = parsed.fragment

            # Workaround for Bug #40, where urllib.urljoin constructs improperly formatted urls on Linux when url starts with file:///
            # As a side effect, this also makes it possible to load files even when given the wrong number of slashes
            if parsed.scheme == "file":
                path = parsed.path.lstrip("/\\")
                netloc = parsed.netloc.lstrip("/\\")
                if netloc:
                    url = urlunparse(("file", "/" + netloc, path, "", "", ""))
                else:
                    url = urlunparse(("file", "", "/" + path, "", "", ""))
                self._current_url = url
                self._html.post_event(utilities.URL_CHANGED_EVENT)

            # If url is different than the current one, load the new site
            if force or (method == "POST") or ((urldefrag(url)[0]).replace("/", "") != (urldefrag(self._previous_url)[0]).replace("/", "")):
                view_source = False
                if url.startswith("view-source:"):
                    view_source = True
                    url = url.replace("view-source:", "")
                    parsed = urlparse(url)

                location = parsed.netloc if parsed.netloc else parsed.path
                self._html.post_message(f"Connecting to {location}", True)
                if self._html.insecure_https: self._html.post_message("WARNING: Using insecure HTTPS session", True)
                
                data, newurl, filetype, code = self._html.download_url(url, data, method, decode)
                self._html.post_message(f"Successfully connected to {location}", True)

                if utilities.get_current_thread().isrunning():
                    if view_source:
                        newurl = "view-source:"+newurl
                        if self._current_url != newurl:
                            self._current_url = newurl
                            self._html.post_event(utilities.URL_CHANGED_EVENT, True)
                        data = str(data).replace("<","&lt;").replace(">", "&gt;")
                        data = data.splitlines()
                        length = int(len(str(len(data))))
                        if len(data) > 1:
                            data = "</code><br><code>".join(data)
                            data = data.rsplit("<br><code>", 1)[0]
                            data = data.split("</code><br>", 1)[1]
                        else:
                            data = "".join(data)
                        text = self._get_about_page("about:view-source", length*9, data)
                        self.load_html(text, newurl, _thread_safe=thread_safe)
                    elif "image" in filetype:
                        name = self._html.image_manager.allocate_image_name()
                        if name:
                            data, data_is_image = self._html.image_manager.check_images(data, name, url, filetype)
                            self._html.post_to_queue(lambda data=data, name=name, url=url, filetype=filetype, data_is_image=data_is_image: self._finish_loading_image(data, name, url, filetype, data_is_image))
                        else:
                            self.load_html(self._get_about_page("about:image", name), newurl, _thread_safe=thread_safe)
                    else:
                        if self._current_url != newurl:
                            self._current_url = newurl
                            self._html.post_event(utilities.URL_CHANGED_EVENT, True)
                        self.load_html(data, newurl, fragment, _thread_safe=thread_safe)
            else:
                # If no requests need to be made, we can signal that the page is done loading, handle fragments, etc.
                self._html.fragment = fragment
                self._html.post_to_queue(self._finish_loading_nothing)
        except Exception as error:
            self._html.post_to_queue(lambda url=url, error=error, code=code: self._finish_loading_error(url, error, code))

        self._thread_in_progress = None

    def _finish_loading_image(self, data, name, url, filetype, data_is_image):
        # NOTE: must be run in main thread
        # Inject the image into the webpage, as it has already been downloaded

        if self._current_url != url:
            self._html.post_event(utilities.URL_CHANGED_EVENT)
        text = self._get_about_page("about:image", name)
        self._html.image_manager.finish_fetching_images(None, data, name, url, filetype, data_is_image)
        self.load_html(text, url)
    
    def _finish_loading_nothing(self):
        # NOTE: must be run in main thread

        self._html._handle_load_finish()
        self._finish_css()
    
    def _finish_loading_error(self, url, error, code):
        # NOTE: must be run in main thread

        self._html.post_message(f"ERROR: could not load {url}: {error}")
        if "CERTIFICATE_VERIFY_FAILED" in str(error):
            self._html.post_message(f"Check that you are using the right url scheme. Some websites only support http.\n\
This might also happen if your Python distribution does not come installed with website certificates.\n\
This is a known Python bug on older MacOS systems. \
Running something along the lines of \"/Applications/Python {'.'.join(utilities.PYTHON_VERSION[:2])}/Install Certificates.command\" (with the qoutes) to install the missing certificates may do the trick.\n\
Otherwise, use 'HtmlFrame(master, insecure_https=True)' to ignore website certificates or 'HtmlFrame(master, ssl_cafile=[path_to_your_cafile])' to specify the path to your CA file if you know where it is.")
        self.on_navigate_fail(url, error, code)

    def _finish_css(self):     
        ## TODO: consider handling add_html/insert_html this way too   
        if self._waiting_for_reset:
            self._waiting_for_reset = False
            for style in self._accumulated_styles:
                self.add_css(style)
            self._accumulated_styles = []

    def register_JS_object(self, name, obj):
        utilities.deprecate("register_JS_object", "javascript", "register")
        return self.javascript.register(name, obj)
    
    def _on_script(self, attributes, tag_contents):
        self.javascript._on_script(attributes, tag_contents)

    def _on_element_script(self, node_handle, attribute, attr_contents):
        self.javascript._on_element_script(node_handle, attribute, attr_contents)


class HtmlLabel(HtmlFrame):
    """The :class:`HtmlLabel` widget is a label-like HTML widget. It inherits from the :class:`HtmlFrame` class. 
    
    For a complete list of avaliable methods, properties, configuration options, and generated events, see the :class:`HtmlFrame` docs.
    
    This widget also accepts two additional parameters:

    :param text: The HTML content of the widget
    :type text: str
    :param style: The CSS code of the widget
    :type style: str
    """

    def __init__(self, master, text="", style="", **kwargs):
        HtmlFrame.__init__(self, master, vertical_scrollbar=False, shrink=True, **kwargs)

        tags = list(self._html.bindtags())
        tags.remove("Html")
        self._html.bindtags(tags)

        self.style = style

        if text:
            self.load_html(text)
        if style:
            self.add_css(style)
        
    def configure(self, **kwargs):
        ""
        if "text" in kwargs:
            self.load_html(kwargs.pop("text"))
            if "style" not in kwargs:
                self.add_css(self.style)
        if "style" in kwargs:
            self.style = style = kwargs.pop("style")
            self.add_css(style)
        if kwargs: super().configure(**kwargs)

    def cget(self, key):
        ""
        if "text" == key:
            return "".join(self._html.serialize_node(0).splitlines())
        elif "style" == key:
           return "".join(self._html.serialize_node_style(0).splitlines())
        return super().cget(key)

    def config(self, **kwargs):
        ""
        self.configure(**kwargs)

class HtmlText(HtmlFrame):
    """The :class:`HtmlText` widget is a text-like HTML widget. It inherits from the :class:`HtmlFrame` class. 
    
    For a complete list of avaliable methods, properties, configuration options, and generated events, see the :class:`HtmlFrame` docs.

    The intent of this class is to eventually mimic the Tkinter Text widget API. 

    This widget accepts the following :py:class:`tk.Text` parameters:

    :param selectbackground:
    :type selectbackground: str
    :param selectforeground:
    :type selectforeground: str
    :param insertontime:
    :type insertontime: int
    :param insertofftime:
    :type insertofftime: int
    :param insertwidth:
    :type insertwidth: int
    :param insertbackground:
    :type insertbackground: str
    """

    def __init__(self, master, selectbackground="#9bc6fa", selectforeground="#000", insertontime=600, insertofftime=300, insertwidth=1, insertbackground=None, **kwargs):
        if "caret_browsing_enabled" in kwargs:
            raise RuntimeError("caret browsing is always enabled in this widget")

        HtmlFrame.__init__(self, master, caret_browsing_enabled=True, **kwargs)
        
        insertontime = self._check_value(self._html.caret_manager.blink_delays[0], insertontime)
        insertofftime = self._check_value(self._html.caret_manager.blink_delays[1], insertofftime)
        insertwidth = self._check_value(self._html.caret_manager.caret_width, insertwidth)

        self._html.caret_manager.blink_delays = [insertontime, insertofftime]
        self._html.caret_manager.caret_width = insertwidth
        self._html.caret_manager.caret_colour = insertbackground
        self._html.selected_text_highlight_color = selectbackground
        self._html.selected_text_color = selectforeground

    def configure(self, **kwargs):
        ""
        if "caret_browsing_enabled" in kwargs:
            raise RuntimeError("caret browsing is always enabled in this widget")
        if "selectbackground" in kwargs:
            self._html.selected_text_highlight_color = kwargs.pop("selectbackground")
            self._html.selection_manager.update_tags()
        if "selectforeground" in kwargs:
            self._html.selected_text_color = kwargs.pop("selectforeground")
            self._html.selection_manager.update_tags()
        if "insertontime" in kwargs:
            value = self._check_value(self._html.caret_manager.blink_delays[0], kwargs.pop("insertontime"))
            self._html.caret_manager.blink_delays[0] = value
        if "insertofftime" in kwargs:
            value = self._check_value(self._html.caret_manager.blink_delays[1], kwargs.pop("insertofftime"))
            self._html.caret_manager.blink_delays[1] = value
        if "insertwidth" in kwargs:
            value = self._check_value(self._html.caret_manager.caret_width, kwargs.pop("insertwidth"))
            self._html.caret_manager.caret_width = value
        if "insertbackground" in kwargs:
            self._html.caret_manager.caret_colour = kwargs.pop("insertbackground")
        if kwargs: super().configure(**kwargs)

    def cget(self, key):
        ""
        if "selectbackground" == key:
            return self._html.selected_text_highlight_color
        elif "selectforeground" == key:
            return self._html.selected_text_color
        elif "insertontime" == key:
            return self._html.caret_manager.blink_delays[0]
        elif "insertofftime" == key:
            return self._html.caret_manager.blink_delays[1]
        elif "insertwidth" == key:
            return self._html.caret_manager.caret_width
        elif "insertbackground" == key:
            return self._html.caret_manager.caret_colour
        return super().cget(key)

    def config(self, **kwargs):
        ""
        self.configure(**kwargs)

    ### TODO: add more methods

class HtmlParse(HtmlFrame):
    """The :class:`HtmlParse` class parses HTML but does not spawn a widget. It inherits from the :class:`HtmlFrame` class. 
    
    For a complete list of avaliable methods, properties, configuration options, and generated events, see the :class:`HtmlFrame` docs.
    
    New in version 4.4."""
    def __init__(self, **kwargs):
        self.root = root = tk.Tk()

        self._is_destroying = False

        for flag in ["events_enabled", "images_enabled", "forms_enabled"]:
            if flag not in kwargs:
                kwargs[flag] = False
                
        HtmlFrame.__init__(self, root, **kwargs)

        root.withdraw()

    def destroy(self):
        super().destroy()
        self.root.destroy()