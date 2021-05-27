import os
import sys

from bindings import TkinterWeb
from utils import (AutoScrollbar, StoppableThread, cachedownload, download,
                   notifier, threadname)

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:
    import Tkinter as tk
    import ttk


class HtmlFrame(ttk.Frame):
    def __init__(self, master, messages_enabled=True, vertical_scrollbar="auto", horizontal_scrollbar=False, **kw):
        ttk.Frame.__init__(self, master, **kw)

        if messages_enabled:
            self.message_func = message_func = notifier
        else:
            self.message_func = message_func = lambda message: None

        # setup scrollbars and HTML widget
        self.html = html = TkinterWeb(self, message_func)
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

        # state and settings variables
        self.master = master
        self.current_url = ""
        self.cursor = ""
        self.thread_in_progress = None
        self.broken_page_msg = """<html>
                                    <head><title>Error 404</title></head>
                                    <body style="text-align:center;">
                                        <h2>Oops.</h2><p></p>
                                        <h3>The page you've requested could not be found.<h3>
                                    </body>
                                  </html>"""
        html.cursor_change_func = self.change_cursor
        html.link_click_func = self.load_url
        html.form_submit_func = self.load_form_data
        self.done_loading_func = lambda: None
        self.url_change_func = lambda url: None
        self.html.done_loading_func = self.done_loading

        self.message_func(
            "Welcome to TkinterWeb 3.5! \nhttps://github.com/Andereoo/TkinterWeb")

        self.message_func(
            "Debugging messages are enabled. \nUse the parameter `messages_enabled = False` when calling HtmlFrame() to disable these messages.")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def load_website(self, website_url, decode=None, force=False):
        "Load a website from the specified URL"
        if (not website_url.startswith("https://")) and (not website_url.startswith("http://")):
            website_url = "https://" + str(website_url)
        self.load_url(website_url, decode, force)

    def load_file(self, file_url, decode=None, force=False):
        "Load a locally stored file from the specified path"
        if not file_url.startswith("file://"):
            file_url = "file://" + str(file_url)
        self.load_url(file_url, decode, force)

    def load_url(self, url, decode=None, force=False):
        """Load a website (https:// or http://) or a file (file://) from the specified URL.
        We use threading here to prevent the GUI from freezing while fetching the website.
        Technically Tkinter isn't threadsafe and will crash when doing this, but under certain circumstances we can get away with it.
        As long as we do not use the .join() method and no errors are raised in the mainthread, we should be okay.
        """
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
            parsed2 = urlparse(self.current_url)

            if parsed.scheme == "file":
                netloc = parsed.path
            else:
                netloc = parsed.netloc
            if parsed2.scheme == "file":
                netloc2 = parsed2.path
            else:
                netloc2 = parsed2.netloc
            if method == "GET":
                url = str(url) + str(data)

            # if url is different than the current one, load the new site.
            if force or (method == "POST") or not ((netloc == netloc2) and (parsed.path == parsed2.path) and (parsed.query == parsed2.query)):
                self.message_func("Connecting to {0}.".format(netloc))
                if (parsed.scheme == "file") or (not self.html.caches_enabled):
                    data, newurl, filetype = download(
                        url, data, method, decode)
                else:
                    data, newurl, filetype = cachedownload(
                        url, data, method, decode)
                if threadname().isrunning():
                    self.url_change_func(newurl)
                    if "image" in filetype:
                        try:
                            self.load_html(
                                """<img src="heximagedata:{}">""".format(data.hex()), newurl)
                        except AttributeError:
                            self.load_html(
                                """<img src="{}">""".format(newurl), newurl)
                    else:
                        self.load_html(data, newurl)
                    self.current_url = newurl
            else:
                # if no requests need to be made, we can signal that the page is done loading
                self.html.done_loading_func()
            # handle URI fragments
            frag = parsed.fragment
            if frag:
                self.html.tk.call(self.html._w, "_force")
                try:
                    node = self.html.search("[name=%s]" % frag)
                    node2 = self.html.search("#"+str(frag))
                    if node:
                        self.html.yview(node)
                    elif node2:
                        self.html.yview(node2)
                except Exception:
                    pass
        except Exception as error:
            self.message_func(
                "An error has been encountered while loading {}: {}.".format(url, error))
            self.load_html(self.broken_page_msg)
            self.current_url = ""

        self.thread_in_progress = None

    def stop(self):
        "Stop loading a page"
        if self.thread_in_progress:
            self.thread_in_progress.stop()
        self.html.stop()
        self.url_change_func(self.current_url)
        self.done_loading()

    def bind(self, *args, **kwargs):
        "Redirect bindings"
        self.html.bind(*args, **kwargs)

    def done_loading(self):
        self.in_progress = False
        self.done_loading_func()

    def set_zoom(self, multiplier):
        "Set the zoom multiplier"
        self.html.zoom(float(multiplier))

    def get_zoom(self):
        "Get the zoom multiplier"
        return self.html.zoom(None)

    def set_fontscale(self, multiplier):
        "Set the fontsize multiplier"
        self.html.fontscale(float(multiplier))

    def get_fontscale(self):
        "Get the fontsize multiplier"
        return self.html.fontscale(None)

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

    def enable_stylesheets(self, isenabled=True):
        "Enable or disable stylesheet loading"
        self.html.stylesheets_enabled = isenabled

    def enable_images(self, isenabled=True):
        "Enable or disable image loading"
        self.html.images_enabled = isenabled

    def enable_forms(self, isenabled=True):
        "Enable or disable form-filling"
        self.html.forms_enabled = isenabled

    def enable_caches(self, isenabled=True):
        "Enable or disable file caches"
        self.html.caches_enabled = isenabled

    def change_cursor(self, cursor):
        "Handle cursor changes"
        if self.cursor != cursor:
            self.cursor = cursor
            self.config(cursor=cursor)

    def get_currently_hovered_node_tag(self):
        "Get the tag of the HTML element the mouse pointer is currently over"
        try:
            tag = self.html.get_node_tag(self.html.currently_hovered_node)
            if tag == "":
                tag = self.html.get_node_tag(
                    self.html.get_node_parent(self.html.currently_hovered_node))
        except tk.TclError:
            tag = ""
        return tag

    def get_currently_hovered_node_text(self):
        "Get the text content of the HTML element the mouse pointer is currently over"
        try:
            text = self.html.get_node_text(self.html.currently_hovered_node)
            if text == "":
                text = self.html.get_node_text(
                    self.html.get_node_parent(self.html.currently_hovered_node))
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
                self.html.currently_hovered_node, attribute)
            if attr == "":
                attr = self.html.get_node_attribute(self.html.get_node_parent(
                    self.html.currently_hovered_node), attribute)
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
        if sys.platform == "darwin":
            self.html.yview_scroll(int(-1*(event.delta)), "units")
        else:
            self.html.yview_scroll(int(-1*(event.delta)/40), "units")

    def scroll_x11(self, event):
        if event.num == 4:
            self.html.yview_scroll(-4, "units")
        else:
            self.html.yview_scroll(4, "units")

    def load_html(self, html_source, base_url=None):
        "Reset parser and send html code to it"
        self.current_url = ""
        self.html.reset()
        self.html.base_url = base_url
        self.add_html(html_source)

    def add_html(self, html_source):
        "Parse HTML and add it to the end of the current document."
        self.html.parse(html_source)

    def add_css(self, css_source):
        "Parse CSS code"
        self.html.parse_css(css_source)


