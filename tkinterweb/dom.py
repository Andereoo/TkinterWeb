"""
A thin wrapper on top of bindings.py that offers some JavaScript-like functions 
and converts Tkhtml nodes into Python objects

Some of the Tcl code in this file is borrowed from the Tkhtml/Hv3 project. See tkhtml/COPYRIGHT.

Copyright (c) 2025 Andereoo
"""

from tkinter import TclError


COMPOSITE_PROPERTIES = {
    "margin": ("margin-top", "margin-right", "margin-bottom", "margin-left"),
    "padding": ("padding-top", "padding-right", "padding-bottom", "padding-left"),
    "border-width": ("border-top-width", "border-right-width", "border-bottom-width", "border-left-width"),
    "border-style": ("border-top-style", "border-right-style", "border-bottom-style", "border-left-style"),
    "border-color": ("border-top-color", "border-right-color", "border-bottom-color", "border-left-color"),
    "border": ("border-width", "border-style", "border-color"),
    "outline": ("outline-color", "outline-style", "outline-width"),
    "background": ("background-color", "background-image", "background-repeat", "background-attachment", "background-position"),
    "list-style": ("list-style-type", "list-style-position", "list-style-image"),
    "cue": ("cue-before", "cue-after"),
    "font": ("font-style", "font-variant", "font-weight", "font-size", "line-height", "font-family"),
}


def escape_Tcl(string):
    string = str(string)
    escaped = ""
    special_chars = '"\\$[]'
    for char in string:
        if char in special_chars:
            escaped += "\\"
        escaped += char
    return escaped


def extract_nested(nested):
    if isinstance(nested, tuple) and len(nested):
        return extract_nested(nested[0])
    return nested


def camel_case_to_property(string):
    new_string = ""
    for i in string:
        if i.isupper():
            new_string += "-" + i.lower()
        else:
            new_string += i
    return new_string

    # this also works:
    # from re import finditer
    # matches = finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', string)
    # return "-".join([m.group(0).lower() for m in matches])

def flatten(data):
    """Recursively flattens nested tuples and lists into a single list."""
    if isinstance(data, tuple):
        return flatten(data[0])
    else:
        return data

