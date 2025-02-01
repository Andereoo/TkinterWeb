"""
The core Python bindings to Tkhtml3

Copyright (c) 2025 Andereoo
"""

import platform
import re
import sys

from urllib.parse import urlencode, urljoin, urlparse, urlunparse

import tkinter as tk

from imageutils import *
from utilities import *


class Combobox(tk.Widget):
    "Bindings for Bryan Oakley's combobox widget"

    def __init__(self, master):
        load_combobox(master)
        try:
            tk.Widget.__init__(self, master, "::combobox::combobox")
        except tk.TclError:
            load_combobox(master, force=True)
            tk.Widget.__init__(self, master, "::combobox::combobox")
        self.configure(
            highlightthickness=0,
            borderwidth=0,
            editable=False,
            takefocus=0,
            selectbackground="#6eb9ff",
            relief="flat",
            elementborderwidth=0,
            buttonbackground="white",
        )
        self.data = [""]
        self.values = [""]
        self.default = 0

    def insert(self, data, values, selected):
        for elem in reversed(data):
            self.tk.call(self._w, "list", "insert", 0, elem)
        self.data = data
        self.values = values
        if selected:
            self.default = self.values.index(selected)
        self.reset()

    def reset(self):
        self.tk.call(self._w, "select", self.default)

    def get(self):
        val = self.tk.call(self._w, "curselection")[0]
        return self.values[val]


