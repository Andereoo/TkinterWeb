
## *`tkinterweb.HtmlLabel` Documentation*

## Overview
**The `HtmlLabel` class is a Tkinter widget that displays styled HTML in a label-like widget.**

## Usage
**The HtmlLabel widget is very easy to use.**

Here is an example:

```
import tkinter as tk
from tkinterweb import HtmlLabel #import the HtmlLabel widget

root = tk.Tk() #create the Tkinter window

### The important part: create the html widget and attach it to the window
myhtmllabel = HtmlLabel(root, text='<b style="color:blue">Wow! Tkinter Labels can actually show HTML!</b>') # create the label

myhtmllabel.pack() # attach the HtmlLabel widget to the window

root.mainloop()
```
HTML can also be loaded using the `load_html` command to change the content of the label on demand.


## Class API 

### HtmlLabel constructors:
* `master` Parent (tkinter widget)
* `text` Set the content of the widget (string) **Default: ""**
* `messages_enabled` Enable messages (boolean) **Default: False**
* `**kw` Other optional `HtmlFrame` arguments


### Useful Methods:
#### `load_html(html_source, base_url="")`
Parses the supplied HTML code.

Parameters
* **html_source** *(string)* - Specifies the HTML code
* **base_url** *(string)* - Specifies the base url to use when parsing stylesheets and images. If this argument is not supplied, it will be set to the current working directory.

---
#### `on_link_click(function)`
Set TkinterWeb to call the specified python function whenever a link is clicked.
When a link is clicked on a webpage, a variable containing the url of the clicked link will be passed to the specified function.

Parameters
* **function** *(python function)* - Specifies the function to call when a link is clicked.

---
#### `set_zoom(multiplier)`
Set the zoom multiplier of the document.

Parameters
* **multiplier** *(float or integer)* - Specifies the zoom multiplier.

---

All HtmlFrame methods can also be used on the HtmlLabel widget. For a complete list of avaliable methods, see the [HtmlFrame docs](HTMLFRAME.md#useful-methods).
