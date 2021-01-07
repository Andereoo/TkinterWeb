import sys
import requests
import os

from utils import _AutoScrollbar, notifier

from tkhtml_bindings import TkinterWeb

try:
    from urllib.request import Request, urlopen
except ImportError: # Python 2
    from urllib2 import urlopen, Request

try:
    from urllib.parse import urlparse, urljoin
except ImportError: # Python 2
    from urlparse import urlparse, urljoin

try:
    import tkinter as tk
    from tkinter import ttk
except ImportError: # Python 2
    import Tkinter as tk
    import ttk

class HtmlFrame(ttk.Frame):
    def __init__(self, master, messages_enabled=True, fontscale=1.0, zoom=1.0, vertical_scrollbar="auto", horizontal_scrollbar=False, **kw):
        ttk.Frame.__init__(self, master, **kw)

        self.master = master
        self.current_url = ""
        self.broken_file_msg = """<html>
                                    <head>
                                        <title>Error 404</title>
                                    </head>
                                        <body style="text-align:center;">
                                            <h2>Oops.</h2>
                                            <p></p>
                                            <h3>The file you've requested could not be read.<h3>
                                    </body>
                                </html>"""
        self.broken_webpage_msg = """<html>
                                    <head>
                                        <title>Error 404</title>
                                    </head>
                                        <body style="text-align:center;">
                                            <h2>Oops.</h2>
                                            <p></p>
                                            <h3>The webpage you've requested could not be found.<h3>
                                    </body>
                                </html>"""

        if messages_enabled:
            message_func = notifier
        else:
            message_func = lambda a, b: None
        html = self.html = TkinterWeb(self, message_func, fontscale=float(fontscale), zoom=float(zoom))
        html.grid(row=0, column=0, sticky=tk.NSEW)

        html._cursor_change_func = self.change_cursor
            
        if vertical_scrollbar:
            if vertical_scrollbar == "auto":
                vsb = _AutoScrollbar(self, orient=tk.VERTICAL, command=html.yview)
            else:
                vsb = ttk.Scrollbar(self, orient=tk.VERTICAL, command=html.yview)
            html.configure(yscrollcommand=vsb.set)
            vsb.grid(row=0, column=1, sticky=tk.NSEW)
            html.bind_all("<MouseWheel>", self.scroll)
        if horizontal_scrollbar:
            if horizontal_scrollbar == "auto":
                hsb = _AutoScrollbar(self, orient=tk.HORIZONTAL, command=html.xview)
            else:
                hsb = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=html.xview)
            html.configure(xscrollcommand=hsb.set)
            hsb.grid(row=1, column=0, sticky=tk.NSEW)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    def load_website(self, website_url, base_url=None):
        "Load a website from the specified URL"
        try:
            parsed = urlparse(website_url)
            parsed2 = urlparse(self.current_url)

            #if url is different than the current one, load the new site.
            if not ((parsed.netloc == parsed2.netloc) and (parsed.path == parsed2.path)):
                response = requests.get(website_url)
                urldata = response.text
                base_url = (base_url if base_url else website_url)
                self.load_html(urldata, base_url)
                self.current_url = website_url

            #handle URI fragments
            frag = parsed.fragment
            if frag != "":
                self.html.tk.call(self.html._w, "_force")
                try:
                    node = self.html.search("[name=%s]" % frag)
                    if node != "":
                        self.html.yview(node)
                    else:
                        try:
                            node = self.html.search("#"+str(frag))
                            if node != "":
                                self.html.yview(node)
                            else:
                                pass
                        except:
                            pass
                except:
                    try:
                        node = self.html.search("#"+str(frag))
                        if node != "":
                            self.html.yview(node)
                        else:
                            pass
                    except:
                        pass
                
        except Exception:
            self.load_html(self.broken_webpage_msg)

    def load_file(self, file_url, base_url=None):
        "Load a locally stored file from the specified path"
        self.current_url = file_url
        if base_url is not None:
            if not base_url.startswith("file://"):
                base_url = "file://"+str(base_url)
        else:
            if not file_url.startswith("file://"):
                base_url = "file://"+os.path.join(os.path.dirname(file_url), "")
            else:
                base_url = os.path.join(os.path.dirname(file_url), "")
        try:
            with open(file_url, "r") as file:
                filedata = file.read()
            self.load_html(filedata, base_url)
        except Exception:
            self.load_html(self.broken_file_msg)

    def on_link_click(self, function):
        "Allows for handling link clicks"
        self.html._link_click_func = function

    def on_title_change(self, function):
        "Allows for handling title changes"
        self.html._title_change_func = function

    def set_recursive_hover_depth(self, depth):
        "Change the max recursion depth to add a css 'hover' flag onto HTML elements"
        self.html._recursive_hovering_count = int(depth)

    def set_broken_webpage_message(self, html):
        "Set the HTML that is shown whan a requested webpage could not be reached"
        self.broken_webpage_msg = html

    def set_broken_file_message(self, html):
        "Set the HTML that is shown whan a requested file could not be reached"
        self.broken_file_msg = html

    def add_visited_links(self, links):
        "Add links to the list of visited links"
        self.html.visited_links.extend(links)

    def clear_visited_links(self):
        "Clear the list of visited links"
        self.html.visited_links = []

    def set_message_func(self, function):
        "Change the message output function"
        self.html._message_func = function

    def enable_stylesheets(self, isenabled=True):
        "Enable or disable stylesheet loading"
        self.html.stylesheets_enabled = isenabled

    def enable_images(self, isenabled=True):
        "Enable or disable image loading"
        self.html.images_enabled = isenabled

    def change_cursor(self, cursor):
        "Handle cursor changes"
        self.config(cursor=cursor)

    def get_currently_hovered_node_tag(self):
        "Get the tag of the HTML element the mouse pointer is currently over"
        tag = self.html._get_node_tag(self.html.currently_hovered_node)
        if tag == "":
            tag = self.html._get_node_tag(self.html._get_node_parent(self.html.currently_hovered_node))
        return tag

    def get_currently_hovered_node_text(self):
        "Get the text content of the HTML element the mouse pointer is currently over"
        text = self.html._get_node_text(self.html.currently_hovered_node)
        if text == "":
            text = self.html._get_node_text(self.html._get_node_parent(self.html.currently_hovered_node))
        return text

    def get_currently_hovered_node_attribute(self, attribute):
        """
        Get the specified attribute of the HTML element the mouse pointer is currently over
        For example, if the mouse is hovering over the element
        "<a href='example.com'></a>", calling "get_currently_hovered_node_attribute('href')" will return "example.com."
        """
        try:
            text = self.html._get_node_attr(self.html.currently_hovered_node, attribute)
        except Exception:
            try:
                text = self.html._get_node_attr(self.html._get_node_parent(self.html.currently_hovered_node), attribute)
            except Exception:
                text = ""
        return text

    def get_currently_selected_text(self):
        "Get the text that is currently highlighted/selected."
        return self.html._get_selected_text()

    def scroll(self, event):
        "Handle mouse/touchpad scrolling"
        if sys.platform == "darwin":
            self.html.yview_scroll(int(-1*(event.delta)), "units")
        else:
            self.html.yview_scroll(int(-1*(event.delta)/40), "units")

    def load_html(self, html_source, base_url=None):
        "Reset parser and send html code to it"
        self.current_url = ""
        self.html.reset()
        self.html._base_url = base_url
        self.html._images = set()
        # This a modification that deals with the <title> element in 64-bit Tkhtml becuse that can cause some trouble
        if "<title>" in html_source:
            if sys.platform == "win64":
                html_source.replace("<title>", "<div>").replace("</title>", "</div>") #the div tag pretty much does nothing so we replace the title tag with the div tag
                self.add_html(html_source)
            else:
                self.add_html(html_source)
        else:
            self.add_html(html_source)

    def add_html(self, html_source):
        "Parse HTML and add it to the end of the current document."
        self.html.parse(html_source)

    def add_css(self, css_source):
        "Parse CSS code"
        self.html.parce_css(css_source)
        