class TkinterWeb(tk.Widget):
    "Bindings for the Tkhtml3 HTML widget"

    def __init__(self, master, message_func, embed_obj, manage_vsb_func, manage_hsb_func, overflow_scroll_frame=None, cfg={}, **kwargs):
        self.message_func = message_func
        self.manage_vsb_func = manage_vsb_func
        self.manage_hsb_func = manage_hsb_func
        self.overflow_scroll_frame = overflow_scroll_frame

        folder = get_tkhtml_folder()

        # provide OS information for troubleshooting
        self.message_func(
            "Starting TkinterWeb for {} {} with Python {}".format(
                "64-bit" if sys.maxsize > 2**32 else "32-bit",
                platform.system(),
                str(sys.version_info[0:3])
                .replace(", ", ".")
                .replace(")", "")
                .replace("(", ""),
            )
        )

        # pre-load custom stylesheet, set default parse mode, and register image loading infrastructure
        if "imagecmd" not in kwargs:
            kwargs["imagecmd"] = master.register(self.on_image)
        if "drawcleanupcrashcmd" not in kwargs:
            kwargs["drawcleanupcrashcmd"] = master.register(self.on_drawcleanupcrash)
        if "defaultstyle" not in kwargs:
            kwargs["defaultstyle"] = DEFAULTSTYLE
        if "parsemode" not in kwargs:
            kwargs["parsemode"] = DEFAULTPARSEMODE
        # if "enablelayout" not in kwargs:
        #    kwargs["enablelayout"] = True
        # if "logcmd" not in kwargs:
        #    kwargs["logcmd"] = tkhtml_notifier

        # load the Tkhtml3 widget
        try:
            load_tkhtml(master, folder)
            tk.Widget.__init__(self, master, "html", cfg, kwargs)
        except tk.TclError:
            load_tkhtml(master, folder, force=True)
            tk.Widget.__init__(self, master, "html", cfg, kwargs)

        self.message_func(f"Tkhtml3 successfully loaded from {folder}")

        # widget settings
        self.stylesheets_enabled = True
        self.images_enabled = True
        self.forms_enabled = True
        self.caches_enabled = True
        self.objects_enabled = True
        self.ignore_invalid_images = True
        self.prevent_crashes = True
        self.dark_theme_enabled = False
        self.image_inversion_enabled = False
        self.base_url = ""
        self.recursive_hovering_count = 10
        self.max_thread_count = 20
        self.image_alternate_text_enabled = True
        self.image_alternate_text_font = get_alt_font()
        self.image_alternate_text_size = 14
        self.image_alternate_text_threshold = 10
        self.find_match_highlight_color = "#ef0fff"
        self.find_match_text_color = "#fff"
        self.find_current_highlight_color = "#38d878"
        self.find_current_text_color = "#fff"
        self.selected_text_highlight_color = "#3584e4"
        self.selected_text_color = "#fff"
        self.visited_links = []
        self.title_change_func = self.placeholder
        self.icon_change_func = self.placeholder
        self.cursor_change_func = self.placeholder
        self.link_click_func = self.placeholder
        self.form_submit_func = self.placeholder
        self.done_loading_func = self.placeholder
        self.downloading_resource_func = self.placeholder
        self.image_setup_func = self.placeholder
        self.radiobutton_token = "TKWtsvLKac1"
        self.insecure_https = False
        self.embedded_widget_attr_name = "widgetid"

        # widget status variables
        self.embed_obj = embed_obj
        self.style_count = 0
        self.active_threads = []
        self.stored_widgets = {}
        self.loaded_images = set()
        self.image_directory = {}
        self.image_name_prefix = "_tkinterweb_img_{}_".format(id(self))
        self.is_selecting = False
        self.downloads_have_occured = False
        self.unstoppable = True
        self.on_embedded_node = None
        self.selection_start_node = None
        self.selection_start_offset = None
        self.selection_end_node = None
        self.selection_end_offset = None
        self.prev_active_node = None
        self.current_node = None
        self.hovered_nodes = []
        self.current_cursor = ""
        self.vsb_type = 2

        # enable form resetting and submission
        self.form_get_commands = {}
        self.form_reset_commands = {}
        self.form_elements = {}
        self.loaded_forms = {}
        self.radio_buttons = {}
        self.waiting_forms = 0

        # other UI variables
        self.cursors = {
            "crosshair": "crosshair",
            "default": "",
            "pointer": "hand2",
            "move": "fleur",
            "text": "xterm",
            "wait": "watch",
            "progress": "box_spiral",
            "help": "question_arrow",
            "none": "none",
        }
        self.dark_theme_regex = re.compile(
            r"([^:;\s{]+)\s?:\s?([^;{!]+)(?=!|;|})"
        )  # ([^:;\s{]+)\s?:\s?([^;{]+)(?=;|})')
        self.dark_theme_limit = 160

        # set up bindtags
        self.node_tag = f"tkinterweb.{id(self)}.nodes"
        self.scrollable_node_tag = f"tkinterweb.{id(self)}.scrollablenodes"
        self.add_bindtags(self, False)

        # bindings
        self.bind("<<Copy>>", self.copy_selection, True)
        self.bind("<B1-Motion>", self.extend_selection, True)
        self.bind("<Button-1>", self.on_click, True)
        self.bind("<ButtonRelease-1>", self.on_click_release, True)
        self.bind_class(self.node_tag, "<Motion>", self.on_mouse_motion, True)

        # register node handlers
        self.register_handler("script", "script", self.on_script)
        self.register_handler("script", "style", self.on_style)
        self.register_handler("node", "link", self.on_link)
        self.register_handler("node", "title", self.on_title)
        self.register_handler("node", "a", self.on_a)
        self.register_handler("node", "base", self.on_base)
        self.register_handler("node", "input", self.on_input)
        self.register_handler("node", "textarea", self.on_textarea)
        self.register_handler("node", "select", self.on_select)
        self.register_handler("node", "form", self.on_form)
        self.register_handler("node", "object", self.on_object)
        self.register_handler("node", "iframe", self.on_iframe)
        self.register_handler("node", "table", self.on_table)
        self.register_handler("node", "img", self.on_image_node)
        self.register_handler("parse", "body", self.on_body) # for some reason using "node" and "body" doesn't return anyting
        self.register_handler("parse", "html", self.on_body) # for some reason using "node" and "html" doesn't return anyting

    def placeholder(self, *args, **kwargs):
        """Blank placeholder function. The only purpose of this is to
        improve readability by avoiding `lambda a, b, c: None` statements."""

    def parse(self, html):
        "Parse HTML code"
        self.downloads_have_occured = False
        self.unstoppable = True
        html = self.crash_prevention(html)
        self.tk.call(self._w, "parse", html)
        if self.embedded_widget_attr_name in html:
            self.setup_widgets()
        # we assume that if no downloads have been made by now the document has finished loading, so we send the done loading signal
        if not self.downloads_have_occured:
            self.after(0, self.done_loading_func)

    def update_default_style(self, stylesheet=None):
        "Update the default stylesheet based on color theme"
        if stylesheet:
            self.config(defaultstyle=stylesheet)
        elif self.dark_theme_enabled:
            self.config(defaultstyle=DEFAULTSTYLE + DARKSTYLE)
        else:
            self.config(defaultstyle=DEFAULTSTYLE)

    def rgb_to_hex(self, red, green, blue, *args):
        "Convert RGB colour code to HEX"
        return f"#{red:02x}{green:02x}{blue:02x}"

    def check_colors(self, rgb, match):
        "Check colour, invert if necessary, and convert"
        if ("background" in match and sum(rgb) < self.dark_theme_limit) or (
            match == "color" and sum(rgb) > self.dark_theme_limit
        ):
            return self.rgb_to_hex(*rgb)
        else:
            rgb[0] = max(1, min(255, 240 - rgb[0]))
            rgb[1] = max(1, min(255, 240 - rgb[1]))
            rgb[2] = max(1, min(255, 240 - rgb[2]))
            return self.rgb_to_hex(*rgb)

    def generate_altered_colour(self, match):
        "Invert document colours. Highly experimental."
        colors = match.group(2).replace("\n", "")
        colors = re.split(r"\s(?![^()]*\))", colors)
        changed = False

        for count, color in enumerate(colors):
            try:
                if color.startswith("#"):
                    changed = True
                    color = color.lstrip("#")
                    lv = len(color)
                    if lv == 3:
                        color = color + color
                        lv = len(color)
                    colors[count] = self.check_colors(
                        list(
                            int(color[i : i + lv // 3], 16)
                            for i in range(0, lv, lv // 3)
                        ),
                        match.group(1),
                    )
                elif color.startswith("rgb(") or color.startswith("rgba("):
                    changed = True
                    colors[count] = self.check_colors(
                        list(
                            map(
                                int,
                                color.lstrip("rgba(")
                                .lstrip("rgb(")
                                .rstrip(")")
                                .strip(" ")
                                .split(","),
                            )
                        ),
                        match.group(1),
                    )
                elif color in COLORMAPPINGS:
                    changed = True
                    colors[count] = COLORMAPPINGS[color]
            except ValueError as error:
                changed = False

        if changed:
            return match.group(1) + ": " + " ".join(colors)
        else:
            return match.group()

    def parse_css(self, sheetid=None, importcmd=None, data="", override=False):
        "Parse CSS code"
        data = self.crash_prevention(data)
        if self.dark_theme_enabled:
            data = re.sub(self.dark_theme_regex, self.generate_altered_colour, data)
        if sheetid and importcmd:
            self.tk.call(
                self._w, "style", "-id", sheetid, "-importcmd", importcmd, data
            )
        elif override:
            self.style_count += 1
            self.tk.call(
                self._w, "style", "-id", "author" + str(self.style_count).zfill(4), data
            )
        else:
            self.tk.call(self._w, "style", data)

    def reset(self):
        "Reset the widget"
        self.stop()
        self.loaded_images = set()
        self.image_directory = {}
        self.form_get_commands = {}
        self.form_elements = {}
        self.loaded_forms = {}
        self.waiting_forms = 0
        self.radio_buttons = {}
        self.hovered_nodes = []
        self.current_node = None
        self.on_embedded_node = None
        self.vsb_type = self.manage_vsb_func()
        self.manage_hsb_func()
        self.tk.call(self._w, "reset")

    def stop(self):
        "Stop loading resources"
        self.unstoppable = False
        for thread in self.active_threads:
            thread.stop()

    def node(self, *args):
        """Retrieve one or more document
        node handles from the current document"""
        nodes = self.tk.call(self._w, "node", *args)
        if nodes:
            return nodes
        else:
            return None, None

    def text(self, *args):
        "Enable interaction with the text of the HTML document"
        return self.tk.call(self._w, "text", *args)

    def tag(self, subcommand, tag_name, *args):
        """Return the name of the Html tag that generated this
        document node, or an empty string if the node is a text node"""
        return self.tk.call(self._w, "tag", subcommand, tag_name, *args)

    def search(self, selector, **kw):
        """Search the document for the specified CSS
        selector; return a Tkhtml3 node if found"""
        opt = ()
        for k, v in kw.items():
            opt = opt + (f"-{k}", v)
        return self.tk.call((self._w, "search", selector) + opt)

    def set_zoom(self, multiplier):
        "Set the page zoom"
        self.tk.call(self._w, "configure", "-zoom", float(multiplier))

    def get_zoom(self):
        "Return the page zoom"
        return self.tk.call(self._w, "cget", "-zoom")

    def set_parsemode(self, mode):
        "Set the page render mode"
        self.tk.call(self._w, "configure", "-parsemode", mode)

    def get_parsemode(self):
        "Return the page render mode"
        return self.tk.call(self._w, "cget", "-parsemode")

    def set_fontscale(self, multiplier):
        "Set the font zoom"
        self.tk.call(self._w, "configure", "-fontscale", multiplier)

    def get_fontscale(self, multiplier):
        "Return the font zoom"
        return self.tk.call(self._w, "cget", "-fontscale")

    def shrink(self, value):
        "Set shrink value for html widget"
        self.tk.call(self._w, "configure", "-shrink", value)

    def xview(self, *args):
        "Used to control horizontal scrolling"
        if args:
            return self.tk.call(self._w, "xview", *args)
        coords = map(float, self.tk.call(self._w, "xview").split())
        return tuple(coords)

    def xview_scroll(self, number, what):
        """Shifts the view in the window left or right, according to number and what.
        "number" is an integer, and "what" is either "units" or "pages"."""
        return self.xview("scroll", number, what)

    def xview_moveto(self, number):
        "Shifts the view horizontally to the specified position"
        return self.xview("moveto", number)

    def yview(self, *args):
        "Used to control the vertical position of the document"
        return self.tk.call(self._w, "yview", *args)

    def yview_scroll(self, number, what):
        """Shifts the view in the window up or down, according to number and what.
        "number" is an integer, and "what" is either "units" or "pages"."""
        return self.yview("scroll", number, what)

    def yview_moveto(self, number):
        "Shifts the view vertically to the specified position"
        return self.yview("moveto", number)

    def bbox(self, node=None):
        "Get the bounding box of the viewport or a specified node"
        return self.tk.call(self._w, "bbox", node)

    def parse_fragment(self, html):
        """Parse a document fragment.
        A document fragment isn't part of the active document but is comprised of nodes like the active document.
        Changes made to the fragment don't affect the document.
        Returns a root node."""
        self.downloads_have_occured = False
        self.unstoppable = True
        html = self.crash_prevention(html)
        fragment = self.tk.call(self._w, "fragment", html)
        # We assume that if no downloads have been made by now the document has finished loading, so we send the done loading signal
        if not self.downloads_have_occured:
            self.done_loading_func()
        return fragment

    def get_node_text(self, node_handle, *args):
        "Get the text content of the given node"
        return self.tk.call(node_handle, "text", *args)

    def set_node_text(self, node_handle, new):
        "Set the text content of the given node"
        return self.tk.call(node_handle, "text", "set", new)

    def get_node_tag(self, node_handle):
        "Get the HTML tag of the given node"
        return self.tk.call(node_handle, "tag")

    def get_node_parent(self, node_handle):
        "Get the parent of the given node"
        return self.tk.call(node_handle, "parent")

    def get_node_children(self, node_handle):
        "Get the children of the given node"
        return self.tk.call(node_handle, "children")

    def get_node_attribute(self, node_handle, attribute, default="", value=None):
        "Get the specified attribute of the given node"
        if value:  # backwards compatability
            return self.tk.call(node_handle, "attribute", attribute, value)
        else:
            return self.tk.call(
                node_handle, "attribute", "-default", default, attribute
            )

    def set_node_attribute(self, node_handle, attribute, value):
        "Set the specified attribute of the given node"
        return self.tk.call(node_handle, "attribute", attribute, value)

    def get_node_property(self, node_handle, node_property):
        "Get the specified attribute of the given node"
        return self.tk.call(node_handle, "property", node_property)

    def insert_node(self, node_handle, children_nodes):
        "Experimental, insert the specified nodes into the parent node"
        return self.tk.call(node_handle, "insert", children_nodes)

    def insert_node_before(self, node_handle, children_nodes, before):
        "Experimental, place the specified nodes is before another node"
        return self.tk.call(node_handle, "insert", "-before", before, children_nodes)

    def delete_node(self, node_handle):
        "Delete the given node"
        return self.tk.call(node_handle, "destroy")

    def set_node_flags(self, node, name):
        "Set dynamic flags on the given node"
        self.tk.call(node, "dynamic", "set", name)

    def remove_node_flags(self, node, name):
        "Set dynamic flags on the given node"
        self.tk.call(node, "dynamic", "clear", name)

    def get_current_node(self, event):
        "Get current node"
        return self.tk.eval(
            f"""set node [lindex [lindex [{self} node {event.x} {event.y}] end] end]"""
        )

    def get_current_node_parent(self, node):
        "Get the parent of the given node"
        return self.tk.eval(f"""set node [lindex [lindex [{node} parent] end] end]""")
    
    def register_handler(self, handler_type, node_tag, callback):
        self.tk.call(self._w, "handler", handler_type, node_tag, self.register(callback))

    def image(self, full=""):
        """Return the name of a new Tk image containing the rendered document.
        The returned image should be deleted when the script has finished with it.
        Note that this command is mainly intended for automated testing.
        Be wary of running this command on large documents.
        Does not work on Windows."""
        return self.tk.call(self._w, "image", full)

    def on_script(self, *args):
        "Currently just ignoring script"

    def on_style(self, attributes, tagcontents):
        "Handle <style> elements"
        if not self.stylesheets_enabled or not self.unstoppable:
            return
        self.downloads_have_occured = True
        self.style_count += 1
        ids = "user." + str(self.style_count).zfill(4)
        handler_proc = self.register(
            lambda new_url, parent_url=self.base_url: self.on_atimport(
                parent_url, new_url
            )
        )
        self.style_thread_check(sheetid=ids, handler=handler_proc, data=tagcontents)

    def on_link(self, node):
        "Handle <link> elements"
        try:
            rel = self.get_node_attribute(node, "rel").lower()
            media = self.get_node_attribute(node, "media", default="all").lower()
        except tk.TclError:
            return

        if (
            ("stylesheet" in rel)
            and ("all" in media or "screen" in media)
            and self.stylesheets_enabled
            and self.unstoppable
        ):
            self.downloads_have_occured = True
            href = self.get_node_attribute(node, "href")
            try:
                url = self.resolve_url(href)
                self.message_func(f"Fetching stylesheet from {shorten(url)}")
                self.style_count += 1
                ids = "user." + str(self.style_count).zfill(4)
                handler_proc = self.register(
                    lambda new_url, parent_url=url: self.on_atimport(
                        parent_url, new_url
                    )
                )
                self.style_thread_check(
                    sheetid=ids, handler=handler_proc, errorurl=href, url=url
                )
            except Exception as error:
                self.message_func(f"Error reading stylesheet {href}: {error}")
        elif "icon" in rel:
            href = self.get_node_attribute(node, "href")
            url = self.resolve_url(href)
            self.icon_change_func(url)

    def on_atimport(self, parent_url, new_url):
        "Load @import scripts"
        if not self.stylesheets_enabled or not self.unstoppable:
            return
        self.downloads_have_occured = True
        self.style_count += 1
        try:
            url = urljoin(parent_url, new_url)
            self.message_func(f"Loading stylesheet from {shorten(url)}")
            ids = "user." + str(self.style_count).zfill(4)
            handler_proc = self.register(
                lambda new_url, parent_url=url: self.on_atimport(parent_url, new_url)
            )

            self.style_thread_check(
                sheetid=ids, handler=handler_proc, errorurl=new_url, url=url
            )

        except Exception as error:
            self.message_func(f"Error loading stylesheet {new_url}: {error}")

    def on_title(self, node):
        "Handle <title> elements"
        for child in self.tk.call(node, "children"):
            self.title_change_func(self.tk.call(child, "text"))

    def on_base(self, node):
        "Handle <base> elements"
        try:
            href = self.get_node_attribute(node, "href")
            self.base_url = self.resolve_url(href)
        except Exception:
            self.message_func(
                "Error setting base url: a <base> element has been found without an href attribute"
            )

    def on_a(self, node):
        "Handle <a> elements"
        self.set_node_flags(node, "link")
        try:
            href = self.get_node_attribute(node, "href")
            url = self.resolve_url(href)
            if url in self.visited_links:
                self.set_node_flags(node, "visited")
        except tk.TclError:
            pass

    def on_iframe(self, node):
        "Handle <iframe> elements"
        if not self.objects_enabled or not self.unstoppable:
            return

        src = self.get_node_attribute(node, "src")
        srcdoc = self.get_node_attribute(node, "srcdoc")

        if srcdoc:
            self.create_iframe(node, None, srcdoc)
        elif src and (src != self.base_url):
            src = self.resolve_url(src)
            self.message_func(f"Creating iframe from {shorten(src)}")
            self.create_iframe(node, src)

    def on_object(self, node):
        "Handle <object> elements"
        if not self.objects_enabled or not self.unstoppable:
            return

        name = self.image_name_prefix + str(len(self.loaded_images))
        url = self.get_node_attribute(node, "data")

        if url != "":
            try:
                # stylecmd behaviour is iffy when using the 'widgetid' attribute because sometimes the styling is done by the time setup_widgets fires
                # instead we try to load widgets presented at <object> elements at runtime
                widgetid = self.nametowidget(url)
                if widgetid.winfo_ismapped():  # Don't display the same widget twice
                    return

                allowscrolling = self.get_node_attribute(node, "allowscrolling", "false") != "false"
                allowstyling = self.get_node_attribute(node, "allowstyling", "false") != "false"
                handleremoval = self.get_node_attribute(node, "handleremoval", "false") != "false"
                if allowstyling:
                    allowstyling = lambda node=node, widgetid=widgetid, widgettype="text": self.handle_node_style(node, widgetid, widgettype)
                else:
                    allowstyling = None
                if handleremoval:
                    handleremoval = lambda widgetid=widgetid: self.handle_node_removal(widgetid)
                else:
                    handleremoval = None

                self.stored_widgets[widgetid] = node
                self.handle_node_replacement(
                    node,
                    widgetid,
                    handleremoval,
                    allowstyling,
                    allowscrolling,
                    False,
                )
            except KeyError:
                url = self.resolve_url(url)
                if url == self.base_url:
                    # Don't load the object if it is the same as the current file
                    # Otherwise the page will load the same object indefinitely and freeze the GUI forever
                    return

                self.message_func(f"Creating object from {shorten(url)}")
                try:
                    if url.startswith("file://") or (not self.caches_enabled):
                        data, newurl, filetype, code = download(url, insecure=self.insecure_https)
                    elif url:
                        data, newurl, filetype, code = cachedownload(
                            url, insecure=self.insecure_https
                        )
                    else:
                        return

                    if data and filetype.startswith("image"):
                        image, error = newimage(
                            data, name, filetype, self.image_inversion_enabled
                        )
                        self.loaded_images.add(image)
                        self.tk.call(
                            node, "override", f"-tkhtml-replacement-image url(replace:{image})"
                        )
                    elif data and filetype == "text/html":
                        self.create_iframe(node, newurl, data)
                except Exception as error:
                    self.message_func(
                        f"Error loading object element: {error}"
                    )

    def on_drawcleanupcrash(self):
        if self.prevent_crashes:
            self.message_func(
                "HtmlDrawCleanup has encountered a critical error. This is being ignored because crash prevention is enabled."
            )
        else:
            self.destroy()

    def on_image_node(self, node):
        url = self.resolve_url(self.get_node_attribute(node, "src"))
        self.image_directory[url] = node

    def on_image(self, url):
        "Handle images"
        if not self.images_enabled or not self.unstoppable:
            return

        self.downloads_have_occured = True
        name = self.image_name_prefix + str(len(self.loaded_images))

        image = blankimage(name)
        self.loaded_images.add(image)

        if url.startswith("replace:"):
            thread = self.begin_download()
            name = url.replace("replace:", "")
            self.finish_download(thread)
        elif any(
            [
                url.startswith("linear-gradient("),
                url.startswith("url("),
                url.startswith("radial-gradient("),
                url.startswith("repeating-linear-gradient("),
                url.startswith("repeating-radial-gradient("),
            ]
        ):
            done = False
            self.message_func(f"Fetching image: {shorten(url)}")
            for image in url.split(","):
                if image.startswith("url("):
                    url = url.split("'), url('", 1)[0]
                    image = strip_css_url(image)
                    url = self.resolve_url(image)
                    self.image_thread_check(url, name)
                    done = True
            if not done:
                self.load_alt_image(url, name)
                self.message_func(
                    f"The image {shorten(url)} could not be shown because it is not supported yet"
                )
                self.image_setup_func(url, True)
        else:
            url = url.split("'), url('", 1)[0]
            url = self.resolve_url(url)
            self.image_thread_check(url, name)
        return name

    def on_form(self, node):
        "Handle <form> elements"
        if not self.forms_enabled:
            return

        inputs = []

        def scan(form):
            for i in self.get_node_children(form):
                tag = self.get_node_tag(i)
                if tag:
                    scan(i)
                if tag.lower() in {"input", "select", "textarea", "button"}:
                    inputs.append(i)
                    self.form_elements[i] = node

        scan(node)
        if len(inputs) == 0:
            self.waiting_forms += 1
        else:
            self.loaded_forms[node] = inputs
            self.message_func("Successfully setup form")

    def on_table(self, node):
        "Handle <form> elements in tables; workaround for Bug #48"
        if not self.forms_enabled:
            return

        if self.waiting_forms > 0:
            inputs = {}

            def scan(element, form):
                for i in self.get_node_children(element):
                    tag = self.get_node_tag(i).lower()
                    if tag == "form":
                        form = i
                    elif tag.lower() in {"input", "select", "textarea", "button"}:
                        if form in inputs:
                            inputs[form].append(i)
                        else:
                            inputs[form] = [i]
                        self.form_elements[i] = form
                    if tag:
                        scan(i, form)

            scan(node, node)
            for form in inputs:
                self.loaded_forms[form] = inputs[form]
                self.message_func("Successfully setup table form")
                self.waiting_forms -= 1

    def on_select(self, node):
        "Handle <select> elements"
        if not self.forms_enabled:
            return
        text = []
        values = []
        selected = None
        for child in self.get_node_children(node):
            if self.get_node_tag(child) == "option":
                try:
                    child2 = self.get_node_children(child)[0]
                    nodevalue = self.get_node_attribute(child, "value")
                    nodeselected = self.get_node_attribute(child, "selected")
                    values.append(nodevalue)
                    text.append(self.get_node_text(child2))
                    if nodeselected:
                        selected = nodevalue
                except IndexError:
                    continue
        if not selected and values:
            selected = values[0]
        widgetid = Combobox(self)
        widgetid.insert(text, values, selected)
        self.form_get_commands[node] = lambda: widgetid.get()
        self.form_reset_commands[node] = lambda: widgetid.reset()
        state = self.get_node_attribute(node, "disabled", False) != "0"
        if state:
            widgetid.configure(state="disabled")
        self.handle_node_replacement(
            node,
            widgetid,
            lambda widgetid=widgetid: self.handle_node_removal(widgetid),
            lambda node=node, widgetid=widgetid, widgettype="text": self.handle_node_style(
                node, widgetid, widgettype
            ),
        )

    def on_textarea(self, node):
        "Handle <textarea> elements"
        if not self.forms_enabled:
            return
        widgetid = ScrolledTextBox(
            self,
            borderwidth=0,
            selectborderwidth=0,
            highlightthickness=0,
        )

        self.form_get_commands[node] = lambda: widgetid.get("1.0", "end-1c")
        self.form_reset_commands[node] = lambda: widgetid.delete("0.0", "end")
        widgetid.insert("1.0", self.get_node_text(self.get_node_children(node), "-pre"))
        state = self.get_node_attribute(node, "disabled", False) != "0"
        if state:
            widgetid.configure(state="disabled")
        self.handle_node_replacement(
            node,
            widgetid,
            lambda widgetid=widgetid: self.handle_node_removal(widgetid),
            lambda node=node, widgetid=widgetid, widgettype="text": self.handle_node_style(
                node, widgetid, widgettype
            ),
        )

    def on_input(self, node):
        "Handle <input> elements"
        if not self.forms_enabled:
            return
        self.tk.eval('set type ""')
        nodetype = self.tk.eval(
            "set nodetype [string tolower [%s attr -default {} type]]" % node
        )
        nodevalue = self.get_node_attribute(node, "value")

        if any(
            (
                nodetype == "image",
                nodetype == "submit",
                nodetype == "reset",
                nodetype == "button",
            )
        ):
            widgetid = None
            self.form_get_commands[node] = self.placeholder
            self.form_reset_commands[node] = self.placeholder
        elif nodetype == "file":
            accept = self.get_node_attribute(node, "accept")
            multiple = (
                self.get_node_attribute(node, "multiple", self.radiobutton_token)
                != self.radiobutton_token
            )
            widgetid = FileSelector(self, accept, multiple)
            self.form_get_commands[node] = widgetid.get_value
            self.form_reset_commands[node] = widgetid.reset
            self.handle_node_replacement(
                node,
                widgetid,
                lambda widgetid=widgetid: self.handle_node_removal(widgetid),
                lambda node=node, widgetid=widgetid: self.handle_node_style(
                    node, widgetid
                ),
            )
        elif nodetype == "color":
            widgetid = ColourSelector(self, nodevalue)
            self.form_get_commands[node] = widgetid.get_value
            self.form_reset_commands[node] = widgetid.reset
            self.handle_node_replacement(
                node,
                widgetid,
                lambda widgetid=widgetid: self.handle_node_removal(widgetid),
                self.placeholder,
            )
        elif nodetype == "hidden":
            widgetid = None
            self.form_get_commands[node] = lambda node=node: self.get_node_attribute(
                node, "value"
            )
            self.form_reset_commands[node] = lambda: None
        elif nodetype == "checkbox":
            variable = tk.IntVar()
            widgetid = tk.Checkbutton(
                self,
                borderwidth=0,
                padx=0,
                pady=0,
                highlightthickness=0,
                variable=variable,
            )
            variable.trace(
                "w", lambda *_, widgetid=widgetid: self.on_input_change(widgetid)
            )
            self.form_get_commands[node] = lambda: variable.get()
            self.form_reset_commands[node] = lambda: variable.set(0)
            self.handle_node_replacement(
                node,
                widgetid,
                lambda widgetid=widgetid: self.handle_node_removal(widgetid),
                lambda node=node, widgetid=widgetid: self.handle_node_style(
                    node, widgetid
                ),
            )
        elif nodetype == "range":
            variable = tk.IntVar()
            variable.set(nodevalue)
            from_ = self.get_node_attribute(node, "min", 0)
            to = self.get_node_attribute(node, "max", 100)
            widgetid = ttk.Scale(self, variable=variable, from_=from_, to=to)
            variable.trace(
                "w", lambda *_, widgetid=widgetid: self.on_input_change(widgetid)
            )
            self.form_get_commands[node] = lambda: variable.get()
            self.form_reset_commands[node] = lambda: variable.set(0)
            self.handle_node_replacement(
                node,
                widgetid,
                lambda widgetid=widgetid: self.handle_node_removal(widgetid),
                lambda node=node, widgetid=widgetid, widgettype="range": self.handle_node_style(
                    node, widgetid, widgettype
                ),
            )
        elif nodetype == "radio":
            name = self.tk.call(node, "attr", "-default", "", "name")
            if name in self.radio_buttons:
                variable = self.radio_buttons[name]
                widgetid = tk.Radiobutton(
                    self,
                    value=nodevalue,
                    variable=variable,
                    tristatevalue=self.radiobutton_token,
                    borderwidth=0,
                    padx=0,
                    pady=0,
                    highlightthickness=0,
                )
            else:
                variable = tk.StringVar(self)
                widgetid = tk.Radiobutton(
                    self,
                    value=nodevalue,
                    variable=variable,
                    tristatevalue=self.radiobutton_token,
                    borderwidth=0,
                    padx=0,
                    pady=0,
                    highlightthickness=0,
                )
                variable.trace(
                    "w", lambda *_, widgetid=widgetid: self.on_input_change(widgetid)
                )
                self.radio_buttons[name] = variable
            self.form_get_commands[node] = lambda: variable.get()
            self.form_reset_commands[node] = lambda: variable.set("")
            self.handle_node_replacement(
                node,
                widgetid,
                lambda widgetid=widgetid: self.handle_node_removal(widgetid),
                lambda node=node, widgetid=widgetid: self.handle_node_style(
                    node, widgetid
                ),
            )
        else:
            widgetid = tk.Entry(
                self, validate="key", borderwidth=0, highlightthickness=0
            )
            widgetid.configure(
                validatecommand=lambda *_, widgetid=widgetid: self.on_input_change(
                    widgetid
                )
            )
            if nodetype == "password":
                widgetid.configure(show="*")
            widgetid.bind(
                "<Return>",
                lambda event, node=node: self.handle_form_submission(
                    node=node, event=event
                ),
            )
            self.form_get_commands[node] = lambda: widgetid.get()
            self.form_reset_commands[node] = (
                lambda widgetid=widgetid, content=nodevalue: self.handle_entry_reset(
                    widgetid, content
                )
            )
            self.handle_node_replacement(
                node,
                widgetid,
                lambda widgetid=widgetid: self.handle_node_removal(widgetid),
                lambda node=node, widgetid=widgetid, widgettype="text": self.handle_node_style(
                    node, widgetid, widgettype
                ),
            )

        if widgetid:
            state = self.get_node_attribute(node, "disabled", self.radiobutton_token)
            if state != self.radiobutton_token:
                widgetid.configure(state="disabled")

    def on_body(self, node, index):
        "Wait for style changes on the root node"
        self.tk.call(node,
                    "replace",
                    node,
                    "-stylecmd",
                    self.register(lambda node=node: self.set_overflow(node)))

    def on_input_change(self, widgetid):
        widgetid.event_generate("<<Modified>>")
        return True

    def on_click(self, event):
        "Set active element flags"

        if not self.current_node:
            # register current node if mouse has never moved
            self.on_mouse_motion(event)

        self.focus_set()
        self.tag("delete", "selection")
        node_handle = self.get_current_node(event)

        if node_handle:
            self.selection_start_node, self.selection_start_offset = self.node(
                True, event.x, event.y
            )

            if node_handle and self.stylesheets_enabled:
                if not self.get_node_tag(node_handle):
                    node_handle = self.get_current_node_parent(node_handle)
                self.set_node_flags(node_handle, "active")
                self.prev_active_node = node_handle

    def on_leave(self, event):
        "Reset cursor and node states when leaving this widget"
        self.set_cursor("default")
        if self.stylesheets_enabled:
            for node in self.hovered_nodes:
                try:
                    self.remove_node_flags(node, "hover")
                    self.remove_node_flags(node, "active")
                except tk.TclError:
                    pass
        self.hovered_nodes = []
        self.current_node = None

    def on_mouse_motion(self, event):
        "Set hover flags and handle the CSS 'cursor' property"
        if self.is_selecting:
            return
        if self.on_embedded_node:
            node_handle = self.on_embedded_node
        else:
            node_handle = self.get_current_node(event)
            if not node_handle:
                self.on_leave(None)
                return

        if (
            node_handle
            and node_handle != self.current_node
            and self.stylesheets_enabled
        ):
            old_handle = self.current_node
            self.current_node = node_handle

            if node_handle != old_handle:
                is_text_node = False
                if not self.get_node_tag(node_handle):
                    node_handle = self.get_current_node_parent(node_handle)
                    is_text_node = True

                cursor = self.get_node_property(node_handle, "cursor")
                if cursor in self.cursors:
                    self.set_cursor(cursor)
                elif is_text_node:
                    self.set_cursor("text")
                else:
                    self.set_cursor("default")

                for node in self.hovered_nodes:
                    self.remove_node_flags(node, "hover")

                self.hovered_nodes = []
                self.handle_recursive_hovering(
                    node_handle, self.recursive_hovering_count
                )

    def on_click_release(self, event):
        "Handle click releases on <a> nodes"
        if self.is_selecting:
            self.is_selecting = False
            self.current_node = None
            self.on_mouse_motion(event)
            return

        node_handle = self.get_current_node(event)

        try:
            if node_handle:
                node_tag = self.get_node_tag(node_handle).lower()

                if not node_tag:
                    node_handle = self.get_node_parent(node_handle)
                    node_tag = self.get_node_tag(node_handle).lower()

                node_type = self.get_node_attribute(node_handle, "type").lower()

                if self.prev_active_node and self.stylesheets_enabled:
                    self.remove_node_flags(self.prev_active_node, "active")
                if node_tag == "a":
                    self.set_node_flags(node_handle, "visited")
                    self.handle_link_click(node_handle)
                elif node_tag == "input" and node_type == "reset":
                    self.handle_form_reset(node_handle)
                elif node_tag == "input" and node_type == "submit":
                    self.handle_form_submission(node_handle)
                elif node_tag == "input" and node_type == "image":
                    self.handle_form_submission(node_handle)
                elif node_tag == "button" and node_type == "submit":
                    self.handle_form_submission(node_handle)
                else:
                    for node in self.hovered_nodes:
                        node_tag = self.get_node_tag(node).lower()
                        if node_tag == "a":
                            self.set_node_flags(node, "visited")
                            self.handle_link_click(node)
                            break
                        elif node_tag == "button":
                            if (self.get_node_attribute(node, "type").lower() == "submit"):
                                self.handle_form_submission(node)
                                break
        except tk.TclError:
            pass

        self.prev_active_node = None

    def on_embedded_mouse_motion(self, event, node_handle):
        self.on_embedded_node = node_handle
        self.on_mouse_motion(event)

    def add_bindtags(self, widgetid, allowscrolling=True):
        "Add bindtags to allow scrolling and on_embedded_mouse function calls"
        if allowscrolling:
            tags = (
                self.node_tag,
                self.scrollable_node_tag,
            )
        else:
            tags = (self.node_tag,)
        widgetid.bindtags(widgetid.bindtags() + tags)

    def crash_prevention(self, data):
        if self.prevent_crashes:
            data = "".join(c for c in data if c <= "\uFFFF")
            data = re.sub(
                "font-family:[^;']*(;)?",
                self.remove_noto_emoji,
                data,
                flags=re.IGNORECASE,
            )
            data = re.sub(r"rgb\([^0-9](.*?)\)", "inherit", data, flags=re.IGNORECASE)
        return data

    def begin_download(self):
        thread = threadname()
        self.active_threads.append(thread)
        self.after(0, self.downloading_resource_func)
        return thread

    def finish_download(self, thread):
        self.active_threads.remove(thread)
        if len(self.active_threads) == 0:
            # call done_loading_func outside of the thread 
            # this stops bad things from happening when Tcl is also being called in the callback
            self.after(0, self.done_loading_func)

    def fix_css_urls(self, match, url):
        "Make relative uris in CSS files absolute"
        newurl = match.group()
        newurl = strip_css_url(newurl)
        newurl = urljoin(url, newurl)
        newurl = f"url('{newurl}')"
        return newurl

    def remove_noto_emoji(self, match):
        "Remove noto color emoji font, which causes Tkinter to crash"
        match = match.group().lower()
        match = match.replace("noto color emoji", "arial")
        return match

    def style_thread_check(self, **kwargs):
        if self.max_thread_count == 0:
            self.fetch_styles(**kwargs)
        elif len(self.active_threads) >= self.max_thread_count:
            self.after(500, lambda kwargs=kwargs: self.style_thread_check(**kwargs))
        else:
            thread = StoppableThread(target=self.fetch_styles, kwargs=kwargs)
            thread.start()

    def image_thread_check(self, url, name):
        if self.max_thread_count == 0:
            self.fetch_images(url, name, url)
        elif len(self.active_threads) >= self.max_thread_count:
            self.after(
                500, lambda url=url, name=name: self.image_thread_check(url, name)
            )
        else:
            thread = StoppableThread(
                target=self.fetch_images,
                args=(
                    url,
                    name,
                    url,
                ),
            )
            thread.start()

    def fetch_styles(self, sheetid, handler, errorurl="", url=None, data=None):
        "Fetch stylesheets and parse the CSS code they contain"
        thread = self.begin_download()

        if url and self.unstoppable:
            try:
                if url.startswith("file://") or (not self.caches_enabled):
                    data = download(url, insecure=self.insecure_https)[0]
                else:
                    data = cachedownload(url, insecure=self.insecure_https)[0]

                matcher = lambda match, url=url: self.fix_css_urls(match, url)
                data = re.sub(r"url\((.*?)\)", matcher, data)

            except Exception as error:
                self.message_func(f"Error loading stylesheet {errorurl}: {error}")

        if data and self.unstoppable:
            self.parse_css(f"{sheetid}.9999", handler, data)
            if url:
                self.message_func(f"Successfully loaded {shorten(url)}")
        self.finish_download(thread)

    def load_alt_image(self, url, name):
        if (url in self.image_directory) and self.image_alternate_text_enabled:
            node = self.image_directory[url]
            nodebox = self.bbox(node)
            alt = self.get_node_attribute(self.image_directory[url], "alt")
            if alt:
                image = textimage(
                    name,
                    alt,
                    nodebox,
                    self.image_alternate_text_font,
                    self.image_alternate_text_size,
                    self.image_alternate_text_threshold,
                )
                self.loaded_images.add(image)
            elif not self.ignore_invalid_images:
                image, error = newimage(
                    BROKENIMAGE, name, "image/png", self.image_inversion_enabled
                )
                self.loaded_images.add(image)

    def fetch_images(self, url, name, urltype):
        "Fetch images and display them in the document"
        thread = self.begin_download()

        self.message_func(f"Fetching image from {shorten(url)}")

        try:
            if url.startswith("file://") or (not self.caches_enabled):
                data, newurl, filetype, code = download(url, insecure=self.insecure_https)
            else:
                data, newurl, filetype, code = cachedownload(
                    url, insecure=self.insecure_https
                )

            if self.unstoppable and data:
                # thread safety
                self.after(0, self.finish_fetching_images, data, name, filetype, url)

        except Exception as error:
            self.load_alt_image(url, name)
            self.message_func(
                f"Error loading image {url}: {error}"
            )
            self.image_setup_func(url, False)

        self.finish_download(thread)

    def finish_fetching_images(self, data, name, filetype, url):
        try:
            image, error = newimage(
                data, name, filetype, self.image_inversion_enabled
            )
            
            if image:
                self.loaded_images.add(image)
                self.message_func(f"Successfully loaded {shorten(url)}")
                self.image_setup_func(url, True)
            elif error == "no_pycairo":
                self.load_alt_image(url, name)
                self.message_func(
                    f"Error loading image {url}: Pycairo is not installed but is required to parse .svg files"
                )
                self.image_setup_func(url, False)
            elif error == "no_rsvg":
                self.load_alt_image(url, name)
                self.message_func(
                    f"Error loading image {url}: Rsvg is not installed but is required to parse .svg files"
                )
                self.image_setup_func(url, False)
            elif error == "corrupt":
                self.load_alt_image(url, name)
                self.message_func(f"The image {url} could not be shown")
                self.image_setup_func(url, False)
        except Exception as error:
            self.load_alt_image(url, name)
            self.message_func(
                f"Error loading image {url}: {error}"
            )
            self.image_setup_func(url, False)

    def handle_link_click(self, node_handle):
        "Handle link clicks"
        href = self.get_node_attribute(node_handle, "href")
        url = self.resolve_url(href)
        self.message_func(f"A link to '{shorten(url)}' has been clicked")
        self.visited_links.append(url)
        self.link_click_func(url)

    def handle_entry_reset(self, widgetid, content):
        "Reset tk.Entry widgets in HTML forms"
        widgetid.delete(0, "end")
        widgetid.insert(0, content)

    def handle_form_reset(self, node):
        "Reset HTML forms"
        if (node not in self.form_elements) or (not self.forms_enabled):
            return

        form = self.form_elements[node]
        #action = self.get_node_attribute(form, "action")

        for formelement in self.loaded_forms[form]:
            self.form_reset_commands[formelement]()

    def handle_form_submission(self, node, event=None):
        "Submit HTML forms"
        if (node not in self.form_elements) or (not self.forms_enabled):
            return

        data = []
        form = self.form_elements[node]
        action = self.get_node_attribute(form, "action")
        method = self.get_node_attribute(form, "method", "GET").upper()

        for formelement in self.loaded_forms[form]:
            nodeattrname = self.get_node_attribute(formelement, "name")
            if nodeattrname:
                nodevalue = self.form_get_commands[formelement]()
                nodetype = self.get_node_attribute(formelement, "type")
                if nodetype == "submit" or nodetype == "reset":
                    continue
                elif nodetype == "file":
                    for value in nodevalue:
                        data.append(
                            (nodeattrname, value),
                        )
                else:
                    data.append(
                        (nodeattrname, nodevalue),
                    )
        if not event:
            nodeattrname = self.get_node_attribute(node, "name")
            nodevalue = self.get_node_attribute(node, "value")
            if nodeattrname and nodevalue:
                data.append(
                    (nodeattrname, nodevalue),
                )

        data = urlencode(data)

        if action == "":
            url = list(urlparse(self.base_url))
            url = url[:-3]
            url.extend(["", "", ""])
            url = urlunparse(url)
        else:
            url = self.resolve_url(action)

        if method == "GET":
            data = "?" + data
        else:
            data = data.encode()

        self.message_func(f"A form has been submitted to {shorten(url)}")
        self.form_submit_func(url, data, method)

    def handle_node_replacement(self, node, widgetid, deletecmd, stylecmd=None, allowscrolling=True, handledelete=True):
        "Replace a Tkhtml3 node with a Tkinter widget"
        if stylecmd:
            if handledelete:
                self.tk.call(
                    node,
                    "replace",
                    widgetid,
                    "-deletecmd",
                    self.register(deletecmd),
                    "-stylecmd",
                    self.register(stylecmd),
                )
            else:
                self.tk.call(
                    node, "replace", widgetid, "-stylecmd", self.register(stylecmd)
                )
        else:
            if handledelete:
                self.tk.call(
                    node, "replace", widgetid, "-deletecmd", self.register(deletecmd)
                )
            else:
                self.tk.call(node, "replace", widgetid)

        self.add_bindtags(widgetid, allowscrolling)

        widgetid.bind(
            "<Enter>",
            lambda event, node_handle=node: self.on_embedded_mouse_motion(
                event, node_handle=node_handle
            ),
        )
        widgetid.bind(
            "<Leave>",
            lambda event, node_handle=None: self.on_embedded_mouse_motion(
                event, node_handle=node_handle
            ),
        )

    def handle_node_removal(self, widgetid):
        widgetid.destroy()

    def handle_node_style(self, node, widgetid, widgettype="button"):
        if widgettype == "button":
            bg = "transparent"
            while bg == "transparent" and node != "":
                bg = self.get_node_property(node, "background-color")
                node = self.get_node_parent(node)
            if bg == "transparent":
                bg = "white"
            widgetid.configure(
                background=bg,
                highlightbackground=bg,
                highlightcolor=bg,
                activebackground=bg,
            )
        elif widgettype == "range":
            bg = "transparent"
            while bg == "transparent" and node != "":
                bg = self.get_node_property(node, "background-color")
                node = self.get_node_parent(node)
            if bg == "transparent":
                bg = "white"
            style = ttk.Style()
            stylename = f"Scale{widgetid}.Horizontal.TScale"
            style.configure(stylename, background=bg)
            widgetid.configure(style=stylename)
        elif widgettype == "text":
            bg = self.get_node_property(node, "background-color")
            fg = self.get_node_property(node, "color")
            font = self.get_node_property(node, "font")
            if bg == "transparent":
                bg = "white"
            if fg == "transparent":
                fg = "white"
            widgetid.configure(background=bg, foreground=fg, font=font)

    def set_overflow(self, node):
        "Look for and handle the overflow property"
        overflow = self.get_node_property(node, "overflow")
        if overflow != "visible": # visible is the tkhtml default, so it's largely meaningless
            overflow_map = {"hidden": 0,
                            "auto": 2,
                            "visible": 1,
                            "scroll": 1,
                            "clip": 0}
            overflow = overflow_map[overflow]
            self.vsb_type = self.manage_vsb_func(overflow)
        
        if self.get_node_attribute(node, "scroll-x"): # tkhtml doesn't support overflow-x
            self.manage_hsb_func(2)

    def set_cursor(self, cursor):
        "Set document cursor"

        if self.current_cursor != cursor:
            cursor = self.cursors[cursor]
            self.cursor_change_func(cursor=cursor)
            self.current_cursor = cursor

    def handle_recursive_hovering(self, node_handle, count):
        "Set hover flags on the parents of the hovered element"
        self.set_node_flags(node_handle, "hover")
        self.hovered_nodes.append(node_handle)

        if count >= 1:
            parent = self.get_current_node_parent(node_handle)
            if parent:
                self.handle_recursive_hovering(parent, count - 1)

    def setup_widgets(self):
        "Replace Tkhtml nodes with Tk widgets when needed"
        widgets = self.search(f"[{self.embedded_widget_attr_name}]")
        for node in widgets:
            widgetid = self.get_node_attribute(node, self.embedded_widget_attr_name)
            if widgetid == "":
                continue
            widgetid = self.nametowidget(widgetid)
            if widgetid.winfo_ismapped():  
                # don't display a widget that is already visible 
                continue
            if widgetid in self.stored_widgets:
                # don't display a widget that is already embedded or about to be embedded
                # this prevents this code from firing after a widget has been embedded by the <object> tag
                continue

            allowscrolling = self.get_node_attribute(node, "allowscrolling", "false") != "false"
            handleremoval = self.get_node_attribute(node, "handleremoval", "false") != "false"
            if handleremoval:
                handleremoval = lambda widgetid=widgetid: self.handle_node_removal(widgetid)
            else:
                handleremoval = None

            self.stored_widgets[widgetid] = node
            self.handle_node_replacement(
                node,
                widgetid,
                handleremoval,
                None,
                allowscrolling,
                False,
            )
            

    def remove_widget(self, widgetid):
        "Remove a stored widget"
        self.delete_node(self.stored_widgets[widgetid])
        del self.stored_widgets[widgetid]

    def replace_widget(self, widgetid, newwidgetid):
        "Replace a stored widget"
        node = self.stored_widgets[widgetid]
        self.tk.call(node, "replace", newwidgetid)

        if newwidgetid in self.stored_widgets:
            self.tk.call(self.stored_widgets[newwidgetid], "replace", widgetid)
            self.stored_widgets[widgetid] = self.stored_widgets[newwidgetid]
        else:
            del self.stored_widgets[widgetid]
        self.stored_widgets[newwidgetid] = node

    def replace_element(self, selector, widgetid):
        "Replace an HTML element with a widget"
        node = self.search(selector)[0]
        self.tk.call(node, "replace", widgetid)
        self.stored_widgets[widgetid] = node

    def find_text(self, searchtext, select, ignore_case, highlight_all):
        "Search for and highlight specific text in the document"
        self.clear_selection()

        nmatches = 0
        matches = []
        selected = []
        match_indexes = []

        self.tag("delete", "findtext")
        self.tag("delete", "findtextselected")

        if len(searchtext) == 0 or select <= 0:
            return nmatches, selected, matches

        doctext = self.text("text")

        try:
            # find matches
            if ignore_case:
                rmatches = re.finditer(
                    searchtext, doctext, flags=re.IGNORECASE | re.MULTILINE
                )
            else:
                rmatches = re.finditer(searchtext, doctext, flags=re.MULTILINE)

            for match in rmatches:
                match_indexes.append(
                    (
                        match.start(0),
                        match.end(0),
                    )
                )
                nmatches += 1

            if len(match_indexes) > 0:
                # highlight matches
                self.message_func(
                    f"{nmatches} results for the search key '{searchtext}' have been found"
                )
                if highlight_all:
                    for num, match in enumerate(match_indexes):
                        match = self.text("index", match_indexes[num][0])
                        match += self.text("index", match_indexes[num][1])
                        matches.append(match)

                selected = self.text("index", match_indexes[select - 1][0])
                selected += self.text("index", match_indexes[select - 1][1])

                for match in matches:
                    node1, index1, node2, index2 = match
                    self.tag("add", "findtext", node1, index1, node2, index2)
                    self.tag(
                        "configure",
                        "findtext",
                        "-bg",
                        self.find_match_highlight_color,
                        "-fg",
                        self.find_match_text_color,
                    )

                node1, index1, node2, index2 = selected
                self.tag("add", "findtextselected", node1, index1, node2, index2)
                self.tag(
                    "configure",
                    "findtextselected",
                    "-bg",
                    self.find_current_highlight_color,
                    "-fg",
                    self.find_current_text_color,
                )

                # scroll to node if selected match is not visible
                nodebox = self.text("bbox", node1, index1, node2, index2)
                docheight = float(self.bbox()[3])

                view_top = docheight * self.yview()[0]
                view_bottom = view_top + self.winfo_height()
                node_top = float(nodebox[1])
                node_bottom = float(nodebox[3])

                if (node_top < view_top) or (node_bottom > view_bottom):
                    self.yview("moveto", node_top / docheight)
            else:
                self.message_func(
                    "No results for the search key '{}' could be found".format(
                        searchtext
                    )
                )
            return nmatches, selected, matches
        except Exception as error:
            self.message_func(
                "Error searching for {}: {}".format(
                    searchtext, error
                )
            )
            return nmatches, selected, matches

    def create_iframe(self, node, url, html=None):
        widgetid = self.embed_obj(self, False, overflow_scroll_frame=self)
        widgetid.copy_settings(self)

        if html:
            widgetid.load_html(html, url)
        elif url:
            widgetid.load_html("<p>Loading...</p>")
            widgetid.load_url(url, insecure=self.insecure_https)

        self.handle_node_replacement(
            node, widgetid, lambda widgetid=widgetid: self.handle_node_removal(widgetid)
        )

    def resolve_url(self, href):
        "Get full url from partial url"
        return urljoin(self.base_url, href)

    def select_all(self):
        "Select all of the text in the document"
        self.clear_selection()
        beginning = self.text("index", 0)
        end = self.text("index", len(self.text("text")))
        self.tag("add", "selection", beginning[0], beginning[1], end[0], end[1])
        self.tag(
            "configure",
            "selection",
            "-bg",
            self.selected_text_highlight_color,
            "-fg",
            self.selected_text_color,
        )

    def clear_selection(self):
        "Clear current selection possible"
        self.tag("delete", "selection")
        self.selection_start_node = None

    def extend_selection(self, event):
        "Alter selection and HTML element states based on mouse movement"
        if self.selection_start_node is None:
            self.tag("delete", "selection")
            return

        try:
            self.selection_end_node, self.selection_end_offset = self.node(
                True, event.x, event.y
            )

            if self.selection_end_node is None:
                return

            self.tag("delete", "selection")
            self.tag(
                "add",
                "selection",
                self.selection_start_node,
                self.selection_start_offset,
                self.selection_end_node,
                self.selection_end_offset,
            )
            self.tag(
                "configure",
                "selection",
                "-bg",
                self.selected_text_highlight_color,
                "-fg",
                self.selected_text_color,
            )

            if not self.is_selecting and self.prev_active_node:
                if len(self.get_selection()) > 0:
                    self.is_selecting = True
                    self.set_cursor("text")
                    if self.stylesheets_enabled:
                        self.remove_node_flags(self.prev_active_node, "active")
                        for node in self.hovered_nodes:
                            self.remove_node_flags(node, "hover")
                    self.prev_active_node = None
                    self.hovered_nodes = []
        except tk.TclError:
            self.set_cursor("default")

    def get_selection(self):
        "Return the currently selected text"
        if self.selection_start_node is None or self.selection_end_node is None:
            return
        start_index = self.text(
            "offset", self.selection_start_node, self.selection_start_offset
        )
        end_index = self.text(
            "offset", self.selection_end_node, self.selection_end_offset
        )
        if start_index > end_index:
            start_index, end_index = end_index, start_index
        whole_text = self.text("text")
        return whole_text[start_index:end_index]

    def copy_selection(self, event=None):
        "Copy the selected text to the clipboard"
        selected_text = self.get_selection()
        self.clipboard_clear()
        self.clipboard_append(selected_text)
        self.message_func(f"The text '{selected_text}' has been copied to the clipboard")
        
    def scroll_x11(self, event, widget=None):
        "Manage scrolling on Linux"
        if not widget:
            widget = event.widget
            
        yview = widget.yview()  

        if event.num == 4:
            if widget.overflow_scroll_frame and (yview[0] == 0 or widget.vsb_type == 0):
                widget.overflow_scroll_frame.scroll_x11(event, widget.overflow_scroll_frame)
            else:
                if widget.vsb_type == 0:
                    return
                widget.yview_scroll(-4, "units")
        else:
            if widget.overflow_scroll_frame and (yview[1] == 1 or widget.vsb_type == 0):
                widget.overflow_scroll_frame.scroll_x11(event, widget.overflow_scroll_frame)
            else:
                if widget.vsb_type == 0:
                    return
                widget.yview_scroll(4, "units")

    def scroll(self, event):
        "Manage scrolling on Windows/MacOS"
        yview = self.yview()      

        if self.overflow_scroll_frame and event.delta > 0 and (yview[0] == 0 or self.vsb_type == 0):
            self.overflow_scroll_frame.scroll(event)
        elif self.overflow_scroll_frame and event.delta < 0 and (yview[1] == 1 or self.vsb_type == 0):
            self.overflow_scroll_frame.scroll(event)
        elif platform.system() == "Darwin":
            if self.vsb_type == 0:
                return
            self.yview_scroll(int(-1*event.delta), "units")
        else:
            if self.vsb_type == 0:
                return
            self.yview_scroll(int(-1*event.delta/30), "units")