> [!WARNING]
> The API changed significantly in version 4.0.0. See [Porting to TkinterWeb 4+](UPGRADING.md) for details.

> [!IMPORTANT]
> The TkinterWeb documentation has moved to https://tkinterweb.readthedocs.io/en/latest/index.html. See you there!

## *`tkinterweb.HtmlFrame` Documentation*

## Overview
**The `HtmlFrame` class is a Tkinter frame that provides additional functionality to the [TkinterWeb widget](TKINTERWEB.md).**

It combines the TkinterWeb widget, automatic scrollbars, error handling, and many convenience methods into one embeddable and easy to use widget. The HtmlFrame widget is also capable managing other Tkinter widgets, which enables combining Tkinter widgets and HTML elements.

## Usage
**The HtmlFrame widget is very easy to use! Here is an example:**

```
import tkinter as tk
from tkinterweb import HtmlFrame # import the HtmlFrame widget

root = tk.Tk() # create the Tkinter window

### The important part: create the html widget and attach it to the window
yourhtmlframe = HtmlFrame(root) # create the HtmlFrame widget
yourhtmlframe.load_html("<h1>Hello, World!</h1>") # load some HTML code
yourhtmlframe.pack(fill="both", expand=True) # attach the HtmlFrame widget to the window

root.mainloop()
```
> [!TIP]
> To load a website, call `yourhtmlframe.load_website("www.yourwebsite.com")`.
> 
> To load a file, call `yourhtmlframe.load_file("/path/to/your/file.html")`.
> 
> To load any generic url, call `yourhtmlframe.load_url(yourwebsiteorfile)`. Keep in mind that the url must be properly formatted and include the url scheme.

The HtmlFrame widget behaves like any other Tkinter widget and supports bindings. It also supports link clicks, form submittions, website title changes, and much, much more! Refer to the API refrence below.

## Tips and Tricks
*Bindings*

Like any other Tkinter widget, mouse and keyboard events can be bound to the HtmlFrame widget.

The following is an example of the usage of bingings with the HtmlFrame widget to show a menu:
```
def on_right_click(event):
    element = yourhtmlframe.get_currently_hovered_element() # get the element under the mouse
    url = element.getAttribute("href") # get the element's 'href' attribute
    if url: #if mouse was clicked on a link
        url = yourhtmlframe.resolve_url(url) # resolve the url so that partial urls are converted to full urls
        menu = tk.Menu(root, tearoff=0) # create the menu
        menu.add_command(label="Open %s" % url, command=lambda url=url: yourhtmlframe.load_url(url)) # add a button to the menu showing the url
        menu.tk_popup(event.x_root, event.y_root, 0) # show the menu
yourhtmlframe.bind("<Button-3>", on_right_click)
```
This will make a popup show if the user right-clicked on a link. Clicking link shown in the popup would load the website.

Similarly, bindings can also be applied to navigation keys:  
```
    yourhtmlframe.bind_all("<Up>", lambda e: yourhtmlframe.yview_scroll(-5, "units"))
    yourhtmlframe.bind_all("<Down>", lambda e: yourhtmlframe.yview_scroll(5, "units"))
    yourhtmlframe.bind_all("<Prior>", lambda e: yourhtmlframe.yview_scroll(-1, "pages"))
    yourhtmlframe.bind_all("<Next>", lambda e: yourhtmlframe.yview_scroll(1, "pages"))
    yourhtmlframe.bind_all("<Home>", lambda e: yourhtmlframe.yview_moveto(0))
    yourhtmlframe.bind_all("<End>", lambda e: yourhtmlframe.yview_moveto(1))
```

---
*Changing the title*

To change the title of the window every time the title of a website changes, use the following:
```
def change_title(event):
    root.title(yourhtmlframe.title) # change the title
    
yourhtmlframe.bind("<<TitleChanged>>", change_title)
```
Similarily, `<<IconChanged>>` fires when the website's icon changes.

---
*Url changes*

Normally, a website's url may change when it is loaded. For example, `https://github.com` will redirect to `https://www.github.com`. This can be handled with a binding to `<<UrlChanged>>`:

```
def url_changed(event):
    updated_url = yourhtmlframe.current_url
    ## Do stuff, such as change the content of a url-bar
    
yourhtmlframe.bind("<<UrlChanged>>", url_changed)
```
This is highly recomended if your app includes an address bar. This event will fire on all page redirects and url changes when stopping page loading.


