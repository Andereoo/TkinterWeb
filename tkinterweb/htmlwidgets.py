"""
TkinterWeb v3.18
This is a wrapper for the Tkhtml3 widget from http://tkhtml.tcl.tk/tkhtml.html, 
which displays styled HTML documents in Tkinter.

Copyright (c) 2023 Andereoo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from bindings import TkinterWeb
from utilities import (AutoScrollbar, StoppableThread, cachedownload, download,
                   notifier, currentpath, threadname)
from imageutils import newimage
import platform

try:
    from urllib.parse import urlparse, urldefrag
except ImportError:
    from urlparse import urlparse, urldefrag

try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:
    import Tkinter as tk
    import ttk


class HtmlFrame(ttk.Frame):
    def __init__(self, master, messages_enabled=True, vertical_scrollbar="auto", horizontal_scrollbar=False, scroll_overflow=None, **kw):
        ttk.Frame.__init__(self, master, **kw)

        if messages_enabled:
            self.message_func = message_func = notifier
        else:
            self.message_func = message_func = lambda message: None

        # setup scrollbars and HTML widget
        self.html = html = TkinterWeb(self, message_func, HtmlFrame)
        html.grid(row=0, column=0, sticky=tk.NSEW)

        if vertical_scrollbar:
            if vertical_scrollbar == "auto":
                self.vsb = vsb = AutoScrollbar(
                    self, orient=tk.VERTICAL, command=html.yview)
            else:
                self.vsb = vsb = ttk.Scrollbar(
                    self, orient=tk.VERTICAL, command=html.yview)

            vsb.bind("<Enter>", html.on_leave)
            vsb.bind("<MouseWheel>", self.scroll)
            vsb.bind("<Button-4>", self.scroll_x11)
            vsb.bind("<Button-5>", self.scroll_x11)
            html.bind("<Button-4>", self.overflow_scroll_x11)
            html.bind("<Button-5>", self.overflow_scroll_x11)
            self.bind_class("{0}.document".format(html),
                            "<MouseWheel>", self.scroll)
            self.bind_class(html.scrollable_node_tag,
                            "<MouseWheel>", self.scroll)
            self.bind_class(html.scrollable_node_tag,
                            "<Button-4>", self.scroll_x11)
            self.bind_class(html.scrollable_node_tag,
                            "<Button-5>", self.scroll_x11)

            html.configure(yscrollcommand=vsb.set)
            vsb.grid(row=0, column=1, sticky=tk.NSEW)

        if horizontal_scrollbar:
            if horizontal_scrollbar == "auto":
                self.hsb = hsb = AutoScrollbar(
                    self, orient=tk.HORIZONTAL, command=html.xview)
            else:
                self.hsb = hsb = ttk.Scrollbar(
                    self, orient=tk.HORIZONTAL, command=html.xview)

            hsb.bind("<Enter>", html.on_leave)

            html.configure(xscrollcommand=hsb.set)
            hsb.grid(row=1, column=0, sticky=tk.NSEW)

        self.bind("<Leave>", html.on_leave)

        # state and settings variables
        self.master = master
        self.scroll_overflow = scroll_overflow
        self.current_url = ""
        self.cursor = ""
        self.image_count = 0
        self.image = None
        self.thread_in_progress = None
        self.broken_page_msg = """<html>
                                    <head><title>Error 404</title></head>
                                    <body style="text-align:center;">
                                        <h2>Oops.</h2><p></p>
                                        <h3>The page you've requested could not be found.</h3>
                                    </body>
                                  </html>"""
        html.cursor_change_func = self.change_cursor
        html.link_click_func = self.load_url
        html.form_submit_func = self.load_form_data
        self.done_loading_func = lambda: None
        self.url_change_func = lambda url: None
        self.html.done_loading_func = self.done_loading

        self.message_func(
            "Welcome to TkinterWeb 3.18! \nhttps://github.com/Andereoo/TkinterWeb")

        self.message_func(
            "Debugging messages are enabled. \nUse the parameter `messages_enabled = False` when calling HtmlFrame() to disable these messages.")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        #Redirected commands
        self.select_all = self.html.select_all
        self.bind = self.html.bind
        self.set_zoom = self.html.set_zoom
        self.get_zoom = self.html.get_zoom
        self.set_fontscale = self.html.set_fontscale
        self.get_fontscale = self.html.get_fontscale
        self.set_parsemode = self.html.set_parsemode
        self.get_parsemode = self.html.get_parsemode
        self.resolve_url = self.html.resolve_url

    def load_website(self, website_url, decode=None, force=False):
        "Load a website from the specified URL"
        if (not website_url.startswith("https://")) and (not website_url.startswith("http://")) and (not website_url.startswith("about:")):
            website_url = "http://" + str(website_url)
        self.load_url(website_url, decode, force)

    def load_file(self, file_url, decode=None, force=False):
        "Load a locally stored file from the specified path"
        file_url = str(file_url).split("/", 1)[1]
        if not file_url.startswith("/"):
            file_url = "/" + file_url
        file_url = "file://" + file_url
        self.load_url(file_url, decode, force)

    def load_url(self, url, decode=None, force=False):
        """Load a website (https:// or http://) or a file (file://) from the specified URL.
        We use threading here to prevent the GUI from freezing while fetching the website.
        Technically Tkinter isn't threadsafe and will crash when doing this, but under certain circumstances we can get away with it.
        As long as we do not use the .join() method and no errors are raised in the mainthread, we should be okay.
        """
        #Workaround for Bug #40, where urllib.urljoin constructs improperly formatted urls on Linux when url starts with file:///
        if not url.startswith("file://///"):
            url = url.replace("file:////", "file:///")
                
        if self.thread_in_progress:
            self.thread_in_progress.stop()
        if self.html.max_thread_count >= 1:
            thread = StoppableThread(target=self.continue_loading, args=(
                url,), kwargs={"decode": decode, "force": force})
            self.thread_in_progress = thread
            thread.start()
        else:
            self.continue_loading(url, decode=decode, force=force)

    def load_form_data(self, url, data, method="GET", decode=None):
        "Load a webpage using form data"
        if self.thread_in_progress:
            self.thread_in_progress.stop()
        if self.html.max_thread_count >= 1:
            thread = StoppableThread(
                target=self.continue_loading, args=(url, data, method, decode,))
            self.thread_in_progress = thread
            thread.start()
        else:
            self.continue_loading(url, data, method, decode)

    def continue_loading(self, url, data="", method="GET", decode=None, force=False):
        "Finish loading urls and handle URI fragments"
        self.html.downloading_resource_func()
        self.url_change_func(url)
        try:
            method = method.upper()
            parsed = urlparse(url)

            if method == "GET":
                url = str(url) + str(data)

            # if url is different than the current one, load the new site.
            if force or (method == "POST") or (self.skim(urldefrag(url)[0]) != self.skim(urldefrag(self.current_url)[0])):
                self.message_func("Connecting to {0}.".format(parsed.netloc))
                if (parsed.scheme == "file") or (not self.html.caches_enabled):
                    data, newurl, filetype = download(
                        url, data, method, decode)
                else:
                    data, newurl, filetype = cachedownload(
                        url, data, method, decode)
                if threadname().isrunning():
                    self.url_change_func(newurl)
                    if "image" in filetype:
                        image, error = newimage(data, "_htmlframe_img_{}_{}_".format(id(self), self.image_count), filetype, self.html.image_inversion_enabled)
                        self.load_html("<img style='max-width:100%' src='replace:{}'></img".format(image))
                        self.image_count += 1
                        self.image = image
                    else:
                        self.load_html(data, newurl)
                    self.current_url = newurl
            else:
                # if no requests need to be made, we can signal that the page is done loading
                self.html.done_loading_func()
            # handle URI fragments
            frag = parsed.fragment
            if frag:
                #self.html.tk.call(self.html._w, "_force")
                try:
                    node = self.html.search("[id=%s]" % frag)
                    if node:
                        self.html.yview(node)
                    else:
                        node = self.html.search("[name=%s]" % frag)
                        if node:
                            self.html.yview(node)
                except Exception:
                    pass
        except Exception as error:
            self.message_func(
                "An error has been encountered while loading {}: {}.".format(url, error))
            self.load_html(self.broken_page_msg)
            self.current_url = ""

        self.thread_in_progress = None

    def skim(self, url):
        return url.replace("/", "")

    def stop(self):
        "Stop loading a page"
        if self.thread_in_progress:
            self.thread_in_progress.stop()
        self.html.stop()
        self.url_change_func(self.current_url)
        self.done_loading()

    def done_loading(self):
        self.in_progress = False
        self.done_loading_func()

    def on_link_click(self, function):
        "Allows for handling link clicks"
        self.html.link_click_func = function

    def on_form_submit(self, function):
        "Allows for handling form submissions"
        self.html.form_submit_func = function

    def on_title_change(self, function):
        "Allows for handling title changes"
        self.html.title_change_func = function

    def on_icon_change(self, function):
        "Allows for handling page icon changes"
        self.html.icon_change_func = function

    def on_url_change(self, function):
        "Allows for handling url redirects"
        self.url_change_func = function

    def on_done_loading(self, function):
        "Alllows for handling the finishing of all outstanding requests"
        self.done_loading_func = function

    def on_downloading_resource(self, function):
        "Allows for handling resource downloads"
        self.html.downloading_resource_func = function

    def set_recursive_hover_depth(self, depth):
        "Change the max recursion depth to add a css 'hover' flag onto HTML elements"
        self.html.recursive_hovering_count = int(depth)

    def set_maximum_thread_count(self, maximum):
        "Change the maximum number of threads that can run at any given point in time"
        self.html.max_thread_count = int(maximum)

    def set_broken_webpage_message(self, html):
        "Set the HTML that is shown whan a requested webpage could not be reached"
        self.broken_page_msg = html

    def add_visited_links(self, links):
        "Add links to the list of visited links"
        self.html.visited_links.extend(links)

    def clear_visited_links(self):
        "Clear the list of visited links"
        self.html.visited_links = []

    def ignore_invalid_images(self, value):
        "Choose to ignore broken images"
        self.html.ignore_invalid_images = value

    def set_message_func(self, function):
        "Change the message output function"
        self.message_func = function
        self.html.message_func = function

    def enable_stylesheets(self, enabled=True):
        "Enable or disable stylesheet loading"
        self.html.stylesheets_enabled = enabled

    def enable_images(self, enabled=True):
        "Enable or disable image loading"
        self.html.images_enabled = enabled

    def enable_forms(self, enabled=True):
        "Enable or disable form-filling"
        self.html.forms_enabled = enabled

    def enable_objects(self, enabled=True):
        "Enable or disable <iframe> and <object> elements"
        self.html.objects_enabled = enabled

    def enable_caches(self, enabled=True):
        "Enable or disable file caches"
        self.html.caches_enabled = enabled

    def enable_crash_prevention(self, enabled=True):
        "Enable or disable extra crash prevention measures"
        "Disabling this will remove all emojis, the noto color emoji font, and invalid rgb functions"
        self.html.prevent_crashes = enabled

    def enable_dark_theme(self, enabled=True, invert_images=True):
        "Enable or disable dark theme"
        "This will cause page colours to be 'inverted' if enabled is set to True"
        "This will also cause images to be inverted if 'invert_images' is also set to True"
        if (enabled or invert_images): 
            self.message_func("Warning: dark theme has been enabled. This feature is highly experimental and may cause freezes or crashes.")
        self.html.dark_theme_enabled = enabled
        self.html.image_inversion_enabled = invert_images
        self.html.update_default_style()

    def copy_settings(self, html):
        self.set_message_func(html.message_func)
        self.set_recursive_hover_depth(html.recursive_hovering_count)
        self.set_maximum_thread_count(html.max_thread_count)
        self.ignore_invalid_images(html.ignore_invalid_images)
        self.enable_stylesheets(html.stylesheets_enabled)
        self.enable_images(html.images_enabled)
        self.enable_forms(html.forms_enabled)
        self.enable_objects(html.objects_enabled)
        self.enable_caches(html.caches_enabled)
        self.set_parsemode(html.get_parsemode())

    def find_text(self, searchtext, select=1, ignore_case=True, highlight_all=True):
        "Search for and highlight specific text"
        return self.html.find_text(searchtext, select, ignore_case, highlight_all)

    def change_cursor(self, cursor):
        "Handle cursor changes"
        if self.cursor != cursor:
            self.cursor = cursor
            self.config(cursor=cursor)

    def get_current_link(self, resolve=True):
        "Convenience method for getting the url of the current hyperlink"
        if self.get_currently_hovered_node_tag().lower() == "a": 
            href = self.get_currently_hovered_node_attribute("href")
            if resolve:
                return self.resolve_url(href)
            else:
                return href
        else:
            return ""

    def get_currently_hovered_node_tag(self):
        "Get the tag of the HTML element the mouse pointer is currently over"
        try:
            tag = self.html.get_node_tag(self.html.current_node)
            if tag == "":
                tag = self.html.get_node_tag(
                    self.html.get_node_parent(self.html.current_node))
        except tk.TclError:
            tag = ""
        return tag

    def get_currently_hovered_node_text(self):
        "Get the text content of the HTML element the mouse pointer is currently over"
        try:
            text = self.html.get_node_text(self.html.current_node)
            if text == "":
                text = self.html.get_node_text(
                    self.html.get_node_parent(self.html.current_node))
        except tk.TclError:
            text = ""
        return text

    def get_currently_hovered_node_attribute(self, attribute):
        """
        Get the specified attribute of the HTML element the mouse pointer is currently over
        For example, if the mouse is hovering over the element
        "<a href='example.com'></a>", calling "get_currently_hovered_node_attribute('href')" will return "example.com."
        """
        try:
            attr = self.html.get_node_attribute(
                self.html.current_node, attribute)
            if attr == "":
                attr = self.html.get_node_attribute(self.html.get_node_parent(
                    self.html.current_node), attribute)
        except tk.TclError:
            attr = ""
        return attr

    def get_currently_selected_text(self):
        "Get the text that is currently highlighted/selected."
        return self.html.get_selection()

    def replace_widget(self, oldwidget, newwidget):
        "Replace a stored widget"
        self.html.replace_widget(oldwidget, newwidget)

    def replace_element(self, cssselector, newwidget):
        "Replace an HTML element with a widget"
        self.html.replace_html(cssselector, newwidget)

    def remove_widget(self, widget):
        "Remove a stored widget"
        self.html.remove_widget(widget)

    def scroll(self, event):
        "Handle mouse/touchpad scrolling"
        yview = self.html.yview()
        if self.scroll_overflow and yview[0] == 0 and event.delta > 0:
            self.scroll_overflow.scroll(event)
        elif self.scroll_overflow and yview[1] == 1 and event.delta < 0:
            self.scroll_overflow.scroll(event)
        elif platform.system() == "Darwin":
            self.html.yview_scroll(int(-1*event.delta), "units")
        else:
            self.html.yview_scroll(int(-1*event.delta/30), "units")

    def scroll_x11(self, event):
        yview = self.html.yview()
        if event.num == 4:
            if self.scroll_overflow and yview[0] == 0:
                self.scroll_overflow.scroll_x11(event)
            else:
                self.html.yview_scroll(-4, "units")
        else:
            if self.scroll_overflow and yview[1] == 1:
                self.scroll_overflow.scroll_x11(event)
            else:
                self.html.yview_scroll(4, "units")
    
    def overflow_scroll_x11(self, event):
        yview = self.html.yview()
        if event.num == 4 and self.scroll_overflow and yview[0] == 0:
            self.scroll_overflow.scroll_x11(event)
        elif self.scroll_overflow and yview[1] == 1:
            self.scroll_overflow.scroll_x11(event)

    def load_html(self, html_source, base_url=None):
        "Reset parser and send html code to it"
        self.html.reset()
        if not base_url:
            path = currentpath(False)
            if not path.startswith("/"):
                path = "/{0}".format(path)
            base_url = "file://{0}/".format(path)
        self.current_url = base_url
        self.html.base_url = base_url
        self.html.parse(html_source)

    def add_html(self, html_source):
        "Parse HTML and add it to the end of the current document."
        self.html.parse(html_source)

    def add_css(self, css_source):
        "Parse CSS code"
        self.html.parse_css(data=css_source)


class HtmlLabel(HtmlFrame):
    def __init__(self, master, text="", messages_enabled=False, **kw):
        HtmlFrame.__init__(self, master, messages_enabled=messages_enabled, vertical_scrollbar=False, horizontal_scrollbar=False, **kw)

        tags = list(self.html.bindtags())
        tags.remove("Html")
        self.html.bindtags(tags)
        
        self.html.shrink(True)

        self.load_html(text)
