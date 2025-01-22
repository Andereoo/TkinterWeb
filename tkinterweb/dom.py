"""
TkinterWeb v3.24
This is a wrapper for the Tkhtml3 widget from http://tkhtml.tcl.tk/tkhtml.html, 
which displays styled HTML documents in Tkinter.

Copyright (c) 2025 Andereoo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

"""
Some of this code is borrowed from the Hv3 project. Thanks!
"""

class TkwDocumentObjectModel:
    def __init__(self, htmlwidget):
        self.tk = htmlwidget.tk
        self.html = htmlwidget.html

        self.html.tk.createcommand("node_to_html", self.node_to_html)
        self.html.tk.createcommand("text_content_get", self.text_content)

    def node_to_html(self, node, isDeep=True):
        return self.tk.eval(r"""
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
            """ % (isDeep, self.extract_nested(node))
        )

    def get_inner_html(self, node):
        return self.tk.eval("""
            set node %s
            if {[$node tag] eq ""} {error "$node is not an HTMLElement"}

            set ret ""
            foreach child [$node children] {
                append ret [node_to_html $child 1]
            }
            update
            return $ret
            """ % self.extract_nested(node)
        )

    def set_inner_html(self, node, new):
        self.tk.eval("""
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
            set children [$tkw fragment $newHtml]
            $node insert $children

            $tkw configure -parsemode $oldmode
            update
            """ % (self.html, self.extract_nested(node), self.escape_Tcl(new))
        )

    def create_element(self, tagname):
        return self.tk.eval("""
            set node [%s fragment "<%s>"]
            if {$node eq ""} {error "DOMException NOT_SUPPORTED_ERR"}
            return $node
            """ % (self.html, tagname)
        )

    def create_text_node(self, text):
        return self.tk.eval("""
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
                set node [$tkw fragment $escaped]
            }
            return $node
            """ % (self.html, self.escape_Tcl(text))
        )

    def text_content(self, node, text=None):
        return self.tk.eval("""
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
            """ % (self.extract_nested(node), self.create_text_node(text) if text else '""')
        )

    def body(self):
        return self.tk.eval(f"""set body [lindex [[{self.html} node] children] 1]""")
    
    def extract_nested(self, nested):
        if isinstance(nested, tuple) and len(nested):
            return self.extract_nested(nested[0])
        return nested


    def escape_Tcl(self, string):
        string = str(string)
        escaped = ""
        special_chars = '"\\$[]'
        for char in string:
            if char in special_chars: escaped += "\\"
            escaped += char
        return escaped

