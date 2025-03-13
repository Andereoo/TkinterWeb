"""
Widgets that expand on the functionality of the basic bindings
by adding scrolling, file loading, and many other convenience functions

Copyright (c) 2025 Andereoo
"""

from urllib.parse import urldefrag, urlparse

from bindings import TkinterWeb
from utilities import *
from utilities import __version__
from imageutils import create_RGB_image
from dom import HTMLDocument, HTMLElement

from tkinter import ttk


pythonmonkey = None


class HtmlFrame(ttk.Frame):
    """TkinterWeb's flagship HTML widget.

    :param master: The parent widget.
    :type master: :py:class:`tkinter.Widget`

    The following flags are optional and can be used to register callbacks:

    :param on_navigate_fail: The function to be called when a url cannot be loaded. The target url, error, and code will be passed as arguments. By default the TkinterWeb error page is shown.
    :type on_navigate_fail: function
    :param on_link_click: The function to be called when a hyperlink is clicked. The target url will be passed as an argument. By default the url is navigated to.
    :type on_link_click: function
    :param on_form_submit: The function to be called when a form is submitted. The target url, data, and method ("GET" or "POST") will be passed as arguments. By default the response is loaded.
    :type on_form_submit: function
    :param on_script: The function to be called when a ``<script>`` element is encountered. This can be used to connect a script handler, such as a JavaScript engine. The script element's attributes and contents will be passed as arguments.
    :type on_script: function
    :param on_element_script: The function to be called when a JavaScript event attribute on an element is encountered. This can be used to connect a script handler, such as a JavaScript engine, or even to run your own Python code. The element's corresponding Tkhtml3 node, relevant attribute, and attribute contents will be passed as arguments. New in version 4.1.
    :type on_element_script: callable
    :param on_resource_setup: The function to be called when an image or stylesheet load finishes. The resource's url, type ("stylesheet" or "image"), and whether setup was successful or not (True or False) will be passed as arguments.
    :type on_resource_setup: function
    :param message_func: The function to be called when a debug message is issued. This only works if :attr:`messages_enabled` is set to True. The message will be passed as an argument. By default the message is printed.
    :type message_func: function

    The following flags are optional and can be used to change the widget's appearance:

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

    The following flags are optional and can be used to enable or disable certain features:

    :param messages_enabled: Enable/disable messages. This is enabled by default.
    :type messages_enabled: bool
    :param selection_enabled: Enable/disable selection. This is enabled by default.
    :type selection_enabled: bool
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

    The following flags are optional and can be used to change widget colors and styling:

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
    :param dark_style: The stylesheet used to set the default appearance of HTML elements when dark mode is enabled. It is generally best to leave this setting alone.
    :type dark_style: str

    The following flags are optional and can be used to change download behaviour:

    :param insecure_https: If True, website certificate errors are ignored. This can be used to work around issues where :py:mod:`ssl` is unable to get a page's certificate on some older Mac systems.
    :type insecure_https: bool
    :param headers: The headers used by urllib's :py:class:`~urllib.request.Request` when fetching a resource.
    :type headers: dict

    The following flags are optional and can be used to change HTML rendering behaviour:

    :param experimental: If True, experimental features will be enabled. You will need to compile the cutting-edge Tkhtml widget from https://github.com/Andereoo/TkinterWeb-Tkhtml/tree/experimental and replace the default Tkhtml binary for your system with the experimental version. Unless you need to screenshot the full page on Windows or print your page for now it is likely best to use the default Tkhtml binary and leave this setting alone.
    :type experimental: bool
    :param use_prebuilt_tkhtml: If True (the default), the Tkhtml binary for your system supplied by TkinterWeb will be used. If your system isn't supported and you don't want to compile the Tkhtml widget from https://github.com/Andereoo/TkinterWeb-Tkhtml yourself, you could try installing Tkhtml3 system-wide and set :attr:`use_prebuilt_tkhtml` to False. Note that some crash prevention features will no longer work.
    :type use_prebuilt_tkhtml: bool
    :param parsemode: The parse mode. In "html" mode, explicit XML-style self-closing tags are not handled specially and unknown tags are ignored. "xhtml" mode is similar to "html" mode except that explicit self-closing tags are recognized. "xml" mode is similar to "xhtml" mode except that XML CDATA sections and unknown tag names are recognized. It is usually best to leave this setting alone.
    :type parsemode: "xml", "xhtml", or "html"
    :param mode: The rendering engine mode. It is usually best to leave this setting alone.
    :type mode: "standards", "almost standards", or "quirks"

    Optional ttk.Frame arguments are also supported but not listed.
    
    :raise TypeError: If the value type is wrong and cannot be converted to the correct type."""

    def __init__(self, master, **kwargs):
        # state and settings variables
        style = ttk.Style()

        self._current_url = ""
        self._previous_url = ""
        self._accumulated_styles = []
        self._waiting_for_reset = False
        self._thread_in_progress = None
        self._prev_height = 0
        self._button = None
        self._DOM_cache = None

        self._htmlframe_options = {
            "on_navigate_fail": self.show_error_page,
            "vertical_scrollbar": "auto",
            "horizontal_scrollbar": False,
            "about_page_background": style.lookup('TFrame', 'background'),
            "about_page_foreground": style.lookup('TLabel', 'foreground'),
        }
        self.tkinterweb_options = {
            "on_link_click": self.load_url,
            "on_form_submit": self.load_form_data,
            "on_script": self._on_script,
            "on_element_script": self._on_element_script,
            "on_resource_setup": placeholder,
            "message_func": notifier,
            "messages_enabled": True,
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
            "default_style": DEFAULT_STYLE,
            "dark_style": DARK_STYLE,
            "insecure_https": False,
            "headers": HEADERS,
            "experimental": False,
            # no impact after loading
            "use_prebuilt_tkhtml": True,
            # internal
            "overflow_scroll_frame": None,
            "embed_obj": HtmlFrame,
            "manage_vsb_func": self._manage_vsb,
            "manage_hsb_func": self._manage_hsb,
        }
        self.tkhtml_options = {
            "zoom": 1.0,
            "fontscale": 1.0,
            "parsemode": DEFAULT_PARSE_MODE,
            "shrink": False,
            "mode": DEFAULT_ENGINE_MODE,
        }
                            
        for key, value in self._htmlframe_options.items():
            if key in kwargs:
                value = self._check_value(self._htmlframe_options[key], kwargs.pop(key))
                self._htmlframe_options[key] = value
            setattr(self, key, value)

        for key in list(kwargs.keys()):
            if key in self.tkinterweb_options:
                value = self._check_value(self.tkinterweb_options[key], kwargs.pop(key))
                self.tkinterweb_options[key] = value
            elif key in self.tkhtml_options:
                self.tkhtml_options[key] = kwargs.pop(key)

        super().__init__(master, **kwargs)

        # setup sub-widgets
        self._html = html = TkinterWeb(self, self.tkinterweb_options, **self.tkhtml_options)
        self._hsb = hsb = AutoScrollbar(self, orient="horizontal", command=html.xview)
        self._vsb = vsb = AutoScrollbar(self, orient="vertical", command=html.yview)

        html.configure(xscrollcommand=hsb.set, yscrollcommand=vsb.set)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        html.grid(row=0, column=0, sticky="nsew")
        hsb.grid(row=1, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="nsew")

        self._manage_hsb(self.horizontal_scrollbar)
        self._manage_vsb(self.vertical_scrollbar)

        # html.document only applies to the document it is bound to (which makes things easy)
        # for some reason, binding to Html only works on Linux and binding to html.document only works on Windows
        # Html fires on all documents (i.e. <iframe> elements), so it has to be handled slightly differently
        if not self._html.overflow_scroll_frame:
            self.bind_class("Html", "<Button-4>", html.scroll_x11)
            self.bind_class("Html", "<Button-5>", html.scroll_x11)
        self.bind_class(f"{html}.document", "<MouseWheel>", html.scroll)

        self.bind_class(html.scrollable_node_tag, "<Button-4>", lambda event, widget=html: html.scroll_x11(event, widget))
        self.bind_class(html.scrollable_node_tag, "<Button-5>", lambda event, widget=html: html.scroll_x11(event, widget))
        self.bind_class(html.scrollable_node_tag, "<MouseWheel>", html.scroll)

        vsb.bind("<Button-4>", lambda event, widget=html: html.scroll_x11(event, widget))
        vsb.bind("<Button-5>", lambda event, widget=html: html.scroll_x11(event, widget))
        vsb.bind("<MouseWheel>", html.scroll)

        hsb.bind("<Enter>", html._on_leave)
        vsb.bind("<Enter>", html._on_leave)

        self.bind("<Leave>", html._on_leave)
        self.bind("<Enter>", html._on_mouse_motion)
        html.bind("<Configure>", self._handle_resize)

        
        self.bind = html.bind

        self._html.post_message(f"""Welcome to TkinterWeb {__version__}!

The API changed in version 4.
See https://github.com/Andereoo/TkinterWeb for details.

Debugging messages are enabled
Use the parameter `messages_enabled = False` when calling HtmlFrame() or HtmlLabel() to disable these messages""")

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
    
    @property
    def document(self):
        """The DOM manager. Use this to access :class:`~tkinterweb.dom.HTMLDocument` methods to manupulate the DOM.
        
        :rtype: :class:`~tkinterweb.dom.HTMLDocument`"""
        if self._DOM_cache is None:  # lazy loading of Document Object Model
            self._DOM_cache = HTMLDocument(self.html)
        return self._DOM_cache
    
    @property
    def html(self):
        """The underlying html widget. Use this to access underlying :class:`~tkinterweb.TkinterWeb` methods.
        
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
            elif key in self.tkinterweb_options:
                value = self._check_value(self.tkinterweb_options[key], kwargs.pop(key))
                setattr(self._html, key, value)
            elif key in self.tkhtml_options:
                self._html[key] = kwargs.pop(key)
                if key == "zoom":
                    self._handle_resize(force=True)
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
        elif key in self.tkinterweb_options.keys():
            return getattr(self._html, key)
        elif key in self.tkhtml_options.keys():
            return self._html.cget(key)
        return super().cget(key)
    
    def __getitem__(self, key):
        return self.cget(key)

    def __setitem__(self, key, value):
        self.configure(**{key: value})

    def load_html(self, html_source, base_url=None):
        """Clear the current page and parse the given HTML code.
        
        :param html_source: The HTML code to render.
        :type html_source: str
        :param base_url: The base url to use when parsing stylesheets and images. If this argument is not supplied, it will be set to the current working directory.
        :type base_url: str, optional"""
        self._html.reset()

        if base_url == None:
            path = WORKING_DIR
            if not path.startswith("/"):
                path = f"/{path}"
            base_url = f"file://{path}/"
        self._html.base_url = self._current_url = base_url
        self._html.parse(html_source)

        self._finish_css()
        self._handle_resize(force=True)

    def load_file(self, file_url, decode=None, force=False):
        """Convenience method to load a local HTML file.
        
        :param file_url: The HTML file to render.
        :type file_url: str
        :param decode: The decoding to use when loading the file.
        :type decode: str or None, optional
        :param force: Force the page to reload all elements.
        :type force: bool, optional"""
        self._previous_url = self._current_url
        if not file_url.startswith("file://"):
            if PLATFORM.system == "Windows" and not file_url.startswith("/"):
                file_url = "file:///" + str(file_url)
            else:
                file_url = "file://" + str(file_url)
            self._current_url = file_url
            self._html.post_event(URL_CHANGED_EVENT)
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
            self._html.post_event(URL_CHANGED_EVENT)
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
        if url in BUILTIN_PAGES:
            self.load_html(BUILTIN_PAGES[url].format(self.about_page_background, self.about_page_foreground, "", "", ""), url)
            return

        self._waiting_for_reset = True

        # ugly workaround for Bug #40, where urllib.urljoin constructs improperly formatted urls on Linux when url starts with file:///
        if not url.startswith("file://///"):
            newurl = url.replace("file:////", "file:///")
            if newurl != url:
                url = newurl
                self._current_url = url
                self._html.post_event(URL_CHANGED_EVENT)

        if self._thread_in_progress:
            self._thread_in_progress.stop()
        if self._html.maximum_thread_count >= 1:
            thread = StoppableThread(target=self._continue_loading, args=(
                url,), kwargs={"decode": decode, "force": force})
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
        if self._html.maximum_thread_count >= 1:
            thread = StoppableThread(
                target=self._continue_loading, args=(url, data, method, decode))
            self._thread_in_progress = thread
            thread.start()
        else:
            self._continue_loading(url, data, method, decode)

    def add_html(self, html_source):
        """Parse HTML and add it to the end of the current document. Unlike :meth:`HtmlFrame.load_html`, :meth:`HtmlFrame.add_html` adds rendered HTML code without clearing the original document.
        
        :param html_source: The HTML code to render.
        """
        self._previous_url = ""
        if not self._html.base_url:
            path = WORKING_DIR
            if not path.startswith("/"):
                path = f"/{path}"
            base_url = f"file://{path}/"
            self._html.base_url = self._current_url = base_url
        self._html.parse(html_source)

        self._finish_css()
        self._handle_resize(force=True)

    def add_css(self, css_source):
        """Send CSS stylesheets to the parser. This can be used to alter the appearance of already-loaded documents.
        
        :param css_source: The CSS code to parse.
        :type url: str"""
        if self._waiting_for_reset:
            self._accumulated_styles.append(css_source)
        else:
            self._html.parse_css(data=css_source, override=True)

    def stop(self):
        """Stop loading this page and abandon all pending requests."""
        if self._thread_in_progress:
            self._thread_in_progress.stop()
        self._html.stop()
        self._current_url = self._previous_url
        self._html.post_event(URL_CHANGED_EVENT)
        self._html.post_event(DONE_LOADING_EVENT)

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
        nmatches, selected, matches = self._html.find_text(text, select, ignore_case, highlight_all)
        if detailed:
            return nmatches, selected, matches
        else:
            return nmatches
        
    def get_currently_hovered_element(self, ignore_text_nodes=True):
        """Get the element under the mouse. Particularly useful for creating right-click menus or displaying hints when the mouse moves.
        
        :param ignore_text_nodes: If True, text nodes (i.e. the contents of a ``<p>`` element) will be ignored and their parent node returned. It is generally best to leave leave this at the default.
        :type ignore_text_nodes: bool, optional
        :return: The element under the mouse.
        :rtype: :class:`~tkinterweb.dom.HTMLElement`"""
        node = self._html.current_node
        if ignore_text_nodes:
            if not self._html.get_node_tag(self._html.current_node):
                node = self._html.get_node_parent(self._html.current_node)
        return HTMLElement(self.document, node)

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
        :raises: NotImplementedError if experimental mode is not enabled, :attr:`full` is set to True, and TkinterWeb is running on Windows."""
        if self._html.experimental or PLATFORM.system != "Windows":
            self._html.post_message(f"Taking a screenshot of {self._current_url}...")
            image, data = self._html.image(full=full)
            height = len(data)
            width = len(data[0].split())
            image = create_RGB_image(data, width, height)
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
        :raises: NotImplementedError if experimental mode is not enabled."""
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

            self._html.update() # update the root window to ensure HTML is rendered
            file = self._html.postscript(cnf)
            # no need to save - Tkhtml handles that for us
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
            self.load_html(BUILTIN_PAGES["about:error"].format(self.about_page_background, self.about_page_foreground, code, self._button), url)

    def select_all(self):
        """Select all text in the document."""
        self._html.select_all()

    def clear_selection(self):
        """Clear the current selection."""
        self._html.clear_selection()

    def get_selection(self):
        """Return any selected text.

        :return: The current selection.
        :rtype: str"""
        self._html.get_selection()

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

    def replace_widget(self, old_widget, new_widget):
        """Removes the old widget from the document, and replaces it with the new widget. 
        
        If both widgets are already shown in the document, their locations will be swapped.
        
        :param old_widget: The Tkinter widget to replace. This widget must be currently managed by TkinterWeb.
        :type old_widget: :py:class:`tkinter.Widget`
        :param new_widget: The new Tkinter widget to show. This may be any Tkinter widget.
        :type new_widget: :py:class:`tkinter.Widget`"""
        self._html.replace_widget(old_widget, new_widget)

    def replace_element(self, selector, new_widget):
        """Replaces the content of the element matching the specified CSS selector with the specified widget. 
        
        This command will scan the document for any elements that match the specified CSS selector. If multiple elements match the specified selector, only the first element will be replaced.
        
        :param selector: Specifies the CSS selector to search for.
        :type selector: str
        :param new_widget: The new Tkinter widget to show. This may be any Tkinter widget.
        :type new_widget: :py:class:`tkinter.Widget`"""
        self._html.replace_element(selector, new_widget)
        
    def remove_widget(self, old_widget):
        """Removes the specified widget from the document.
        
        :param old_widget: The Tkinter widget to remove. This widget must be currently managed by TkinterWeb.
        :type old_widget: :py:class:`tkinter.Widget`"""
        self._html.remove_widget(old_widget)

    def register_JS_object(self, name, obj):
        """Register new JavaScript object. This can be used to access Python variables, functions, and classes from JavaScript (eg. to add a callback for the JavaScript ``alert()`` function). 
        
        JavaScript must be enabled. New in version 4.1.
        
        :param name: The name of the new JavaScript object.
        :type name: str
        :param obj: The Python object to pass.
        :type obj: anything
        :raises: RuntimeError if JavaScript is not enabled."""
        if self.html.javascript_enabled:
            if not pythonmonkey:
                self._initialize_javascript()
            pythonmonkey.eval(f"(function(pyObj) {{globalThis.{name} = pyObj}})")(obj)
        else:
            raise RuntimeError("JavaScript support must be enabled to register a JavaScript object")

    def _check_value(self, old, new):
        expected_type = type(old)
        if callable(old) or old == None:
            if not callable(new):
                raise TypeError(f"expected callable object, got \"{expected_type.__name__}\"")
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
            resizeable_elements = self.document.querySelectorAll(f"[{BUILTIN_ATTRIBUTES['vertical-align']}]")
            for element in resizeable_elements:
                element.style.height = f"{height/self['zoom']}px"
        self._prev_height = height

    def _manage_vsb(self, allow=None):
        "Show or hide the scrollbars."
        if allow == None:
            allow = self.vertical_scrollbar
        if allow == "auto":
            allow = 2
        self._vsb.set_type(allow)
        return allow
    
    def _manage_hsb(self, allow=None):
        "Show or hide the scrollbars."
        if allow == None:
            allow = self.horizontal_scrollbar
        if allow == "auto":
            allow = 2
        self._hsb.set_type(allow)
        return allow

    def _continue_loading(self, url, data="", method="GET", decode=None, force=False):
        "Finish loading urls and handle URI fragments."
        code = 404
        self._current_url = url

        self._html.post_event(DOWNLOADING_RESOURCE_EVENT)
        
        try:
            method = method.upper()
            parsed = urlparse(url)

            if method == "GET":
                url = str(url) + str(data)

            # if url is different than the current one, load the new site
            if force or (method == "POST") or ((urldefrag(url)[0]).replace("/", "") != (urldefrag(self._previous_url)[0]).replace("/", "")):
                view_source = False
                if url.startswith("view-source:"):
                    view_source = True
                    url = url.replace("view-source:", "")
                    parsed = urlparse(url)
                self._html.post_message(f"Connecting to {parsed.netloc}")
                if self._html.insecure_https:
                    self._html.post_message("WARNING: Using insecure HTTPS session")
                if (parsed.scheme == "file") or (not self._html.caches_enabled):
                    data, newurl, filetype, code = download(
                        url, data, method, decode, self._html.insecure_https, tuple(self._html.headers.items()))
                else:
                    data, newurl, filetype, code = cache_download(
                        url, data, method, decode, self._html.insecure_https, tuple(self._html.headers.items()))
                self._html.post_message(f"Successfully connected to {parsed.netloc}")
                if get_current_thread().isrunning():
                    if view_source:
                        newurl = "view-source:"+newurl
                        if self._current_url != newurl:
                            self._current_url = newurl
                            self._html.post_event(URL_CHANGED_EVENT)
                        data = str(data).replace("<","&lt;").replace(">", "&gt;")
                        data = data.splitlines()
                        length = int(len(str(len(data))))
                        if len(data) > 1:
                            data = "</code><br><code>".join(data)
                            data = data.rsplit("<br><code>", 1)[0]
                            data = data.split("</code><br>", 1)[1]
                        else:
                            data = "".join(data)
                        self.load_html(BUILTIN_PAGES["about:view-source"].format(self.about_page_background, self.about_page_foreground, length*9, data), newurl)
                    elif "image" in filetype:
                        self.load_html("", newurl)
                        if self._current_url != newurl:
                            self._html.post_event(URL_CHANGED_EVENT)
                        name = self._html.image_name_prefix + str(len(self._html.loaded_images))
                        self._html.finish_fetching_images(None, data, name, filetype, newurl)
                        self.add_html(BUILTIN_PAGES["about:image"].format(self.about_page_background, self.about_page_foreground, name))
                    else:
                        if self._current_url != newurl:
                            self._current_url = newurl
                            self._html.post_event(URL_CHANGED_EVENT)
                        self.load_html(data, newurl)
            else:
                # if no requests need to be made, we can signal that the page is done loading
                self._html.post_event(DONE_LOADING_EVENT)
                self._finish_css()

            # handle URI fragments
            frag = parsed.fragment
            if frag:
                #self._html.tk.call(self._html._w, "_force")
                self._html.update()
                try:
                    frag = ''.join(char for char in frag if char.isalnum() or char in ("-", "_"))
                    node = self._html.search(f"[id={frag}]")
                    if node:
                        self._html.yview(node)
                    else:
                        node = self._html.search(f"[name={frag}]")
                        if node:
                            self._html.yview(node)
                except Exception:
                    pass
        except Exception as error:
            self._html.post_message(f"ERROR: could not load {url}: {error}")
            if "CERTIFICATE_VERIFY_FAILED" in str(error):
                self._html.post_message(f"Check that you are using the right url scheme. Some websites only support http.\n\
This might also happen if your Python distribution does not come installed with website certificates.\n\
This is a known Python bug on older MacOS systems. \
Running something along the lines of \"/Applications/Python {'.'.join(PYTHON_VERSION[:2])}/Install Certificates.command\" (with the qoutes) to install the missing certificates may do the trick.\n\
Otherwise, use 'configure(insecure_https=True)' to ignore website certificates.")
            self.on_navigate_fail(url, error, code)

        self._thread_in_progress = None

    def _finish_css(self):        
        if self._waiting_for_reset:
            self._waiting_for_reset = False
            for style in self._accumulated_styles:
                self.add_css(style)
            self._accumulated_styles = []

    def _initialize_javascript(self):
        # Lazy loading of JS engine
        global pythonmonkey
        try:
            import pythonmonkey
            self.register_JS_object("document", self.document)
        except ModuleNotFoundError:
            raise ModuleNotFoundError("PythonMonkey is required to run JavaScript files but is not installed.")

    def _on_script(self, attributes, tag_contents):
        if self.html.javascript_enabled and not pythonmonkey:
            self._initialize_javascript()
        try:
            pythonmonkey.eval(tag_contents)
        except Exception as error:
            if "src" in attributes:
                self.html.post_message(f"ERROR: the JavaScript interpreter encountered an error while running the script from {attributes['src']}: {error}")
            else:
                self.html.post_message(f"ERROR: the JavaScript interpreter encountered an error while running a script: {error}")

    def _on_element_script(self, node_handle, attribute, attr_contents):
        if self.html.javascript_enabled and not pythonmonkey:
            self._initialize_javascript()
        try:
            element = HTMLElement(self.document, node_handle)
            pythonmonkey.eval(f"(element) => {{function run() {{ {attr_contents} }}; run.bind(element)()}}")(element)
        except Exception as error:
            self.html.post_message(f"ERROR: the JavaScript interpreter encountered an error while running an {attribute} script: {error}")


class HtmlLabel(HtmlFrame):
    """The :class:`HtmlLabel` widget inherits from the :class:`HtmlFrame`. For a complete list of avaliable methods, configuration options, generated events, and state variables, see the :class:`HtmlFrame` docs.
    
    This class also accepts one additional parameter:

    :param text: Set the HTML content of the widget
    :type text: str
    """
    def __init__(self, master, text="", **kwargs):
        HtmlFrame.__init__(self, master, vertical_scrollbar=False, shrink=True, **kwargs)

        tags = list(self._html.bindtags())
        tags.remove("Html")
        self._html.bindtags(tags)

        self.load_html(text)
