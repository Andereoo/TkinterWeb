"""
A thin wrapper on top of bindings.py that offers some JavaScript-like functions 
and converts Tkhtml nodes into Python objects

Some of the Tcl code in this file is borrowed from the Tkhtml/Hv3 project. See tkhtml/COPYRIGHT.

Copyright (c) 2025 Andereoo
"""

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

def node_to_html(self, node, deep=True):
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

def generate_text_node(htmlwidget, text):  # Taken from hv3_dom_core.tcl line 219
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


class TkwDocumentObjectModel:
    def __init__(self, htmlwidget):
        self.html = htmlwidget
        self.html.tk.createcommand("parse_fragment", self.html.parse_fragment)
        self.html.tk.createcommand("node_to_html", node_to_html)

    def createElement(self, tagname):  # Taken from hv3_dom_core.tcl line 214
        "Create a new HTML element with the given tag name"
        return HtmlElement(
            self.html,
            self.html.tk.eval("""
            set node [%s fragment "<%s>"]
            if {$node eq ""} {error "DOMException NOT_SUPPORTED_ERR"}
            return $node
            """ % (self.html, tagname)),
        )

    def createTextNode(self, text):
        "Create a new text node with the given text conent"
        return HtmlElement(self.html, generate_text_node(self.html, text))

    @property
    def body(self):  # Taken from hv3_dom_html.tcl line 161
        "Return the document body element"
        return HtmlElement(
            self.html,
            self.html.tk.eval(f"""set body [lindex [[{self.html} node] children] 1]"""),
        )

    @property
    def documentElement(self):
        "Return the document body element"
        return HtmlElement(
            self.html,
            self.html.tk.eval(f"""set body [lindex [{self.html} node] 0]"""),
        )

    def getElementById(self, query):
        "Return an element given an id"
        newquery = f"[id='{query}']"
        node = self.html.search(newquery, index=0)
        return HtmlElement(self.html, node)

    def getElementsByClassName(self, query):
        "Return a list of elements given a class name"
        newquery = [f".{i}" for i in query.split()]
        nodes = self.html.search(" ".join(newquery))
        return tuple(HtmlElement(self.html, node) for node in nodes)

    def getElementsByName(self, query):
        "Return a list of elements matching a given name attribute"
        newquery = f"[name='{query}']"
        nodes = self.html.search(newquery)
        return tuple(HtmlElement(self.html, node) for node in nodes)

    def getElementsByTagName(self, query):
        "Return a list of elements given a tag name"
        nodes = self.html.search(query)
        return tuple(HtmlElement(self.html, node) for node in nodes)

    def querySelector(self, query):
        "Return the first element that matches a given CSS selector"
        node = self.html.search(query, index=0)
        return HtmlElement(self.html, node)

    def querySelectorAll(self, query):
        "Return a list of elements that match a given CSS selector"
        nodes = self.html.search(query)
        return tuple(HtmlElement(self.html, node) for node in nodes)


class CSSStyleDeclaration:
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
        return style[prop]

    def __setattr__(self, prop, value):
        if prop in ("node", "html"):
            super().__setattr__(prop, value)
        else:
            self.__setitem__(prop.replace("_", "-"), value)

    def __getattr__(self, prop):
        return self.__getitem__(prop.replace("_", "-"))

    @property
    def cssText(self):
        return self.html.get_node_attribute(self.node, "style")
    
    @property
    def cssProperties(self):
        return self.html.get_node_properties(self.node)
    
    @property
    def cssInlineProperties(self):
        return self.html.get_node_properties(self.node, "-inline")


