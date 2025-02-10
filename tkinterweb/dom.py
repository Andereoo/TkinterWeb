"""
A thin wrapper on top of bindings.py that offers some JavaScript-like functions 
and converts Tkhtml nodes into Python objects

Some of the Tcl code in this file is borrowed from the Tkhtml/Hv3 project. See the copyright at tkhtml/COPYRIGHT.

Copyright (c) 2025 Andereoo
"""

from utilities import extract_nested


def escape_Tcl(string):
    string = str(string)
    escaped = ""
    special_chars = '"\\$[]'
    for char in string:
        if char in special_chars:
            escaped += "\\"
        escaped += char
    return escaped


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

    @property  # attr
    def body(self):  # Taken from hv3_dom_html.tcl line 161
        "Return the document body element"
        return HtmlElement(
            self.html,
            self.html.tk.eval(f"""set body [lindex [[{self.html} node] children] 1]"""),
        )

    def getElementById(self, query):  # Taken from hv3_dom_html.tcl line 127
        "Return an element given an id"
        node = self.html.tk.eval("""
            set selector [subst -nocommands {[id="%s"]}]
            set node [%s search $selector -index 0]
            if {$node ne ""} { return  $node }
            return null
            """ % (escape_Tcl(query), self.html))
        return HtmlElement(self.html, node)

    def getElementsByClassName(self, query):
        "Return a list of elements given a class name"
        newquery = []
        for classname in query.split():
            if classname.startswith("."):
                newquery.append(classname)
            else:
                newquery.append(f".{classname}")
        nodes = self.html.tk.eval(" ".join(newquery))
        return tuple(HtmlElement(self.html, node) for node in nodes)

    def getElementsByName(self, query):  # Taken from hv3_dom_html.tcl line 110
        "Return a list of elements matching a given name attribute"
        nodes = self.html.tk.eval("""
            set selector [subst -nocommands {[name="%s"]}]
            return search $selector
            """ % (escape_Tcl(query), self.html))
        return tuple(HtmlElement(self.html, node) for node in nodes)

    def getElementsByTagName(self, query):
        "Return a list of elements given a tag name"
        nodes = self.html.search(query)
        return tuple(HtmlElement(self.html, node) for node in nodes)

    def querySelector(self, query):
        "Return the first element that matches a given CSS selector"
        node = self.html.search(query, index=1)
        return HtmlElement(self.html, node)

    def querySelectorAll(self, query):
        "Return a list of elements that match a given CSS selector"
        nodes = self.html.search(query)
        return tuple(HtmlElement(self.html, node) for node in nodes)


class CSSStyleDeclaration:
    def __init__(self, node, htmlwidget):
        self.node = node
        self.html = htmlwidget
        self.style = dict(
            (j.strip() for j in i.split(":")) for i in self.cssText.split(";") if i
        )

    def __getitem__(self, prop):
        return self.style[prop]

    def __setitem__(self, prop, value):
        self.style[prop] = value
        style = "; ".join(f"{p}: {v}" for p, v in self.style.items()) + ";"
        self.html.set_node_attribute(self.node, "style", style)
        self.__getitem__(prop)

    @property
    def cssText(self):
        return self.html.get_node_attribute(self.node, "style")

    @property
    def length(self):
        return len(self.style)


class HtmlElement:
    def __init__(self, htmlwidget, node):
        self.html = htmlwidget
        self.node = node
        self.contains_widgets = False
        self.styleCache = None  # Initialize style as None

    def setup_elem_widgets(self):  # internal
        if self.html.bbox(self.node):  # only bother setting up widgets if visible; otherwise bad things can happen
            for node in children:
                if node.contains_widgets == True:
                    self.html.setup_widgets()
                    break

    @property
    def style(self):
        if self.styleCache is None:  # Lazy loading of style
            self.styleCache = CSSStyleDeclaration(self.node, self.html)
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
        if contents:
            contents = str(contents)
            self.html.tk.eval("""
                set tkw %s
                set node %s
                
                if {[$node tag] eq ""} {error "$node is not an HTMLElement"}

                # Destroy the existing children (and their descendants) of $node.
                set children [$node children]
                $node remove $children
                foreach child $children {
                    $child destroy
                }
                
                set newHtml "%s"
                # Insert the new descendants, created by parsing $newHtml.
                set children [parse_fragment $newHtml]
                $node insert $children
                update  ;# This must be done to see changes on-screen
                """ % (self.html, extract_nested(self.node), escape_Tcl(contents))
            )
            if self.html.embedded_widget_attr_name in contents:
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

    def getAttribute(self, attribute):
        "Get the value of the given attribute"
        return self.html.get_node_attribute(self.node, attribute)

    def setAttribute(self, attribute, value):
        "Set the value of the given attribute"
        return self.html.set_node_attribute(self.node, attribute, value)

    @property
    def tagName(self):  # attr
        "Return the tag name of the element"
        return self.html.get_node_tag(self.node)

    def _style(self, property, value=None):  # attr
        "Get and set the value of the given CSS property"
        if value:
            style = self.html.get_node_attribute(self.node, "style")
            style = dict((j.strip() for j in i.split(":")) for i in style.split(";") if i)
            style[property] = value
            style = "; ".join(": ".join(i) for i in style.items()) + ";"
            return self.html.set_node_attribute(self.node, "style", style)
        else:
            return self.html.get_node_property(self.node, property)

    @property
    def parentElement(self):  # attr
        "Return the element's parent element"
        return HtmlElement(self.html, self.html.get_node_parent(self.node))

    @property
    def children(self):  # attr
        "Return the element's children elements"
        return [HtmlElement(self.html, i) for i in self.html.get_node_children(self.node)]

    def remove(self):
        "Delete the element"
        self.html.delete_node(self.node)

    def appendChild(self, children):
        "Insert the specified children into the element"
        try:
            tkhtml_children_nodes = []
            for node in children:
                tkhtml_children_nodes.append(node.node)
        except TypeError:
            tkhtml_children_nodes = [children.node]
            children = [children]
        self.html.insert_node(self.node, tkhtml_children_nodes)
        self.setup_elem_widgets()

    def insertBefore(self, children, before):
        "Insert the specified children before a specified child element"
        try:
            tkhtml_children_nodes = []
            for node in children:
                tkhtml_children_nodes.append(node.node)
        except TypeError:
            tkhtml_children_nodes = [children.node]
            children = [children]
        self.html.insert_node_before(self.node, tkhtml_children_nodes, before.node)
        self.setup_elem_widgets()

    def querySelector(self, query):
        "Return the first element that matches a given CSS selector"
        node = self.html.search(query, index=1, root=self.node)
        return HtmlElement(self.html, node)

    def querySelectorAll(self, query):
        "Return a list of elements that match a given CSS selector"
        nodes = self.html.search(query, root=self.node)
        return [HtmlElement(self.html, node) for node in nodes]