class HTMLDocument:
    """Access this class via the :attr:`~tkinterweb.HtmlFrame.document` property of the :class:`~tkinterweb.HtmlFrame` and :class:`~tkinterweb.HtmlLabel` widgets.
    
    :param html: The :class:`~tkinterweb.TkinterWeb` instance this class is tied to.
    :type html: :class:`~tkinterweb.TkinterWeb`
    
    :ivar html: The associated :class:`~tkinterweb.TkinterWeb` instance."""
    def __init__(self, html):
        self.html = html
        self.html.tk.createcommand("parse_fragment", self.html.parse_fragment)
        self.html.tk.createcommand("node_to_html", self._node_to_html)

    @property
    def body(self):  # taken from hv3_dom_html.tcl line 161
        """The document body element.

        :rtype: :class:`HTMLElement`"""
        return HTMLElement(
            self, self.html.tk.eval(f"""set body [lindex [[{self.html} node] children] 1]"""),
        )
        #return self.querySelector("body")

    @property
    def documentElement(self):
        """The document root element.

        :rtype: :class:`HTMLElement`"""
        return HTMLElement(
            self, self.html.tk.eval(f"""set root [lindex [{self.html} node] 0]"""),
        )
    
    def createElement(self, tagname):  # taken from hv3_dom_core.tcl line 214
        """Create and return a new HTML element with the given tag name.

        :param tagname: The new element's HTML tag.
        :type tagname: str
        :rtype: :class:`HTMLElement`"""
        return HTMLElement(
            self,
            self.html.tk.eval("""
            set node [%s fragment "<%s>"]
            if {$node eq ""} {error "DOMException NOT_SUPPORTED_ERR"}
            return $node
            """ % (self.html, tagname)),
        )

    def createTextNode(self, text):
        """Create and return a new text node with the given text content.
        
        :param text: The text content of the new node.
        :type text: str
        :rtype: :class:`HTMLElement`"""
        return HTMLElement(
            self, 
            self.html.tk.eval("""
            set tkw %s
            set text "%s"
            if {$text eq ""} {
                # Special case - The [fragment] API usually parses an empty string
                # to an empty fragment. So create a text node with text "X", then 
                # set the text to an empty string.
                set node [$tkw fragment X]
                $node text set ""
            } else {
                set escaped [string map {< &lt; > &gt;} $text]
                set node [parse_fragment $escaped]
            }
            return $node
            """ % (self.html, escape_Tcl(text)))
        )


    def getElementById(self, query, _root=None):
        """Return an element that matches a given id.
        
        :param query: The element id to be searched for.
        :type query: str
        :rtype: :class:`HTMLElement`
        :raises: :py:class:`tkinter.TclError`"""
        node = self.html.search(f"[id='{query}']", index=0, root=_root)
        return HTMLElement(self, node)

    def getElementsByClassName(self, query, _root=None):
        """Return all elements that match a given class name.
        
        :param query: The class to be searched for.
        :type query: str
        :rtype: list[:class:`HTMLElement`]
        :raises: :py:class:`tkinter.TclError`"""
        nodes = self.html.search(" ".join(f".{i}" for i in query.split()), root=_root)
        return [HTMLElement(self, node) for node in nodes]

    def getElementsByName(self, query, _root=None):
        """Return all elements that match a given given name attribute.
        
        :param query: The name to be searched for.
        :type query: str
        :rtype: list[:class:`HTMLElement`]
        :raises: :py:class:`tkinter.TclError`"""
        nodes = self.html.search(f"[name='{query}']", root=_root)
        return [HTMLElement(self, node) for node in nodes]

    def getElementsByTagName(self, query, _root=None):
        """Return all elements that match a given tag name.
        
        :param query: The tag to be searched for.
        :type query: str
        :rtype: list[:class:`HTMLElement`]
        :raises: :py:class:`tkinter.TclError`"""
        nodes = self.html.search(query, root=_root)
        return [HTMLElement(self, node) for node in nodes]

    def querySelector(self, query, _root=None):
        """Return the first element that matches a given CSS selector.
        
        :param query: The CSS selector to be searched for.
        :type query: str
        :rtype: :class:`HTMLElement`
        :raises: :py:class:`tkinter.TclError`"""
        node = self.html.search(query, index=0, root=_root)
        return HTMLElement(self, node)

    def querySelectorAll(self, query, _root=None):
        """Return all elements that match a given CSS selector.
        
        :param query: The CSS selector to be searched for.
        :type query: str
        :rtype: list[:class:`HTMLElement`]
        :raises: :py:class:`tkinter.TclError`"""
        nodes = self.html.search(query, root=_root)
        return [HTMLElement(self, node) for node in nodes]
    
    def _node_to_html(self, node, deep=True):  # From hv3_dom_core.tcl line 311 and line 329
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
                    set void {
                        area base br col embed hr img input keygen link meta param source track wbr
                    }  ;# Don't add closing tags if is self-closing (void-elements)
                    if {[lsearch -exact $void $tag] != -1} {
                        return $ret
                    } elseif {%d} {
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
        ) # May split this into 2 methods in future


