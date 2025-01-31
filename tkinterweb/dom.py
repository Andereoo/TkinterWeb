"""
A thin wrapper on top of bindings.py that offers some JavaScript-like functions 
and converts Tkhtml nodes into Python objects

Some of the Tcl code in this file is borrowed from the Tkhtml/Hv3 project. See the copyright at tkhtml/COPYRIGHT.

Copyright (c) 2025 Andereoo
"""


def extract_nested(nested):
    if isinstance(nested, tuple) and len(nested):
        return extract_nested(nested[0])
    return nested


def escape_Tcl(string):
    string = str(string)
    escaped = ""
    special_chars = '"\\$[]'
    for char in string:
        if char in special_chars:
            escaped += "\\"
        escaped += char
    return escaped


def generate_text_node(htmlwidget, text):
    return htmlwidget.tk.eval(
        """
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
        """
        % (htmlwidget, escape_Tcl(text))
    )


class TkwDocumentObjectModel:
    def __init__(self, htmlwidget):
        self.html = htmlwidget
        self.html.tk.createcommand("parse_fragment", self.html.parse_fragment)

    def createElement(self, tagname):
        "Create a new HTML element with the given tag name"
        return HtmlElement(
            self.html,
            self.html.tk.eval(
            """
            set node [%s fragment "<%s>"]
            if {$node eq ""} {error "DOMException NOT_SUPPORTED_ERR"}
            return $node
            """
                % (self.html, tagname)
            ),
        )

    def createTextNode(self, text):
        "Create a new text node with the given text conent"
        return HtmlElement(self.html, generate_text_node(self.html, text))

    def body(self):  # attr
        "Return the document body element"
        return HtmlElement(
            self.html,
            self.html.tk.eval(f"""set body [lindex [[{self.html} node] children] 1]"""),
        )

    def getElementById(self, query):
        "Return an element given an id"
        if not query.startswith("#"):
            query = f"#{query}"
        node = self.html.search(query)
        return HtmlElement(self.html, node)

    def getElementsByClassName(self, query):
        "Return a list of elements given a class name"
        newquery = []
        for classname in query.split():
            if classname.startswith("."):
                newquery.append(classname)
            else:
                newquery.append(f".{classname}")
        nodes = self.html.search(" ".join(newquery))
        return [HtmlElement(self.html, node) for node in nodes]

    def getElementsByName(self, query):
        "Return a list of elements matching a given name attribute"
        newquery = []
        for classname in query.split():
            if classname.startswith("[name=") and classname.endswith("]"):
                newquery.append(classname)
            else:
                newquery.append(f"[name={classname}]")
        nodes = self.html.search(" ".join(newquery))
        return [HtmlElement(self.html, node) for node in nodes]

    def getElementsByTagName(self, query):
        "Return a list of elements given a tag name"
        nodes = self.html.search(query)
        return [HtmlElement(self.html, node) for node in nodes]

    def querySelector(self, query):
        "Return the first element that matches a given CSS selector"
        node = self.html.search(query)
        return HtmlElement(self.html, node)

    def querySelectorAll(self, query):
        "Return a list of elements that match a given CSS selector"
        nodes = self.html.search(query)
        return [HtmlElement(self.html, node) for node in nodes]


class HtmlElement:
    def __init__(self, htmlwidget, node):
        self.html = htmlwidget
        self.node = node
        self.contains_widgets = False

        self.html.tk.createcommand("node_to_html", self.node_to_html)
        self.html.tk.createcommand("text_content_get", self.textContent)
        self.html.tk.createcommand("parse_fragment", self.html.parse_fragment)

    def node_to_html(self, node, deep=True):  # internal
        return self.html.tk.eval(
            r"""
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
                    if {%s} {
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
            """
            % (deep, extract_nested(node))
        )

    def find_nested_children(self, node):  # internal
        children = []
        for child in self.html.get_node_children(node):
            children.append(HtmlElement(self.html, child))
            children += self.find_nested_children(child)
        return children

    def innerHTML(self, contents=None):  # attr
        "Get and set the inner HTML of an element"
        if contents:
            self.html.tk.eval(
                """
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
                set oldmode [$tkw cget -parsemode]
                $tkw configure -parsemode html
                # Insert the new descendants, created by parseing $newHtml.
                set children [parse_fragment $newHtml]
                $node insert $children

                $tkw configure -parsemode $oldmode
                update
                """
                % (self.html, extract_nested(self.node), escape_Tcl(contents))
            )
            if self.html.embedded_widget_attr_name in contents:
                self.contains_widgets = True
                if self.html.bbox(
                    self.node
                ):  # only bother setting up widgets if visible; won't work otherwise
                    self.html.setup_widgets()
            else:
                self.contains_widgets = False
        else:
            return self.html.tk.eval(
                """
                set node %s
                if {[$node tag] eq ""} {error "$node is not an HTMLElement"}

                set ret ""
                foreach child [$node children] {
                    append ret [node_to_html $child 1]
                }
                update
                return $ret
                """
                % extract_nested(self.node)
            )

    def textContent(self, contents=None):  # attr
        "Get and set the text content of an element"
        return self.html.tk.eval(
            """
            proc get_child_text {node} {
                set t ""
                foreach child [$node children] {
                    if {[$child tag] eq ""} {
                        append t [$child text -pre]
                    } else {
                        append t [get_child_text $child]
                    }
                }
                return $t
            }
            set node %s
            if {$node eq ""} {error "DOMException NOT_SUPPORTED_ERR"}
            set textnode %s
            if {$textnode ne ""} {
                foreach child [$node children] {
                    $child destroy
                }
                $node insert $textnode
            } else {
                return [get_child_text $node]
            }
            """
            % (extract_nested(self.node), generate_text_node(self.html, contents) if contents else '""')
        )

    def getAttribute(self, attribute):
        "Get the value of the given attribute"
        return self.html.get_node_attribute(self.node, attribute)

    def setAttribute(self, attribute, value):
        "Set the value of the given attribute"
        return self.html.set_node_attribute(self.node, attribute, value)

    def tagName(self):  # attr
        "Return the tag name of the element"
        return self.html.get_node_tag(self.node)

    def style(self, property, value=None):  # attr
        "Get and set the value of the given CSS property"
        if value:
            styles = self.html.get_node_attribute(self.node, "style")
            newstyles = []
            if styles:
                styles = styles.split(";")
                for style in styles:
                    style = style.strip()
                    parts = style.split(":")
                    if style and parts[0] != property:
                        newstyles.append(style)
                newstyles.append(f"{property}:{value}")
            else:
                newstyles = [f"{property}:{value}"]
            return self.html.set_node_attribute(
                self.node, "style", "; ".join(newstyles)
            )
        else:
            return self.html.get_node_property(self.node, property)

    def parentElement(self):  # attr
        "Return the element's parent element"
        return HtmlElement(self.html, self.html.get_node_parent(self.node))

    def children(self, deep=True):  # attr
        "Return the element's children elements"
        if deep:
            return self.find_nested_children(self.node)
        else:
            return [
                HtmlElement(self.html, child)
                for child in self.html.get_node_children(self.node)
            ]

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

        # only bother setting up widgets if visible; otherwise bad things can happen
        if self.html.bbox(self.node):  
            for node in children:
                if node.contains_widgets == True:
                    self.html.setup_widgets()
                    break

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
        if self.html.bbox(self.node):  # only bother setting up widgets if visible; won't work otherwise
            for node in children:
                if node.contains_widgets == True:
                    self.html.setup_widgets()
                    break