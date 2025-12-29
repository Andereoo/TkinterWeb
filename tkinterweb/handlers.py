"""
Node handlers and associated extensions to Tkhtml3

Copyright (c) 2021-2025 Andrew Clarke
"""

import tkinter as tk

from urllib.parse import urlencode, urlparse

from . import subwidgets, utilities, imageutils

class NodeManager(utilities.BaseManager):
    "Handle hyperlinks, body/html elements, and title/meta/base elements."
    def __init__(self, html):
        super().__init__(html)

    def __repr__(self):
        return f"{self.html._w}::{self.__class__.__name__.lower()}"

    # --- Handle title, base, and meta elements -------------------------------

    def _on_title(self, node):
        "Handle <title> elements. We could use a script handler but then the node is no longer visible to the DOM."
        children = self.html.get_node_children(node)
        if children: # Fix for Bug #136, where an empty title tag raises an exception
            self.html.title = self.html.get_node_text(self.html.get_node_children(node), "-pre")
            self.html.post_event(utilities.TITLE_CHANGED_EVENT)

    def _on_base(self, node):
        "Handle <base> elements."
        href = self.html.get_node_attribute(node, "href", "")
        if href:
            self.html.base_url = self.html.resolve_url(href)
    
    def _on_meta(self, node):
        "Partly handle <meta> elements."
        if self.html.get_node_attribute(node, "http-equiv") == "refresh":
            content = self.html.get_node_attribute(node, "content").split(";")
            if len(content) == 2:
                if content[1].startswith("url="):
                    url = self.html.resolve_url(content[1].lstrip("url="))
                    self.html.post_message(f"Redirecting to '{utilities.shorten(url)}'")
                    self.html.visited_links.append(url)
                    self.html.on_link_click(url)

    # --- Handle hyperlinks ---------------------------------------------------

    def _on_a(self, node):
        "Handle <a> elements."
        self.html.set_node_flags(node, "link")
        try:
            href = self.html.get_node_attribute(node, "href")
            url = self.html.resolve_url(href)
            if url in self.html.visited_links:
                self.html.set_node_flags(node, "visited")
        except tk.TclError:
            pass

    def _on_a_value_change(self, node, attribute, value):
        if attribute == "href":
            url = self.html.resolve_url(value)
            if url in self.html.visited_links:
                self.html.set_node_flags(node, "visited")
            else:
                self.html.remove_node_flags(node, "visited")

    # --- Handle body elements ------------------------------------------------

    def _on_body(self, node, index):
        "Wait for style changes on the root node."
        self.html.replace_node_contents(node,
                    node,
                    "-stylecmd",
                    self.html.register(lambda node=node: self._set_overflow(node)))
        
    def _on_html(self, node, index):
        self._on_body(node, index)

    def _handle_overflow_property(self, overflow, overflow_function):
        if overflow != "visible": # Visible is the Tkhtml default, so it's largely meaningless
            overflow_map = {"hidden": 0,
                            "auto": 2,
                            "scroll": 1,
                            "clip": 0}
            if overflow in overflow_map:
                overflow = overflow_map[overflow]
                return overflow_function(overflow)
        return None

    def _set_overflow(self, node):
        "Look for and handle the overflow property."
        # Eventually we'll make overflow a composite property of overflow-x and overflow-y
        # But for now it's its own thing and the only one of the three that is actually respected by Tkhtml in rendering
        if self.html.experimental: 
            overflow_options = ("overflow", "overflow-y")
            self._handle_overflow_property(self.html.get_node_property(node, "overflow-x") , self.html.manage_hsb_func)
        else:
            overflow_options = ("overflow",)
            
        for overflow_type in overflow_options:
            overflow = self.html.get_node_property(node, overflow_type) 
            overflow = self._handle_overflow_property(overflow, self.html.manage_vsb_func)
        
        overflow = self.html.get_node_attribute(node, utilities.BUILTIN_ATTRIBUTES["overflow-x"]) # Tkhtml doesn't support overflow-x
        overflow = self._handle_overflow_property(overflow, self.html.manage_hsb_func)

        background = self.html.get_node_property(node, "background-color")
        if background != "transparent" and self.html.motion_frame_bg != background: # Transparent is the Tkhtml default, so it's largely meaningless
            self.html.motion_frame_bg = background
            self.html.motion_frame.config(bg=background)


