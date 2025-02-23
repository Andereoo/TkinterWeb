"""
Widgets that expand on the functionality of the basic bindings
by adding scrolling, file loading, and many other convenience functions

Copyright (c) 2025 Andereoo
"""

from urllib.parse import urldefrag, urlparse

from bindings import TkinterWeb
from utilities import (PLATFORM, WORKING_DIR, PYTHON_VERSION, BUILTIN_PAGES, DONE_LOADING_EVENT, 
                       DOWNLOADING_RESOURCE_EVENT, URL_CHANGED_EVENT, DEFAULT_PARSE_MODE, DEFAULT_STYLE, 
                       DARK_STYLE, AutoScrollbar, StoppableThread, 
                       cachedownload, download, threadname, notifier, __version__)
from imageutils import createRGBimage
from dom import TkwDocumentObjectModel, HtmlElement

import tkinter as tk
from tkinter import ttk


class HtmlFrame(ttk.Frame):
    def __init__(self, master, **kwargs):
        # state and settings variables
        self.current_url = ""

        self._previous_url = ""
        self._accumulated_styles = []
        self._waiting_for_reset = False
        self._thread_in_progress = None
        self._prev_height = 0

        self.htmlframe_options = {
            "vertical_scrollbar": "auto",
            "horizontal_scrollbar": False,
            "broken_webpage_message": "",
        }
        self.tkinterweb_options = {
            "link_click_func": self.load_url,
            "form_submit_func": self.load_form_data,
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
            "image_alternate_text_enabled": True,
            "visited_links": [],
            "find_match_highlight_color": "#ef0fff",
            "find_match_text_color": "#fff",
            "find_current_highlight_color": "#38d878",
            "find_current_text_color": "#fff",
            "selected_text_highlight_color": "#3584e4",
            "selected_text_color": "#fff",
            "default_style": DEFAULT_STYLE,
            "dark_style": DEFAULT_STYLE + DARK_STYLE,
            "insecure_https": False,
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
            "mode": "standards",
        }
                            
        for key, value in self.htmlframe_options.items():
            if key in kwargs:
                value = self.htmlframe_options[key] = kwargs.pop(key)
            setattr(self, key, value)

        for key in list(kwargs.keys()):
            if key in self.tkinterweb_options:
                value = self._check_value(self.tkinterweb_options[key], kwargs.pop(key))
                self.tkinterweb_options[key] = value
            elif key in self.tkhtml_options:
                self.tkhtml_options[key] = kwargs.pop(key)

        super().__init__(master, **kwargs)

        # setup sub-widgets
        self.html = html = TkinterWeb(self, self.tkinterweb_options, **self.tkhtml_options)
        self.hsb = hsb = AutoScrollbar(self, orient=tk.HORIZONTAL, command=html.xview)
        self.vsb = vsb = AutoScrollbar(self, orient=tk.VERTICAL, command=html.yview)
        self.document = TkwDocumentObjectModel(html)
        self.style = ttk.Style()

        self.background = self.style.lookup('TFrame', 'background')
        self.foreground = self.style.lookup('TLabel', 'foreground')

        html.configure(xscrollcommand=hsb.set)
        html.configure(yscrollcommand=vsb.set)

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
        if not self.html.overflow_scroll_frame:
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

        # redirected commands
        self.select_all = html.select_all
        self.clear_selection = html.clear_selection
        self.get_selection = html.get_selection
        self.resolve_url = html.resolve_url
        self.yview = html.yview
        self.yview_moveto = html.yview_moveto
        self.yview_scroll = html.yview_scroll
        self.replace_widget = html.replace_widget
        self.replace_element = html.replace_element
        self.remove_widget = html.remove_widget
        self.bind = html.bind

        self.html.post_message(f"Welcome to TkinterWeb {__version__}! \nhttps://github.com/Andereoo/TkinterWeb\n\nDebugging messages are enabled \nUse the parameter `messages_enabled = False` when calling HtmlFrame() or HtmlLabel() to disable these messages")

    def configure(self, **kwargs):
        for key in list(kwargs.keys()):
            if key in self.htmlframe_options:
                value = self._check_value(self.htmlframe_options[key], kwargs.pop(key))
                setattr(self, key, value)
                if key == "vertical_scrollbar":
                    self._manage_vsb(value)
                elif key == "horizontal_scrollbar":
                    self._manage_hsb(value)
            elif key in self.tkinterweb_options:
                value = self._check_value(self.tkinterweb_options[key], kwargs.pop(key))
                setattr(self.html, key, value)
            elif key in self.tkhtml_options:
                self.html[key] = kwargs.pop(key)
        super().configure(**kwargs)

    def config(self, **kwargs):
        self.configure(**kwargs)

    def cget(self, key):
        if key in self.htmlframe_options:
            return getattr(self, key)
        elif key in self.tkinterweb_options.keys():
            return getattr(self.html, key)
        elif key in self.tkhtml_options.keys():
            return self.html.cget(key)
        return super().cget(key)
    
    def __getitem__(self, key):
        return self.cget(key)

    def __setitem__(self, key, value):
        self.configure(**{key: value})

    @property
    def base_url(self):
        return self.html.base_url

    @property
    def title(self):
        return self.html.title
    
    @property
    def icon(self):
        return self.html.icon

    def load_html(self, html_source, base_url=None):
        "Reset parser and send html code to it"
        self.html.reset()

        if base_url == None:
            path = WORKING_DIR
            if not path.startswith("/"):
                path = f"/{path}"
            base_url = f"file://{path}/"
        self.html.base_url = self.current_url = base_url
        self.html.parse(html_source)

        self._finish_css()
        self._handle_resize()

    def load_file(self, file_url, decode=None, force=False):
        "Convenience method to load a locally stored file from the specified path"
        self._previous_url = self.current_url
        if not file_url.startswith("file://"):
            if PLATFORM.system == "Windows" and not file_url.startswith("/"):
                file_url = "file:///" + str(file_url)
            else:
                file_url = "file://" + str(file_url)
            self.current_url = file_url
            self.html.post_event(URL_CHANGED_EVENT, url=file_url)
        self.load_url(file_url, decode, force)

    def load_website(self, website_url, decode=None, force=False):
        "Convenience method to load a website from the specified URL"
        self._previous_url = self.current_url
        if (not website_url.startswith("https://")) and (not website_url.startswith("http://")) and (not website_url.startswith("about:")):
            website_url = "http://" + str(website_url)
            self.current_url = website_url
            self.html.post_event(URL_CHANGED_EVENT, url=website_url)
        self.load_url(website_url, decode, force)

    def load_url(self, url, decode=None, force=False):
        "Load a website or a file from the specified URL"
        if not self.current_url == url:
            self._previous_url = self.current_url
        if url in BUILTIN_PAGES:
            self.load_html(BUILTIN_PAGES[url].format(self.background, self.foreground, "", "No file selected"), url)
            return

        self._waiting_for_reset = True

        # ugly workaround for Bug #40, where urllib.urljoin constructs improperly formatted urls on Linux when url starts with file:///
        if not url.startswith("file://///"):
            newurl = url.replace("file:////", "file:///")
            if newurl != url:
                url = newurl
                self.current_url = url
                self.html.post_event(URL_CHANGED_EVENT, url=url)

        if self._thread_in_progress:
            self._thread_in_progress.stop()
        if self.html.maximum_thread_count >= 1:
            thread = StoppableThread(target=self._continue_loading, args=(
                url,), kwargs={"decode": decode, "force": force})
            self._thread_in_progress = thread
            thread.start()
        else:
            self._continue_loading(url, decode=decode, force=force)

    def load_form_data(self, url, data, method="GET", decode=None):
        "Load a webpage using form data"
        self._previous_url = self.current_url
        if self._thread_in_progress:
            self._thread_in_progress.stop()
        if self.html.maximum_thread_count >= 1:
            thread = StoppableThread(
                target=self._continue_loading, args=(url, data, method, decode))
            self._thread_in_progress = thread
            thread.start()
        else:
            self._continue_loading(url, data, method, decode)

    def add_html(self, html_source):
        "Parse HTML and add it to the end of the current document"
        self._previous_url = ""
        if not self.html.base_url:
            path = WORKING_DIR
            if not path.startswith("/"):
                path = f"/{path}"
            base_url = f"file://{path}/"
            self.html.base_url = self.current_url = base_url
        self.html.parse(html_source)

    def add_css(self, css_source):
        "Parse CSS code"
        if self._waiting_for_reset:
            self._accumulated_styles.append(css_source)
        else:
            self.html.parse_css(data=css_source, override=True)

    def stop(self):
        "Stop loading a page"
        if self._thread_in_progress:
            self._thread_in_progress.stop()
        self.html.stop()
        self.current_url = self._previous_url
        self.html.post_event(URL_CHANGED_EVENT, url=self.current_url)
        self.html.post_event(DONE_LOADING_EVENT)

    def find_text(self, searchtext, select=1, ignore_case=True, highlight_all=True, detailed=False):
        "Search for and highlight specific text"
        nmatches, selected, matches = self.html.find_text(searchtext, select, ignore_case, highlight_all)
        if detailed:
            return nmatches, selected, matches
        else:
            return nmatches
        
    def get_currently_hovered_element(self, ignore_text_nodes=True):
        "Return the element under the mouse"
        node = self.html.current_node
        if ignore_text_nodes:
            if not self.html.get_node_tag(self.html.current_node):
                node = self.html.get_node_parent(self.html.current_node)
        return HtmlElement(self.html, node)
    
    def yview_toelement(self, element):
        "Scroll to a given element"
        self.html.yview(element.node)

    def screenshot_page(self, file=None, full=False):
        "Take a screenshot"
        self.html.post_message(f"Taking a screenshot of {self.current_url}...")
        image, data = self.html.image(full=full)
        height = len(data)
        width = len(data[0].split())
        image = createRGBimage(data, width, height)
        if file:
            image.save(file)
        self.html.post_message(f"Screenshot taken: {width}px by {height}px!")
        return image

    def print_page(self, file=None, cnf={}, **kwargs):
        "Print the page"
        cnf |= kwargs
        self.html.post_message(f"Printing {self.current_url}...")
        if file:
            cnf["file"] = file
        if "pagesize" in cnf:
            pageheights = {
                "A3": "1191", "A4": "842", "A5": "595",
                "LEGAL": "792", "LETTER": "1008"
            }
            pagewidths = {
                "A3": "842", "A4": "595", "A5": "420",
                "LEGAL": "612", "LETTER": "612"
            }
            try:
                cnf["pageheight"] = pageheights[cnf["pagesize"].upper()]
                cnf["pagewidth"] = pagewidths[cnf["pagesize"].upper()]
                self.html.post_message(f"Setting printer page size to {cnf["pageheight"]}px by {cnf["pagewidth"]}px.")
            except KeyError:
                raise KeyError("Parameter 'pagesize' must be A3, A4, A5, Legal, or Letter")
            del cnf["pagesize"]

        self.html.update() # update the root window to ensure HTML is rendered
        file = self.html.postscript(cnf)
        # no need to save - tkhtml handles that for us
        self.html.post_message("Printed!")
        return file
    
    def save_page(self, file=None):
        "Save the page"
        self.html.post_message(f"Saving {self.current_url}...")
        html = self.document.documentElement.innerHTML
        if file:
            with open(file, "w+") as handle:
                handle.write(html)
        self.html.post_message("Saved!")
        return html
    
    def snapshot_page(self, file=None, allow_agent=False):
        "Save a snapshot of the page"
        self.html.post_message(f"Snapshotting {self.current_url}...")
        title = ""
        icon = ""
        base = ""
        style = ""
        
        for rule in self.html.get_computed_styles():
            selector, prop, origin = rule
            if origin == "agent" and not allow_agent: continue
            style += f"{selector} {{{prop}}}\n"

        if self.html.title: title = f"\n        <title>{self.html.title}</title>"
        if self.html.icon: icon = f"\n        <link rel=\"icon\" type=\"image/x-icon\" href=\"/{self.html.icon}\">"
        if self.html.base_url: base = f"\n        <base href=\"{self.html.base_url}\"</base>"
        if style: style = f"\n        <style>{style}</style>"
        body = self.document.body.innerHTML

        html = f"""<html>\n    <head>{title}{icon}{base}{style}\n    </head>\n    <body>\n        {body}\n    </body>\n</html>"""
        if file:
            with open(file, "w+") as handle:
                handle.write(html)
        self.html.post_message("Saved!")
        return html
    
    def _check_value(self, old, new):
        expected_type = type(old)
        if callable(old) or old == None:
            if not callable(new):
                raise TypeError(f"expected callable object, got \"{expected_type.__name__}\"")
        elif not isinstance(new, expected_type):
            try:
                new = expected_type(new)
            except (TypeError, ValueError,):
                raise TypeError(f"expected {expected_type.__name__}, got \"{new}\"")
        return new
    
    def _handle_resize(self, event=None):
        if (event and self._prev_height != event.height) or (not event):
            resizeable_elements = self.document.querySelectorAll("[tkinterweb-full-page]")
            for element in resizeable_elements:
                element.style.height = f"{self._prev_height}px"
        if event:
            self._prev_height = event.height

    def _manage_vsb(self, allow=None):
        "Show or hide the scrollbars"
        if allow == None:
            allow = self.vertical_scrollbar
        if allow == "auto":
            allow = 2 
        self.vsb.set_type(allow)
        return allow
    
    def _manage_hsb(self, allow=None):
        "Show or hide the scrollbars"
        if allow == None:
            allow = self.horizontal_scrollbar
        if allow == "auto":
            allow = 2
        self.hsb.set_type(allow)
        return allow

    def _continue_loading(self, url, data="", method="GET", decode=None, force=False):
        "Finish loading urls and handle URI fragments"
        code = 404
        self.current_url = url

        self.html.post_event(DOWNLOADING_RESOURCE_EVENT)
        
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
                self.html.post_message(f"Connecting to {parsed.netloc}")
                if self.html.insecure_https:
                    self.html.post_message("WARNING: Using insecure HTTPS session")
                if (parsed.scheme == "file") or (not self.html.caches_enabled):
                    data, newurl, filetype, code = download(
                        url, data, method, decode, self.html.insecure_https)
                else:
                    data, newurl, filetype, code = cachedownload(
                        url, data, method, decode, self.html.insecure_https)
                self.html.post_message(f"Successfully connected to {parsed.netloc}")
                if threadname().isrunning():
                    if view_source:
                        newurl = "view-source:"+newurl
                        if self.current_url != newurl:
                            self.current_url = newurl
                            self.html.post_event(URL_CHANGED_EVENT, url=newurl)
                        data = str(data).replace("<","&lt;").replace(">", "&gt;")
                        data = data.splitlines()
                        length = int(len(str(len(data))))
                        if len(data) > 1:
                            data = "</code><br><code>".join(data)
                            data = data.rsplit("<br><code>", 1)[0]
                            data = data.split("</code><br>", 1)[1]
                        else:
                            data = "".join(data)
                        self.load_html(BUILTIN_PAGES["about:view-source"].format(self.background, self.foreground, length*9, data), newurl)
                    elif "image" in filetype:
                        self.load_html("", newurl)
                        if self.current_url != newurl:
                            self.html.post_event(URL_CHANGED_EVENT, url=newurl)
                        name = self.html.image_name_prefix + str(len(self.html.loaded_images))
                        self.html.finish_fetching_images(data, name, filetype, newurl)
                        self.add_html(BUILTIN_PAGES["about:image"].format(self.background, self.foreground, name))
                    else:
                        if self.current_url != newurl:
                            self.current_url = newurl
                            self.html.post_event(URL_CHANGED_EVENT, url=newurl)
                        self.load_html(data, newurl)
            else:
                # if no requests need to be made, we can signal that the page is done loading
                self.html.post_event(DONE_LOADING_EVENT)
                self._finish_css()

            # handle URI fragments
            frag = parsed.fragment
            if frag:
                #self.html.tk.call(self.html._w, "_force")
                self.html.update()
                try:
                    frag = ''.join(char for char in frag if char.isalnum() or char in ("-", "_"))
                    node = self.html.search(f"[id={frag}]")
                    if node:
                        self.html.yview(node)
                    else:
                        node = self.html.search(f"[name={frag}]")
                        if node:
                            self.html.yview(node)
                except Exception:
                    pass
        except Exception as error:
            self._on_error(url, error, code)

        self._thread_in_progress = None

    def _on_error(self, url, error, code):
        self.html.post_message(f"Error loading {url}: {error}")
        if self.broken_webpage_message:
            self.load_html(self.broken_webpage_message, url)
        else:
            self.load_html(BUILTIN_PAGES["about:error"].format(self.background, self.foreground, code), url)
        
        if "CERTIFICATE_VERIFY_FAILED" in str(error):
            self.html.post_message(f"Check that you are using the right url scheme. Some websites only support http.\n\
This might also happen if your Python distribution does not come installed with website certificates.\n\
This is a known Python bug on older MacOS systems. \
Running something along the lines of \"/Applications/Python {".".join(PYTHON_VERSION[:2])}/Install Certificates.command\" (with the qoutes) to install the missing certificates may do the trick.\n\
Otherwise, use 'configure(insecure_https=True)' to ignore website certificates.")

    def _finish_css(self):        
        if self._waiting_for_reset:
            self._waiting_for_reset = False
            for style in self._accumulated_styles:
                self.add_css(style)
            self._accumulated_styles = []

class HtmlLabel(HtmlFrame):
    def __init__(self, master, text="", **kwargs):
        HtmlFrame.__init__(self, master, vertical_scrollbar=False, shrink=True, **kwargs)

        tags = list(self.html.bindtags())
        tags.remove("Html")
        self.html.bindtags(tags)

        self.load_html(text)