class HtmlElement:
    def __init__(self, htmlwidget, node):
        self.html = htmlwidget
        self.node = node
        self.contains_widgets = False
        self.styleCache = None  # Initialize style as None
        self.html.bbox(node)  # Check if the node is valid

    @property
    def style(self):
        if self.styleCache is None:  # Lazy loading of style
            self.styleCache = CSSStyleDeclaration(self.html, self.node)
        return self.styleCache

    @property
    def innerHTML(self):  # Taken from hv3_dom2.tcl line 61
        "Get the inner HTML of an element"
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
    def innerHTML(self, contents):  # Taken from hv3_dom2.tcl line 88
        "Set the inner HTML of an element"
        self.html.tk.eval("""
            set node %s
                
            if {[$node tag] eq ""} {error "$node is not an HTMLElement"}

            # Destroy the existing children (and their descendants) of $node.
            set children [$node children]
            $node remove $children
            foreach child $children {
                $child destroy
            }

            set newHtml "%s"
            # Insert the new descendants, created by parseing $newHtml.
            set children [parse_fragment $newHtml]
            $node insert $children

            update
            """ % (extract_nested(self.node), escape_Tcl(contents))
        )
        if self.html.embedded_widget_attr_name in str(contents):
            self.contains_widgets = True
            if self.html.bbox(self.node):  # only bother setting up widgets if visible; won't work otherwise
                self.html.setup_widgets()
        else:
            self.contains_widgets = False

    @property
    def textContent(self):  # Original for this project
        "Get the text content of an element."
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
    def textContent(self, contents):  # Ditto
        "Set the text content of an element."
        self.html.tk.eval("""
            set node %s
            set textnode %s
            if {$textnode eq ""} {error "$node is empty"}
            foreach child [$node children] {
                $child destroy
            }
            $node insert $textnode
            update  ;# This must be done to see changes on-screen
            """ % (extract_nested(self.node), generate_text_node(self.html, contents))
        )

    @property
    def attributes(self):  # attr
        return self.html.get_node_attributes(self.node)

    @property
    def tagName(self):  # attr
        "Return the tag name of the element"
        return self.html.get_node_tag(self.node)

    @property
    def parentElement(self):  # attr
        "Return the element's parent element"
        return HtmlElement(self.html, self.html.get_node_parent(self.node))

    @property
    def children(self):  # attr
        "Return the element's children elements"
        return [HtmlElement(self.html, i) for i in self.html.get_node_children(self.node)]

    def getAttribute(self, attribute):
        "Get the value of the given attribute"
        return self.html.get_node_attribute(self.node, attribute)

    def setAttribute(self, attribute, value):
        "Set the value of the given attribute"
        return self.html.set_node_attribute(self.node, attribute, value)

    def remove(self):
        "Delete the element"
        self.html.delete_node(self.node)

    def appendChild(self, children):
        "Insert the specified children into the element"
        self._insert_children(children)

    def insertBefore(self, children, before):
        "Insert the specified children before a specified child element"
        self._insert_children(children, before)

    def _insert_children(self, children, before=None):  # internal
        "Helper method to insert children at a specified position"
        # Ensure children is a list
        children = children if isinstance(children, list) else [children]
        # Extract node commands
        tkhtml_children_nodes = [i.node for i in children]
        # Insert the nodes based on the position
        if before:
            self.html.insert_node_before(self.node, tkhtml_children_nodes, before.node)
        else:
            self.html.insert_node(self.node, tkhtml_children_nodes)

        # Set up widgets if the element is visible
        if self.html.bbox(self.node):
            if any(node.contains_widgets for node in children):
                self.html.setup_widgets()

    def getElementById(self, query):
        "Return an element given an id"
        newquery = f"[id='{query}']"
        node = self.html.search(newquery, index=0, root=self.node)
        return HtmlElement(self.html, node)

    def getElementsByClassName(self, query):
        "Return a list of elements given a class name"
        newquery = [f".{i}" for i in query.split()]
        nodes = self.html.search(" ".join(newquery), root=self.node)
        return tuple(HtmlElement(self.html, node) for node in nodes)

    def getElementsByName(self, query):
        "Return a list of elements matching a given name attribute"
        newquery = f"[name='{query}']"
        nodes = self.html.search(newquery, root=self.node)
        return tuple(HtmlElement(self.html, node) for node in nodes)

    def getElementsByTagName(self, query):
        "Return a list of elements given a tag name"
        nodes = self.html.search(query, root=self.node)
        return tuple(HtmlElement(self.html, node) for node in nodes)

    def querySelector(self, query):
        "Return the first element that matches a given CSS selector"
        node = self.html.search(query, index=0, root=self.node)
        return HtmlElement(self.html, node)

    def querySelectorAll(self, query):
        "Return a list of elements that match a given CSS selector"
        nodes = self.html.search(query, root=self.node)
        return tuple(HtmlElement(self.html, node) for node in nodes)