class FormManager(utilities.BaseManager):
    "Handle forms and form elements."
    def __init__(self, html):
        super().__init__(html)
        self.radiobutton_token = "TKWtsvLKac1"

        self.reset()

    def __repr__(self):
        return f"{self.html._w}::{self.__class__.__name__.lower()}"
    
    def reset(self):
        self.waiting_forms = 0
        self.form_nodes = {}
        self.form_widgets = {}
        self.loaded_forms = {}
        self.radio_buttons = {}

    def _handle_form_reset(self, node):
        "Reset HTML forms."
        if node not in self.form_nodes:
            return

        form = self.form_nodes[node]

        for formelement in self.loaded_forms[form]:
            if formelement in self.form_widgets:
                nodetype = self.html.get_node_attribute(formelement, "type")
                nodetag = self.html.get_node_tag(formelement)
                widget = self.form_widgets[formelement]
                if nodetag == "textarea":
                    nodevalue = self.html.get_node_text(self.html.get_node_children(formelement), "-pre")
                    widget.set(nodevalue)
                elif nodetype == "checkbox":
                    if self.html.get_node_attribute(formelement, "checked", "false") != "false": widget.variable.set(1)
                    else: widget.variable.set(0)
                elif nodetype == "radio":
                    nodevalue = self.html.get_node_attribute(formelement, "value")
                    if self.html.get_node_attribute(formelement, "checked", "false") != "false": 
                        widget.variable.set(nodevalue)
                else:
                    nodevalue = self.html.get_node_attribute(formelement, "value")
                    widget.set(nodevalue)

    def _handle_form_submission(self, node, event=None):
        "Submit HTML forms."
        if node not in self.form_nodes:
            return

        data = []
        form = self.form_nodes[node]
        action = self.html.get_node_attribute(form, "action")
        method = self.html.get_node_attribute(form, "method", "GET").upper()

        for formelement in self.loaded_forms[form]:
            nodeattrname = self.html.get_node_attribute(formelement, "name")

            if nodeattrname:
                nodetype = self.html.get_node_attribute(formelement, "type")

                if formelement in self.form_widgets:
                    nodevalue = self.form_widgets[formelement].get()
                    if nodetype == "number":
                        if not self.form_widgets[formelement].check():
                            return
                elif self.html.get_node_tag(formelement) == "hidden":
                    nodevalue = self.html.get_node_attribute(formelement, "value")
                    
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
            nodeattrname = self.html.get_node_attribute(node, "name")
            nodevalue = self.html.get_node_attribute(node, "value")
            if nodeattrname and nodevalue:
                data.append(
                    (nodeattrname, nodevalue),
                )

        data = urlencode(data)

        if action == "":
            url = urlparse(self.html.base_url)
            url = f"{url.scheme}://{url.netloc}{url.path}"
        else:
            url = self.html.resolve_url(action)

        if method == "GET":
            data = "?" + data
        else:
            data = data.encode()

        self.html.post_message(f"A form was submitted to {utilities.shorten(url)}")
        self.html.on_form_submit(url, data, method)

    # --- Handle forms --------------------------------------------------------

    def _on_form(self, node):
        "Handle <form> elements."
        inputs = self.html.search("input, select, textarea, button", root=node)
        for i in inputs:
            self.form_nodes[i] = node

        if len(inputs) == 0:
            self.waiting_forms += 1
        else:
            self.loaded_forms[node] = inputs
            self.html.post_message("Successfully setup form")
            #self.html.post_message(f"Successfully setup form element {node}")

    def _on_table(self, node):
        """Handle <form> elements in tables; workaround for bug #48."
        In tables, Tkhtml doesn't seem to notice that forms have children.
        We get all children of the table and associate inputs with the previous form.
        Not perfect, but it usually works.
        If a <td> tag is not present, this fails, as Tkhtml seems to not even notice inputs at all"""        
        if self.waiting_forms > 0:
            form = None
            inputs = {}

            for node in (self.html.search("*")):
                tag = self.html.get_node_tag(node)
                if tag == "form":
                    form = node
                    inputs[form] = []
                elif tag.lower() in {"input", "select", "textarea", "button"} and form:
                    self.form_nodes[node] = form
                    inputs[form].append(node)
           
            for form in inputs:
                self.loaded_forms[form] = inputs[form]
                self.waiting_forms -= 1
                self.html.post_message("Successfully setup table form")
                #self.html.post_message(f"Successfully setup table form element {node}")

    # --- Handle dropdowns ----------------------------------------------------

    def _on_select(self, node):
        "Handle <select> elements."
        text = []
        values = []
        selected = None
        for child in self.html.get_node_children(node):
            if self.html.get_node_tag(child) == "option":
                try:
                    child2 = self.html.get_node_children(child)[0]
                    nodevalue = self.html.get_node_attribute(child, "value")
                    nodeselected = self.html.get_node_attribute(child, "selected")
                    values.append(nodevalue)
                    text.append(self.html.get_node_text(child2))
                    if nodeselected:
                        selected = nodevalue
                except IndexError:
                    continue
        if not selected and values:
            selected = values[0]
        widgetid = subwidgets.Combobox(self.html)
        widgetid.insert(text, values, selected)
        widgetid.configure(onchangecommand=lambda *_, widgetid=widgetid: self._on_input_change(node, widgetid))
        self.form_widgets[node] = widgetid
        state = self.html.get_node_attribute(node, "disabled", False) != "0"
        if state:
            widgetid.configure(state="disabled")
        self.html.widget_manager.handle_node_replacement(
            node,
            widgetid,
            lambda widgetid=widgetid: self.html.widget_manager._handle_node_removal(widgetid),
            lambda node=node, widgetid=widgetid, widgettype="text": self.html.widget_manager._handle_node_style(
                node, widgetid, widgettype
            ),
        )
        #self.html.post_message(f"Successfully setup select element {node}")

    def _on_select_value_change(self, node, attribute, value):
        return self._on_input_value_change(node, attribute, value)

    # --- Handle textareas ----------------------------------------------------

    def _on_textarea(self, node):
        "Handle <textarea> elements."
        widgetid = subwidgets.ScrolledTextBox(self.html, self.html.get_node_text(self.html.get_node_children(node), "-pre"), lambda widgetid, node=node: self._on_input_change(node, widgetid))

        self.form_widgets[node] = widgetid
        state = self.html.get_node_attribute(node, "disabled", False) != "0"
        if state:
            widgetid.configure(state="disabled")
        self.html.widget_manager.handle_node_replacement(
            node,
            widgetid,
            lambda widgetid=widgetid: self.html.widget_manager._handle_node_removal(widgetid),
            lambda node=node, widgetid=widgetid, widgettype="text": self.html.widget_manager._handle_node_style(
                node, widgetid, widgettype
            ),
        )
        #self.html.post_message(f"Successfully setup select element {node}")

    # --- Handle inputs -------------------------------------------------------

    def _on_input(self, node):
        "Handle <input> elements."
        self.html.tk.eval('set type ""')
        nodetype = self.html.tk.eval(
            "set nodetype [string tolower [%s attr -default {} type]]" % node
        )
        nodevalue = self.html.get_node_attribute(node, "value")
        state = self.html.get_node_attribute(node, "disabled", "false")

        if nodetype in {"image", "submit", "reset", "button"}:
            return
        elif nodetype == "file":
            accept = self.html.get_node_attribute(node, "accept")
            multiple = (
                self.html.get_node_attribute(node, "multiple", self.radiobutton_token)
                != self.radiobutton_token
            )
            widgetid = subwidgets.FileSelector(self.html, accept, multiple, lambda widgetid, node=node: self._on_input_change(node, widgetid))
            stylecmd = lambda node=node, widgetid=widgetid: self.html.widget_manager._handle_node_style(
                node, widgetid
            )
        elif nodetype == "color":
            widgetid = subwidgets.ColourSelector(self.html, nodevalue, lambda widgetid, node=node: self._on_input_change(node, widgetid))
            stylecmd = utilities.placeholder
        elif nodetype == "checkbox":
            if self.html.get_node_attribute(node, "checked", "false") != "false": 
                checked = 1
            else:
                checked = 0

            widgetid = subwidgets.FormCheckbox(self.html, checked, lambda widgetid, node=node: self._on_input_change(node, widgetid))
            widgetid.set = lambda nodevalue, node=node: self.html.set_node_attribute(node, "value", nodevalue)
            widgetid.get = lambda node=node: self.html.get_node_attribute(node, "value")
            stylecmd = lambda node=node, widgetid=widgetid: self.html.widget_manager._handle_node_style(
                node, widgetid
            )
        elif nodetype == "range":
            widgetid = subwidgets.FormRange(self.html, 
                nodevalue,
                self.html.get_node_attribute(node, "min", 0),
                self.html.get_node_attribute(node, "max", 100),
                self.html.get_node_attribute(node, "step", 1),
                lambda widgetid, node=node: self._on_input_change(node, widgetid)
            )
            stylecmd = lambda node=node, widgetid=widgetid, widgettype="range": self.html.widget_manager._handle_node_style(
                node, widgetid, widgettype
            )
        elif nodetype == "number":
            widgetid = subwidgets.FormNumber(self.html, 
                nodevalue,
                self.html.get_node_attribute(node, "min", 0),
                self.html.get_node_attribute(node, "max", 100),
                self.html.get_node_attribute(node, "step", 1),
                lambda widgetid, node=node: self._on_input_change(node, widgetid)
            )
            stylecmd = lambda node=node, widgetid=widgetid: self.html.widget_manager._handle_node_style(
                node, widgetid
            )
        elif nodetype == "radio":
            name = self.html.get_node_attribute(node, "name", "")
            if self.html.get_node_attribute(node, "checked", "false") != "false": 
                checked = True
            else:
                checked = False
            
            if name in self.radio_buttons:
                variable = self.radio_buttons[name]
            else:
                variable = None

            widgetid = subwidgets.FormRadioButton(
                self.html,
                self.radiobutton_token,
                nodevalue,
                checked,
                variable,
                lambda widgetid, node=node: self._on_input_change(node, widgetid)
            )
            widgetid.set = lambda nodevalue, node=node: self.html.set_node_attribute(node, "value", nodevalue)
            self.radio_buttons[name] = widgetid.variable
            stylecmd = lambda node=node, widgetid=widgetid: self.html.widget_manager._handle_node_style(
                node, widgetid
            )
        else:
            widgetid = subwidgets.FormEntry(self.html, nodevalue, nodetype, lambda widgetid, node=node: self._on_input_change(node, widgetid))
            widgetid.bind(
                "<Return>",
                lambda event, node=node: self._handle_form_submission(
                    node=node, event=event
                ),
            )
            stylecmd = lambda node=node, widgetid=widgetid, widgettype="text": self.html.widget_manager._handle_node_style(
                node, widgetid, widgettype
            )

        self.form_widgets[node] = widgetid
        self.html.widget_manager.handle_node_replacement(
            node,
            widgetid,
            lambda widgetid=widgetid: self.html.widget_manager._handle_node_removal(widgetid),
            stylecmd
        )

        if state != "false": 
            widgetid.configure(state="disabled")
        #self.html.post_message(f"Successfully setup {nodetype if nodetype else "text"} input element {node}")

    def _on_input_value_change(self, node, attribute, value):
        if node not in self.form_widgets:
            return

        nodetype = self.html.get_node_attribute(node, "type")
        widget = self.form_widgets[node]
        if attribute == "value" and nodetype not in {"checkbox", "radio"}:
            widget.set(value)
        elif attribute in {"min", "max", "step"} and nodetype in {"range", "number"}:
            CONFIG_MAP = {"min": "from_", "max": "to", "step": "step"}
            widget.configure(**{CONFIG_MAP[attribute]: value})
        elif attribute == "checked":
            if nodetype == "checkbox":
                widget.variable.set(1 if value != "false" else 0)
            elif nodetype == "radio":
                nodevalue = self.html.get_node_attribute(node, "value")
                if value != "false":
                    widget.variable.set(nodevalue)

    def _on_input_change(self, node, widgetid):
        widgetid.event_generate(utilities.FIELD_CHANGED_EVENT)
        self.html.event_manager.post_element_event(node, "onchange", None, utilities.FIELD_CHANGED_EVENT)
        return True

