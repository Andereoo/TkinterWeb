
## *`TkinterWeb.HtmlLabel` Documentation*

## Overview
**The `HtmlLabel` class is a Tkinter widget that provides HTML parsing abilities to a label-like widget.**
It behaves as a Tkinter Label widget, but allows for displaying HTML documents and rich text.

## Usage
**The HtmlLabel widget is extremely easy to use.**

Here is an example:

```
from tkinterweb import HtmlLabel #import the HtmlLabel widget
try:
  import tkinter as tk #python3
except ImportError:
  import Tkinter as tk #python2
root = tk.Tk() #create the Tkinter window

### The important part: create the html widget and attach it to the window
myhtmllabel = HtmlLabel(root, text="<b style="color:blue">Wow! Tkinter Labels can actually show HTML!</b>") #create the label

myhtmllabel.pack() #attach the HtmlLabel widget to the parent window

root.mainloop()
```
HTML can also be loaded using the `load_html` command to dynamically change the content of the label.


## Class API 

### HtmlFrame constructors:
* `master` Parent (tkinter widget)
* `text` Set the content of the widget (string) **Default: ""**
* `messages_enabled` Enable messages (boolean) **Default: True**
* `**kw` Other optional `ttk.Frame` arguments


### Useful Methods:

---
#### **load_html**(html_source, base_url="")
Parses the supplied HTML code. If the 

Parameters
* **html_source** *(string)* - Specifies the HTML code
* **base_url** *(string)* - Specifies the base url to use when parsing stylesheets and images. If this argument is not supplied, it will be set as the location of your script. 

---
#### **add_html**(html_source)
Send HTML code to the parser.
Unlike `load_html`, `add_html` parses the specified HTML code and adds it to the end of the webpage without clearing the original document.

Parameters
* **html_source** *(string)* - Specifies the code to parse and add to the end of the document. Must be valid HTML code.

---
#### **add_css**(css_source)
Send CSS stylesheets to the parser.
This can be used to remotely alter the appearance of websites.

Parameters
* **css_source** *(string)* - Specifies the code to parse. Must be valid CSS code.

---
#### **on_link_click**(function)
Set TkinterWeb to call the specified python function whenever a link is clicked.
When a link is clicked on a webpage, a variable containing the url of the clicked link will be passed to the specified function.

Parameters
* **function** *(python function)* - Specifies the function to call when a link is clicked.

---
#### **set_zoom**(multiplier)
Set the zoom multiplier of the document.

Parameters
* **multiplier** *(float or integer)* - Specifies the zoom multiplier.

---
#### **get_zoom**()
Return the zoom multiplier of the document.

Return type
* *float*

---
#### **set_fontscale**(multiplier)
Set the zoom multiplier of the document's text.

Parameters
* **multiplier** *(float or integer)* - Specifies the fontscale multiplier.

---
#### **get_fontscale**()
Return the zoom multiplier of the document's text.

Return type
* *float*

---

