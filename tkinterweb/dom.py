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


class HTMLDocument:
    """Access this class via the :attr:`~tkinterweb.HtmlFrame.document` property of the :attr:`~tkinterweb.HtmlFrame` and :attr:`~tkinterweb.HtmlLabel` widgets.
    
    :param htmlwidget: The :class:`~tkinterweb.TkinterWeb` instance this class is tied to.
    :type htmlwidget: :class:`~tkinterweb.TkinterWeb`"""
    def __init__(self, htmlwidget):
        self.html = htmlwidget
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
        return self.html.tk.eval("""
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
            """ % (self.html, escape_Tcl(text))
        )

    def getElementById(self, query):
        """Return an element given an id.
        
        :param query: The element id to be searched for.
        :type query: str
        :rtype: :class:`HTMLElement`
        :raises: :py:class:`tkinter.TclError`"""
        node = self.html.search(f"[id='{query}']", index=0)
        return HTMLElement(self, node)

    def getElementsByClassName(self, query):
        """Return all elements that match given a class name.
        
        :param query: The class to be searched for.
        :type query: str
        :rtype: tuple[:class:`HTMLElement`]
        :raises: :py:class:`tkinter.TclError`"""
        nodes = self.html.search(" ".join(f".{i}" for i in query.split()))
        return tuple(HTMLElement(self, node) for node in nodes)

    def getElementsByName(self, query):
        """Return all elements that match a given given name attribute.
        
        :param query: The name to be searched for.
        :type query: str
        :rtype: tuple[:class:`HTMLElement`]
        :raises: :py:class:`tkinter.TclError`"""
        nodes = self.html.search(f"[name='{query}']")
        return tuple(HTMLElement(self, node) for node in nodes)

    def getElementsByTagName(self, query):
        """Return all elements that match a given tag name.
        
        :param query: The tag to be searched for.
        :type query: str
        :rtype: tuple[:class:`HTMLElement`]
        :raises: :py:class:`tkinter.TclError`"""
        nodes = self.html.search(query)
        return tuple(HTMLElement(self, node) for node in nodes)

    def querySelector(self, query):
        """Return the first element that matches a given CSS selector.
        
        :param query: The CSS selector to be searched for.
        :type query: str
        :rtype: :class:`HTMLElement`
        :raises: :py:class:`tkinter.TclError`"""
        node = self.html.search(query, index=0)
        return HTMLElement(self, node)

    def querySelectorAll(self, query):
        """Return all elements that match a given CSS selector.
        
        :param query: The CSS selector to be searched for.
        :type query: str
        :rtype: tuple[:class:`HTMLElement`]
        :raises: :py:class:`tkinter.TclError`"""
        nodes = self.html.search(query)
        return tuple(HTMLElement(self, node) for node in nodes)
    
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
    :type node: Tkhtml3 node"""
    def __init__(self, document_manager, node):
        self.document = document_manager
        self.html = document_manager.html
        self.node = node
        self.style_cache = None  # initialize style as None
        self.html.bbox(node)  # check if the node is valid

        # we need this here or crashes happen if multiple Tkhtml instances exist (depending on the Tkhtml version)
        # no idea why, but hey, it works
        self.html.tk.createcommand("parse_fragment", self.html.parse_fragment)
        
    @property
    def style(self):
        """Manage the element's styling.

        :rtype: :class:`~tkinterweb.dom.CSSStyleDeclaration`
        """
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
        "Set the inner HTML of an element"
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
        "Set the text content of an element."
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
            """ % (extract_nested(self.node), self.document.createTextNode(contents))
        )

    @property
    def attributes(self):
        """Return the attributes of the element.
        
        :rtype: str"""
        return self.html.get_node_attributes(self.node)

    @property
    def tagName(self):
        """Return the tag name of the element"

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
        
        :rtype: list(:class:`HTMLElement`)
        :raises: :py:class:`tkinter.TclError`"""
        return [HTMLElement(self, i) for i in self.html.get_node_children(self.node)]

    def getAttribute(self, attribute):
        """Return the value of the given attribute..
        
        :param attribute: The attribute to return.
        :type attribute: str
        :rtype: str"""
        return self.html.get_node_attribute(self.node, attribute)

    def setAttribute(self, attribute, value):
        """Set the value of the given attribute..
        
        :param attribute: The attribute to return.
        :type attribute: str
        :param value: The new value of the given attribute.
        :type value: str
        :rtype: str"""
        self.html.set_node_attribute(self.node, attribute, value)

        tag = self.tagName
        if attribute == "href" and tag == "a":
            self.html._on_a(self.node)
        if attribute == "data" and tag == "object":
            self.html._on_object(self.node)
        if attribute in ("src", "srcdoc",) and tag == "iframe":
            self.html._on_iframe(self.node)
        
    def remove(self):
        """Delete the element. Cannot be used on ``<html>`` or ``<body>`` elements.

        :raises: :py:class:`tkinter.TclError`"""
        self.html.delete_node(self.node)

    def appendChild(self, children):
        """Insert the specified children into the element.
        
        :param children: The element(s) to be added into the element.
        :type children: list, tuple, or HTMLElement"""
        self._insert_children(children)

    def insertBefore(self, children, before):
        """Insert the specified children before a given child element.
        
        :param children: The element(s) to be added into the element.
        :type children: list, tuple, or HTMLElement
        :param before: The child element that the added elements should be placed before.
        :type before: HTMLElement
        :raises: :py:class:`tkinter.TclError`"""
        self._insert_children(children, before)

    def getElementById(self, query):
        """Return an element that is a child of the current element and matches the given id.
        
        :param query: The element id to be searched for.
        :type query: str
        :rtype: :class:`HTMLElement`
        :raises: :py:class:`tkinter.TclError`"""
        node = self.html.search(f"[id='{query}']", index=0, root=self.node)
        return HTMLElement(self, node)

    def getElementsByClassName(self, query):
        """Return all elements that are children of the current element and match the given class name.
        
        :param query: The class to be searched for.
        :type query: str
        :rtype: tuple[:class:`HTMLElement`]
        :raises: :py:class:`tkinter.TclError`"""
        nodes = self.html.search(" ".join(f".{i}" for i in query.split()), root=self.node)
        return tuple(HTMLElement(self, node) for node in nodes)

    def getElementsByName(self, query):
        """Return all elements that are children of the current element and match the given name attribute.
        
        :param query: The name to be searched for.
        :type query: str
        :rtype: tuple[:class:`HTMLElement`]
        :raises: :py:class:`tkinter.TclError`"""
        nodes = self.html.search(f"[name='{query}']", root=self.node)
        return tuple(HTMLElement(self, node) for node in nodes)

    def getElementsByTagName(self, query):
        """Return all elements that are children of the current element and match the given tag name.
        
        :param query: The tag to be searched for.
        :type query: str
        :rtype: tuple[:class:`HTMLElement`]
        :raises: :py:class:`tkinter.TclError`"""
        nodes = self.html.search(query, root=self.node)
        return tuple(HTMLElement(self, node) for node in nodes)

    def querySelector(self, query):
        """Return the first element that are children of the current element and match the given CSS selector.
        
        :param query: The CSS selector to be searched for.
        :type query: str
        :rtype: :class:`HTMLElement`
        :raises: :py:class:`tkinter.TclError`"""
        node = self.html.search(query, index=0, root=self.node)
        return HTMLElement(self, node)

    def querySelectorAll(self, query):
        """Return all elements that are children of the current element and match the given CSS selector.
        
        :param query: The CSS selector to be searched for.
        :type query: str
        :rtype: tuple[:class:`HTMLElement`]
        :raises: :py:class:`tkinter.TclError`"""
        nodes = self.html.search(query, root=self.node)
        return tuple(HTMLElement(self, node) for node in nodes)
    
    def scrollIntoView(self):
        "Scroll the viewport so that this element is visible."
        self.html.yview(self.node)
    
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


class CSSStyleDeclaration:
    """Access this class via the :attr:`~tkinterweb.dom.HTMLElement.style` property of the :attr:`~tkinterweb.dom.HTMLElement` class.
    
    :param element_manager: The :class:`~tkinterweb.dom.HTMLElement` instance this class is tied to.
    :type element_manager: :class:`~tkinterweb.dom.HTMLElement`"""
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
                        return ""
                    if computed: values.append(computed)
            
                if len(values) == len(COMPOSITE_PROPERTIES[property]):
                    if all(x == values[0] for x in values): value = values[0]
                    else: value = " ".join(values)

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
        
        :param property: The CSS property to set.
        :type property: str
        :returns: the old value of the given property, or "" if the property did not exist.
        :rtype: str"""
        self.__setitem__(property, value)