class ScriptManager(utilities.BaseManager):
    "Handle scripts."
    def __init__(self, html):
        super().__init__(html)
        self.pending_scripts = []

    def __repr__(self):
        return f"{self.html._w}::{self.__class__.__name__.lower()}"
    
    def _on_script(self, attributes, tag_contents):
        """A JavaScript engine could be used here to parse the script.
        Returning any HTMl code here (should) cause it to be parsed in place of the script tag."""
        attributes = attributes.split()
        attributes = dict(zip(attributes[::2], attributes[1::2])) # Make attributes a dict

        if "src" in attributes:
            self.html._thread_check(self.fetch_scripts, attributes, self.html.resolve_url(attributes["src"]))
        elif "defer" in attributes:
            self.pending_scripts.append((attributes, tag_contents))
        else:
            return self.html.on_script(attributes, tag_contents)
    
    def fetch_scripts(self, attributes, url=None, data=None):
        "Fetch and run scripts"
        # NOTE: this method is thread-safe and is designed to run in a thread

        thread = self.html._begin_download()

        if url and thread.isrunning():
            self.html.post_message(f"Fetching script from {utilities.shorten(url)}", True)
            try:
                data = self.html.download_url(url)[0]
            except Exception as error:
                self.html.post_to_queue(lambda message=f"ERROR: could not load script {url}: {error}",
                            url=url: self.html._finish_resource_load(message, url, "script", False))

        if data and thread.isrunning():
            if "defer" in attributes:
                self.pending_scripts.append((attributes, data))
            else:
                self.html.post_to_queue(lambda attributes=attributes, data=data: self.html.on_script(attributes, data))
                
            if url:
                self.html.post_to_queue(lambda message=f"Successfully loaded {utilities.shorten(url)}", 
                            url=url: self.html._finish_resource_load(message, url, "script", True))

        self.html._finish_download(thread)

    def _submit_deferred_scripts(self):
        if self.pending_scripts:
            for index, script in enumerate(self.pending_scripts):
                self.on_script(*script)
            self.pending_scripts = []


