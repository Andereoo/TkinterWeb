"""
A thin wrapper on top of bindings.py that offers some JavaScript-like functions 
and converts Tkhtml nodes into Python objects

Some of the Tcl code in this file is borrowed from the Tkhtml/Hv3 project. See tkhtml/COPYRIGHT.

Copyright (c) 2025 Andereoo
"""

from tkinter import TclError


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

def generate_text_node(htmlwidget, text):  # taken from hv3_dom_core.tcl line 219
    return htmlwidget.tk.eval("""
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
        """ % (htmlwidget, escape_Tcl(text))
    )

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
    """Access this class via the :attr:`~tkinterweb.HtmlFrame.document` property of the :class:`~tkinterweb.HtmlFrame` and :class:`~tkinterweb.HtmlLabel` widgets.
    
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
            self.html,
            self.html.tk.eval(f"""set body [lindex [[{self.html} node] children] 1]"""),
        )
        #return self.querySelector("body")

    @property
    def documentElement(self):
        """The document root element.

        :rtype: :class:`HTMLElement`"""
        return HTMLElement(
            self.html,
            self.html.tk.eval(f"""set root [lindex [{self.html} node] 0]"""),
        )
    
    def createElement(self, tagname):  # taken from hv3_dom_core.tcl line 214
        """Create and return a new HTML element with the given tag name.

        :param tagname: The new element's HTML tag.
        :type tagname: str
        :rtype: :class:`HTMLElement`"""
        return HTMLElement(
            self.html,
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
        return HTMLElement(self.html, generate_text_node(self.html, text))

    def getElementById(self, query):
        """Return an element that matches a given id.
        
        :param query: The element id to be searched for.
        :type query: str
        :rtype: :class:`HTMLElement`
        :raises: :py:class:`tkinter.TclError`"""
        newquery = f"[id='{query}']"
        node = self.html.search(newquery, index=0)
        return HTMLElement(self.html, node)

    def getElementsByClassName(self, query):
        """Return all elements that match a given class name.
        
        :param query: The class to be searched for.
        :type query: str
        :rtype: tuple[:class:`HTMLElement`]
        :raises: :py:class:`tkinter.TclError`"""
        newquery = [f".{i}" for i in query.split()]
        nodes = self.html.search(" ".join(newquery))
        return tuple(HTMLElement(self.html, node) for node in nodes)

    def getElementsByName(self, query):
        """Return all elements that match a given given name attribute.
        
        :param query: The name to be searched for.
        :type query: str
        :rtype: tuple[:class:`HTMLElement`]
        :raises: :py:class:`tkinter.TclError`"""
        newquery = f"[name='{query}']"
        nodes = self.html.search(newquery)
        return tuple(HTMLElement(self.html, node) for node in nodes)

    def getElementsByTagName(self, query):
        """Return all elements that match a given tag name.
        
        :param query: The tag to be searched for.
        :type query: str
        :rtype: tuple[:class:`HTMLElement`]
        :raises: :py:class:`tkinter.TclError`"""
        nodes = self.html.search(query)
        return tuple(HTMLElement(self.html, node) for node in nodes)

    def querySelector(self, query):
        """Return the first element that matches a given CSS selector.
        
        :param query: The CSS selector to be searched for.
        :type query: str
        :rtype: :class:`HTMLElement`
        :raises: :py:class:`tkinter.TclError`"""
        node = self.html.search(query, index=0)
        return HTMLElement(self.html, node)

    def querySelectorAll(self, query):
        """Return all elements that match a given CSS selector.
        
        :param query: The CSS selector to be searched for.
        :type query: str
        :rtype: tuple[:class:`HTMLElement`]
        :raises: :py:class:`tkinter.TclError`"""
        nodes = self.html.search(query)
        return tuple(HTMLElement(self.html, node) for node in nodes)
    
    def _node_to_html(self, node, deep=True):
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


class CSSStyleDeclaration:
    """Access this class via the :attr:`~tkinterweb.dom.HTMLElement.style` property of the :attr:`~tkinterweb.dom.HTMLElement` class.
    
    :param htmlwidget: The :class:`~tkinterweb.TkinterWeb` instance this class is tied to.
    :type htmlwidget: :class:`~tkinterweb.TkinterWeb`
    :param node: The Tkhtml3 node this class should modify.
    :type node: Tkhtml3 node
    
    
    All camel-cased supported CSS properties are valid properties. Examples include ``color``, ``backgroundColor``, and ``fontFamily``.

    CSS properties can also be returned or set as key-value pairs (eg. ``CSSStyleDeclaration["background-color"]``)
    """
    def __init__(self, htmlwidget, node):
        self.html = htmlwidget
        self.node = node

    def __getitem__(self, prop):
        return self.html.get_node_property(self.node, prop)

    def __setitem__(self, prop, value):
        style = self.html.get_node_properties(self.node, "-inline")
        style[prop] = value
        sStr = " ".join(f"{p}: {v};" for p, v in style.items())
        self.html.set_node_attribute(self.node, "style", sStr)

    def __setattr__(self, prop, value):
        if prop in ("node", "html"):
            super().__setattr__(prop, value)
        else:
            self.__setitem__(camel_case_to_property(prop), value)

    def __getattr__(self, prop):
        try:
            return self.__getitem__(camel_case_to_property(prop))
        except TclError:
            raise TclError(f"no such property: {prop}")

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
    

class HTMLElement:
    """:param htmlwidget: The :class:`~tkinterweb.TkinterWeb` instance this class is tied to.
    :type htmlwidget: :class:`~tkinterweb.TkinterWeb`
    :param node: The Tkhtml3 node this class represents.
    :type node: Tkhtml3 node"""
    def __init__(self, htmlwidget, node):
        self.html = htmlwidget
        self.node = node
        self.styleCache = None  # initialize style as None
        self.html.bbox(node)  # check if the node is valid

        # we need this here or crashes happen if multiple Tkhtml instances exist (depending on the Tkhtml version)
        # no idea why, but hey, it works
        self.html.tk.createcommand("parse_fragment", self.html.parse_fragment)
        
    @property
    def style(self):
        """Manage the element's styling. For instance, to make the element have a blue background, use ``yourhtmlelememt.style.backgroundColor = "blue"``.

        :rtype: :class:`~tkinterweb.dom.CSSStyleDeclaration`
        """
        if self.styleCache is None:  # lazy loading of style
            self.styleCache = CSSStyleDeclaration(self.html, self.node)
        return self.styleCache

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
                update
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
            #foreach child $children {
            #    $child destroy
            #}

            set newHtml "%s"
            # Insert the new descendants, created by parseing $newHtml.
            set children [parse_fragment $newHtml]
            $node insert $children

            update
            """ % (extract_nested(self.node), escape_Tcl(contents))
        )

    @property
    def textContent(self):  # original for this project
        """Get and set the text content of an element. Cannot be used on ``<html>`` elements.
        
        :rtype: str
        :raises: :py:class:`tkinter.TclError`"""
        return self.html.tk.eval("""
            proc get_child_text {node} {
                set z ""
                foreach child [$node children] {
                    if {[$child tag] eq ""} {
                        append z [$child text -pre]
                    } else {
                        append z [get_child_text $child]
                    }
                }
                return $z
            }
            set node %s
            return [get_child_text $node]
            """ % extract_nested(self.node)
        )

    @textContent.setter
    def textContent(self, contents):  # ditto
        "Set the text content of an element."
        self.html.tk.eval("""
            set node %s
            set tag [$node tag]
            set textnode %s
            if {$textnode eq ""} {error "$node is empty"}
            if {$tag eq "html"} {error "textContent cannot be set on <$tag> elements"}
            $node remove [$node children]
            #foreach child [$node children] {
            #    $child destroy
            #}
            $node insert $textnode
            update  ;# This must be done to see changes on-screen
            """ % (extract_nested(self.node), generate_text_node(self.html, contents))
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
        return HTMLElement(self.html, self.html.get_node_parent(self.node))

    @property
    def children(self):
        """Get the element's children elements.
        
        :rtype: list[class:`HTMLElement`]
        :raises: :py:class:`tkinter.TclError`"""
        return [HTMLElement(self.html, i) for i in self.html.get_node_children(self.node)]

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
        newquery = f"[id='{query}']"
        node = self.html.search(newquery, index=0, root=self.node)
        return HTMLElement(self.html, node)

    def getElementsByClassName(self, query):
        """Return all elements that are children of the current element and match the given class name.
        
        :param query: The class to be searched for.
        :type query: str
        :rtype: tuple[:class:`HTMLElement`]
        :raises: :py:class:`tkinter.TclError`"""
        newquery = [f".{i}" for i in query.split()]
        nodes = self.html.search(" ".join(newquery), root=self.node)
        return tuple(HTMLElement(self.html, node) for node in nodes)

    def getElementsByName(self, query):
        """Return all elements that are children of the current element and match the given name attribute.
        
        :param query: The name to be searched for.
        :type query: str
        :rtype: tuple[:class:`HTMLElement`]
        :raises: :py:class:`tkinter.TclError`"""
        newquery = f"[name='{query}']"
        nodes = self.html.search(newquery, root=self.node)
        return tuple(HTMLElement(self.html, node) for node in nodes)

    def getElementsByTagName(self, query):
        """Return all elements that are children of the current element and match the given tag name.
        
        :param query: The tag to be searched for.
        :type query: str
        :rtype: tuple[:class:`HTMLElement`]
        :raises: :py:class:`tkinter.TclError`"""
        nodes = self.html.search(query, root=self.node)
        return tuple(HTMLElement(self.html, node) for node in nodes)

    def querySelector(self, query):
        """Return the first element that is a child of the current element and matches the given CSS selector.
        
        :param query: The CSS selector to be searched for.
        :type query: str
        :rtype: :class:`HTMLElement`
        :raises: :py:class:`tkinter.TclError`"""
        node = self.html.search(query, index=0, root=self.node)
        return HTMLElement(self.html, node)

    def querySelectorAll(self, query):
        """Return all elements that are children of the current element and match the given CSS selector.
        
        :param query: The CSS selector to be searched for.
        :type query: str
        :rtype: tuple[:class:`HTMLElement`]
        :raises: :py:class:`tkinter.TclError`"""
        nodes = self.html.search(query, root=self.node)
        return tuple(HTMLElement(self.html, node) for node in nodes)
    
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