class HtmlLabel(ttk.Frame):
    def __init__(self, master, text="", messages_enabled=False, **kw):
        ttk.Frame.__init__(self, master, **kw)

        self.master = master
        self.cursor = ""

        if messages_enabled:
            self.message_func = message_func = notifier
        else:
            self.message_func = message_func = lambda message: None

        self.html = html = TkinterWeb(self, message_func)
        html.pack(expand=True, fill="both")

        html.cursor_change_func = self.change_cursor

        html.bindtags([html])
        html.shrink(True)

        self.load_html(text)

    def set_zoom(self, multiplier):
        "Set the zoom multiplier"
        self.html.zoom(float(multiplier))

    def get_zoom(self):
        "Get the zoom multiplier"
        return self.html.zoom(None)

    def set_fontscale(self, multiplier):
        "Set the fontsize multiplier"
        self.html.fontscale(float(multiplier))

    def get_fontscale(self):
        "Get the fontsize multiplier"
        return self.html.fontscale(None)

    def on_link_click(self, function):
        "Allows for handling link clicks"
        self.html.link_click_func = function

    def on_form_submit(self, function):
        "Allows for handling form submissions"
        self.html.form_submit_func = function

    def change_cursor(self, cursor):
        "Handle cursor changes"
        if self.cursor != cursor:
            self.config(cursor=cursor)
            self.cursor = cursor

    def replace_widget(self, oldwidget, newwidget):
        "Replace a stored widget"
        self.html.replace_widget(oldwidget, newwidget)

    def replace_element(self, cssselector, newwidget):
        "Replace an HTML element with a widget"
        self.html.replace_html(cssselector, newwidget)

    def remove_widget(self, widget):
        "Remove a stored widget"
        self.html.remove_widget(widget)

    def load_html(self, html_source, base_url=None):
        "Reset parser and send html code to it"
        if not base_url:
            path = os.getcwd()
            if not path.startswith("/"):
                path = "/{0}".format(path)
            base_url = "file://{0}/".format(path)

        self.html.reset()
        self.html.base_url = base_url
        self.add_html(html_source)

    def add_html(self, html_source):
        "Parse HTML and add it to the end of the current document."
        self.html.parse(html_source)

    def add_css(self, css_source):
        "Parse CSS code"
        self.html.parse_css(css_source)