class StyleManager(utilities.BaseManager):
    "Handle stylesheets."
    def __init__(self, html):
        super().__init__(html)

    def __repr__(self):
        return f"{self.html._w}::{self.__class__.__name__.lower()}"
    
    def _on_style(self, attributes, tag_contents):
        "Handle <style> elements."
        self.html._thread_check(self.fetch_styles, data=tag_contents)

    def _on_link(self, node):
        "Handle <link> elements."
        try:
            rel = self.html.get_node_attribute(node, "rel").lower()
            media = self.html.get_node_attribute(node, "media", default="all").lower()
            href = self.html.get_node_attribute(node, "href")
            url = self.html.resolve_url(href)
        except tk.TclError:
            return

        if (
            ("stylesheet" in rel)
            and ("all" in media or "screen" in media)
        ):
            self.html._thread_check(self.fetch_styles, node, url)
            # Onload is fired if and when the stylesheet is parsed
        elif "icon" in rel:
            self.html.icon = url
            self.html.post_event(utilities.ICON_CHANGED_EVENT)
            self.html.event_manager.post_element_event(node, "onload", None, utilities.ELEMENT_LOADED_EVENT)
        else:
            self.html.event_manager.post_element_event(node, "onload", None, utilities.ELEMENT_LOADED_EVENT)

    def _on_atimport(self, parent_url, new_url):
        "Load @import scripts."
        try:
            new_url = self.html.resolve_url(new_url, parent_url)
            self.html.post_message(f"Loading stylesheet from {utilities.shorten(new_url)}")

            self.html._thread_check(self.fetch_styles, url=new_url)

        except Exception as error:
            self.html.post_message(f"ERROR: could not load stylesheet {new_url}: {error}")
           
    def _fix_css_urls(self, match, url):
        "Make relative uris in CSS files absolute."
        newurl = match.group()
        newurl = utilities.strip_css_url(newurl)
        newurl = self.html.resolve_url(newurl, url)
        newurl = f"url('{newurl}')"
        return newurl
    
    def fetch_styles(self, node=None, url=None, data=None):
        "Fetch stylesheets and parse the CSS code they contain"
        # NOTE: this method is thread-safe and is designed to run in a thread

        thread = self.html._begin_download()
        if url and thread.isrunning():
            self.html.post_message(f"Fetching stylesheet from {utilities.shorten(url)}", True)
            try:
                data = self.html.download_url(url)[0]
            except Exception as error:
                self.html.post_to_queue(lambda message=f"ERROR: could not load stylesheet {url}: {error}",
                    url=url: self.html._finish_resource_load(message, url, "stylesheet", False))

        if data and thread.isrunning():
            self.html.post_to_queue(lambda node=node, url=url, data=data: self._finish_fetching_styles(node, url, data))
                        
        self.html._finish_download(thread)

    def _finish_fetching_styles(self, node, url, data):
        # NOTE: this must run in the main thread

        self.html.style_count += 1
        sheetid = "user." + str(self.html.style_count).zfill(4)

        self.html.parse_css(f"{sheetid}.9999", data, url)
        if node:
            self.html.event_manager.post_element_event(node, "onload", None, utilities.ELEMENT_LOADED_EVENT)
        if url:
            self.html.post_message(f"Successfully loaded {utilities.shorten(url)}")
            self.html.on_resource_setup(url, "stylesheet", True)


