"""
Widgets that expand on the functionality of the basic bindings
by adding scrolling, file loading, and many other convenience functions

Copyright (c) 2021-2025 Andrew Clarke
"""

from . import bindings, dom, js, utilities, subwidgets, imageutils

from urllib.parse import urldefrag, urlparse, urlunparse

import tkinter as tk
from tkinter.ttk import Frame, Style


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

    Widget appearance:

    :param visited_links: The list used to determine if a hyperlink should be given the CSS ``:visited`` flag.
    :type visited_links: list
    :param zoom: The page zoom multiplier.
    :type zoom: float
    :param fontscale: The page fontscale multiplier.
    :type fontscale: float
    :param defaultstyle: The default stylesheet to use when parsing HTML. Use caution when changing this setting. The default is ``tkintereb.utilities.DEFAULT_STYLE``.
    :type defaultstyle: str

    Widget sizing and overflow:

    :param vertical_scrollbar: Show the vertical scrollbar. You can also set the CSS ``overflow`` property on the ``<html>`` or ``<body>`` element instead.
    :type vertical_scrollbar: bool, "auto", or "dynamic"
    :param horizontal_scrollbar: Show the horizontal scrollbar. It is usually best to leave this hidden. You can also set the ``tkinterweb-overflow-x="scroll" | "auto" | "hidden"`` attribute on the ``<html>`` or ``<body>`` element instead.
    :type horizontal_scrollbar: bool, "auto", or "dynamic"
    :param shrink: If False, the widget's width and height are set by the width and height options as per usual. If this option is set to True, the widget's width and height are determined by the current document.
    :type shrink: bool
    param textwrap: Determines whether text is allowed to wrap. This is similar to the CSS ``text-wrap: normal | nowrap`` property, but more forceful. By default, wrapping will be disabled when shrink is True and will be enabled when shrink is False. Make sure the tkinterweb-tkhtml-extras package is installed; this is only partially supported in Tkhtml version 3.0. New in version 4.17.
    :type textwrap: bool or "auto"
    
    Debugging:

    :param messages_enabled: Enable/disable messages. This is enabled by default.
    :type messages_enabled: bool
    :param message_func: The function to be called when a debug message is issued. This only works if :attr:`messages_enabled` is set to True. The message will be passed as an argument. By default the message is printed.
    :type message_func: function

    Features:

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
    :param caches_enabled: Enable/disable caching. Disabling this option will conserve memory, but will also result in longer page and image reload times. This is enabled by default. Largely for debugging.
    :type caches_enabled: bool
    :param crash_prevention_enabled: Enable/disable crash prevention. In older Tkhtml versions, disabling this option may improve page load speed, but crashes will occur on some websites. This is enabled by default. Largely for debugging.
    :type crash_prevention_enabled: bool
    :param events_enabled: Enable/disable generation of Tk events. This is enabled by default. Largely for debugging.
    :type events_enabled: bool
    :param threading_enabled: Enable/disable threading. Has no effect if the Tcl/Tk build does not support threading. This is enabled by default. Largely for debugging.
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

    Widget colours and styling:

    :param find_match_highlight_color: The background colour of matches found by :py:func:`find_text()`. 
    :type find_match_highlight_color: str
    :param find_match_text_color: The foreground colour of matches found by :py:func:`find_text()`. 
    :type find_match_text_color: str
    :param find_current_highlight_color: The background colour of the current match selected by :py:func:`find_text()`. 
    :type find_current_highlight_color: str
    :param find_current_text_color: The foreground colour of the current match selected by :py:func:`find_text()`. 
    :type find_current_text_color: str
    :param selected_text_highlight_color: The background colour of selected text. 
    :type selected_text_highlight_color: str
    :param selected_text_color: The foreground colour of selected text. 
    :type selected_text_color: str

    Download behaviour:

    :param insecure_https: If True, website certificate errors are ignored. This can be used to work around issues where :py:mod:`ssl` is unable to get a page's certificate on some older Mac systems.
    :type insecure_https: bool
    :param ssl_cafile: Path to a file containing CA certificates. This can be used to work around issues where :py:mod:`ssl` is unable to get a page's certificate on some older Mac systems. New in version 4.5.
    :type ssl_cafile: bool or str
    :param headers: The headers used by urllib's :py:class:`~urllib.request.Request` when fetching a resource.
    :type headers: dict
    :param request_timeout: The number of seconds to wait when fetching a resource before timing out. New in version 4.6.
    :type request_timeout: int
    :param request_func: The function to be called when a resource is requested. This overrides all other download settings. The callback must accept the following arguments: the resource's url, data, method ("GET" or "POST"), and encoding. The callback must return the following: url, data, file type, and HTTP code.
    :type request_func: function

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

    Other ttk.Frame arguments, such as ``width``, ``height``, and ``style`` are also supported.
    
    :raise TypeError: If the value type is wrong and cannot be converted to the correct type."""

    def __init__(self, master, *, zoom = 1.0, fontscale = 1.0, messages_enabled = True, vertical_scrollbar = "dynamic", horizontal_scrollbar = False, \
                    on_navigate_fail = None, on_link_click = None, on_form_submit = None, on_script = None, on_element_script = None, on_resource_setup = None, \
                    message_func = utilities.notifier, request_func = None, caret_browsing_enabled = False, selection_enabled = True, \
                    stylesheets_enabled = True, images_enabled = True, forms_enabled = True, objects_enabled = True, caches_enabled = True, \
                    dark_theme_enabled = False, image_inversion_enabled = False, javascript_enabled = False, events_enabled = True, \
                    threading_enabled = True, crash_prevention_enabled = True, image_alternate_text_enabled = True, ignore_invalid_images = True, \
                    visited_links = [], find_match_highlight_color = "#f1a1f7", find_match_text_color = "#000", find_current_highlight_color = "#8bf0b3", \
                    find_current_text_color = "#000", selected_text_highlight_color = "#9bc6fa", selected_text_color = "#000", \
                    insecure_https = False, ssl_cafile = None, request_timeout = 15, headers = utilities.HEADERS, experimental = False, \
                    use_prebuilt_tkhtml = True, tkhtml_version = "", parsemode = utilities.DEFAULT_PARSE_MODE, \
                    shrink = False, textwrap="auto", mode = utilities.DEFAULT_ENGINE_MODE, defaultstyle = "", height = 0, width = 0, **kwargs):
        
        # State and settings variables
        self._current_url = ""
        self._previous_url = ""
        self._accumulated_styles = []
        self._waiting_for_reset = False
        self._thread_in_progress = None
        self._prev_height = 0
        self._prev_configure = ()
        self._button = None
        self._style = None

        # Deprecations
        self._check_deprecations(**kwargs)

        ### TODO: it would be really nice to better match the parameters, function names, and events used in stock Tkinter widgets
        ### Not really reasonable at this point

        # Before I had kwargs mapped directly do these dicts, but then autocomplete didn't work
        # Probably I just need fewer options.
        self._htmlframe_options = {
            "on_navigate_fail": self.show_error_page if on_navigate_fail is None else on_navigate_fail,
            "vertical_scrollbar": vertical_scrollbar,
            "horizontal_scrollbar": horizontal_scrollbar,
            "unshrink": False,
            "about_page_background": kwargs.pop("about_page_background", ""), # will be removed
            "about_page_foreground": kwargs.pop("about_page_foreground", "") # will be removed
        }
        self._tkinterweb_options = {
            "on_link_click": self.load_url if on_link_click is None else on_link_click,
            "on_form_submit": self.load_form_data if on_form_submit is None else on_form_submit,
            "on_script": self._on_script if on_script is None else on_script ,
            "on_element_script": self._on_element_script if on_element_script is None else on_element_script,
            "on_resource_setup": utilities.placeholder if on_resource_setup is None else on_resource_setup,
            "message_func": message_func,
            "messages_enabled": messages_enabled,
            "caret_browsing_enabled": caret_browsing_enabled,
            "selection_enabled": selection_enabled,
            "stylesheets_enabled": stylesheets_enabled,
            "images_enabled": images_enabled,
            "forms_enabled": forms_enabled,
            "objects_enabled": objects_enabled,
            "caches_enabled": caches_enabled,
            "dark_theme_enabled": dark_theme_enabled,
            "image_inversion_enabled": image_inversion_enabled,
            "crash_prevention_enabled": crash_prevention_enabled,
            "events_enabled": events_enabled,
            "threading_enabled": threading_enabled,
            "javascript_enabled": javascript_enabled,
            "image_alternate_text_enabled": image_alternate_text_enabled,
            "ignore_invalid_images": ignore_invalid_images,
            "visited_links": visited_links,
            "find_match_highlight_color": find_match_highlight_color,
            "find_match_text_color": find_match_text_color,
            "find_current_highlight_color": find_current_highlight_color,
            "find_current_text_color": find_current_text_color,
            "selected_text_highlight_color": selected_text_highlight_color,
            "selected_text_color": selected_text_color,
            "default_style": kwargs.pop("default_style", utilities.DEFAULT_STYLE), # will be removed
            "dark_style": kwargs.pop("dark_style", utilities.DARK_STYLE), # will be removed
            "request_func": request_func,
            "insecure_https": insecure_https,
            "ssl_cafile": ssl_cafile,
            "request_timeout": request_timeout,
            "headers": headers,
            "experimental": experimental,
            "use_prebuilt_tkhtml": use_prebuilt_tkhtml,
            "tkhtml_version": tkhtml_version,
            # Internal
            "overflow_scroll_frame": kwargs.pop("overflow_scroll_frame", None),
            "embed_obj": kwargs.pop("embed_obj", HtmlFrame),
            "manage_vsb_func": kwargs.pop("manage_vsb_func", self._manage_vsb),
            "manage_hsb_func": kwargs.pop("manage_hsb_func", self._manage_hsb),
        }
        self._tkhtml_options = {
            "zoom": zoom,
            "fontscale": fontscale,
            "parsemode": parsemode,
            "shrink": shrink,
            "textwrap": textwrap,
            "mode": mode,
            "defaultstyle": defaultstyle,
            "height": height,
            "width": width,
        }

        # Some have no impact after loading
        # Shrink seems to cause segfaults
        self.final_options = {"use_prebuilt_tkhtml", "tkhtml_version", "experimental", "shrink"}
                            
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
            self.bind_class("Html", "<Button-4>", html._scroll_x11)
            self.bind_class("Html", "<Button-5>", html._scroll_x11)
            self.bind_class("Html", "<Shift-Button-4>", html._xscroll_x11)
            self.bind_class("Html", "<Shift-Button-5>", html._xscroll_x11)

        for i in (f"{html}.document", html.scrollable_node_tag):
            self.bind_class(i, "<MouseWheel>", html._scroll)
            self.bind_class(i, "<Shift-MouseWheel>", html._xscroll)

        self.bind_class(html.scrollable_node_tag, "<Button-4>", lambda event, widget=html: html._scroll_x11(event, widget))
        self.bind_class(html.scrollable_node_tag, "<Button-5>", lambda event, widget=html: html._scroll_x11(event, widget))
        self.bind_class(html.scrollable_node_tag, "<Shift-Button-4>", lambda event, widget=html: html._xscroll_x11(event, widget))
        self.bind_class(html.scrollable_node_tag, "<Shift-Button-5>", lambda event, widget=html: html._xscroll_x11(event, widget))

        # Overwrite the default bindings for scrollbars so that:
        # A) scrolling on the page while loading stops it from tracking the fragment
        # B) scrolling horizontally on a vertical scrollbar scrolls horizontally (the default is to scroll vertically)
        # C) scrolling vertically on a horizontal scrollbar scrolls vertically (the default is to block scrolling)
        for i in (vsb, hsb):
            i.bind("<Button-4>", lambda event, widget=html: html._scroll_x11(event, widget))
            i.bind("<Button-5>", lambda event, widget=html: html._scroll_x11(event, widget))
            i.bind("<MouseWheel>", html._scroll)
            i.bind("<Shift-Button-4>", lambda event, widget=html: html._xscroll_x11(event, widget))
            i.bind("<Shift-Button-5>", lambda event, widget=html: html._xscroll_x11(event, widget))
            i.bind("<Shift-MouseWheel>", html._xscroll)
            i.bind("<Enter>", html._on_leave)

        self.bind("<Leave>", html._on_leave)
        self.bind("<Enter>", html._on_mouse_motion)
        self.bind_class(html.tkinterweb_tag, "<Configure>", self._handle_html_resize)
        
        if shrink: super().bind("<Configure>", self._handle_frame_resize)

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
    
    @property # could use utilities.lazy_manager(None) and save some work, but then autocomplete fails
    def document(self):
        """The DOM manager. Use this to access :class:`~tkinterweb.dom.HTMLDocument` methods to manupulate the DOM.
        
        :rtype: :class:`~tkinterweb.dom.HTMLDocument`"""
        try:
            return self._document
        except AttributeError:
            self._document = dom.HTMLDocument(self._html)
            return self._document

    @property
    def javascript(self):
        """The JavaScript manager. Use this to access :class:`~tkinterweb.js.JSEngine` methods.
        
        :rtype: :class:`~tkinterweb.js.JSEngine`"""
        try:
            return self._javascript
        except AttributeError:
            self._javascript = js.JSEngine(self._html, self.document)
            return self._javascript

    @property
    def html(self):
        """The underlying html widget. Use this to access internal :class:`~tkinterweb.TkinterWeb` methods.
        
        :rtype: :class:`~tkinterweb.TkinterWeb`"""
        return self._html
    
    def grid_propagate(self, *args, **kwargs):
        ""
        utilities.warn("grid_propagate is being ignored, because since version 4.13 widget geometry is always respected by default. If this is a problem, please file a bug report.")
        pass

    def pack_propagate(self, *args, **kwargs):
        ""
        utilities.warn("pack_propagate is being ignored, because since version 4.13 widget geometry is always respected by default. If this is a problem, please file a bug report.")
        pass

    def _check_deprecations(self, **kwargs):
        if "default_style" in kwargs:
            utilities.deprecate_param("default_style", "utilities.DEFAULT_STYLE")
        if "dark_style" in kwargs:
            utilities.deprecate_param("dark_style", "utilities.DARK_STYLE")
        if "about_page_background" in kwargs:
            utilities.deprecate_param("about_page_background", "ttk.Style().configure('TFrame', background=)")
        if "about_page_foreground" in kwargs:
            utilities.deprecate_param("about_page_foreground", "ttk.Style().configure('TFrame', foreground=)")

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
        self._handle_html_resize(force=True)

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
        self.load_url(file_url, decode, force)

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
            
        if self._html.threading_enabled and not url.startswith("file://"):
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
        self._handle_html_resize(force=True)

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
        self._handle_html_resize(force=True)

        if return_element:
            return dom.HTMLElement(self.document, node)
    
    def add_css(self, css_source, priority="author"):
        """Send CSS stylesheets to the parser. This can be used to alter the appearance of already-loaded documents.
        
        :param css_source: The CSS code to parse.
        :type css_source: str
        :param priority: The priority of the CSS code. CSS code loaded by webpages is "user" priority. "agent" is lower priority than "user" and "author" (the default) is higher .
        :type priority: "agent", "user", or "author"
        """
        if self._waiting_for_reset:
            self._accumulated_styles.append(css_source)
        else:
            self._html.parse_css(data=css_source, fallback_priority=priority)

    def stop(self):
        """Stop loading this page and abandon all pending requests."""
        if self._thread_in_progress:
            self._thread_in_progress.stop()
        self._html.stop()
        if self._thread_in_progress:
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
        :rtype: :class:`~tkinterweb.dom.HTMLElement` or None"""
        if not self._html.current_hovered_node:
            return None
        
        if ignore_text_nodes:
            node = self._html.hovered_nodes[0]
        else:
            node = self._html.current_hovered_node
        return dom.HTMLElement(self.document, node)
    
    def get_caret_position(self, return_element=True):
        """Get the position of the caret. This can be used to modify the document's text when the user types. 

        :param return_element: Determines whether the index returned should be relative to the start of an element or the document.
        :type return_element: bool

        If ``return_element=True``:

            :return: The :class:`~tkinterweb.dom.HTMLElement` under the caret, the element's :class:`~tkinterweb.dom.HTMLElement.textContent`, and an index representing the position in that string that the caret is at. If the caret is not visible, this method will return None.
            :rtype: :class:`~tkinterweb.dom.HTMLElement`, str, and int, or None

            The element returned will always be a text node. If you need to change the style or HTML content of a text node you will first need to get its parent.

        If ``return_element=False``:

            :return: The text content of the page, and an index representing the position in that string that the caret is at. If the caret is not visible, this method will return None.
            :rtype: str and int, or None 
        
        Changed in version 4.16."""
        if self._html.caret_manager.node:
            if return_element:
                text, index = self._html.tkhtml_offset_to_text_index(self._html.caret_manager.node, self._html.caret_manager.offset)
                return dom.HTMLElement(self.document, self._html.caret_manager.node), text, index
            else:
                return self._html.text("text"), self._html.text("offset", self._html.caret_manager.node, self._html.caret_manager.offset)
        else:
            return None
        
    def get_caret_page_position(self):
        utilities.deprecate_param("get_caret_page_position", "get_caret_position(return_element=False)")
        pos = self.get_caret_position(False)
        if pos: pos = pos[1]
        return pos
        
    def set_caret_position(self, element=None, index=0):
        """Set the position of the caret, given an index and, optionally, an HTML element.

        If the given index extends out of the bounds of the given element, the caret will be moved into the preceeding or following elements.
        
        :param element: Specifies the element to place the caret in. This element must be a text node, must contain text, and must be visible.
        :type element, optional: :class:`~tkinterweb.dom.HTMLElement`
        :param index: The index in the element's :class:`~tkinterweb.dom.HTMLElement.textContent` to place the caret at. If ``element`` is None, the index will be used relative to the page's text content.
        :type index: int

        :raise RuntimeError: If caret browsing is disabled or the given element is empty or has been removed.
        
        Changed in version 4.16."""
        if not self._html.caret_browsing_enabled:
            # This is here not because things break when caret browsing is disabled,
            # But because I bet someone somewhere is trying to set the caret's position
            # With caret browsing disabled and pulling their hair out over it
            raise RuntimeError("cannot modify the caret when caret browsing is disabled")
        
        if element:
            text, offset = self._html.tkhtml_offset_to_text_index(element.node, index, True)
            if not self._html.bbox(element.node):
                raise RuntimeError(f"the element {element} is not visible.")
            if text == "":
                raise RuntimeError(f"the element {element} either is empty or is not a text node. Either provide a different element or set the caret's position using set_caret_page_position.")
            self._html.caret_manager.set(element.node, offset, recalculate=True)
        else:
            self._html.caret_manager.set(None, index, recalculate=True)

    def set_caret_page_position(self, index):
        utilities.deprecate_param("set_caret_page_position", f"set_caret_position(index={index})")
        self.set_caret_position(index=index)

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

    def get_selection_position(self, return_elements=True):
        """Get the start position, end position, and, optionally, contained elements of selected text.
        
        :param return_elements: Determines whether the indexes returned should be relative to the start of an element or the document.
        :type return_elements: bool

        If ``return_elements=True``:

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
                
            :rtype: A pair of (:class:`~tkinterweb.dom.HTMLElement`, str, int) tuples and a list of :class:`~tkinterweb.dom.HTMLElement` objects, or None

            The elements returned will always be text nodes. If you need to change the style or HTML content of a text node you will first need to get its parent.
            
        If ``return_elements=False``:
            
            :return: The document's text, and two indexes representing the selection's start and end positions in that string. 
            :rtype: str, int, and int, or None

        If no selection is found, this method will return None
        
        Changed in version 4.16."""

        if self._html.selection_manager.selection_start_node and self._html.selection_manager.selection_end_node:
            if return_elements:
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
                    
                    text, index = self._html.tkhtml_offset_to_text_index(start_node, start_offset)
                    text2, index2 = self._html.tkhtml_offset_to_text_index(end_node, end_offset)

                    contained_nodes = []
                    excluded_nodes = {dom.extract_nested(start_node), dom.extract_nested(end_node)}
                    page_index = true_start_index
                    for page_index in range(true_start_index, true_end_index + 1):
                        node, offset = self._html.text("index", page_index)
                        if node not in contained_nodes and str(dom.extract_nested(node)) not in excluded_nodes:
                            contained_nodes.append(node)

                    return (
                        (dom.HTMLElement(self.document, start_node), text, index),
                        (dom.HTMLElement(self.document, end_node), text2, index2),
                        list(dom.HTMLElement(self.document, node) for node in contained_nodes),
                    )
                else:
                    element = dom.HTMLElement(self.document, self._html.selection_manager.selection_start_node)
                    start_offset, end_offset = sorted([self._html.selection_manager.selection_start_offset, self._html.selection_manager.selection_end_offset])
                    text, index = self._html.tkhtml_offset_to_text_index(self._html.selection_manager.selection_start_node, start_offset)
                    text2, index2 = self._html.tkhtml_offset_to_text_index(self._html.selection_manager.selection_start_node, end_offset)
                    return (
                        (element, text, index),
                        (element, text2, index2),
                        [],
                    ) 
            else:
                start_index = self._html.text("offset", self._html.selection_manager.selection_start_node, self._html.selection_manager.selection_start_offset)
                end_index = self._html.text("offset", self._html.selection_manager.selection_end_node, self._html.selection_manager.selection_end_offset)
                start_index, end_index = tuple(sorted([start_index, end_index]))
                return self._html.text("text"), start_index, end_index
        else:
            return None
        
    def get_selection_page_position(self):
        utilities.deprecate_param("get_selection_page_position", f"get_selection_position(return_elements=False)")
        pos = self.get_selection_position(return_elements=False)
        if pos: pos = pos[1:]
        return pos
        
    def set_selection_position(self, start_element=None, start_index=0, end_element=None, end_index=0):
        """Set the current selection, given starting and ending text indexes and, optionally, HTML elements.
        
        :param start_element: Specifies the element to begin the selection in. This element must be text nodes, must contain text, and must be visible.
        :type start_element, optional: :class:`~tkinterweb.dom.HTMLElement`
        :param start_index: The index in the element's :class:`~tkinterweb.dom.HTMLElement.textContent` to begin the selection at. If ``start_element`` is None, this index instead is relative to the page's text content.
        :type start_index: int
        :param end_element: Specifies the element to end the selection in. This element must be text nodes, must contain text, and must be visible.
        :type end_element, optional: :class:`~tkinterweb.dom.HTMLElement`
        :param end_index: The index in the element's :class:`~tkinterweb.dom.HTMLElement.textContent` to end the selection at. If ``end_element`` is None, this index instead is relative to the page's text content.
        :type end_index: int

        :raise RuntimeError: If selection is disabled or the given elements are empty or have been removed.
        
        Changed in version 4.16."""
        if not self._html.selection_enabled:
            raise RuntimeError("cannot modify the selection when selection is disabled")

        if start_element:
            text, start_offset = self._html.tkhtml_offset_to_text_index(start_element.node, start_index, True)
            if not self._html.bbox(start_element.node):
                raise RuntimeError(f"the element {start_element} is not visible.")
            if text == "":
                raise RuntimeError(f"the element {start_element} either is empty or is not a text node. Either provide a different element or set the selection using set_selection_page_position.")
            start_node = start_element.node
        else:
            start_node, start_offset = self._html.text("index", start_index)

        if end_element:
            text, end_offset = self._html.tkhtml_offset_to_text_index(end_element.node, end_index, True)
            if not self._html.bbox(end_element.node):
                raise RuntimeError(f"the element {end_element} is not visible.")
            if text == "":
                raise RuntimeError(f"the element {end_element} either is empty or is not a text node. Either provide a different element or set the selection using set_selection_page_position.")
            end_node = end_element.node
        else:
            end_node, end_offset = self._html.text("index", end_index)

        self._html.selection_manager.reset_selection_type()
        self._html.selection_manager.begin_selection(start_node, start_offset)
        self._html.selection_manager.extend_selection(end_node, end_offset)

    def set_selection_page_position(self, start_index, end_index):
        utilities.deprecate_param("set_selection_page_position", f"set_selection_position(start_index={start_index}, end_index={end_index})")
        self.set_selection_position(start_index=start_index, end_index=end_index)

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
        elif not isinstance(new, expected_type) and old not in {"auto", "dynamic"} and new not in {"auto", "dynamic"}:
            try:
                new = expected_type(new)
            except (TypeError, ValueError,):
                raise TypeError(f"expected {expected_type.__name__}, got \"{new}\"")
        return new
    
    def _handle_html_resize(self, event=None, force=False):
        """Make all elements with the 'tkinterweb-full-page' attribute the same height as the html widget.
        This can be used in conjunction with table elements to vertical align pages,
        which is otherwise not possible with Tkhtml. Hopefully we won't need this forever."""
        if self._html.cget("shrink"):
            return

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

    def _handle_frame_resize(self, event):
        # Tkhtml doesn't handle resizing outwards when shrink is enabled
        # Disabling text wrapping works great except that it has no effect on multiple inline text nodes in Tkhtml

        # When the widget resizes, resize it to the screen's width, and let it shrink back
        # Otherwise, the widget will shrink when it can and return
        # Not ideal, but still less ideal than the default behaviour

        ### TODO: Needs improvement
        ### TODO: Fix from within Tkhtml???

        if self.unshrink:
            if event.x and self._prev_configure != (event.width, event.x):
                # if not self._html.using_tkhtml30:
                #    self._html.configure(textwrap=False)
                #    self.after(10, lambda: self._html.configure(textwrap=True))
                self.after_idle(lambda: self._html.configure(
                    width=self.winfo_screenwidth(), 
                    height=event.height)
                )
                self._prev_configure = (event.width, event.x)

    def _adjust_allow(self, allow):
        if allow == "auto":
            return 2
        elif allow == "dynamic":
            if self._html.cget("shrink") == 1:
                return 0
            else:
                return 2
        else:
            return allow

    def _manage_vsb(self, allow=None, check=False):
        "Show or hide the scrollbars."
        if check:
            return self._vsb.scroll
        if allow == None:
            allow = self.vertical_scrollbar
        allow = self._adjust_allow(allow)
        self._vsb.set_type(allow, *self._html.yview())
        return allow
    
    def _manage_hsb(self, allow=None, check=False):
        "Show or hide the scrollbars."
        if check:
            return self._hsb.scroll
        if allow == None:
            allow = self.horizontal_scrollbar
        allow = self._adjust_allow(allow)
        self._hsb.set_type(allow, *self._html.xview())
        return allow

    def _get_about_page(self, url, i1="", i2=""):
        style_type = None
        if not self.about_page_background: 
            if not self._style: self._style = Style()
            style_type = self.cget("style")
            self.about_page_background = self._style.lookup(style_type, "background")
        if not self.about_page_foreground: 
            if not self._style: self._style = Style()
            if not style_type: style_type = self.cget("style")
            self.about_page_foreground = self._style.lookup(style_type, "foreground")

        return utilities.BUILTIN_PAGES[url].format(bg=self.about_page_background, fg=self.about_page_foreground, i1=i1, i2=i2)

    def _continue_loading(self, url, data="", method="GET", decode=None, force=False, thread_safe=False):
        "Finish loading urls and handle URI fragments."
        # NOTE: this runs in a thread

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

                thread = utilities.get_current_thread()

                location = parsed.netloc if parsed.netloc else parsed.path
                self._html.post_message(f"Connecting to {location}", True)
                if self._html.insecure_https: self._html.post_message("WARNING: Using insecure HTTPS session", True)
                
                newurl, data, filetype, code = self._html.download_url(url, data, method, decode)
                self._html.post_message(f"Successfully connected to {location}", True)

                if thread.isrunning():
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
                            data, data_is_image = self._html.image_manager.check_images(data, name, url, filetype, thread.is_subthread)
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
        self._html.image_manager.finish_fetching_images(data, name, url, filetype, data_is_image)
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
        ### TODO: consider handling add_html/insert_html this way too   
        ### But then again I don't think they're quite as commonly used
        ### And these days one could just bind to DOM_CONTENT_LOADED_EVENT

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

    def configure(self, **kwargs):
        """
        Change the widget's configuration options. See above for options.
        """
        # Deprecations
        self._check_deprecations(**kwargs)

        # 
        for key in list(kwargs.keys()):
            if key in self.final_options:
                raise NotImplementedError(f"{key} should not be changed after the widget is loaded")

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
                    self._handle_html_resize(force=True)
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
        "Remove an event binding."
        if sequence in {"<Leave>", "<Enter>"}:
            super().unbind(sequence, *args, **kwargs)
        else:
            self._html.unbind(sequence, *args, **kwargs)
    
    def __getitem__(self, key):
        return self.cget(key)

    def __setitem__(self, key, value):
        self.configure(**{key: value})