class HTMLElement:
    """:param document_manager: The :class:`~tkinterweb.dom.HTMLDocument` instance this class is tied to.
    :type document_manager: :class:`~tkinterweb.dom.HTMLDocument`

    :param node: The Tkhtml3 node this class represents.
    :type node: Tkhtml3 node
    :ivar html: The element's corresponding :class:`~tkinterweb.TkinterWeb` instance.
    :ivar node: The element's corresponding Tkhtml node."""
    def __init__(self, document_manager, node):
        self.document = document_manager
        self.html = document_manager.html
        self.node = flatten(node)
        self.style_cache = None  # initialize style as None
        self.html.bbox(node)  # check if the node is valid

        # we need this here or crashes happen if multiple Tkhtml instances exist (depending on the Tkhtml version)
        # no idea why, but hey, it works
        self.html.tk.createcommand("parse_fragment", self.html.parse_fragment)
        
    @property
    def style(self):
        """Manage the element's styling. For instance, to make the element have a blue background, use ``yourhtmlelement.style.backgroundColor = "blue"``.

        :rtype: :class:`~tkinterweb.dom.CSSStyleDeclaration`"""
        if self.style_cache is None:  # lazy loading of style
            self.style_cache = CSSStyleDeclaration(self)
        return self.style_cache

    @property
    def innerHTML(self):  # taken from hv3_dom2.tcl line 61
        """Get and set the inner HTML of the element. Cannot be used on ``<html>`` elements.
        
        :rtype: str
        :raises: :py:class:`tkinter.TclError`"""
        return self.html.tk.eval("""
            set node %s
            if {[$node tag] eq ""} {error "$node is not an HTMLElement"}

            set ret ""
            foreach child [$node children] {
                append ret [node_to_html $child 1]
            }
            return $ret
            """ % extract_nested(self.node)
        )

    @innerHTML.setter
    def innerHTML(self, contents):  # taken from hv3_dom2.tcl line 88
        self.html.tk.eval("""
            set node %s
            set tag [$node tag]
            if {$tag eq ""} {error "$node is not an HTMLElement"}
            if {$tag eq "html"} {error "innerHTML cannot be set on <$tag> elements"}

            # Destroy the existing children (and their descendants) of $node.
            set children [$node children]
            $node remove $children
            foreach child $children {
                $child destroy
            }

            # Insert the new descendants, created by parseing $newHtml.
            set newHtml "%s"
            set children [parse_fragment $newHtml]
            $node insert $children

            update  ;# This must be done to see changes on-screen
            """ % (extract_nested(self.node), escape_Tcl(contents))
        )
        self.html.send_onload(root=self.node)

    @property
    def textContent(self):  # Original for this project
        """Get and set the text content of an element. Cannot be used on ``<html>`` elements.
        
        :rtype: str
        :raises: :py:class:`tkinter.TclError`"""
        return self.html.tk.eval("""
            proc get_child_text {node} {
                set txt ""
                foreach child [$node children] {
                    if {[$child tag] eq ""} {
                        append txt [$child text -pre]
                    } else {
                        append txt [get_child_text $child]
                    }
                }
                return $txt
            }
            return [get_child_text %s]
            """ % extract_nested(self.node)
        )

    @textContent.setter
    def textContent(self, contents):  # Ditto
        self.html.tk.eval("""
            set node %s
            set textnode %s
            if {$textnode eq ""} {error "$node is empty"}
            if {[$node tag] eq "html"} {error "textContent cannot be set on <$tag> elements"}
            $node remove [$node children]
            foreach child [$node children] {
                $child destroy
            }
            $node insert $textnode
            
            update  ;# This must be done to see changes on-screen
            """ % (extract_nested(self.node), self.document.createTextNode(contents).node)
        )

    @property
    def attributes(self):
        """Return the element's attributes.
        
        :rtype: str"""
        return self.html.get_node_attributes(self.node)

    @property
    def tagName(self):
        """Return the element's tag name.

        :rtype: str"""
        return self.html.get_node_tag(self.node)

    @property
    def parentElement(self):
        """Get the element's parent element.
        
        :rtype: :class:`HTMLElement`
        :raises: :py:class:`tkinter.TclError`"""
        return HTMLElement(self, self.html.get_node_parent(self.node))

    @property
    def children(self):
        """Get the element's children elements.
        
        :rtype: list[:class:`HTMLElement`]
        :raises: :py:class:`tkinter.TclError`"""
        return [HTMLElement(self, i) for i in self.html.get_node_children(self.node)]
    
    @property
    def widget(self): # not a JS property, but could be useful
        """Get and set the element's widget. Only works on ``<object>`` elements.

        :rtype: :py:class:`tkinter.Widget` or None"""
        if self.tagName == "object":
            data = self.getAttribute("data")
            try:
                return self.html.nametowidget(data)
            except KeyError:
                return None
        else:
            return None
        
    @widget.setter
    def widget(self, widget): # not a JS property, but could be useful
        if self.tagName == "object":
            # really we should do better than set the data attribute
            # right now this also can be used to set the object's url
            # but in practice it shouldn't really matter
            self.setAttribute("data", widget)
    
    @property
    def value(self):
        """Get and set the input's value. Only works on ``<input>``, ``<textarea>``, and ``<select>`` elements.
        
        :rtype: str"""
        if self.node in self.html.form_widgets:
            return self.html.form_widgets[self.node].get()
        return None
        
    @value.setter
    def value(self, value):
        if self.node in self.html.form_widgets:
            self.html.form_widgets[self.node].set(value)

    @property
    def checked(self):
        """Convenience property for the ``checked`` HTML attribute. Check/uncheck a radiobutton or checkbox or see if the element is checked.
        
        :rtype: bool"""
        if self.node in self.html.form_widgets:
            if self.html.get_node_attribute(self.node, "checked", "false") != "false":
                return True
            else:
                return False
        return None
        
    @checked.setter
    def checked(self, value):
        if self.node in self.html.form_widgets:
            self.html.set_node_attribute(self.node, "checked", value)

    @property
    def onchange(self):
        """Convenience property for the ``onchange`` HTML attribute. Get and set the JavaScript code to execute when the input element's value changes
        
        :rtype: str"""
        return self.getAttribute("onchange")
    
    @onchange.setter
    def onchange(self, callback):
        self.setAttribute("onchange", callback)

    @property
    def onload(self):
        """Convenience property for the ``onload`` HTML attribute. Get and set the code to execute when the element loads.
        
        :rtype: str"""
        return self.getAttribute("onload")
    
    @onload.setter
    def onload(self, callback):
        self.setAttribute("onload", callback)

    @property
    def onclick(self):
        """Convenience property for the ``onclick`` HTML attribute. Get and set the code to execute when the element is clicked.
        
        :rtype: str"""
        return self.getAttribute("onclick")
    
    @onclick.setter
    def onclick(self, callback):
        self.setAttribute("onclick", callback)

    @property
    def oncontextmenu(self):
        """Convenience property for the ``oncontextmenu`` HTML attribute. Get and set the code to execute when the element is right-clicked.
        
        :rtype: str"""
        return self.getAttribute("oncontextmenu")
    
    @oncontextmenu.setter
    def oncontextmenu(self, callback):
        self.setAttribute("oncontextmenu", callback)

    @property
    def ondblclick(self):
        """Convenience property for the ``ondblclick`` HTML attribute. Get and set the code to execute when the element is double-clicked.
        
        :rtype: str"""
        return self.getAttribute("ondblclick")
    
    @ondblclick.setter
    def ondblclick(self, callback):
        self.setAttribute("ondblclick", callback)

    @property
    def onmousedown(self):
        """Convenience property for the ``onmousedown`` HTML attribute. Get and set the code to execute when any mouse button is pressed over the element.
        
        :rtype: str"""
        return self.getAttribute("onmousedown")
    
    @onmousedown.setter
    def onmousedown(self, callback):
        self.setAttribute("onmousedown", callback)

    @property
    def onmouseenter(self):
        """Convenience property for the ``onmouseenter`` HTML attribute. Get and set the code to execute when the mouse moves onto the element.
        
        :rtype: str"""
        return self.getAttribute("onmouseenter")
    
    @onmouseenter.setter
    def onmouseenter(self, callback):
        self.setAttribute("onmouseenter", callback)

    @property
    def onmouseleave(self):
        """Convenience property for the ``onmouseleave`` HTML attribute. Get and set the code to execute when the mouse moves out of the element.
        
        :rtype: str"""
        return self.getAttribute("onmouseleave")
    
    @onmouseleave.setter
    def onmouseleave(self, callback):
        self.setAttribute("onmouseleave", callback)

    @property
    def onmousemove(self):
        """Convenience property for the ``onmousemove`` HTML attribute. Get and set the code to execute when the mouse moves over the element.
        
        :rtype: str"""
        return self.getAttribute("onmousemove")
    
    @onmousemove.setter
    def onmousemove(self, callback):
        self.setAttribute("onmousemove", callback)

    @property
    def onmouseout(self):
        """Convenience property for the ``onmouseout`` HTML attribute. Get and set the code to execute when the mouse moves out of the element or its parent elements.
        
        :rtype: str"""
        return self.getAttribute("onmouseout")
    
    @onmouseout.setter
    def onmouseout(self, callback):
        self.setAttribute("onmouseout", callback)

    @property
    def onmouseover(self):
        """Convenience property for the ``onmouseover`` HTML attribute. Get and set the code to execute when the mouse moves into the element or its children elements.
        
        :rtype: str"""
        return self.getAttribute("onmouseover")
    
    @onmouseover.setter
    def onmouseover(self, callback):
        self.setAttribute("onmouseover", callback)

    @property
    def onmouseup(self):
        """Convenience property for the ``onmouseup`` HTML attribute. Get and set the code to execute when the mouse button is released over the element.
        
        :rtype: str"""
        return self.getAttribute("onmouseup")
    
    @onmouseup.setter
    def onmouseup(self, callback):
        self.setAttribute("onmouseup", callback)

    def getAttribute(self, attribute):
        """Return the value of the given attribute..
        
        :param attribute: The attribute to return.
        :type attribute: str
        :rtype: str"""
        return self.html.get_node_attribute(self.node, attribute)

    def setAttribute(self, attribute, value):
        """Set the value of the given attribute..
        
        :param attribute: The attribute to set.
        :type attribute: str
        :param value: The new value of the given attribute.
        :type value: str"""
        self.html.set_node_attribute(self.node, attribute, value)
        
    def remove(self):
        """Delete the element. Cannot be used on ``<html>`` or ``<body>`` elements.

        :raises: :py:class:`tkinter.TclError`"""
        self.html.delete_node(self.node)

    def appendChild(self, children):
        """Insert the specified children into the element.
        
        :param children: The element(s) to be added into the element.
        :type children: list, tuple, or :class:`HTMLElement`"""
        self._insert_children(children)

    def insertBefore(self, children, before):
        """Insert the specified children before a given child element.
        
        :param children: The element(s) to be added into the element.
        :type children: list, tuple, or :class:`HTMLElement`
        :param before: The child element that the added elements should be placed before.
        :type before: :class:`HTMLElement`
        :raises: :py:class:`tkinter.TclError`"""
        self._insert_children(children, before)

    def getElementById(self, query):
        """Return an element that is a child of the current element and matches the given id.
        
        :param query: The element id to be searched for.
        :type query: str
        :rtype: :class:`HTMLElement`
        :raises: :py:class:`tkinter.TclError`"""
        return self.document.getElementById(query, self.node)

    def getElementsByClassName(self, query):
        """Return all elements that are children of the current element and match the given class name.
        
        :param query: The class to be searched for.
        :type query: str
        :rtype: list[:class:`HTMLElement`]
        :raises: :py:class:`tkinter.TclError`"""
        return self.document.getElementsByClassName(query, self.node)

    def getElementsByName(self, query):
        """Return all elements that are children of the current element and match the given name attribute.
        
        :param query: The name to be searched for.
        :type query: str
        :rtype: list[:class:`HTMLElement`]
        :raises: :py:class:`tkinter.TclError`"""
        return self.document.getElementsByName(query, self.node)

    def getElementsByTagName(self, query):
        """Return all elements that are children of the current element and match the given tag name.
        
        :param query: The tag to be searched for.
        :type query: str
        :rtype: list[:class:`HTMLElement`]
        :raises: :py:class:`tkinter.TclError`"""
        return self.document.getElementsByTagName(query, self.node)

    def querySelector(self, query):
        """Return the first element that is a child of the current element and matches the given CSS selector.
        
        :param query: The CSS selector to be searched for.
        :type query: strvalue
        :rtype: :class:`HTMLElement`
        :raises: :py:class:`tkinter.TclError`"""
        return self.document.querySelector(query, self.node)

    def querySelectorAll(self, query):
        """Return all elements that are children of the current element and match the given CSS selector.
        
        :param query: The CSS selector to be searched for.
        :type query: str
        :rtype: list[:class:`HTMLElement`]
        :raises: :py:class:`tkinter.TclError`"""
        return self.document.querySelectorAll(query, self.node)
    
    def scrollIntoView(self):
        "Scroll the viewport so that this element is visible."
        self.html.yview(self.node)

    def getBoundingClientRect(self):
        """Get the element's position and size.

        :rtype: :class:`~tkinterweb.dom.DOMRect`"""
        return DOMRect(self)
    
    def _insert_children(self, children, before=None):
        "Helper method to insert children at a specified position"
        # ensure children is a list
        children = children if isinstance(children, list) else [children]
        # extract node commands
        tkhtml_children_nodes = [i.node for i in children]
        # insert the nodes based on the position
        if before:
            self.html.insert_node_before(self.node, tkhtml_children_nodes, before.node)
        else:
            self.html.insert_node(self.node, tkhtml_children_nodes)
        self.html.send_onload(children=[child.node for child in children])

        #for node in tkhtml_children_nodes:
        #    print(node)
        #    tag = self.html.get_node_tag(node)
        #    print(tag)
        #    if tag == "a":
        #        self.html._on_a(self.node)
        #    if tag == "object":
        #        self.html._on_object(self.node)
        #    if tag == "iframe":
        #        self.html._on_iframe(self.node)