---
*Search the page*

Use `find_text` to search the page for specific text. To search the document for the word 'python', for example, the following may be used:
```
number_of_matches = yourhtmlframe.find_text("python")
```
Refer to the API reference for more information and [bug 18](https://github.com/Andereoo/TkinterWeb/issues/18#issuecomment-881649007) or the [sample web browser](../examples/TkinterWebBrowser.py) for a sample find bar.

---
*Embed a widget*

There are many ways to embed widgets in your HtmlFrame. One way is to use `<object>` elements:
```
yourcanvas = tkinter.Canvas(yourhtmlframe)
yourhtmlframe.load_html(f"<p>This is a canvas!</p><object data="{yourcanvas}"></object>")
```
Refer to [Geometry Management with TkinterWeb](GEOMETRY.md) for more information.

---
*Done loading?*

The `<<DoneLoading>>` event fires when the document is done loading. 

When binding to `<<DoneLoading>>` to, for example, change a 'stop' button to a 'refresh' button, it is generally a good idea to bind to `<<DownloadingResource>>` to do the opposite. Otherwise, the document may show that is is done loading while it is still loading.

---
*Stop loading*

The method `stop()` can be used to stop loading a webpage. If `load_url`, `load_website`, or `load_file` was used to load the document, passing `yourhtmlframe.current_url` with `force=True`  will force a page refresh. Refer to the API refrence below for more information.

---
*Link clicks*

Link clicks can also be easily handled. By default, when a link is clicked, it will be automatically loaded.
To, for example, run some code before loading the new website, use the following: 
```
yourhtmlframe = HtmlFrame(master, on_link_click=load_new_page)

def load_new_page(url):
    ## Do stuff
    yourhtmlframe.load_url(url) # load the new website    
```
Similarily, `on_form_submit` can be used to override the default form submission handlers. Refer to the API reference below.

---
*Zooming*

Setting the zoom of the HtmlFrame widget is very easy. This can be used to improve accessibility in your application. To set the zoom to 2x magnification the following can be used: 
```
yourhtmlframe.configure(zoom=2)
# or yourhtmlframe["zoom"] = 2
```
To zoom only the text, use `fontscale=2` instead.

---
*Manipulating the DOM*

Refer to [DOM Manipulation with TkinterWeb](DOM.md).

---

## Class API 

### HtmlFrame constructors:
* `master`: Parent (Tkinter widget)
*`**kwargs`: Any supported configuration options. See [`configure()`](#configure-kwargs) for a list of options.

### Key Subclasses:
* `document` (`tkinterweb.dom.HTMLDocument` instance): see [DOM Manipulation with TkinterWeb](DOM.md).
* `html` (`tkinterweb.bindings.TkinterWeb` instance): see the [TkinterWeb widget documentation](TKINTERWEB.md).

### Virtual Events:
* `<<DownloadingResource>>`/`utilities.DOWNLOADING_RESOURCE_EVENT`:
  - Generated whenever a new resource is being downloaded.
* `<<DoneLoading>>`/`utilities.DONE_LOADING_EVENT`:
  - Generated whenever all outstanding resources have been downloaded.
  - This is generally a good indicator as to when the website is done loading, but may be generated multiple times while loading a page.
* `<<UrlChanged>>`/`utilities.URL_CHANGED_EVENT`:
  - Generated whenever the url the widget is navigating to changes. Use `current_url` to get the url.
* `<<IconChanged>>`/`utilities.ICON_CHANGED_EVENT`:
  - Generated whenever the icon of a webpage changes. Use `icon` to get the icon.
* `<<TitleChanged>>`/`utilities.TITLE_CHANGED_EVENT`:
  - Generated whenever the title of a website or file has changed. Use `title` to get the title.
* `<<Modified>>`:
  - Generated whenever the content of any `<input>` element changes.

### State Variables:
* `current_url`: The document's url.
* `base_url`: The documents's base url. This is automatically generated from the `current_url` but will also change if explicitly specified by the document. Read-only.
* `title`: The document's title (if specified by the document). Read-only.
* `icon`: The document's icon url (if specified by the document). Read-only.

### Key Methods:
Below are methods that are specific to this widget. Other general Tkinter widget methods, such as `bind`, `pack`, and `grid`, are also supported but not listed.

#### `configure(**kwargs)`
Change the widget's configuration options. Below are the supported options:
* `on_navigate_fail`:
  - The function to be called when a url cannot be loaded. This can be used to override the default error page. The target url, error, and code will be passed as arguments. **Default: HtmlFrame.show_error_page**
* `on_link_click`:
  - The function to be called when a hyperlink is clicked. The target url will be passed as an argument. **Default: HtmlFrame.load_url**
* `on_form_submit`:
  - The function to be called when a form is submitted. The target url, data, and method (GET or POST) will be passed as arguments. **Default: HtmlFrame.load_form_data**
* `on_script`:
  - The function to be called when a `<script>` element is encountered. This can be used to connect a script handler, such as a JavaScript engine. The script element's attributes and contents will be passed as arguments. **Ignored by default.**
* `on_resource_setup`: 
  - The function to be called when an image or stylesheet load finishes. The resource's url, type ("stylesheet" or "image"), and whether setup was successful or not (True or False) will be passed as arguments. **Ignored by default.**
* `message_func`:
  - The function to be called when a debug message is issued. The message will be passed as an argument. **Default: utilities.notifier**
    
* `visited_links`:
  - The list used to determine if a hyperlink should be given the CSS `:visited` flag. **Default: list()**
* `zoom`:
  - The page zoom multiplier. **Default: 1.0**
* `fontscale`:
  - The page fontscale multiplier. **Default: 1.0**
    
* `vertical_scrollbar`:
  - Show the vertical scrollbar. May be True, False, or "auto". Consider using the CSS property `overflow-y` (experimental mode only) or `overflow`  on the `<html>` or `<body>` element instead. **Default: "auto"**
* `horizontal_scrollbar`:
  - Show the horizontal scrollbar. May be True, False, or "auto". Consider using the CSS property `overflow-x` (experimental mode only) or adding the attribute `tkinterweb-overflow-x=[True, False, or "auto"]` on the `<html>` or `<body>` element instead. **Default: False**
* `shrink`:
  - If False, the widget's width and height are set by the width and height options as per usual. You may still need to call `grid_propagate(0)` or `pack_propagate(0)` for Tkinter to respect the set width and height. If this option is set to True, the widget's requested width and height are determined by the current document. **Default: False**
    
* `messages_enabled`:
  - Enable messages. **Default: True**
* `selection_enabled`:
  - Enable selection. **Default: True**
* `stylesheets_enabled`:
  - Enable stylesheets. **Default: True**
* `images_enabled`:
  - Enable images. **Default: True**
* `forms_enabled`:
  - Enable forms and form elements. **Default: True**
* `objects_enabled`:
  - Enable embedding of `<object>` and `<iframe>` elements. **Default: True**
* `caches_enabled`:
  - Enable caching. Disabling this option will conserve memory, but will also result in longer page and image reload times. **Default: True**
* `crash_prevention_enabled`:
  - Enable crash prevention. Disabling this option may improve page load speed, but crashes will occur on some websites. **Default: True**
* `events_enabled`:
  - Enable generation of Tk events. **Default: True**
* `threading_enabled`:
  - Enable threading. Has no effect if the Tcl/Tk build does not support threading. **Default: True**
* `image_alternate_text_enabled`:
  - Enable the display of alt text for broken images. **Default: True**
* `dark_theme_enabled`:
  - Enable dark mode. May cause hangs or crashes on more complex websites. **Default: False**
* `image_inversion_enabled`:
  - Enable image inversion. May cause hangs or crashes on more complex websites. **Default: False**
* `ignore_invalid_images`:
  - Ignore invalid images. If enabled and alt text is disabled or the image has no alt text, a broken image icon will be displayed in place of the image. **Default: True**
    
* `about_page_background`:
  - The default background color of built-in pages, intended to better integrate custom documents with Tkinter. **Default: ttk.Style.lookup('TFrame', 'background')**
* `about_page_foreground`:
  - The default text color of built-in pages. **Default: ttk.Style.lookup('TLabel', 'foreground')**
* `find_match_highlight_color`:
  - The highlight color of matches found by `find_text()`. **Default: "#ef0fff"**
* `find_match_text_color`:
  - The text color of matches found by `find_text()`. **Default: "#fff"**
* `find_current_highlight_color`:
  - The highlight color of the current match selected by `find_text()`. **Default: "#38d878"**
* `find_current_text_color`:
  - The text color of the current match selected by `find_text()`. **Default: "#fff"**
* `selected_text_highlight_color`:
  - The highlight color of selected text. **Default: "#3584e4"**
* `selected_text_color`:
  - The text color of selected text. **Default: "#fff"**
    
* `default_style`:
  - The stylesheet used to set the default appearance of HTML elements. It is generally best to leave this setting alone. **Default: utilities.DEFAULT_STYLE**
* `dark_style`:
  - The stylesheet used to set the default appearance of HTML elements when dark mode is enabled. It is generally best to leave this setting alone. **Default: utilities.DARK_STYLE**
* `insecure_https`:
  - If True, website certificate errors are ignored. This is a workaround for issues where `ssl` is unable to get a page's certificate on some older Mac systems. **Default: False**
* `headers`:
  - The headers used by urllib's Request when fetching a resource (dict). **Default: utilities.HEADERS**
* `experimental`:
  - If True, experimental features will be enabled. You will need to compile the cutting-edge Tkhtml widget from https://github.com/Andereoo/TkinterWeb-Tkhtml/tree/experimental and replace the default Tkhtml binary for your system with the experimental version. Unless you need to screenshot the page on Windows or print your page for now it is likely best to use the default Tkhtml binary and leave this setting alone. **Default: False**
* `use_prebuilt_tkhtml`:
  - If True, the Tkhtml binary for your system supplied by TkinterWeb will be used. If your system isn't supported and you don't want to compile the Tkhtml widget from https://github.com/Andereoo/TkinterWeb-Tkhtml yourself, you could try installing Tkhtml3 system-wide and set `use_prebuilt_tkhtml` to False. Note that some crash prevention features will no longer work. **Default: True**

* `parsemode`:
  - The parse mode. May be "xml", "xhtml", or "html". In "html" mode, explicit XML-style self-closing tags are not handled specially and unknown tags are ignored. "xhtml" mode is similar to "html" mode except that explicit self-closing tags are recognized. "xml" mode is similar to "xhtml" mode except that XML CDATA sections and unknown tag names are recognized. It is usually best to leave this setting alone. **Default: "xml"**
* `mode`:
  - The rendering engine mode. May be "standards", "almost standards", or "quirks". It is usually best to leave this setting alone. **Default: "standards"**
* Other optional `ttk.Frame` arguments

Configuration options can also be set and returned as key-value pairs.

---
#### `cget(**kwargs)`
Return the value of the specified configuration option. See above for options.

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
Loads and parses html from the given url. A local file will be loaded if the url begins with "file://". If the url begins with "https://" or "http://", a website will be loaded. If the url begins with "view-source:", the source code of the webpage will be displayed. Loading "about:tkinterweb" will open a page with debugging information.

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
#### `find_text(searchtext, select=1, ignore_case=True, highlight_all=True, detailed=False)`
Search the document for text and highlight matches. 
This will return the number of matches found.

Parameters
* **searchtext** *(string)* - Specifies the Regex expression to use to find text. If this is set to a blank string (`""`), all highlighted text will be cleared.
* **select** *(integer)* - Specifies the index of the match to select and scroll to. 
* **ignore_case** *(boolean)* - Specifies whether or not uppercase and lowercase letters whould be treated as different characters.
* **highlight_all** *(boolean)* - Specifies whether or not all matches should be highlighted.
* **detailed** *(boolean)* - If True, this function will also return information on the nodes that were found. See [#93](https://github.com/Andereoo/TkinterWeb/issues/93#issuecomment-2052516492) for more details.

Return type
* *integer*

---
#### `get_currently_hovered_element(ignore_text_nodes=True)`
Returns the element under the mouse. Useful for creating right-click menus or displaying hints when the mouse moves.

Parameters
* **ignore_text_nodes** *(boolean)* - If True, text nodes (i.e. the contents of a `<p>` element) will be ignored and their parent node returned. It is generally best to leave leave this set to True.

Return type
* *HTMLElement*

---
#### `screenshot_page(self, filename=None, full=False)`
Take a screenshot.
On Windows, this method requires experimental mode to be enabled.
This command should be used with care, particularily if `full` is set to True, as large documents can result in very large images that take a long time to create and consume large amounts of memory. 

Parameters
* **filename** *(string)* - Specifies the file path to save the screenshot to. If None, the image is not saved to the disk.
* **full** *(boolean)* - If True, the entire page is captured. If False, only the visible content is captured. 

Return type
* *PIL.Image*

---
#### `print_page(self, filename=None, cnf={}, **kwargs)`
Print the document to a PostScript file.
This method is experimental and requires experimental mode to be enabled.

Parameters
* **filename** *(string)* - Specifies the file path to print the page to. If None, the document is not saved to the disk.
* **cnf |= kwargs** *(boolean)* - Valid options are colormap, colormode, file, fontmap, height, pageanchor, pageheight, pagesize (can be A3, A4, A5, LEGAL, and LETTER), pagewidth, pagex, pagey, nobg, noimages, rotate, width, x, and y. 

Return type
* *string*

---
#### `save_page(self, filename=None)`
Save the page as an HTML file.

Parameters
* **filename** *(string)* - Specifies the file path to print the page to. If None, the document is not saved to the disk.

Return type
* *string*
---

#### `snapshot_page(self, filename=None, allow_agent=False)`
Save a snapshot of the document. Unlike `save_page`, which returns the original document, `snapshot_page` returns the page as rendered. 
`<link>` elements are ignored and instead one `<style>` element contains all of the necessary CSS information for the document.
This can be useful for saving documents for offline use.

Parameters
* **filename** *(string)* - Specifies the file path to print the page to. If None, the document is not saved to the disk.
* **allow_agent** *(string)* - If True, CSS properties added by the rendering engine (eg. those affected by the widget's `default_style` option) are also included.

Return type
* *string*
    
---
#### `select_all()`
Select all text in the document.

---
#### `clear_selection()`
Clear the current selection.

---
#### `get_selection()`
Return any selected text.

---
#### `resolve_url(url)`
Generate a full url from the specified url. This can be used to generate full urls when given a relative url.

Parameters
* **url** *(string)* - Specifies the url to modify.

Return type
* *string*

---
#### `yview(*args)`
Adjust the viewport. This method uses the standard interface copied from the Tkinter Canvas and Text widgets.
If a Tkhtml3 node is supplied as an argument, the document will scroll to the top of the given node.

---
#### `yview_moveto(number)`
Shifts the view vertically to the specified position.

Parameters
* **number** *(float)* - Specifies the position to be scrolled to.

---
#### `yview_scroll(number, what)`
Shifts the view in the window up or down.

Parameters
* **number** *(float)* - Specifies the number of 'whats' to scroll; may be positive to scroll down or negative to scroll up.
* **what** *(string)* - Either "units" or "pages".

---
#### `replace_widget(oldwidget, newwidget)`
Removes the `oldwidget` from the document, and replaces it with the `newwidget`. If both `oldwidget` and `newwidget` are currently shown in the document, their locations will be swapped.

Parameters
* **oldwidget** *(tkinter.Widget)* - Specifies the Tkinter widget to replace. This widget must be currently managed by TkinterWeb.
* **newwidget** *(tkinter.Widget)* - Specifies the new Tkinter widget to show. This may be any Tkinter widget.

---
#### `replace_element(cssselector, newwidget)`
Replaces the content of the element matching the specified CSS selector with the specified widget. This command will scan the document for any elements that match the specified CSS selector. If multiple elements match the specified selector, only the first element will be replaced. For example, the following code will replace the 'text' HTML element with a button. 

```
yourbutton = tkinter.Button(yourhtmlframe)
yourhtmlframe.load_html("<p id='text'>some text</p>")
yourhtmlframe.replace_element("#text", yourbutton)
```

Parameters
* **cssselector** *(string)* - Specifies the CSS selector to search for.
* **newwidget** *(tkinter.Widget)* - Specifies the new Tkinter widget to show. This may be any Tkinter widget.

---
#### `remove_widget(oldwidget)`
Removes the specified widget from the document. 

Parameters
* **oldwidget** *(tkinter.Widget)* - Specifies the Tkinter widget to remove. This widget must be currently managed by TkinterWeb.
