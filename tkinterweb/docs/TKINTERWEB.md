## *`TkinterWeb.TkinterWeb` Documentation*

## Overview
**The `TkinterWeb` class is the low-level widget that bridges the gap between the underlying Tcl Tkhtml3 widget and Tkinter. It provides the basic functionality nessessary for accessing Tkhtml3 from Python scripts.**

## Usage
**Because the main purpose of the TkinterWeb widget is simply to call Tkhtml3 functions, using this widget is not particularily straightfoward and is missing a lot of functionality.**
**Do not use this widget unless absolutely nessessary. Instead use the [HtmlFrame widget](HTMLFRAME.md).**


The HtmlFrame widget is built on top of this widget, so variables and functions in this API can be called from the HtmlFrame via `yourhtmlframe.html.variableorfunction`. This enables access to underlying settings and commands that are not a part of the HtmlFrame API.

---

## Class API 

### TkinterWeb constructors:
* `master` Parent (tkinter widget)
* `message_func` Function to be used when writing debug messages (boolean)
* `embed_obj` Object to be used for embedded content. Generally, it is best to set this to HtmlFrame.
* `scroll_overflow` Allow scoll overflowing **Default: True**
* `cfg` Configuration details to be passed to the Tkhtml engine **Default: {}**
* `**kw` Other optional arguments

### Widget settings variables:
*The following are the major variables that can be changed to alter the behaviour of the TkinterWeb widget. Please refer to the [source code](../bindings.py) for more details.*
```
stylesheets_enabled = True
images_enabled = True
forms_enabled = True
caches_enabled = True
objects_enabled = True
ignore_invalid_images = True
prevent_crashes = True
dark_theme_enabled = False
image_inversion_enabled = False
base_url = ""
recursive_hovering_count = 10
max_thread_count = 20
find_match_highlight_color = "#ef0fff"
find_match_text_color = "#fff"
find_current_highlight_color = "#38d878"
find_current_text_color = "#fff"
selected_text_highlight_color = "#3584e4"
selected_text_color = "#fff"
visited_links = []
title_change_func = self.placeholder
icon_change_func = self.placeholder
cursor_change_func = self.placeholder
link_click_func = self.placeholder
form_submit_func = self.placeholder
done_loading_func = self.placeholder
downloading_resource_func = self.placeholder
 ```

### Useful Methods:
*This is a subset of the functions provided by the TkinterWeb widget. Please refer to the [source code](../bindings.py) for more details.*

---
#### `clear_selection()`
Clear the current selection.

---
#### `copy_selection(event=None)`
Copy the selected text to the clipboard.

---
#### `delete_node(node_handle)`
Delete the given node.

---
#### `find_text(searchtext, select, ignore_case, highlight_all)`       
Search for and highlight specific text in the document.

---
#### `generate_altered_colour(match)`
Invert document colours. Highly experimental.

---
#### `get_current_node(event)`
Get the node below the mouse cursor.

---
#### `get_current_node_parent(node)`
Get the parent of the given node and clean the output.

---
#### `get_fontscale(multiplier)`
Return the font zoom.

---
#### `get_node_attribute(node_handle, attribute, default='', value=None)`
Get the value of a specified attribute of the given node. If provided, the value of the specified attribute will be set to `value`.

---
#### `get_node_children(node_handle)`
Get the children of the given node.

---
#### `get_node_parent(node_handle)`
Get the parent of the given node.

---
#### `get_node_property(node_handle, node_property)`
Get the specified property of the given node.

---
#### `get_node_tag(node_handle)`
Get the HTML tag of the given node.

---
#### `get_node_text(node_handle)`
Get the text content of the given node.

---
#### `get_parsemode(self)`
Return the page render mode.

---
#### `get_selection(self)`
Return the current selection.

---
#### `get_zoom(self)`
Return the page zoom.

---
#### `insert_node(node_handle, children_nodes)`
Experimental, insert the specified nodes into the parent node.

---
#### `insert_node_before(node_handle, children_nodes, before)`
Same as the last one except node is placed before another node.

---
#### `node(*args)`
Retrieve one or more document  node handles from the current document.       

---
#### `on_mouse_motion(event)`
Set hover flags and handle the CSS 'cursor' property.

---
#### `parse(html)`
Parse HTML code.

---
#### `parse_css(sheetid=None, importcmd=None, data='')`
Parse CSS code.

---
#### `parse_fragment(html)`
Part of a document comprised of nodes just like a standard document difference is that the document fragment isn't part of the active document. Changes made to the fragment don't affect the document. Returns a root node.

---
#### `remove_node_flags(node, name)`
Set dynamic flags on the given node.

---
#### `remove_widget(widgetid)`
Remove a stored widget.

---
#### `replace_html(selector, widgetid)`
Replace an HTML element with a widget.

---
#### `replace_widget(widgetid, newwidgetid)`
Replace a stored widget.

---
#### `reset(self)`
Reset the widget.

---
#### `resolve_url(href)`
Get full url from partial url.

---
#### `search(selector)`
Search the document for the specified CSS  selector; return a Tkhtml3 node if found.

---
#### `select_all(self)`
Select all of the text in the document.

---
#### `set_fontscale(multiplier)`
Set the font zoom.

---
#### `set_node_flags(node, name)`
Set dynamic flags on the given node.

---
#### `set_parsemode(mode)`
Set the page render mode.

---
#### `set_node_text(mode)`
Set the text content of the given node.

---
#### `set_zoom(multiplier)`
Set the page zoom.

---
#### `shrink(value)`
Set shrink value for html widget.

---
#### `stop(self)`
Stop loading resources.

---
#### `tag(subcommand, tag_name, *args)`
Return the name of the HTML tag that generated this document node, or an empty string if the node is a text node.

---
#### `text(*args)`
Enable interaction with the text of the HTML document.

---
#### `update_default_style(stylesheet=None)`
Update the default stylesheet based on color theme.

---
#### `xview(*args)`
Used to control horizontal scrolling.

---
#### `xview_moveto(number)`
Shifts the view horizontally to the specified position.

---
#### `xview_scroll(number, what)`
Shifts the view in the window left or right, according to number and  what. "number" is an integer, and "what" is either "units" or "pages".

---
#### `yview(*args)`
Used to control the vertical position of the document.

---
#### `yview_moveto(number)`
Shifts the view vertically to the specified position.

---
#### `yview_scroll(number, what)`
Shifts the view in the window up or down, according to number and  what. "number" is an integer, and "what" is either "units" or "pages".

---