class ImageManager(utilities.BaseManager):
    "Handle images."
    def __init__(self, html):
        super().__init__(html)

        self.loaded_images = {}
        self.image_directory = {}
        self.loaded_image_counter = 0
        self.image_name_prefix = f"_tkinterweb_img_{id(self.html)}_"
        self.image_alternate_text_font = utilities.get_alt_font()
        self.image_alternate_text_size = 14
        self.image_alternate_text_threshold = 10

    def __repr__(self):
        return f"{self.html._w}::{self.__class__.__name__.lower()}"
    
    def reset(self):
        self.image_directory = {}

    def _on_img(self, node):
        url = self.html.resolve_url(self.html.get_node_attribute(node, "src"))
        self.image_directory[url] = node
    
    def _on_img_value_change(self, node, attribute, value):
        if attribute == "src":
            url = self.html.resolve_url(value)
            if node in self.image_directory.values():
                for k, v in frozenset(self.image_directory.items()):
                    if v == node:
                        del self.image_directory[k]
                        break
            self.image_directory[url] = node
            # if self.html.experimental:
            #     c = self.html.get_node_children(node)
            #     if c: self.html.destroy_node(c)

    def load_alt_text(self, url, name):
        # NOTE: this must run in the main thread

        if (url in self.image_directory):
            node = self.image_directory[url]
            if not self.html.ignore_invalid_images:
                image = imageutils.data_to_image(utilities.BROKEN_IMAGE, name, "image/png", self.html.image_inversion_enabled, self.html.dark_theme_limit)
            elif self.html.image_alternate_text_enabled:
                try:  # Ensure thread safety when closing
                    alt = self.html.get_node_attribute(node, "alt")
                    if alt:
                        ### Should work, but doesn't
                        #if self.html.experimental: 
                        #    # Insert the parsed fragment directly if in experimental mode
                        #    self.html.insert_node(node, self.html.parse_fragment(alt))
                        #else:

                        # Generate an image with alternate text if not in experimental mode
                        try:
                            image = imageutils.text_to_image(
                                name, alt, self.html.bbox(node),
                                self.image_alternate_text_font,
                                self.image_alternate_text_size,
                                self.image_alternate_text_threshold,
                            )
                        except (ImportError, ModuleNotFoundError,):
                            self.html.post_message(f"ERROR: could not display alternate text for the image {url}: PIL and PIL.ImageTk must be installed")
                            return
                    else:
                        return
                except (RuntimeError, tk.TclError): 
                    return  # Widget no longer exists
        elif not self.html.ignore_invalid_images:
            image = imageutils.data_to_image(utilities.BROKEN_IMAGE, name, "image/png", self.html.image_inversion_enabled, self.html.dark_theme_limit)
        else:
            return
        
        if name in self.loaded_images:
            self.loaded_images[name] = (self.loaded_images[name], image)
        else:
            self.loaded_images[name] = image

    def _on_image_cmd(self, url):
        "Handle images."
        name = self.allocate_image_name()

        if url.startswith(self.image_name_prefix):
            name = url
        else:
            image = imageutils.blank_image(name)
            self.loaded_images[name] = image

            if any({
                    url.startswith("linear-gradient("),
                    url.startswith("radial-gradient("),
                    url.startswith("repeating-linear-gradient("),
                    url.startswith("repeating-radial-gradient("),
                }):
                self.html.post_message(f"Fetching image: {utilities.shorten(url)}")
                self.load_alt_text(url, name)
                for image in url.split(","):
                    self.html.post_message(f"ERROR: could not display the image {utilities.shorten(url)} because it is not supported yet")
                self.html.on_resource_setup(url, "image", False)
            else:
                url = url.split("), url(", 1)[0].replace("'", "").replace('"', "")
                url = self.html.resolve_url(url)
                if url in self.image_directory:
                    node = self.image_directory[url]
                else:
                    node = None
                self.html._thread_check(self.fetch_images, node, url, name)

        return list((name, self.html.register(self._on_image_delete)))

    def fetch_images(self, node, url, name):
        "Fetch images and display them in the document."
        # NOTE: this method is thread-safe and is designed to run in a thread

        thread = self.html._begin_download()
        if thread.isrunning():
            self.html.post_message(f"Fetching image from {utilities.shorten(url)}", True)

            if url == self.html.base_url:
                self.html.post_to_queue(lambda url=url, name=name, error="ERROR: image url not specified": self._on_image_error(url, name, error))
            else:
                try:
                    data, url, filetype, code = self.html.download_url(url)
                    data, data_is_image = self.check_images(data, name, url, filetype)                
                        
                    if thread.isrunning():
                        self.html.post_to_queue(lambda node=node, data=data, name=name, url=url, filetype=filetype, data_is_image=data_is_image: self.finish_fetching_images(node, data, name, url, filetype, data_is_image))
                except Exception as error:
                    self.html.post_to_queue(lambda url=url, name=name, error=f"ERROR: could not load image {url}: {error}": self._on_image_error(url, name, error))

        self.html._finish_download(thread)

    def check_images(self, data, name, url, filetype):
        "Invert images if needed and convert SVG images to PNGs."
        # NOTE: this method is thread-safe and is designed to run in a thread

        data_is_image = False
        if "svg" in filetype:
            try:
                data = imageutils.svg_to_png(data)
            except (ValueError, ImportError, ModuleNotFoundError,):
                raise RuntimeError(f"could not display the image {url}: either PyGObject, CairoSVG, or both PyCairo and Rsvg must be installed to parse .svg files.")
            
        if self.html.image_inversion_enabled:
            try:
                data = imageutils.invert_image(data, self.html.dark_theme_limit)
                data_is_image = True
            except (ImportError, ModuleNotFoundError,):
                error = f"ERROR: could not invert the image {url}: PIL and PIL.ImageTk must be installed."
                self.html.post_to_queue(lambda url=url, name=name, error=error: self._on_image_error(url, name, error))
            
        return data, data_is_image

    def finish_fetching_images(self, node, data, name, url, filetype, data_is_image=False):
        # NOTE: this must run in the main thread

        try:
            image = imageutils.data_to_image(data, name, filetype, data_is_image)
            
            self.html.post_message(f"Successfully loaded {utilities.shorten(url)}")
            self.html.on_resource_setup(url, "image", True)
            if node:
                self.html.event_manager.post_element_event(node, "onload", None, utilities.ELEMENT_LOADED_EVENT)
            #if self.html.experimental:
            #    node = self.html.search(f'img[src="{url}"]')
            #    if node:
            #        if self.html.get_node_children(node): self.html.delete_node(self.html.get_node_children(node))
            if name in self.loaded_images:
                self.loaded_images[name] = (self.loaded_images[name], image)
            else:
                self.loaded_images[name] = image

            return image
        except (ImportError, ModuleNotFoundError,):
            error = f"ERROR: could not display image {url}: PIL and PIL.ImageTk must be installed"
            self._on_image_error(url, name, error)
        except Exception as error:
            self._on_image_error(url, name, f"ERROR: could not display image {url}: {error}")

    def _on_image_error(self, url, name, error):
        # NOTE: this must run in the main thread
        self.html.post_message(error)
        self.load_alt_text(url, name)
        self.html.on_resource_setup(url, "image", False)

    def _on_image_delete(self, name):
        # Remove the reference to the image in the main thread
        self.html.post_to_queue(lambda name=name: self._finish_image_delete(name))

    def _finish_image_delete(self, name):
        # NOTE: this must run in the main thread
        del self.loaded_images[name]

    def allocate_image_name(self):
        "Get a unique image name."
        name = self.image_name_prefix + str(self.loaded_image_counter)
        self.loaded_image_counter += 1
        return name
    
