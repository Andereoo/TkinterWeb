"""
Widgets that expand on the functionality of the basic bindings
by adding scrolling, file loading, and many other convenience functions

Copyright (c) 2025 Andereoo
"""

import platform
from urllib.parse import urldefrag, urlparse

from bindings import TkinterWeb
from utilities import (WORKING_DIR, AutoScrollbar, StoppableThread, cachedownload, download,
                       notifier, threadname, extract_nested)
from imageutils import newimage, createRGBimage
from dom import TkwDocumentObjectModel

import tkinter as tk
from tkinter import ttk

import pathlib


class HtmlFrame(ttk.Frame):
    def __init__(self, master, messages_enabled=True, vertical_scrollbar="auto", horizontal_scrollbar=False, overflow_scroll_frame=None, **kw):
        ttk.Frame.__init__(self, master, **kw)

        if messages_enabled:
            self.message_func = message_func = notifier
        else:
            self.message_func = message_func = lambda message: None

        # setup scrollbars and HTML widget
        self.html = html = TkinterWeb(self, message_func, HtmlFrame, self.manage_vsb, overflow_scroll_frame)
        html.grid(row=0, column=0, sticky=tk.NSEW)

        self.document = TkwDocumentObjectModel(html)

        if horizontal_scrollbar:
            if horizontal_scrollbar == "auto":
                self.hsb = hsb = AutoScrollbar(
                    self, orient=tk.HORIZONTAL, command=html.xview)
            else:
                self.hsb = hsb = ttk.Scrollbar(
                    self, orient=tk.HORIZONTAL, command=html.xview)

            hsb.bind("<Enter>", html.on_leave)
            html.configure(xscrollcommand=hsb.set)
            hsb.grid(row=1, column=0, sticky="nsew")

        self.vsb = vsb = AutoScrollbar(
            self, orient=tk.VERTICAL, command=self.html.yview)
        self.vsb_type = None

        vsb.bind("<Enter>", self.html.on_leave)
        self.html.configure(yscrollcommand=vsb.set)
        vsb.grid(row=0, column=1, sticky="nsew")

        self.manage_vsb(vertical_scrollbar)

        # for some reason, binding to Html only works on Linux and binding to html.document only works on Windows
        # html.document only applies to the document it is bound to (which makes things easy)
        # Html fires on all documents (i.e. <iframe> elements), so it has to be handled slightly differently
        if not overflow_scroll_frame:
            self.bind_class("Html", "<Button-4>", self.html.scroll_x11)
            self.bind_class("Html", "<Button-5>", self.html.scroll_x11)
        self.bind_class(f"{self.html}.document", "<MouseWheel>", self.html.scroll)

        self.bind_class(self.html.scrollable_node_tag, "<Button-4>", lambda event, widget=html: self.html.scroll_x11(event, widget))
        self.bind_class(self.html.scrollable_node_tag, "<Button-5>", lambda event, widget=html: self.html.scroll_x11(event, widget))
        self.bind_class(self.html.scrollable_node_tag, "<MouseWheel>", self.html.scroll)

        self.bind("<Leave>", html.on_leave)
        self.bind("<Enter>", html.on_mouse_motion)

        # state and settings variables
        self.master = master
        self.current_url = ""
        self.cursor = ""
        self.accumulated_styles = []
        self.waiting_for_reset = False
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
            "Welcome to TkinterWeb v3.25! \nhttps://github.com/Andereoo/TkinterWeb")

        self.message_func(
            "Debugging messages are enabled. \nUse the parameter `messages_enabled = False` when calling HtmlFrame() or HtmlLabel() to disable these messages.")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # redirected commands
        self.select_all = self.html.select_all
        self.bind = self.html.bind
        self.set_zoom = self.html.set_zoom
        self.get_zoom = self.html.get_zoom
        self.set_fontscale = self.html.set_fontscale
        self.get_fontscale = self.html.get_fontscale
        self.set_parsemode = self.html.set_parsemode
        self.get_parsemode = self.html.get_parsemode
        self.resolve_url = self.html.resolve_url

        self.replace_widget = self.html.replace_widget
        self.replace_element = self.html.replace_element
        self.remove_widget = self.html.remove_widget

        self.yview = self.html.yview
        self.yview_moveto = self.html.yview_moveto
        self.yview_scroll = self.html.yview_scroll

        self.html.tk.createcommand("resolve_uri", self.resolve_uri)
        self.html.tk.createcommand("node_to_html", self.node_to_html)

    def manage_vsb(self, allow):
        "Show or hide the scrollbars"
        if allow == "auto":
            allow = 2
        if self.vsb_type != allow:
            self.vsb.set_type(allow)
            self.vsb_type = allow

    def yview_toelement(self, selector, index=0):
        "Find an element that matches a given CSS selectors and scroll to it"
        nodes = self.html.search(selector)
        if nodes:
            try:
                self.html.yview(nodes[index])
            except IndexError:
                pass

    def load_website(self, website_url, decode=None, force=False, insecure=None):
        "Load a website from the specified URL"
        if (not website_url.startswith("https://")) and (not website_url.startswith("http://")) and (not website_url.startswith("about:")):
            website_url = "http://" + str(website_url)
        self.load_url(website_url, decode, force, insecure)

    def load_file(self, file_url, decode=None, force=False, insecure=None):
        "Load a locally stored file from the specified path"
        if not file_url.startswith("file://"):
            if platform.system() == "Windows" and not file_url.startswith("/"):
                file_url = "file:///" + str(file_url)
            else:
                file_url = "file://" + str(file_url)
        self.load_url(file_url, decode, force, insecure)

    def load_url(self, url, decode=None, force=False, insecure=None):
        """Load a website (https:// or http://) or a file (file://) from the specified URL.
        We use threading here to prevent the GUI from freezing while fetching the website.
        Technically Tkinter isn't threadsafe, 
        but as long as we do not use the .join() method and no errors are raised in the mainthread, we can get away with it.
        """
        self.waiting_for_reset = True

        # workaround for Bug #40, where urllib.urljoin constructs improperly formatted urls on Linux when url starts with file:///
        if not url.startswith("file://///"):
            url = url.replace("file:////", "file:///")

        if self.thread_in_progress:
            self.thread_in_progress.stop()
        if self.html.max_thread_count >= 1:
            thread = StoppableThread(target=self.continue_loading, args=(
                url,), kwargs={"decode": decode, "force": force, "insecure": insecure})
            self.thread_in_progress = thread
            thread.start()
        else:
            self.continue_loading(url, decode=decode, force=force, insecure=insecure)

    def load_form_data(self, url, data, method="GET", decode=None, insecure=None):
        "Load a webpage using form data"
        if self.thread_in_progress:
            self.thread_in_progress.stop()
        if self.html.max_thread_count >= 1:
            thread = StoppableThread(
                target=self.continue_loading, args=(url, data, method, decode), kwargs={"insecure": insecure})
            self.thread_in_progress = thread
            thread.start()
        else:
            self.continue_loading(url, data, method, decode)

    def continue_loading(self, url, data="", method="GET", decode=None, force=False, insecure=None):
        "Finish loading urls and handle URI fragments"
        if insecure == None:
            insecure = self.html.insecure_https
        else:
            self.html.insecure_https = insecure

        self.html.downloading_resource_func()
        self.url_change_func(url)
        
        try:
            method = method.upper()
            parsed = urlparse(url)

            if method == "GET":
                url = str(url) + str(data)

            # if url is different than the current one, load the new site
            if force or (method == "POST") or (self.skim(urldefrag(url)[0]) != self.skim(urldefrag(self.current_url)[0])):
                self.message_func("Connecting to {0}.".format(parsed.netloc))
                if insecure:
                    self.message_func("WARNGING: Using insecure HTTPS session")
                if (parsed.scheme == "file") or (not self.html.caches_enabled):
                    data, newurl, filetype = download(
                        url, data, method, decode, insecure)
                else:
                    data, newurl, filetype = cachedownload(
                        url, data, method, decode, insecure)
                if threadname().isrunning():
                    self.url_change_func(newurl)
                    if "image" in filetype:
                        image, error = newimage(data, f"_htmlframe_img_{id(self)}_{self.image_count}_", filetype, self.html.image_inversion_enabled)
                        if error:
                            self.html.image_setup_func(url, False)
                        else:
                            self.html.image_setup_func(url, True)
                        self.load_html(f"<img style='max-width:100%' src='replace:{image}'></img")
                        self.image_count += 1
                        self.image = image
                    else:
                        self.load_html(data, newurl)
                    self.current_url = newurl
            else:
                # if no requests need to be made, we can signal that the page is done loading
                self.html.done_loading_func()
                self.finish_css()

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
            self.message_func(
                f"An error has been encountered while loading {url}: {error}.")
            self.load_html(self.broken_page_msg)
            self.current_url = ""
            
            if "CERTIFICATE_VERIFY_FAILED" in str(error):
                python_version = ".".join(platform.python_version_tuple()[:2])
                self.message_func(
                    f"Check that you are using the right url scheme. Some websites only support http.\n\
This might also happen if your Python distribution does not come installed with website certificates.\n\
This is a known Python bug on older MacOS systems. \
Running something along the lines of \"/Applications/Python {python_version}/Install Certificates.command\" (with the qoutes) to install the missing certificates may do the trick.\n\
Otherwise, use 'insecure=True' when loading a page to ignore website certificates.")

        self.thread_in_progress = None

    def skim(self, url):
        return url.replace("/", "")

    def resolve_uri(self):
        base = urlparse(self.html.base_url)
        uri = f"{base.scheme}://{base.netloc}{base.path}"
        print(uri)
        return uri

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

    def on_image_setup(self, function):
        "Callback for image loading"
        self.html.image_setup_func = function

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
        """Enable or disable extra crash prevention measures
        Disabling this will remove all emojis, the noto color emoji font, and invalid rgb functions"""
        self.html.prevent_crashes = enabled

    def enable_dark_theme(self, enabled=True, invert_images=True):
        """Enable or disable dark theme
        This will cause page colours to be 'inverted' if enabled is set to True
        This will also cause images to be inverted if 'invert_images' is also set to True"""
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

    def find_text(self, searchtext, select=1, ignore_case=True, highlight_all=True, detailed=False):
        "Search for and highlight specific text"
        nmatches, selected, matches = self.html.find_text(searchtext, select, ignore_case, highlight_all)
        if detailed:
            return nmatches, selected, matches
        else:
            return nmatches

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
        """Get the specified attribute of the HTML element the mouse pointer is currently over
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

    def load_html(self, html_source, base_url=None):
        "Reset parser and send html code to it"
        self.html.reset()
        if not base_url:
            path = WORKING_DIR
            if not path.startswith("/"):
                path = f"/{path}"
            base_url = f"file://{path}/"
        self.html.base_url = self.current_url = base_url
        self.html.parse(html_source)

        self.finish_css()

    def finish_css(self):        
        if self.waiting_for_reset:
            self.waiting_for_reset = False
            for style in self.accumulated_styles:
                self.add_css(style)
            self.accumulated_styles = []

    def add_html(self, html_source):
        "Parse HTML and add it to the end of the current document."
        if not self.current_url:
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

    def screenshot(self, name="", full=False):
        image = self.html.image("-full" if full else None)
        data = image[next(iter(image))]
        height = len(data)
        width = len(data[0].split())
        self.message_func(f"Screenshot taken: {name} {width}x{height}.")
        return createRGBimage(data, name, width, height)

    def node_to_html(self, node, deep=True):  # internal
        return self.html.tk.eval(r"""
            proc TclNode_to_html {node} {
                set tag [$node tag]
                if {$tag eq ""} {
                    append ret [$node text -pre]
                } else {
                    append ret <$tag
                    foreach {zKey zVal} [$node attribute] {
                        set zEscaped [string map [list "\x22" "\x5C\x22"] $zVal]
                        append ret " $zKey=\"$zEscaped\""
                    }
                    append ret >
                    if {%d} {
                        append ret [node_to_childrenHtml $node]
                    }
                    append ret </$tag>
                }
            }
            proc node_to_childrenHtml {node} {
                set ret ""
                foreach child [$node children] {
                    append ret [TclNode_to_html $child]
                }
                return $ret
            }
            return [TclNode_to_html %s]
            """ % (int(deep), extract_nested(node))
        )

    def create_snapshot(self, filename=None):
        htmltext = self.html.tk.eval(r"""
            set html %s
            set zTitle ""
            set zStyle "\n"
            set zBody ""

            set zBase [resolve_uri]

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
            # It has to be writen like this because it outputs the indention
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
        if filename:
            if not pathlib.Path(filename).suffix:
                filename = f"{filename}.{self.html.get_parsemode()}"
            file = open(filename, "w")
            file.write(htmltext)
            file.close()
            
        return htmltext

    def print_page(self, cnf={}, **kw):
        cnf |= kw
        if "pagesize" in cnf:
            pagesizes = {
                "A3": "842x1191", "A4": "595x842", "A5": "420x595",
                "Legal": "612x792", "Letter": "612x1008"
            }
            cnf["pagesize"] = pagesizes[cnf["pagesize"].upper()]
            self.message_func(cnf["pagesize"])

        self.html.update()  # Update the root window to ensure HTML is rendered
        self.message_func("Printing...")
        file = self.html.postscript(cnf)
        self.message_func("Printed.")
        if "file" in cnf and not file: file = cnf["file"]
        return file


class HtmlLabel(HtmlFrame):
    def __init__(self, master, text="", messages_enabled=False, **kw):
        HtmlFrame.__init__(self, master, messages_enabled=messages_enabled, vertical_scrollbar=False, horizontal_scrollbar=False, **kw)

        tags = list(self.html.bindtags())
        tags.remove("Html")
        self.html.bindtags(tags)

        self.html.shrink(True)

        self.load_html(text)
