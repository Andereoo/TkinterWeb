# TkinterWeb 
**A fast and simple cross-platform webbrowser for Tkinter.**

&nbsp;
&nbsp;
## Overview
**TkinterWeb offers bindings for the Tkhtml3 widget from http://tkhtml.tcl.tk/tkhtml.html, which enables loading HTML and CSS code into Tkinter applications.**

Both Python 2 and Python 3, as well as MacOS, Windows, and Linux are supported. 

&nbsp;
&nbsp;
## Usage

**TkinterWeb can be used in any Tkinter application. Here is an example:**
```
from tkinterweb import HtmlFrame #import the HTML browser
try:
  import tkinter as tk #python3
except ImportError:
  import Tkinter as tk #python2

root = tk.Tk() #create the tkinter window
frame = HtmlFrame(root) #create HTML browser
frame.load_website("http://tkhtml.tcl.tk/tkhtml.html") #load a website
frame.pack(fill="both", expand=True) #attach the HtmlFrame widget to the parent window
root.mainloop()
```
![TkinterWeb](/tkinterweb/images/screenshot.png)

Some other tricks can be found in [the HtmlFrame documentation](/tkinterweb/docs/HTMLFRAME.md#tips-and-tricks)

&nbsp;
&nbsp;
## Installation
**To install TkinterWeb, simply type `pip install tkinterweb` in the command prompt or terminal.**
That's it.


&nbsp;
&nbsp;
## Dependencies
**In order to load webpages and show images, TkinterWeb requires the following packages:**
* Tkinter (which is automatically installed on most Python versions)
* PIL (can be installed via `pip install pillow`)
* Requests (can be installed via `pip install requests`)

Pip will automatically install PIL and Requests when installing TkinterWeb.

&nbsp;
&nbsp;
## API documentation
**TkinterWeb ships with a few classes that make it quick and easy to use.**

Documentation and additional information for these classes can be found in the corresponding API refrence pages:
* [`TkinterWeb.HtmlFrame`](/tkinterweb/docs/HTMLFRAME.md)
* [`TkinterWeb.Demo`](/tkinterweb/docs/DEMO.md)
* [`TkinterWeb.TkinterWeb`](/tkinterweb/docs/TKINTERWEB.md)

&nbsp;
&nbsp;
## Webpage Compatability
**HTML/CSS:**
* TkinterWeb supports HTML 4.01 and CSS 2.1. A full list of supported CSS declarations can be found at http://tkhtml.tcl.tk/support.html. 
* Most CSS Pseudo-elements, such as `hover` and `active` are also supported. 

**JavaScript:**
* Javascript is currently not supported

**Images:**
* TkinterWeb supports nearly 50 different image types through PIL. Scalable Vector Graphic support is not as straightforward, though. In order to load SVG images:
    * PyCairo must be installed. 
    * Either Rsvg, PyGObject, or CairoSVG must also be installed. 
* Without these packages, TkinterWeb will still function properly, but SVG files will not be shown.

&nbsp;
&nbsp;
## Contributing
**TkinterWeb happily accepts contributions.**

**The best way to contribute to this project is to go to the [issues tab](https://github.com/Andereoo/TkinterWeb/issues) and report bugs or submit a feature request. **
This helps TkinterWeb become both more stable and more powerful.

&nbsp;
&nbsp;
## Credits
**TkinterWeb is based on the TkinterHtml package.**
