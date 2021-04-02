
## *`TkinterWeb.HtmlFrame` Documentation*

## Overview
**The `HtmlFrame` class is a Tkinter frame that provides additional functionality to the [TkinterWeb widget](TKINTERWEB.md).**
It combines the TkinterWeb browser, automatic scrollbars, cursor handling capability, and many convenience methods into one embeddable and easy to use widget. The HtmlFrame widget is also capable of holding Tkinter widgets, which provides the ability to combine Tkinter widgets and HTML elements.

## Usage
**The HtmlFrame widget is extremely easy to use.**

The HtmlFrame widget behaves like any other Tkinter widget. This also means that Tkinter functions such as `grid()`, `destroy()`, or `pack()` work on the HtmlFrame. 

Here is an example:

```
from tkinterweb import HtmlFrame #import the HtmlFrame widget
try:
  import tkinter as tk #python3
except ImportError:
  import Tkinter as tk #python2
root = tk.Tk() #create the Tkinter window

### The important part: create the html widget and attach it to the window
myhtmlframe = HtmlFrame(root) #create HTML browser
myhtmlframe.pack(fill="both", expand=True) #attach the HtmlFrame widget to the parent window

root.mainloop()
```
To load a website, call `myhtmlframe.load_website("www.yourwebsite.com")`

The HtmlFrame widget can also load files and custom HTML code. It also supports clicking on links and handling website titles. In order to use these features, refer to the API refrence below.

## Tips and Tricks
*Changing the title*

It is very easy to handle title changes with the HtmlFrame widget.
To change the title of `root`(see example above) every time the title of a website changes, paste the following code into your script:
```
def change_title(title):
    root.title(title) # change the title
    
myhtmlframe.on_title_change(self.change_title)
```
---
*Link clicks*

Link clicks can also be easily handled.
To follow a link every time it is clicked, use the following: 
```
def load_new_page(url):
    myhtmlframe.load_website(url) #load the new website
    
myhtmlframe.on_link_click(load_new_page)
```
---
*Zooming*

Setting the zoom of the HtmlFrame widget is very easy. This can be used to add accessibility features to your application. To set the zoom to 2x magnification the following can be used: 
```
myhtmlframe.set_zoom(2)
```
To zoom only the text, use `set_fontscale()` instead.

---
*Bindings*

Like any other Tkinter widget, mouse and keyboard events can be bound to the HtmlFrame widget.

An example of the usage of bingings with the HtmlFrame widget can be seen below:
```
def on_right_click(event):
    "Do stuff"
    
myhtmlframe.bind("<Button-3>", on_right_click)
```
The above code will call `on_right_click` every time the user right-clicks on the HtmlFrame widget.
This can be extended with the following:
```
if myhtmlframe.get_currently_hovered_node_tag() == "a": #if the mouse is over a link
    link = myhtmlframe.get_currently_hovered_node_attribute("href") #get the link's url
    menu = tk.Menu(root, tearoff=0) #create the menu
    menu.add_command(label=link) #add a button to the menu showing the url
    menu.tk_popup(event.x_root, event.y_root, 0) #show the menu
```
Putting the above code inside the `on_right_click` function will make a popup show if the user right-clicked on a link. 