class HtmlLabel(HtmlFrame):
    """The :class:`HtmlLabel` widget is a label-like HTML widget. It inherits from the :class:`HtmlFrame` class. 
    
    For a complete list of avaliable methods, properties, configuration options, and generated events, see the :class:`HtmlFrame` docs.
    
    This widget also accepts one additional parameter:

    :param text: The HTML or text content of the widget
    :type text: str

    By default the widget will be styled to match the :py:class:`ttk.Label` style. To change this, alter the ttk style or use CSS.
    """

    def __init__(self, master, *, text="", **kwargs):
        if "style" not in kwargs: 
            kwargs["style"] = "TLabel"
        else:
            utilities.warn("Since version 4.14 the style keyword no longer sets the HtmlLabel's CSS code. Please use the add_css() method instead.")
        
        HtmlFrame.__init__(self, master, shrink=True, **kwargs)

        tags = list(self._html.bindtags())
        tags.remove("Html")
        self._html.bindtags(tags)

        self._style = Style()

        if text: self.load_html(text)
        # I'd like to just make this an else statement to prevent the widget from being a massive white screen when text=""
        elif self.unshrink or (not self._html.using_tkhtml30 and not self._html.cget("textwrap")):
            # A fellow in issue 145 mentioned layout issues when this was used
            # I can't seem to reproduce it though...?
            self.load_html("<body></body>", _relayout=False)
    
    def load_html(self, *args, _relayout=True, **kwargs):
        ""
        # Match the ttk theme
        style_type = self.cget("style")
        bg = self._style.lookup(style_type, 'background')
        fg = self._style.lookup(style_type, 'foreground')
        style = self._html.default_style + \
            (self._html.dark_style if self._html.dark_theme_enabled else "") +\
            f"BODY {{ background-color: {bg}; color: {fg}; }}"
        self._html.configure(defaultstyle=style)
        
        # Load the HTML
        super().load_html(*args, **kwargs)

        # This stops infinite flickering when tables are present
        # My computer was having this bug for a while but now I don't experience it
        # But this doesn't seem to have any major side effects
        if _relayout:
            self.update_idletasks()
            self._html.relayout()

    def configure(self, **kwargs):
        ""
        if "text" in kwargs:
            self.load_html(kwargs.pop("text"))
            
        if "style" in kwargs:
            utilities.warn("Since version 4.14 the style keyword no longer sets the HtmlLabel's CSS code. Please use the add_css() method instead.")

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

    The intent of this widget is to mimic the Tkinter Text widget. 

    This widget accepts the following :py:class:`tk.Text` parameters:

    :param background: the widget's background colour
    :type background: str
    :param foreground: the widget's foreground (text) colour
    :type foreground: str
    :param selectbackground: the background colour of selected text
    :type selectbackground: str
    :param selectforeground: the foreground colour of selected text
    :type selectforeground: str
    :param insertontime: the number of milliseconds the insertion cursor is visible
    :type insertontime: int
    :param insertofftime: the number of milliseconds the insertion cursor is invisible
    :type insertofftime: int
    :param insertwidth: the width of the insertion cursor in pixels
    :type insertwidth: int
    :param insertbackground: the background colour of the insertion cursor
    :type insertbackground: str
    :param state: the widget's state (``"normal"`` or ``"disabled"``)
    :type state: str

    Changed in version 4.15.
    """

    def __init__(self, master, *, background="#ffffff", foreground="#000000", selectbackground="#9bc6fa", selectforeground="#000", insertontime=600, insertofftime=300, insertwidth=1, insertbackground=None, state="enabled", **kwargs):
        self._background = kwargs.pop("bg", background)
        self._foreground = kwargs.pop("fg", foreground)

        self.preserve_flow = True # mostly for debugging

        if "horizontal_scrollbar" not in kwargs:
            kwargs["horizontal_scrollbar"] = "dynamic"
        
        if state == "enabled":
            caret_browsing_enabled=True
        elif state == "disabled":
            caret_browsing_enabled=False
        else:
            raise ValueError("state must be 'enabled' or 'disabled'")

        HtmlFrame.__init__(self, master, caret_browsing_enabled=caret_browsing_enabled, **kwargs)
        self.configure(selectbackground=selectbackground, selectforeground=selectforeground, 
                       insertontime=insertontime, insertofftime=insertofftime, 
                       insertwidth=insertwidth, insertbackground=insertbackground)
                
        self._html.text_mode = True

        self.load_html("<body><div>\xa0</div></body>")

        if state == "enabled":
            self._html.bind("<Key>", self._on_key)

    def load_html(self, *args, **kwargs):
        ""
        # Match the set background and foreground
        style = self._html.default_style + \
            (self._html.dark_style if self._html.dark_theme_enabled else "") +\
            f"BODY {{ background-color: {self._background}; color: {self._foreground}; }}"
        self._html.configure(defaultstyle=style)
        
        # Load the HTML
        super().load_html(*args, **kwargs)

    def _duplicate(self, element):
        "Duplicate an element."
        parent = element.parentElement

        new = self.document.createElement(parent.tagName)
        new.className = parent.className
        new.setAttribute("style", parent.getAttribute("style"))

        # Wrap inline elements in a div so that they display on an new line
        # Return the inner element so that setting the textContent doesn't overwrite this structure
        if parent.style.display == "inline":
            outer = self.document.createElement("div")
            outer.appendChild(new)
            new, inner = outer, new
        else:
            inner = new

        sibling = parent.nextSibling
        if sibling:
            parent.parentElement.insertBefore(new, sibling)
        else:
            parent.parentElement.appendChild(new)

        return inner, element
    
    def _delete(self, element):
        parent = element.parentElement
        element.remove()
        if len(parent.children) == 0:
            self._delete(parent)
    
    def _check_text(self, text):
        if not text.strip():
            return "\xa0"
        return text
    
    def _strip_text(self, text):
        if text == "\xa0":
            return ""
        return text

    def _next_in_document(self, node):
        # Go to first child if exists
        if node.children:
            return node.children[0]
        # Otherwise, next sibling
        if node.nextSibling:
            return node.nextSibling
        # Otherwise, go up parents until we find a parent's nextSibling
        while node.parentElement:
            node = node.parentElement
            if node.nextSibling:
                return node.nextSibling
        return None  # reached the end of the tree

    def _descendants(self, node):
        result = []
        stack = list(node.children)

        while stack:
            current = stack.pop()
            result.append(current)
            stack.extend(current.children)

        return result

    def _remove_between(self, element1, element2):
        current = self._next_in_document(element1)
        to_remove = []
        while current and current != element2:
            to_remove.append(current)
            current = self._next_in_document(current)
          
        for node in to_remove:
            descendants = self._descendants(node)
            if element1 in descendants or element2 in descendants:
                continue

            node.remove()

    def delete(self, start_index, end_index=None, start_element=None, end_element=None):
        """Delete text between two points.
        
        :param start_index: The starting index to delete text from. Similar to the :py:class:`tk.Text` widget, if this is "sel.first", this will be the beginning of the selection.
        :type start_index: int or "sel.first"
        :param end_index: The ending index to delete text at. If this is "sel.last", this will be the end of the selection. If this is "end", this will be the end of the document or the end of the ending element if provided. If this is None, only the character at the start index will be deleted.
        :type end_index: int, "sel.last", "end", or None, optional
        :param start_element: If provided, the start index will be used relative to this element's :class:`~tkinterweb.dom.HTMLElement.textContent`.
        :type start_element: None or :class:`~tkinterweb.dom.HTMLElement`, optional
        :param end_element: If provided, the end index will be used relative to this element's :class:`~tkinterweb.dom.HTMLElement.textContent`.
        :type end_element: None or :class:`~tkinterweb.dom.HTMLElement`, optional

        :raise RuntimeError: if "sel.first" or "self.last" is requested but no text is selected.

        New in version 4.16.
        """
        pos = self.get_caret_position(return_element=False)

        # Translate string indexes
        selection = None
        if start_index == "sel.first":
            selection = self.get_selection_position(return_elements=False)
            self.clear_selection()
            try:
                start_index = selection[1]
                start_element = None
            except TypeError:
                raise RuntimeError("no text is selected")

        if end_index == "sel.last":
            if not selection:
                selection = self.get_selection_position(return_elements=False)
                self.clear_selection()
            try:
                end_index = selection[2]
                end_element = None
            except TypeError:
                raise RuntimeError("no text is selected")

        elif end_index is None:
            end_index = start_index + 1
        if end_index == "end":
            if end_element:
                end_index = len(end_element.textContent)
            else:
                end_index = len(self._html.text("text"))

        # Gather data
        if start_element:
            _, ti = self._html.tkhtml_offset_to_text_index(start_element.node, start_index, True)
            abs1 = self._html.text("offset", start_element.node, ti)
            text1 = start_element.textContent
        else:
            abs1 = start_index
            start_element, start_index = self._html.text("index", start_index)
            text1, start_index = self._html.tkhtml_offset_to_text_index(start_element, start_index)
            start_element = dom.HTMLElement(self.document, start_element)

        if end_element:
            _, ti = self._html.tkhtml_offset_to_text_index(end_element.node, end_index, True)
            abs2 = self._html.text("offset", end_element.node, ti)
            text2 = end_element.textContent
        else:
            abs2 = end_index
            end_element, end_index = self._html.text("index", end_index)
            text2, end_index = self._html.tkhtml_offset_to_text_index(end_element, end_index)
            end_element = dom.HTMLElement(self.document, end_element)

        # Ensure index 1 comes before index 2
        if abs1 > abs2:
            end_element, start_element = start_element, end_element
            end_index, start_index = start_index, end_index
        
        # Deletions
        if start_element == end_element:
            start_element.textContent = self._check_text(text1[:start_index] + text2[end_index:])
        else:
            start_element.textContent = self._check_text(self._strip_text(text1[:start_index]) + self._strip_text(text2[end_index:]))
            self._remove_between(start_element, end_element)
            self._delete(end_element)
        
        # Shift the caret if needed
        if pos and pos[1] > abs1:
            index = max(pos[1] + len(self._html.text("text")) - len(pos[0]), abs1)
            self.set_caret_position(index=index)
    
    def insert(self, index, text_or_element, element=None):
        """Insert text or an element at the given index.
        
        :param index: The index to insert text at. Similar to the :py:class:`tk.Text` widget, if this is "insert", this method will insert at the caret's position. If this is "end", this will insert at the end of the document or the end of the element if provided.
        :type index: int, "end", or "insert"
        :param text_or_element: The text or HTML element to insert.
        :type text_or_element: str or :class:`~tkinterweb.dom.HTMLElement`
        :param element: If provided, the given index will be used relative to this element's :class:`~tkinterweb.dom.HTMLElement.textContent`.
        :type element: None or :class:`~tkinterweb.dom.HTMLElement`, optional

        :raise RuntimeError: if "insert" is requested but the caret is not visible.

        New in version 4.16.
        """
        pos = self.get_caret_position(return_element=False)

        # Translate string indexes
        if index == "end":
            if element:
                index = len(element.textContent)
            else:
                index = len(self._html.text("text"))
        elif index == "insert":
            try:
                element, text, index = self.get_caret_position()
            except TypeError:
                raise RuntimeError("the caret is not visible")
        
        # Gather data
        if element:
            text = element.textContent
            if pos:
                _, offset = self._html.tkhtml_offset_to_text_index(element.node, index, True)
                abs_index = self._html.text("offset", element.node, offset)
        else:
            abs_index = index
            element, index = self._html.text("index", index)
            text, index = self._html.tkhtml_offset_to_text_index(element, index)
            element = dom.HTMLElement(self.document, element)
        
        # Insertions
        if isinstance(text_or_element, dom.HTMLElement):
            element2, element = self._duplicate(element)
            element.textContent = self._strip_text(text[:index])
            element2.textContent = text[index:]
            element2.parentElement.insertBefore(text_or_element, element2)

            children = text_or_element.children
            while children:
                text_or_element = text_or_element.children[-1]
                children = text_or_element.children
            #if pos and pos[1] >= abs_index:
            #    self.set_caret_position(text_or_element, len(text_or_element.textContent))
        else:
            element.textContent = self._strip_text(text[:index]) + text_or_element + text[index:]
        
        # Shift the caret if needed
        if pos and pos[1] >= abs_index:
            index = pos[1] + len(self._html.text("text")) - len(pos[0])
            self.set_caret_position(index=index)

    def _on_key_selection(self, event, selection):
        "Handle key presses when text is selected."
        self._html.selection_manager.clear_selection()

        start, end, middle = selection
        start_element, start_element_text, start_element_index = start
        end_element, end_element_text, end_element_index = end

        # We don't want to insert any characters when pressing Return, BackSpace, or Delete
        if event.keysym in {"Return", "KP_Enter", "BackSpace", "Delete"}:
            event.char = ""
        # Map spaces to non-breaking spaces
        elif event.char == " ": 
            event.char = "\xa0"

        # If the text to delete is within one element, cut out the section
        # If the resulting text is empty, make it \xa0 to prevent the node from collapsing
        if start_element == end_element:
            # If pressing Return, split the node into two
            if event.keysym in {"Return", "KP_Enter"}:
                new, start_element = self._duplicate(start_element)
                text1 = start_element_text[:start_element_index]
                text2 = start_element_text[end_element_index:]
                start_element.textContent = self._check_text(text1)
                new.textContent = self._check_text(text2)
                start_element = new.children[0]
                start_element_index = 0
            else:
                start_element.textContent = self._check_text(self._strip_text(start_element_text[:start_element_index]) + event.char + start_element_text[end_element_index:])
        else:
            # Otherwise, first delete all nodes in between if self.preserve_flow
            if self.preserve_flow:
                self._remove_between(start_element, end_element)
            else:
                # Or, delete all text nodes in between
                for element in middle:
                    self._delete(element)

            # If pressing Return, cut the end of the start node and the beginning of the end node
            if event.keysym in {"Return", "KP_Enter"}:
                start_element.textContent = self._check_text(start_element_text[:start_element_index] + event.char)
                end_element.textContent = self._check_text(end_element_text[end_element_index:])
                start_element = end_element
                start_element_index = 0

            # Otherwise, cut out the section and move the end node's text into the start node
            # Delete the end node
            else:
                start_element.textContent = self._check_text(self._strip_text(start_element_text[:start_element_index]) + event.char + end_element_text[end_element_index:])
                self._delete(end_element)

        self.set_caret_position(start_element, start_element_index + len(event.char))

    def _on_key(self, event):
        "Handle key presses."
        if not event.char:
            return
        
        if event.state & 0x4:
            if event.keysym == "v":
                # Ctrl-V
                event.char = self._html.clipboard_get()
            elif event.keysym == "x":
                # Ctrl-X
                self._html.selection_manager.copy_selection()
                event.keysym = "BackSpace"
            elif event.keysym not in {"BackSpace", "Delete", "Return", "KP_Enter"}:
                # Ctrl-[anything else that isn't Return, BackSpace, or Delete]
                return

        selection = self.get_selection_position()
        if selection:
            # Nodes can be technically marked as selected without actually being highlighted
            if self._html.selection_manager.get_selection():
                return self._on_key_selection(event, selection)
        
        caret_position = self.get_caret_position()
        if not caret_position:
            return
        element, text, index = caret_position

        if event.keysym == "BackSpace":
            self._html.caret_manager.shift_left(event)
            caret_position = self.get_caret_position()
            element2, text2, index2 = caret_position

            # If the text to delete is within one element, cut out the section
            # If the resulting text is empty, make it \xa0 to prevent the node from collapsing
            if element == element2:
                newtext = self._check_text(text[:index2] + text[index:])
                element.textContent = newtext
            # Otherwise, cut out the section and move the start node's text into the end node
            # Delete the start node
            else:
                element2.textContent = self._check_text(self._strip_text(text2[:index2]) + self._strip_text(text[index:]))
                if self.preserve_flow:
                    self._remove_between(element2, element)
                self._delete(element)
                self._html.caret_manager.update()
            return

        if event.keysym == "Delete":
            self._html.caret_manager.shift_right(event, update=False)
            caret_position = self.get_caret_position()
            element2, text2, index2 = caret_position

            # If the text to delete is within one element, cut out the section
            # If the resulting text is empty, make it \xa0 to prevent the node from collapsing
            if element == element2:
                element.textContent = self._check_text(text[:index] + text[index2:])
                self.set_caret_position(element, index)
            # Otherwise, cut out the section but move the end node's text to the start node
            # Delete the end node
            # Strip the start node's text in case it is \xa0
            else:
                text = self._strip_text(text[:index])
                element.textContent = self._check_text(text + text2[index2:])
                if self.preserve_flow:
                    self._remove_between(element, element2)
                self._delete(element2)

                self.set_caret_position(element, len(text))
            return

        # Create a new node with the same tag and class as the current node
        # Move this node's text to the right of the caret into the new node
        if event.keysym in {"Return", "KP_Enter"}:
            element, new = self._duplicate(element)
            element.textContent = self._check_text(text[index:])
            new.textContent = self._check_text(text[:index])
            self.shift_caret_right()
            return
        
        # Map spaces to non-breaking spaces
        if event.char == " ": event.char = "\xa0"

        # Insert characters
        text2 = self._strip_text(text[:index])
        newtext = text2 + event.char + text[index:]
        element.textContent = newtext
        self.set_caret_position(element, len(text2) + len(event.char))

    def configure(self, **kwargs):
        ""
        if "caret_browsing_enabled" in kwargs:
            raise RuntimeError("caret browsing is always enabled in this widget")

        if "background" in kwargs:
            self._background = kwargs.pop("background")
            self.add_css(f"BODY {{ background-color: {self._background}; }}", "agent")
        if "foreground" in kwargs:
            self._foreground = kwargs.pop("foreground")
            self.add_css(f"BODY {{ color: {self._foreground}; }}", "agent")
        if "bg" in kwargs:
            self._background = kwargs.pop("bg")
            self.add_css(f"BODY {{ background-color: {self._background}; }}", "agent")
        if "fg" in kwargs:
            self._foreground = kwargs.pop("fg")
            self.add_css(f"BODY {{ color: {self._foreground}; }}", "agent")
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
            self._html.caret_manager.caret_color = kwargs.pop("insertbackground")
        if "state" in kwargs:
            state = kwargs.pop("state")
            if state == "enabled":
                self._html.bind("<Key>", self._on_key)
                self._html.caret_browsing_enabled = True
            elif state == "disabled":
                self._html.unbind("<Key>")
                self._html.caret_browsing_enabled = False
            else:
                raise ValueError("state must be 'enabled' or 'disabled'")

        if kwargs: super().configure(**kwargs)

    def cget(self, key):
        ""
        if "background" == key:
            return self._background
        elif "foreground" == key:
            return self._foreground
        elif "bg" == key:
            return self._background
        elif "fg" == key:
            return self._foreground
        elif "selectbackground" == key:
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
            return self._html.caret_manager.caret_color
        elif "state" == key:
            return "enabled" if self._html.caret_browsing_enabled else "disabled"
        
        return super().cget(key)

    def config(self, **kwargs):
        ""
        self.configure(**kwargs)


class HtmlParse(HtmlFrame):
    """The :class:`HtmlParse` class parses HTML but does not spawn a widget. It inherits from the :class:`HtmlFrame` class. 
    
    For a complete list of avaliable methods, properties, configuration options, and generated events, see the :class:`HtmlFrame` docs.
    
    New in version 4.4."""
    
    def __init__(self, **kwargs):
        self.root = root = tk.Tk()

        self._is_destroying = False

        for flag in {"events_enabled", "images_enabled", "forms_enabled"}:
            if flag not in kwargs:
                kwargs[flag] = False
                
        HtmlFrame.__init__(self, root, **kwargs)

        root.withdraw()

    def destroy(self):
        super().destroy()
        self.root.destroy()