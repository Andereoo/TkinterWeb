"""
Widgets that expand on the functionality of the basic bindings
by adding scrolling, file loading, and many other convenience functions

Copyright (c) 2025 Andereoo
"""

from urllib.parse import urldefrag, urlparse

from bindings import TkinterWeb
from utilities import (PLATFORM, WORKING_DIR, PYTHON_VERSION, BUILTIN_PAGES, 
                       DEBUG_MESSAGE_EVENT, DONE_LOADING_EVENT, LINK_CLICK_EVENT, FORM_SUBMISSION_EVENT, 
                       DOWNLOADING_RESOURCE_EVENT, URL_CHANGED_EVENT,
                       AutoScrollbar, StoppableThread, 
                       cachedownload, download, threadname, notifier, __version__)
from imageutils import createRGBimage
from dom import TkwDocumentObjectModel, HtmlElement

import tkinter as tk
from tkinter import ttk


class HtmlFrame(ttk.Frame):
    def __init__(self, master, messages_enabled=False, vertical_scrollbar="auto", horizontal_scrollbar=False, overflow_scroll_frame=None, **kw):
        ttk.Frame.__init__(self, master, **kw)

        # state and settings variables
        self.current_url = ""
        self.previous_url = ""
        self.accumulated_styles = []
        self.waiting_for_reset = False
        self.thread_in_progress = None
        self.broken_webpage_message = ""

        # setup sub-widgets
        self.html = html = TkinterWeb(self, HtmlFrame, self._manage_vsb, self._manage_hsb, messages_enabled, overflow_scroll_frame)
        html.grid(row=0, column=0, sticky=tk.NSEW)

        self.document = TkwDocumentObjectModel(html)

        self.style = ttk.Style()
        self._on_style_change(None)

        self.hsb = hsb = AutoScrollbar(self, orient=tk.HORIZONTAL, command=html.xview)
        self.vsb = vsb = AutoScrollbar(self, orient=tk.VERTICAL, command=html.yview)

        self.hsb_type = None
        self.vsb_type = None
        self.original_hsb_type = horizontal_scrollbar
        self.original_vsb_type = vertical_scrollbar
        
        html.configure(xscrollcommand=hsb.set)
        html.configure(yscrollcommand=vsb.set)
        hsb.grid(row=1, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="nsew")
        self._manage_hsb(horizontal_scrollbar)
        self._manage_vsb(vertical_scrollbar)

        # setup default virtual event bindings
        html.bind(LINK_CLICK_EVENT, lambda event: self.load_url(event.url))
        html.bind(FORM_SUBMISSION_EVENT, lambda event: self.load_form_data(event.url, event.data, event.method))
        html.bind(DEBUG_MESSAGE_EVENT, lambda event: notifier(event.data))

        # html.document only applies to the document it is bound to (which makes things easy)
        # for some reason, binding to Html only works on Linux and binding to html.document only works on Windows
        # Html fires on all documents (i.e. <iframe> elements), so it has to be handled slightly differently
        if not overflow_scroll_frame:
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
        self.bind("<<ThemeChanged>>", self._on_style_change)

        html.post_event(DEBUG_MESSAGE_EVENT, data=f"Welcome to TkinterWeb {__version__}! \nhttps://github.com/Andereoo/TkinterWeb\n\nDebugging messages are enabled \nUse the parameter `messages_enabled = False` when calling HtmlFrame() or HtmlLabel() to disable these messages", direct_notify=True)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # redirected commands
        self.select_all = html.select_all
        self.clear_selection = html.clear_selection
        self.get_selection = html.get_selection
        self.bind = html.bind
        self.resolve_url = html.resolve_url
        self.yview = html.yview
        self.yview_moveto = html.yview_moveto
        self.yview_scroll = html.yview_scroll
        self.replace_widget = html.replace_widget
        self.replace_element = html.replace_element
        self.remove_widget = html.remove_widget

    @property
    def messages_enabled(self):
        return self.html.messages_enabled
    
    @messages_enabled.setter
    def messages_enabled(self, enabled):
        self.html.messages_enabled = enabled

    @property
    def selection_enabled(self):
        return self.html.selection_enabled
    
    @selection_enabled.setter
    def selection_enabled(self, enabled):
        self.html.selection_enabled = enabled

    @property
    def stylesheets_enabled(self):
        return self.html.stylesheets_enabled
    
    @stylesheets_enabled.setter
    def stylesheets_enabled(self, enabled):
        self.html.stylesheets_enabled = enabled

    @property
    def images_enabled(self):
        return self.html.images_enabled
    
    @images_enabled.setter
    def images_enabled(self, enabled):
        self.html.images_enabled = enabled

    @property
    def forms_enabled(self):
        return self.html.forms_enabled
    
    @forms_enabled.setter
    def forms_enabled(self, enabled):
        self.html.forms_enabled = enabled

    @property
    def objects_enabled(self):
        return self.html.objects_enabled
    
    @objects_enabled.setter
    def objects_enabled(self, enabled):
        self.html.objects_enabled

    @property
    def caches_enabled(self):
        return self.html.caches_enabled
    
    @caches_enabled.setter
    def caches_enabled(self, enabled):
        if self.html.caches_enabled != enabled:
            self.html.caches_enabled = enabled
            self.html.enable_imagecache(enabled)
    
    @property
    def dark_theme_enabled(self):
        return self.html.dark_theme_enabled
    
    @dark_theme_enabled.setter
    def dark_theme_enabled(self, enabled):
        if self.html.dark_theme_enabled != enabled:
            self.html.dark_theme_enabled = enabled    
            if enabled:
                self.html.post_event(DEBUG_MESSAGE_EVENT, data="WARNING: dark theme has been enabled. This feature is experimental and may cause freezes or crashes.")
            self.html.update_default_style()

    @property
    def image_inversion_enabled(self):
        return self.html.image_inversion_enabled
    
    @image_inversion_enabled.setter
    def image_inversion_enabled(self, enabled):
        if self.html.image_inversion_enabled != enabled:
            self.html.image_inversion_enabled = enabled
            if enabled:
                self.html.post_event(DEBUG_MESSAGE_EVENT, data="WARNING: image inversion has been enabled. This feature is experimental and may cause freezes or crashes.")

    @property
    def crash_prevention_enabled(self):
        return self.html.crash_prevention_enabled
    
    @crash_prevention_enabled.setter
    def crash_prevention_enabled(self, enabled):
        self.html.crash_prevention_enabled = enabled

    @property
    def threading_enabled(self):
        return bool(self.html.maximum_thread_count)
    
    @threading_enabled.setter
    def threading_enabled(self, enabled):
        if enabled:
            if self.html.allow_threading:
                self.html.maximum_thread_count = self.html.default_maximum_thread_count
            else:
                self.post_event(DEBUG_MESSAGE_EVENT, data="WARNING: threading will not be enabled because your Tcl/Tk library does not support threading")
                self.html.maximum_thread_count = 0
        else:
            self.html.maximum_thread_count = 0

    @property
    def base_url(self):
        return self.html.base_url

    @property
    def title(self):
        return self.html.title
    
    @property
    def icon(self):
        return self.html.icon
    
    @property
    def visited_links(self):
        return self.html.visited_links
    
    @visited_links.setter
    def visited_links(self, links):
        self.html.visited_links = links

    @property
    def zoom(self):
        return self.html.get_zoom()
    
    @zoom.setter
    def zoom(self, scale):
        self.html.set_zoom(scale)

    @property
    def fontscale(self):
        return self.html.get_fontscale()
    
    @fontscale.setter
    def fontscale(self, scale):
        self.html.set_fontscale(scale)

    @property
    def parsemode(self):
        return self.html.get_parsemode()
    
    @parsemode.setter
    def parsemode(self, mode):
        self.html.set_parsemode(mode)

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

    def load_file(self, file_url, decode=None, force=False, insecure=None):
        "Convenience method to load a locally stored file from the specified path"
        self.previous_url = self.current_url
        if not file_url.startswith("file://"):
            if PLATFORM.system == "Windows" and not file_url.startswith("/"):
                file_url = "file:///" + str(file_url)
            else:
                file_url = "file://" + str(file_url)
            self.current_url = file_url
            self.html.post_event(URL_CHANGED_EVENT, url=file_url)
        self.load_url(file_url, decode, force, insecure)

    def load_website(self, website_url, decode=None, force=False, insecure=None):
        "Convenience method to load a website from the specified URL"
        self.previous_url = self.current_url
        if (not website_url.startswith("https://")) and (not website_url.startswith("http://")) and (not website_url.startswith("about:")):
            website_url = "http://" + str(website_url)
            self.current_url = website_url
            self.html.post_event(URL_CHANGED_EVENT, url=website_url)
        self.load_url(website_url, decode, force, insecure)

    def load_url(self, url, decode=None, force=False, insecure=None):
        "Load a website or a file from the specified URL"
        if not self.current_url == url:
            self.previous_url = self.current_url
        if url in BUILTIN_PAGES:
            self.load_html(BUILTIN_PAGES[url].format(self.background, "", "No file selected"))
            return

        self.waiting_for_reset = True

        # ugly workaround for Bug #40, where urllib.urljoin constructs improperly formatted urls on Linux when url starts with file:///
        if not url.startswith("file://///"):
            newurl = url.replace("file:////", "file:///")
            if newurl != url:
                url = newurl
                self.current_url = url
                self.html.post_event(URL_CHANGED_EVENT, url=url)

        if self.thread_in_progress:
            self.thread_in_progress.stop()
        if self.html.maximum_thread_count >= 1:
            thread = StoppableThread(target=self._continue_loading, args=(
                url,), kwargs={"decode": decode, "force": force, "insecure": insecure})
            self.thread_in_progress = thread
            thread.start()
        else:
            self._continue_loading(url, decode=decode, force=force, insecure=insecure)

    def load_form_data(self, url, data, method="GET", decode=None, insecure=None):
        "Load a webpage using form data"
        self.previous_url = self.current_url
        if self.thread_in_progress:
            self.thread_in_progress.stop()
        if self.html.maximum_thread_count >= 1:
            thread = StoppableThread(
                target=self._continue_loading, args=(url, data, method, decode), kwargs={"insecure": insecure})
            self.thread_in_progress = thread
            thread.start()
        else:
            self._continue_loading(url, data, method, decode)

    def add_html(self, html_source):
        "Parse HTML and add it to the end of the current document"
        self.previous_url = ""
        if not self.html.base_url:
            path = WORKING_DIR
            if not path.startswith("/"):
                path = f"/{path}"
            base_url = f"file://{path}/"
            self.html.base_url = self.current_url = base_url
        self.html.parse(html_source)

    def add_css(self, css_source):
        "Parse CSS code"
        if self.waiting_for_reset:
            self.accumulated_styles.append(css_source)
        else:
            self.html.parse_css(data=css_source, override=True)

    def stop(self):
        "Stop loading a page"
        if self.thread_in_progress:
            self.thread_in_progress.stop()
        self.html.stop()
        self.current_url = self.previous_url
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
        "Convenience method to scroll to a given element"
        self.html.yview(element.node)

    def screenshot(self, file=None, full=False):
        "Take a screenshot"
        self.html.post_event(DEBUG_MESSAGE_EVENT, data=f"Taking a screenshot...")
        image, data = self.html.image(full=full)
        height = len(data)
        width = len(data[0].split())
        image = createRGBimage(data, width, height)
        self.html.post_event(DEBUG_MESSAGE_EVENT, data=f"Screenshot taken: {file} {width}px by {height}px.")
        if file: image.save(file)
        return image

    def print_page(self, cnf={}, **kw):
        "Print the page"
        cnf |= kw
        self.html.post_event(DEBUG_MESSAGE_EVENT, data=f"Printing {self.html.base_url}...")
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
                self.html.post_event(DEBUG_MESSAGE_EVENT, data=f"Setting printer page size to {cnf["pageheight"]}px by {cnf["pagewidth"]}px.")
            except KeyError:
                raise KeyError("Parameter 'pagesize' must be A3, A4, A5, Legal, or Letter")
            del cnf["pagesize"]

        self.html.update() # update the root window to ensure HTML is rendered
        file = self.html.postscript(cnf)
        self.html.post_event(DEBUG_MESSAGE_EVENT, data="Printed!")
        return file
    
    def save_page(self, file=None):
        "Save the page"
        html = self.document.documentElement.innerHTML
        if file:
            with open(file, "w+") as handle:
                handle.write(html)
        return html
    
    def create_snapshot(self, file=None):
        self.html.tk.setvar("zBase", self.html.base_url)
        html = self.html.tk.eval(r"""
            set html %s
            set zTitle ""
            set zStyle "\n"
            set zBody ""

            foreach rule [$html _styleconfig] {
                foreach {selector properties origin} $rule {}
                if {$origin eq "agent"} continue
                append zStyle "$selector { $properties }\n"
            }
            set titlenode [$html search title]
            if {$titlenode ne ""} {
                set child [lindex [$titlenode children] 0]
                if {$child ne ""} { set zTitle [$child text] }
            }
            set bodynode [$html search body]
            set zBody ""
            foreach child [$bodynode children] {
                append zBody [node_to_html $child 1]
            }
            # it has to be writen like this because it outputs the indention
            return [subst {<html>
    <head>
        <title>$zTitle</title>
        <style>$zStyle</style>
        <base href="$zBase"></base>
    </head>
    <body>
        $zBody
    </body>
</html>}]
        """ % self.html)
        if file:
            with open(file, "w+") as handle:
                handle.write(html)
        return html
    
    def copy_settings(self, html):
        "Copy settings from one html widget to this one"
        self.html.stylesheets_enabled = html.stylesheets_enabled
        self.html.images_enabled = html.images_enabled
        self.html.forms_enabled = html.forms_enabled
        self.html.objects_enabled = html.objects_enabled
        self.html.ignore_invalid_images = html.ignore_invalid_images
        self.html.crash_prevention_enabled = html.crash_prevention_enabled
        self.html.dark_theme_enabled = html.dark_theme_enabled
        self.html.image_inversion_enabled = html.image_inversion_enabled
        self.html.caches_enabled = html.caches_enabled
        self.html.recursive_hovering_count = html.recursive_hovering_count
        self.html.maximum_thread_count = html.maximum_thread_count
        self.html.default_maximum_thread_count = html.default_maximum_thread_count
        self.html.image_alternate_text_enabled = html.image_alternate_text_enabled
        self.html.selection_enabled = html.selection_enabled
        self.html.find_match_highlight_color = html.find_match_highlight_color
        self.html.find_match_text_color = html.find_match_text_color
        self.html.find_current_highlight_color = html.find_current_highlight_color
        self.html.find_current_text_color = html.find_current_text_color
        self.html.selected_text_highlight_color = html.selected_text_highlight_color
        self.html.selected_text_color = html.selected_text_color
        self.html.visited_links = html.visited_links
        self.html.insecure_https = html.insecure_https
        self.html.dark_theme_limit = html.dark_theme_limit
        self.html.style_dark_theme_regex = html.style_dark_theme_regex
        self.html.general_dark_theme_regexes = html.general_dark_theme_regexes
        self.html.inline_dark_theme_regexes = html.inline_dark_theme_regexes
    
    def _handle_resize(self, event):
        resizeable_elements = self.document.querySelectorAll("[tkinterweb-full-page]")
        for element in resizeable_elements:
            element.style.height = f"{event.height}px"

    def _on_style_change(self, event):
        self.background = self.style.lookup('TFrame', 'background')

    def _manage_vsb(self, allow=None):
        "Show or hide the scrollbars"
        if allow == None:
            allow = self.original_vsb_type
        if allow == "auto":
            allow = 2 
        if self.vsb_type != allow:
            self.vsb.set_type(allow)
            self.vsb_type = allow
        return allow
    
    def _manage_hsb(self, allow=None):
        "Show or hide the scrollbars"
        if allow == None:
            allow = self.original_hsb_type
        if allow == "auto":
            allow = 2
        if self.hsb_type != allow:
            self.hsb.set_type(allow)
            self.hsb_type = allow
        return allow

    def _continue_loading(self, url, data="", method="GET", decode=None, force=False, insecure=None):
        "Finish loading urls and handle URI fragments"
        if insecure == None:
            insecure = self.html.insecure_https
        else:
            self.html.insecure_https = insecure
        code = 404
        self.current_url = url

        self.html.post_event(DOWNLOADING_RESOURCE_EVENT)
        
        try:
            method = method.upper()
            parsed = urlparse(url)

            if method == "GET":
                url = str(url) + str(data)

            # if url is different than the current one, load the new site
            if force or (method == "POST") or ((urldefrag(url)[0]).replace("/", "") != (urldefrag(self.previous_url)[0]).replace("/", "")):
                view_source = False
                if url.startswith("view-source:"):
                    view_source = True
                    url = url.replace("view-source:", "")
                    parsed = urlparse(url)
                self.html.post_event(DEBUG_MESSAGE_EVENT, data=f"Connecting to {parsed.netloc}")
                if insecure:
                    self.html.post_event(DEBUG_MESSAGE_EVENT, data="WARNING: Using insecure HTTPS session")
                if (parsed.scheme == "file") or (not self.html.caches_enabled):
                    data, newurl, filetype, code = download(
                        url, data, method, decode, insecure)
                else:
                    data, newurl, filetype, code = cachedownload(
                        url, data, method, decode, insecure)
                self.html.post_event(DEBUG_MESSAGE_EVENT, data=f"Successfully connected to {parsed.netloc}")
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
                        self.load_html(BUILTIN_PAGES["about:view-source"].format(self.background, length*9, data), newurl)
                    elif "image" in filetype:
                        self.load_html("", newurl)
                        if self.current_url != newurl:
                            self.html.post_event(URL_CHANGED_EVENT, url=newurl)
                        name = self.html.image_name_prefix + str(len(self.html.loaded_images))
                        self.html.finish_fetching_images(data, name, filetype, newurl)
                        self.add_html(BUILTIN_PAGES["about:image"].format(self.background, name))
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

        self.thread_in_progress = None

    def _on_error(self, url, error, code):
        self.html.post_event(DEBUG_MESSAGE_EVENT, data=f"Error loading {url}: {error}")
        if self.broken_webpage_message:
            self.load_html(self.broken_webpage_message, "")
        else:
            self.load_html(BUILTIN_PAGES["about:error"].format(self.background, code), "")
        
        if "CERTIFICATE_VERIFY_FAILED" in str(error):
            self.html.post_event(DEBUG_MESSAGE_EVENT, data=f"Check that you are using the right url scheme. Some websites only support http.\n\
This might also happen if your Python distribution does not come installed with website certificates.\n\
This is a known Python bug on older MacOS systems. \
Running something along the lines of \"/Applications/Python {".".join(PYTHON_VERSION[:2])}/Install Certificates.command\" (with the qoutes) to install the missing certificates may do the trick.\n\
Otherwise, use 'insecure=True' when loading a page to ignore website certificates.")

    def _finish_css(self):        
        if self.waiting_for_reset:
            self.waiting_for_reset = False
            for style in self.accumulated_styles:
                self.add_css(style)
            self.accumulated_styles = []

class HtmlLabel(HtmlFrame):
    def __init__(self, master, text="", messages_enabled=False, **kw):
        HtmlFrame.__init__(self, master, messages_enabled=messages_enabled, vertical_scrollbar=False, horizontal_scrollbar=False, **kw)

        tags = list(self.html.bindtags())
        tags.remove("Html")
        self.html.bindtags(tags)

        self.html.set_shrink(True)

        self.load_html(text)