class HTMLCollection(list):
    # For some reason this stuff doesn't work in JavaScript
    # We'll use it I find the need and/or if the JS bugit is addressed
    @property
    def length(self):
        return len(self)
    
    def item(self, index):
        return self[int(index)]
    
    def namedItem(self, name):
        for i in self:
            if i.getAttribute("id") == name or i.getAttribute("name") == name:
                return i

class DOMRect:
    """This class generates and stores information about the element's position and size at this point in time.
    
    :param element_manager: The :class:`~tkinterweb.dom.HTMLElement` instance this class is tied to.
    :type element_manager: :class:`~tkinterweb.dom.HTMLElement`
    :ivar x: The element's horizontal offset from the left-hand side of the page.
    :ivar y: The element's vertical offset from the top of the page.
    :ivar width: The element's width.
    :ivar height: The element's height.
    :ivar html: The element's corresponding :class:`~tkinterweb.TkinterWeb` instance.
    :ivar node: The element's corresponding Tkhtml node."""
    def __init__(self, element_manager):
        self.html = element_manager.html
        self.node = element_manager.node

        self.x, self.y, x2, y2 = self.html.bbox(self.node)

        self.width = x2 - self.x
        self.height = y2 - self.y

class CSSStyleDeclaration:
    """Access this class via the :attr:`~tkinterweb.dom.HTMLElement.style` property of the :attr:`~tkinterweb.dom.HTMLElement` class.
    
    :param element_manager: The :class:`~tkinterweb.dom.HTMLElement` instance this class is tied to.
    :type element_manager: :class:`~tkinterweb.dom.HTMLElement`
    :ivar html: The element's corresponding :class:`~tkinterweb.TkinterWeb` instance.
    :ivar node: The element's corresponding Tkhtml node."""
    def __init__(self, element_manager):
        self.html = element_manager.html
        self.node = element_manager.node

    def __getitem__(self, property):
        # Get value from Tkhtml if it is a real and existing property
        try:
            value = self.html.get_node_property(self.node, property, "-inline")
        except TclError:
            # Ignore invalid properties
            value = ""

        if not value:
            # Get value from sub-properties if it is a composite property
            if property in COMPOSITE_PROPERTIES:
                values = []
                for key in COMPOSITE_PROPERTIES[property]:
                    computed = self.__getitem__(key)
                    if len(computed.split()) > 1:
                        # If the sub-properties have multiple values (eg. have their own sub-properties),
                        # Then this property does not have a valid value
                        return ""
                    if computed: values.append(computed)
            
                if len(values) == len(COMPOSITE_PROPERTIES[property]):
                    if all(x == values[0] for x in values): 
                        # Simplify the return value if the values of the sub-properties are all the same
                        value = values[0]
                    else: 
                        value = " ".join(values)

            if not value:
                # Otherwise attempt to get value from 'style' attribute
                style = self.cssInlineStyles
                if property in style: 
                    value = style[property]
                    
        return value

    def __setitem__(self, property, value):
        style = self.html.get_node_properties(self.node, "-inline")
        style[property] = value
        sStr = " ".join(f"{p}: {v};" for p, v in style.items())
        self.html.set_node_attribute(self.node, "style", sStr)

    def __delitem__(self, property):
        value = self.__getitem__(property)

        # Delete the property from the Tkhtml properties list if it exists 
        style = self.html.get_node_properties(self.node, "-inline")
        if property in style: 
            del style[property]
        else:
            # Delete the property from the 'style' attribute if it exists 
            style = self.cssInlineStyles
            if property in style: 
                del style[property]

        # Delete the property's sub-properties properties if applicable
        # Do this regardless of what happens above in case the property exists as a composite while its sub-properties were also set seperately
        if property in COMPOSITE_PROPERTIES:
            def clean(property):
                for key in COMPOSITE_PROPERTIES[property]:
                    if key in COMPOSITE_PROPERTIES:
                        clean(key)
                    elif key in style:
                        del style[key]
            clean(property)

        sStr = " ".join(f"{p}: {v};" for p, v in style.items())
        self.html.set_node_attribute(self.node, "style", sStr)

        return value

    def __setattr__(self, property, value):
        if property in ("node", "html"):
            super().__setattr__(property, value)
        else:
            self.__setitem__(camel_case_to_property(property), value)

    def __getattr__(self, property):
        return self.__getitem__(camel_case_to_property(property))

    @property
    def cssText(self):
        """Return the text of the element's inline style declaration.
        
        :rtype: str"""
        return self.html.get_node_attribute(self.node, "style")
    
    @property
    def length(self):
        """Return the number of style declarations in the element's inline style declaration.
        
        :rtype: int"""
        return len(self.html.get_node_properties(self.node, "-inline"))
    
    @property
    def cssProperties(self): # not a JS function, but could be useful
        """Return all computed properties for the element.
        
        :rtype: dict"""
        return self.html.get_node_properties(self.node)
    
    @property # not a JS function, but could be useful
    def cssInlineProperties(self):
        """Return all inline properties for the element. Similar to the :attr:`cssText` property, but formatted as a dictionary.
        
        :rtype: dict"""
        return self.html.get_node_properties(self.node, "-inline")
    
    @property 
    def cssInlineStyles(self):
        """Return the content of the element's ``style`` attribute, formatted as a dictionary.
        
        :rtype: dict"""
        inline = (self.html.get_node_attribute(self.node, "style"))
        style = {}
        for item in inline.split(";"):
            if item:
                key, old = item.split(":", 1)
                style[key.strip()] = old.strip()
        return style
    
    def getPropertyPriority(self, property):
        """Return the priority of the given inline CSS property.
        
        :param property: The CSS property to search for.
        :type property: str
        :return: "important" or "".
        :rtype: str"""
        style = self.cssInlineStyles
        if property in style:
            value = style[property]
            if value.endswith("!important"): return "important"
        return ""

    def getPropertyValue(self, property):
        """Return the value of the given inline CSS property.
        
        You can also use JavaScript-style camel-cased properties to get a CSS property value. For instance, to get the element's background color, use ``yourhtmlelement.style.backgroundColor``

        :param property: The CSS property to get.
        :type property: str
        :rtype: str"""
        return self.__getitem__(property)

    def removeProperty(self, property):
        """Remove the given inline CSS property.
        
        :param property: The CSS property to remove.
        :type property: str
        :returns: the old value of the given property, or "" if the property did not exist.
        :rtype: str"""
        return self.__delitem__(property)

    def setProperty(self, property, value):
        """Set the value of the given inline CSS property.

        You can also use JavaScript-style camel-cased properties to set a CSS property value. For instance, to make the element have a blue background, use ``yourhtmlelement.style.backgroundColor = "blue"``
        
        :param property: The CSS property to set.
        :type property: str
        :returns: the old value of the given property, or "" if the property did not exist.
        :rtype: str"""
        self.__setitem__(property, value)
