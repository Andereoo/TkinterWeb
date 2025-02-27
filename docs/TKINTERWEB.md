## *`tkinterweb.TkinterWeb` Documentation*

## Overview
**The `TkinterWeb` class is the low-level widget that bridges the gap between the underlying Tkhtml3 widget and Tkinter. It provides the basic functionality nessessary for accessing Tkhtml3 from Python scripts.**

## Usage
**Because the main purpose of the TkinterWeb widget is simply to call Tkhtml3 functions, using this widget is not particularily straightfoward and is missing functionality.**
**Do not use this widget unless absolutely nessessary. Instead use the [HtmlFrame widget](HTMLFRAME.md).**


This API reference is provided becasue the HtmlFrame and HtmlLabel widgets are built on top of the TkinterWeb widget. This widget widget can be accessed through the `html` property of the HtmlFrame and HtmlLabel widgets to access underlying settings and commands that are not a part of the HtmlFrame API.

## Class API 

### TkinterWeb constructors:
* `master` Parent (tkinter widget)
* `tkinterweb_options` Configuration details to be used when setting the widget's settings **Default: {}**
* `**kw` Other optional configuration details to be passed to the Tkhtml engine

### Widget settings variables:
*The following is a subset of the variables that can be changed to alter the behaviour of the TkinterWeb widget. Please refer to the [source code](../tkinterweb/bindings.py) for more details.*
```
caches_enabled = True
dark_theme_enabled = False
image_inversion_enabled = False
crash_prevention_enabled = True
messages_enabled = True
events_enabled = True   
selection_enabled = True
stylesheets_enabled = True
images_enabled = True
forms_enabled = True
objects_enabled = True
ignore_invalid_images = True
image_alternate_text_enabled = True
overflow_scroll_frame = None
default_style = None
dark_style = None
use_prebuilt_tkhtml = True
experimental = False
image_alternate_text_font = get_alt_font()
image_alternate_text_size = 14
image_alternate_text_threshold = 10
find_match_highlight_color = "#ef0fff"
find_match_text_color = "#fff"
find_current_highlight_color = "#38d878"
find_current_text_color = "#fff"
selected_text_highlight_color = "#3584e4"
selected_text_color = "#fff"
visited_links = []
embed_obj = None
manage_vsb_func = placeholder
manage_hsb_func = placeholder
message_func = placeholder
on_link_click = placeholder
on_form_submit = placeholder
on_script = placeholder
recursive_hovering_count = 10
maximum_thread_count = 20
insecure_https = False
headers = {}
dark_theme_limit = 160
style_dark_theme_regex = r"([^:;\s{]+)\s?:\s?([^;{!]+)(?=!|;|})"
general_dark_theme_regexes = [r'(<[^>]+bgcolor=")([^"]*)',r'(<[^>]+text=")([^"]*)',r'(<[^>]+link=")([^"]*)']
inline_dark_theme_regexes = [r'(<[^>]+style=")([^"]*)', r'([a-zA-Z-]+:)([^;]*)']
```

### Useful Methods:
*The following is a subset of the functions provided by the TkinterWeb widget. Please refer to the [source code](../tkinterweb/bindings.py) for more details.*

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
#### `destroy_node(node_handle)`
Destroy the given node and remove it from memory.

---
#### `find_text(searchtext, select, ignore_case, highlight_all)`       
Search for and highlight specific text in the document.

---
#### `get_computed_styles()`
Get a tuple containing the computed CSS rules for each CSS selector

---
#### `get_current_node(event)`
Get the node below the mouse cursor.

---
#### `get_current_node_parent(node)`
Get the parent of the given node and clean the output.

---
#### `get_node_attribute(node_handle, attribute, default='', value=None)`
Get the value of a specified attribute of the given node. If provided, the value of the specified attribute will be set to `value`.

---
#### `get_node_attributes(node_handle)`
Get the attributes of the given node.

---
#### `get_node_children(node_handle)`
Get the children of the given node.

---
#### `get_node_parent(node_handle)`
Get the parent of the given node.

---
#### `get_node_properties(node_handle)`
Get the calculated values of a node's CSS properties. If the node is a text node, return the values of the properties as assigned to the parent node.

---
#### `get_node_property(node_handle, node_property)`
Get the calculated value of a node's CSS property. If the node is a text node, return the value of the property as assigned to the parent node.

---
#### `get_node_tag(node_handle)`
Get the HTML tag of the given node.

---
#### `get_node_text(node_handle)`
Get the text content of the given node.

---
#### `get_selection(self)`
Return the current selection.

---
#### `image(full=False)`
Return the name of a new Tk image containing the rendered document.
The returned image should be deleted when the script has finished with it.
Note that this command is mainly intended for automated testing.
Be wary of running this command on large documents.
Does not work on Windows unless experimental Tkhtml is used.

---
#### `insert_node(node_handle, child_nodes)`
Experimental, insert the specified nodes into the parent node.

---
#### `insert_node_before(node_handle, child_nodes, before)`
Same as the last one except node is placed before another node.

---
#### `node(*args)`
Retrieve one or more document  node handles from the current document.       

---
#### `override_node_properties(self, node_handle, *props)`
Get/set the CSS property override list

---
#### `parse(html)`
Parse HTML code.

---
#### `parse_css(sheetid=None, importcmd=None, data='')`
Parse CSS code.

---
#### `parse_fragment(html)`
Parse part of a document comprised of nodes just like a standard document, except that the document fragment isn't part of the active document. Changes made to the fragment don't affect the document. Returns a root node.

---
#### `postscript(cnf={}, **kwargs)`
Print the contents of the canvas to a postscript file.
Valid options: colormap, colormode, file, fontmap, height, 
pageanchor, pageheight, pagesize, pagewidth, pagex, pagey, 
nobg, noimages, rotate, width, x, and y.
Does not work unless experimental Tkhtml is used.

---
#### `preload_image(url)`
Preload an image. 
Only useful if caches are enabled and reset() is not called after preloading.

---
#### `register_handler(handler_type, node_tag, callback)`
Register a node or script handler. The callback will be executed when the node is being rendered.

---
#### `remove_node_flags(node, name)`
Set dynamic flags on the given node.

---
#### `remove_widget(widgetid)`
Remove a stored widget.

---
#### `replace_element(selector, widgetid)`
Replace an HTML element with a widget.

---
#### `replace_widget(widgetid, newwidgetid)`
Replace a stored widget.

---
#### `reset()`
Reset the widget.

---
#### `resolve_url(href)`
Get full url from partial url.

---
#### `search(selector, cnf={}, **kw)`
Search the document for the specified CSS selector; return a TkHTML-3 node if found.
	-root NODE	Search the sub-tree at NODE
	-index IDX	return the idx'th list entry only
	-length		return the length of the result only
The -index and -length options are mutually exclusive.

---
#### `select_all()`
Select all of the text in the document.

---
#### `set_node_flags(node, name)`
Set dynamic flags on the given node.

---
#### `set_node_text(mode)`
Set the text content of the given text node.

---
#### `stop()`
Stop loading resources.

---
#### `tag(subcommand, tag_name, *args)`
Return the name of the HTML tag that generated this document node, or an empty string if the node is a text node.

---
#### `text(*args)`
Enable interaction with the text of the HTML document.

---
#### `update_default_style()`
Update the default stylesheet based on color theme.

---
### `update_tags()`
Update selection and find tag colors.

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
