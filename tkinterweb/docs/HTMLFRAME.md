
## *`TkinterWeb.HtmlFrame` Documentation*

## Overview
**The `HtmlFrame` class is a Tkinter frame that provides additional functionality to the [TkinterWeb widget](TKINTERWEB.md).**

It combines the TkinterWeb browser, automatic scrollbars, cursor handling capability, and many convenience methods into one embeddable and easy to use widget. The HtmlFrame widget is also capable of holding Tkinter widgets, which provides the ability to combine Tkinter widgets and HTML elements.

## Usage
**The HtmlFrame widget is extremely easy to use.**

The HtmlFrame widget behaves like any other Tkinter widget. This also means that Tkinter functions such as `grid()`, `destroy()`, or `pack()` work on the HtmlFrame. 

Tkinter bindings (such as right-clicks or keyboard presses) can also be used on the HtmlFrame. See [Tips and Tricks](https://github.com/Andereoo/TkinterWeb/blob/main/tkinterweb/docs/HTMLFRAME.md#tips-and-tricks) below for more information.

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
myhtmlframe.load_html("<h1>Hello, World!</h1>") #Load some HTML code
myhtmlframe.pack(fill="both", expand=True) #attach the HtmlFrame widget to the parent window

root.mainloop()
```
To load a website, call `myhtmlframe.load_website("www.yourwebsite.com")`

The HtmlFrame widget can also load files and custom HTML code. It also supports clicking on links, submitting forms, and handling website titles. In order to use these features, refer to the API refrence below.

## Tips and Tricks
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
def on_right_click(event):
  url = myhtmlframe.get_current_link(resolve=True) #get the current link
  if url: #if mouse was clicked on a link
      menu = tk.Menu(root, tearoff=0) #create the menu
      menu.add_command(label="Open %s" % url, command=lambda url=url: myhtmlframe.load_url(url)) #add a button to the menu showing the url
      menu.tk_popup(event.x_root, event.y_root, 0) #show the menu
myhtmlframe.bind("<Button-3>", on_right_click)
```
This will make a popup show if the user right-clicked on a link. Clicking link shown in the popup would load the website.

Similarly, bindings can also be applied to navigation keys:  
```
  myhtmlframe.bind_all("<Up>", lambda e: myhtmlframe.html.yview_scroll(-5, "units"))
  myhtmlframe.bind_all("<Down>", lambda e: myhtmlframe.html.yview_scroll(5, "units"))
  myhtmlframe.bind_all("<Prior>", lambda e: myhtmlframe.html.yview_scroll(-1, "pages"))
  myhtmlframe.bind_all("<Next>", lambda e: myhtmlframe.html.yview_scroll(1, "pages"))
  myhtmlframe.bind_all("<Home>", lambda e: myhtmlframe.html.yview_moveto(0))
  myhtmlframe.bind_all("<End>", lambda e: myhtmlframe.html.yview_moveto(1))
```

---
*Changing the title*

It is very easy to handle title changes with the HtmlFrame widget.
To change the title of `root`(see example above) every time the title of a website changes, use the following:
```
def change_title(title):
    root.title(title) # change the title
    
myhtmlframe.on_title_change(change_title)
```
Similarily, `on_icon_change` can be used to get the website's icon when it is loaded.

---
*Url changes*

Normally, a website's url may change when it is loaded. For example, `www.github.com` will redirect to `https://github.com`. This can be handled with `on_url_change`:

```
def url_changed(url):
    # do something, such as change the text an a url-bar
    
myhtmlframe.on_url_change(url_changed)
```
It is highly recomended to use this method to change the text in a url-bar, for example, instead of changing the text when a page is loaded at first. This method will handle page redirects, and url changes when stopping loading page.


---
*Search the page*

Searching the page for specific text is very straightfoward. To search the document for the word 'python', for example, the following may be used:
```
number_of_matches = myhtmlframe.find_text("python")
```
Refer to the API reference for more information and [Bug 18](https://github.com/Andereoo/TkinterWeb/issues/18#issuecomment-881649007) for sample code.

---
*Done loading?*

The method `on_done_loading` can be used to do something when the document is done loading. 

When using `on_done_loading` to, for example, change the 'stop' button to a 'refresh' button, it is generally a good idea to use `on_downloading_resource` to do the opposite. Otherwise, the document may show that is is done loading while it is still loading.

---
*Stop loading*

The method `stop()` can be used to stop loading a webpage. Likewise, the `force=True` parameter can be passed to `load_url`, `load_website`, or `load_file` to mimic a page refresh. Refer to the API refrence below for more information.

---
*Link clicks*

Link clicks can also be easily handled. By default, when a link is clicked, it will be automatically loaded.
To run some code before loading the new website, use the following: 
```
def load_new_page(url):
    ## Do stuff - insert code here
    myhtmlframe.load_url(url) #load the new website
    
myhtmlframe.on_link_click(load_new_page)
```
Similarily, `on_form_submit` can be used to override the default form submission handlers. Refer to the API reference below.

---
*Zooming*

Setting the zoom of the HtmlFrame widget is very easy. This can be used to add accessibility features to your application. To set the zoom to 2x magnification the following can be used: 
```
myhtmlframe.set_zoom(2)
```
To zoom only the text, use `set_fontscale()` instead.


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
#### `load_website(website_url, decode=None, force=False)`
Loads and parses a website.

Parameters
* **website_url** *(string)* - Specifies the url to load.
* **decode** *(string)* - Specifies the decoding to use when loading the website.
* **force** *(boolean)* - Force the page to reload all elements.

---

#### `load_file(file_url, decode=None, force=False)`
Loads and parses a local HTML file.

Parameters
* **file_url** *(string)* - Specifies the file to load.
* **decode** *(string)* - Specifies the decoding to use when loading the file.
* **force** *(boolean)* - Force the page to reload all elements.

---
#### `load_url(url, decode=None, force=False)`
Loads and parses html from the given url. A local file will be loaded if the url begins with "file://". If the url begins with "https://" or "http://", a website will be loaded. 

Parameters
* **url** *(string)* - Specifies the url to load.
* **decode** *(string)* - Specifies the decoding to use when loading the website.
* **force** *(boolean)* - Force the page to reload all elements.

---
#### `load_html(html_source, base_url="")`
Parses the supplied HTML code. Note that this clears the current page, including any CSS code added using `add_css`.

Parameters
* **html_source** *(string)* - Specifies the HTML code
* **base_url** *(string)* - Specifies the base url to use when parsing stylesheets and images. If this argument is not supplied, it will be set to the current working directory.
---
#### `load_form_data(url, data, method="GET", decode=None)`
Submit the form data to a server.

Parameters
* **url** *(string)* - Specifies the url to load.
* **data** *(string)* - Specifies the data to pass to the server. 
* **method** *(string)* - Specifies the form submission method. This may be either `"GET"` or `"POST"`.
* **decode** *(string)* - Specifies the decoding to use when loading the website.

---
#### `add_html(html_source)`
Send HTML code to the parser.
Unlike `load_html`, `add_html` parses the specified HTML code and adds it to the end of the webpage without clearing the original document.

Parameters
* **html_source** *(string)* - Specifies the code to parse and add to the end of the document. Must be valid HTML code.

---
#### `add_css(css_source)`
Send CSS stylesheets to the parser.
This can be used to remotely alter the appearance of websites.

Parameters
* **css_source** *(string)* - Specifies the code to parse. Must be valid CSS code.

---
#### `stop()`
Stop loading this page.
This will abandon all pending requests and show the document as it is.

---
#### `find_text(searchtext, select=1, ignore_case=True, highlight_all=True)`
Search the document for text and highlight matches. 
This will return the number of matches found.

Parameters
* **searchtext** *(string)* - Specifies the Regex expression to use to find text. If this is set to a blank string (`""`), all highlighted text will be cleared.
* **select** *(integer)* - Specifies the index of the match to select and scroll to. 
* **ignore_case** *(boolean)* - Specifies whether or not uppercase and lowercase letters whould be treated as different characters.
* **highlight_all** *(boolean)* - Specifies whether or not all matches should be highlighted.

Return type
* *integer*

---
#### `select_all()`
Select all text found in the current document. 

---
#### `on_link_click(function)`
Set TkinterWeb to call the specified python function whenever a link is clicked.
When a link is clicked on a webpage, a variable containing the url of the clicked link will be passed to the specified function.

Parameters
* **function** *(python function)* - Specifies the function to call when a link is clicked.

---
#### `on_form_submit(function)`
Set TkinterWeb to call the specified python function whenever a form is submitted.
When an HTML form is submitted, three variables, one containing the url, a second containing the submission data, and a third containing the submission method (GET or POST) will be passed to the specified function.

Parameters
* **function** *(python function)* - Specifies the function to call when a form is submitted.

---
#### `on_title_change(function)`
Set TkinterWeb to call the specified python function whenever the title of a website or file has changed.
When the title of a webpage changes, a variable containing the new title will be passed to the specified function.

Parameters
* **function** *(python function)* - Specifies the function to call when a title changes.

---
#### `on_icon_change(function)`
Set TkinterWeb to call the specified python function whenever the icon of a website or file has changed.
When the icon of a webpage changes, a variable containing the url of the new icon will be passed to the specified function.

Parameters
* **function** *(python function)* - Specifies the function to call when the icon changes.

---
#### `on_url_change(function)`
Set TkinterWeb to call the specified python function whenever the HtmlFrame widget is navigating to a new url.
When an new url is navigated to, a variable containing the new url will be passed to the specified function.

Parameters
* **function** *(python function)* - Specifies the function to call when a url changes.

---
#### `on_done_loading(function)`
Set TkinterWeb to call the specified python function whenever all outstanding resources have been downloaded. This is generally a good indicator as to when the website is done loading. The specified function may be called multiple times while loading a page.

Parameters
* **function** *(python function)* - Specifies the function to call when a webpage is expected to be done loading.

---
#### `on_downloading_resource(function)`
Set TkinterWeb to call the specified python function whenever a new resource is being downloaded.

Parameters
* **function** *(python function)* - Specifies the function to call when a resource is downloaded.

---
#### `on_image_setup(function)`
Set TkinterWeb to call the specified python function whenever the setup of an image is completed.
The url of the image will be passed to the specified function as well as a boolean variable that is set to `True` if the image was successfully loaded and `False` if it could not be displayed.

Parameters
* **function** *(python function)* - Specifies the function to call when an image is setup.

---
#### `set_zoom(multiplier)`
Set the zoom multiplier of the document.

Parameters
* **multiplier** *(float or integer)* - Specifies the zoom multiplier.

---
#### `get_zoom()`
Return the zoom multiplier of the document.

Return type
* *float*

---
#### `set_fontscale(multiplier)`
Set the zoom multiplier of the document's text.

Parameters
* **multiplier** *(float or integer)* - Specifies the fontscale multiplier.

---
#### `get_fontscale()`
Return the zoom multiplier of the document's text.

Return type
* *float*

---
#### `set_parsemode(mode)`
Set the parser mode. The three availiable options are `html`, `xhtml`, and `xhtml`. In `html` mode, explicit XML-style self-closing tags are not handled specially and unknown tags are ignored. `xhtml` mode is similar to `html` mode except that explicit self-closing tags are recognized. `xml` mode is similar to `xhtml` mode except that XML CDATA sections and unknown tag names are recognized. This is the default value.

Parameters
* **mode** *(string)* - Specifies the parse mode.

---
#### `get_parsemode()`
Return the parser mode.

Return type
* *string*

---
#### `resolve_url(url)`
Generate a full url from the specified url. This can be used to generate proper links when given a relative url.

Parameters
* **url** *(string)* - Specifies the url to modify.

Return type
* *string*

---
#### `set_message_func(function)`
Set TkinterWeb to call the specified python function whenever a new message is released.
By default, unless `messages_enabled` was set to `False` when calling `HtmlFrame()`, messages will be printed to the console.
After calling `set_message_func`, whenever a new message is released, a variable containing the main message and a second variable containing more information will be passed to the specified function.

Parameters
* **function** *(python function)* - Specifies the function to call when a message is released.

---
#### `set_broken_webpage_message(html)`
Set the HTML code to be displayed when a webpage cannot be reached.

Parameters
* **html** *(string)* - Specifies the HTML to be parsed when an invalid url is requested. Must be valid HTML code.

---
#### `set_maximum_thread_count(maximum)`
By deafult, TkinterWeb uses threading to improve page load times and to prevent Tkinter from freezing when loading HTML. TkinterWeb allows up to 20 threads to run at once. Increasing this value can improve speed and responsiveness, at the cost of CPU and memory usage while a page is loading. To disable threading altogether, call `set_maximum_thread_count` with a value of 0.

Parameters
* **maximum** *(integer)* - Specifies the maximum number of threads that can run at the same time.

---
#### `set_recursive_hover_depth(depth)`
When a mouse hovers over an element in a webpage, the element under the mouse is flagged as hovered.
TkinterWeb then marks the parent of that element repeatedly, up to the 5th degree. This works fine for most websites, but may cause a few websites to lag slightly. If this is becoming an issue, simply call `set_recursive_hover_depth` and set the *depth* to a smaller integer.

Parameters
* **depth** *(integer)* - Specifies the number of recursions to apply the hover flag to.

---
#### `add_visited_links(links)`
TkinterWeb stores a list of visited websites to determine whether a link on a webpage should be flagged as visited or not visited.
The method add_visited_links enables adding new custom urls to this list. 

Parameters
* **links** *(string or list)* - Specifies the url(s) to be added to the list of visited websites.

---
#### `clear_visited_links()`
Clear the list of visited websites.

---
#### `enable_stylesheets(enabled=True)`
Enable or disable CSS styling.
This is enabled by default.
This method must be invoked *before* loading a webpage to take effect.

Parameters
* **enabled** *(boolean)* - Specifies whether stylesheets should be enabled.

---
#### `enable_images(enabled=True)`
Enable or disable image loading.
This is enabled by default.
This method must be invoked *before* loading a webpage to take effect.

Parameters
* **enabled** *(boolean)* - Specifies whether images should be loaded.

---
#### `enable_forms(enabled=True)`
Enable or disable form-filling capabilities.
This is enabled by default.
This method must be invoked *before* loading a webpage to take effect.

Parameters
* **enabled** *(boolean)* - Specifies whether forms should be handled.

---
#### `enable_objects(enabled=True)`
Enable or disable `<object>` and `<iframe>` embedded elements.
This is enabled by default.
This method must be invoked *before* loading a webpage to take effect.

Parameters
* **enabled** *(boolean)* - Specifies whether objects should be loaded.

---
#### `enable_caches(enabled=True)`
Enable or disable webpage caches.
This is enabled by default.
Disabling this option will conserve memory, but will also result in longer page load times.
This method must be invoked *before* loading a webpage to take effect.

Parameters
* **enabled** *(boolean)* - Specifies whether caches can be used.

---

#### `enable_dark_theme(enabled=True, invert_images=True)`
Enable or disable dark theme.
This is disabled by default.
This function is experimental and may cause hangs or crashes.

Parameters
* **enabled** *(boolean)* - Specifies whether page colours should be inverted.
* **invert_images** *(boolean)* - Specifies images should be inverted.

---
#### `ignore_invalid_images(value)`
Enable or disable showing a broken image icon whenever an image can't be loaded.

Parameters
* **value** *(boolean)* - Specifies whether invalid images should or should not be ignored.

---
#### `get_current_link(resolve=True)`
Convenience method for getting the url of the current hyperlink.

Parameters
* **resolve** *(boolean)* - If True, the url will be resolved before being returned. Otherwise, it will be returned as-is.

---
#### `get_currently_hovered_node_tag()`
Get the tag of the HTML element the mouse is currently over.
For example, if the mouse is hovering over a heading, `get_currently_hovered_node_tag()` would return "h1".

Return type
* *string*

---
#### `get_currently_hovered_node_text()`
Get the text content of the HTML element the mouse is currently over.

Return type
* *string*
---
#### `get_currently_hovered_node_attribute(attribute)`
Get the specified attribute of the HTML element the mouse is currently over.
For example, if the mouse is over a link to python.org, `get_currently_hovered_node_attribute("href")` would return "python.org".
If the current element does not have the specified attribute, an empty string is returned.

Parameters
* **attribute** *(boolean)* - Specifies the attribute

Return type
* *string*

---
#### `get_currently_selected_text()`
Get the text content that is currently highlighted/selected in the HtmlFrame.

Return type
* *string*

---

#### `replace_widget(oldwidget, newwidget)`
Removes the `oldwidget` from the document, and replaces it with the `newwidget`. Note that if both `oldwidget` and `newwidget` are currently shown in the document, their locations will be swapped. See the [geometry management docs](GEOMETRY.md) for more information.

Parameters
* **oldwidget** *(tkinter.Widget)* - Specifies the Tkinter widget to replace. This must be a valid Tkinter widget that is currently managed by TkinterWeb.
* **newwidget** *(tkinter.Widget)* - Specifies the new Tkinter widget to show. This may be any Tkinter widget.

---

#### `replace_element(cssselector, newwidget)`
Replaces the content of the element matching the specified CSS selector with the `newwidget`. See the [geometry management docs](GEOMETRY.md) for more information.

Parameters
* **cssselector** *(string)* - Specifies the CSS selector to search for.
* **newwidget** *(tkinter.Widget)* - Specifies the new Tkinter widget to show. This may be any Tkinter widget.

---

#### `remove_widget(oldwidget)`
Removes the `oldwidget` from the document. 
This method is experimental and may cause issues. If you encounter any issues, please [report them](https://github.com/Andereoo/TkinterWeb/issues). See the [geometry management docs](GEOMETRY.md) for more information.

Parameters
* **oldwidget** *(tkinter.Widget)* - Specifies the Tkinter widget to remove. This must be a valid Tkinter widget that is currently managed by TkinterWeb.

---