---
*Other methods can be found in the [useful methods section](#useful-methods) below.*

---

## Class API 

### HtmlFrame constructors:
* `master` Parent (tkinter widget)
* `messages_enabled` Enable messages (boolean) **Default: True**
* `vertical_scrollbar` Show the vertical scrollbar (True, False, or "auto") **Default: "auto"**
* `horizontal_scrollbar` Show the horizontal scrollbar (True, False, or "auto)" **Default: False**
* `**kw` Other optional `ttk.Frame` arguments

### Useful Methods:

---
#### **load_website**(website_url, base_url=None, decode=None)
Loads and parses a website.

Parameters
* **website_url** *(string)* - Specifies the url to load
* **base_url** *(string)* - Specifies the base url to use when parsing stylesheets and images. If `base_url` is not supplied, it will be automatically generated.
* **decode** *(string)* - Specifies the decoding to use when loading the website

---

#### **load_file**(file_url, base_url=None, decode=None)
Loads and parses a local HTML file.

Parameters
* **file_url** *(string)* - Specifies the file to load
* **base_url** *(string)* - Specifies the base url to use when parsing stylesheets and images. If `base_url` is not supplied, it will be automatically generated.
* **decode** *(string)* - Specifies the decoding to use when loading the file

---
#### **load_url**(url, base_url=None, decode=None)
Loads and parses html from the given url. A local file will be loaded if the url begins with "file://". If the url begins with "https://" or "http://", a website will be loaded. 

Parameters
* **url** *(string)* - Specifies the url to load
* **base_url** *(string)* - Specifies the base url to use when parsing stylesheets and images. If `base_url` is not supplied, it will be automatically generated.
* **decode** *(string)* - Specifies the decoding to use when loading the website

---
#### **load_html**(html_source, base_url="")
Parses the supplied HTML code.

Parameters
* **html_source** *(string)* - Specifies the HTML code
* **base_url** *(string)* - Specifies the base url to use when parsing stylesheets and images.

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
#### **on_title_change**(function)
Set TkinterWeb to call the specified python function whenever the title of a website or file has changed.
When the title of a webpage changes, a variable containing the new title will be passed to the specified function.

Parameters
* **function** *(python function)* - Specifies the function to call when a title changes.

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
#### **set_message_func**(function)
Set TkinterWeb to call the specified python function whenever a new message is released.
By default, unless `messages_enabled` was set to `False` when calling `HtmlFrame()`, messages will be printed to the console.
After calling `set_message_func`, whenever a new message is released, a variable containing the main message and a second variable containing more information will be passed to the specified function.

Parameters
* **function** *(python function)* - Specifies the function to call when a message is released.

---
#### **set_broken_webpage_message**(html)
Set the HTML code to be displayed when a webpage cannot be reached.

Parameters
* **html** *(string)* - Specifies the HTML to be parsed when an invalid url is requested. Must be valid HTML code.

---
#### **set_broken_file_message**(html)
Set the HTML code to be displayed when a file cannot be reached.

Parameters
* **html** *(string)* - Specifies the HTML to be parsed when an invalid file is requested. Must be valid HTML code.

---
#### **set_recursive_hover_depth**(depth)
When a mouse hovers over an element in a webpage, the element under the mouse is flagged as hovered.
TkinterWeb then marks the parent of that element repeatedly, up to the 15th degree. This works fine for most websites, but may cause a few websites to lag slightly. If this is becoming an issue, simply call `set_recursive_hover_depth` and set the *depth* to a smaller integer.

Parameters
* **depth** *(integer)* - Specifies the number of recursions to apply the hover flag to.

---
#### **add_visited_links**(links)
TkinterWeb stores a list of visited websites to determine whether a link on a webpage should be flagged as visited or not visited.
The method add_visited_links enables adding new custom urls to this list. 

Parameters
* **links** *(string or list)* - Specifies the url(s) to be added to the list of visited websites.

---
#### **clear_visited_links**()
Clear the list of visited websites.

---
#### **enable_stylesheets**(isenabled=True)
Enable or disable CSS styling.
This method must be invoked *before* loading a webpage to take effect.

Parameters
* **isenabled** *(boolean)* - Specifies whether stylesheets are enabled or not.

---
#### **enable_images**(isenabled=True)
Enable or disable image loading.
This method must be invoked *before* loading a webpage to take effect.

Parameters
* **isenabled** *(boolean)* - Specifies whether images should or should not be loaded.

---
#### **get_currently_hovered_node_tag**()
Get the tag of the HTML element the mouse is currently over.
For example, if the mouse is hovering over a heading, `get_currently_hovered_node_tag()` would return "h1".

Return type
* *string*

---
#### **get_currently_hovered_node_text**()
Get the text content of the HTML element the mouse is currently over.

Return type
* *string*
---
#### **get_currently_hovered_node_attribute**(attribute)
Get the specified attribute of the HTML element the mouse is currently over.
For example, if the mouse is over a link to python.org, `get_currently_hovered_node_attribute("href")` would return "python.org".
If the current element does not have the specified attribute, an empty string is returned.

Parameters
* **attribute** *(boolean)* - Specifies the attribute

Return type
* *string*

---
#### **get_currently_selected_text**()
Get the text content that is currently highlighted/selected in the HtmlFrame.

Return type
* *string*

---