class ObjectManager(utilities.BaseManager):
    "Handle objects."
    def __init__(self, html):
        super().__init__(html)

        self.loaded_iframes = {}

    def __repr__(self):
        return f"{self.html._w}::{self.__class__.__name__.lower()}"
    
    def reset(self):
        self.loaded_iframes = {}
    
    # --- Handle iframes ------------------------------------------------------

    def _on_iframe(self, node):
        "Handle <iframe> elements."
        src = self.html.get_node_attribute(node, "src")
        srcdoc = self.html.get_node_attribute(node, "srcdoc")
        scrolling = "auto"
        if self.html.get_node_attribute(node, "scrolling") == "no":
            scrolling = False

        if srcdoc:
            self._create_iframe(node, None, srcdoc, scrolling)
        elif src and (src != self.html.base_url):
            src = self.html.resolve_url(src)
            self.html.post_message(f"Creating iframe from {utilities.shorten(src)}")
            self._create_iframe(node, src, vertical_scrollbar=scrolling)

    def _on_iframe_value_change(self, node, attribute, value):
        if attribute == "srcdoc":
            if node in self.loaded_iframes:
                self.loaded_iframes[node].load_html(value)
            else:
                self._create_iframe(node, None, value)
        elif attribute == "src" and (value != self.html.base_url):
            if node in self.loaded_iframes:
                self.loaded_iframes[node].load_url(self.html.resolve_url(value))
            else:
                self._create_iframe(node, value)

    def _create_iframe(self, node, url, html=None, vertical_scrollbar="auto"):
        if self.html.embed_obj:
            widgetid = self.html.embed_obj(self.html,
                messages_enabled=self.html.messages_enabled,
                message_func=self.html.message_func,
                overflow_scroll_frame=self.html,
                stylesheets_enabled = self.html.stylesheets_enabled,
                images_enabled = self.html.images_enabled,
                forms_enabled = self.html.forms_enabled,
                objects_enabled = self.html.objects_enabled,
                ignore_invalid_images = self.html.ignore_invalid_images,
                crash_prevention_enabled = self.html.crash_prevention_enabled,
                dark_theme_enabled = self.html.dark_theme_enabled,
                image_inversion_enabled = self.html.image_inversion_enabled,
                caches_enabled = self.html.caches_enabled,
                threading_enabled = self.html.threading_enabled,
                image_alternate_text_enabled = self.html.image_alternate_text_enabled,
                selection_enabled = self.html.selection_enabled,
                find_match_highlight_color = self.html.find_match_highlight_color,
                find_match_text_color = self.html.find_match_text_color,
                find_current_highlight_color = self.html.find_current_highlight_color,
                find_current_text_color = self.html.find_current_text_color,
                selected_text_highlight_color = self.html.selected_text_highlight_color,
                selected_text_color = self.html.selected_text_color,
                visited_links = self.html.visited_links,
                insecure_https = self.html.insecure_https,
                ssl_cafile = self.html.ssl_cafile,
                request_timeout = self.html.request_timeout,
                caret_browsing_enabled = self.html.caret_browsing_enabled
            )

            if html:
                widgetid.load_html(html, url)
            elif url:
                widgetid.load_url(url)

            self.loaded_iframes[node] = widgetid

            self.html.widget_manager.handle_node_replacement(
                node, widgetid, lambda widgetid=widgetid: self.html.widget_manager._handle_node_removal(widgetid), allowscrolling=False,
            )
        else:
            self.html.post_message(f"WARNING: the embedded page {url} could not be shown because no embed widget was provided.")

    # --- Handle objects ------------------------------------------------------

    def _on_object(self, node, data=None):
        "Handle <object> elements."
        if data == None:
            # This doesn't work when in an attribute handler
            data = self.html.get_node_attribute(node, "data")

        if data != "":
            try:
                # Load widgets presented in <object> elements
                widgetid = self.html.nametowidget(data)
                self.html.widget_manager.set_node_widget(node, widgetid)
            except KeyError:
                data = self.html.resolve_url(data)
                if data == self.html.base_url:
                    # Don't load the object if it is the same as the current file
                    # Otherwise the page will load the same object indefinitely and freeze the GUI forever
                    return

                self.html.post_message(f"Creating object from {utilities.shorten(data)}")
                self.html._thread_check(self.fetch_objects, node, data)

    def _on_object_value_change(self, node, attribute, value):
        if attribute == "data":
            if value:
                self._on_object(node, value)
            else:
                # Reset the element if data is not supplied
                # Force reset because it might contain widgets that are added internally
                self.html.widget_manager.map_node(node, True)

    def fetch_objects(self, node, url):
        # NOTE: this method is thread-safe and is designed to run in a thread

        thread = self.html._begin_download()
        if thread.isrunning():
            try:
                data, url, filetype, code = self.html.download_url(url)

                if data and thread.isrunning():
                    if filetype.startswith("image"):
                        name = self.html.image_manager.allocate_image_name()
                        data, data_is_image = self.html.image_manager.check_images(data, name, url, filetype)
                        self.html.post_to_queue(lambda node=node, data=data, name=name, url=url, filetype=filetype, data_is_image=data_is_image: self._finish_fetching_image_objects(node, data, name, url, filetype, data_is_image))
                    elif filetype == "text/html":
                        self.html.post_to_queue(lambda node=node, data=data, name=name, url=url, filetype=filetype: self._finish_fetching_HTML_objects(node, data, name, url, filetype))

            except Exception as error:
                self.html.post_message(f"ERROR: could not load object element with data {url}: {error}", True)
        
        self.html._finish_download(thread)

    def _finish_fetching_image_objects(self, node, data, name, url, filetype, data_is_image):
        # NOTE: this must run in the main thread

        image = self.html.image_manager.finish_fetching_images(None, data, name, filetype, url, data_is_image)
        self.html.override_node_properties(node, "-tkhtml-replacement-image", f"url({image})")
        self.html.event_manager.post_element_event(node, "onload", None, utilities.ELEMENT_LOADED_EVENT)

    def _finish_fetching_HTML_objects(self, node, data, url, filetype):
        # NOTE: this must run in the main thread

        self._create_iframe(node, url, data)
        self.html.event_manager.post_element_event(node, "onload", None, utilities.ELEMENT_LOADED_EVENT)
