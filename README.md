# TkinterWeb 
**A fast and lightweight web browser widget for Tkinter.**

&nbsp;
&nbsp;
## Overview
**TkinterWeb offers bindings for the Tkhtml3 widget from http://tkhtml.tcl.tk, which enables displaying HTML and CSS code in Tkinter applications.**

All [major operating systems](/docs/FAQ.md#a-note-on-tkhtml-binaries) running Python 3+ are supported. 

&nbsp;
&nbsp;
## Usage

**TkinterWeb provides:**
* A [frame](/docs/HTMLFRAME.md) widget to display websites, help files, and any other styled HTML in Tkinter
* A [label](/docs/HTMLLABEL.md) widget that can display styled HTML
* A [geometry manager](/docs/GEOMETRY.md) to display Tkinter widgets *and HTML elements* together in a Tkinter application

**TkinterWeb can be used in any Tkinter application. Here is an example:**
```
import tkinter as tk
from tkinterweb import HtmlFrame # import the HtmlFrame widget

root = tk.Tk() # create the Tkinter window
frame = HtmlFrame(root) # create the HtmlFrame widget
frame.load_website("http://tkhtml.tcl.tk/tkhtml.html") # load a website
frame.pack(fill="both", expand=True) # attach the HtmlFrame widget to the window
root.mainloop()
```
![TkinterWeb](/images/tkinterweb-tkhtml.png)

Some other tricks, such as handling page title changes, link clicks, and navigation key presses, can be found in the [HtmlFrame documentation](/docs/HTMLFRAME.md#tips-and-tricks).

&nbsp;
&nbsp;
## Installation
To install TkinterWeb, simply type `pip install tkinterweb` in the command prompt or terminal.
That's it.

&nbsp;
&nbsp;
## Dependencies
**In order to load webpages and show images, TkinterWeb requires the following packages:**
* Tkinter (which is automatically packaged with most Python installations)
* PIL (can be installed via `pip install pillow`)
* PIL.ImageTk (may be automatically installed with PIL on some systems, otherwise needs to be installed)

Pip will automatically install PIL when installing TkinterWeb.

&nbsp;
&nbsp;
## API Documentation
**Documentation and additional information on built-in classes can be found in the corresponding API reference pages:**
* [`tkinterweb.Demo`](/docs/DEMO.md)
* [`tkinterweb.HtmlFrame`](/docs/HTMLFRAME.md)
* [`tkinterweb.HtmlLabel`](/docs/HTMLLABEL.md)
* [`tkinterweb.TkinterWeb`](/docs/TKINTERWEB.md)

Other notable built-in classes:
* `tkinterweb.Notebook` (a Tkhtml-compatible drop-in replacement for `ttk.Notebook`). See [Frequently Asked Questions](https://github.com/Andereoo/TkinterWeb/blob/main/docs/FAQ.md).

&nbsp;
&nbsp;
## FAQs
See [Frequently Asked Questions](https://github.com/Andereoo/TkinterWeb/blob/main/docs/FAQ.md).

&nbsp;
&nbsp;
## Webpage Compatability
**HTML/CSS:**
* TkinterWeb supports HTML 4.01 and CSS 2.1. A full list of supported CSS declarations can be found at http://tkhtml.tcl.tk/support.html. 
* Most CSS pseudo-elements, such as `:hover` and `:active` are also supported. 

**JavaScript:**
* Javascript is not supported at the moment. It is up to the user to connect a JavaScript interpreter by registering a callback for scripts and manipulating the document through Python. See [DOM Manipulation with TkinterWeb](/docs/DOM.md).

**Images:**
* TkinterWeb supports nearly 50 different image types through PIL. However, in order to load Scalable Vector Graphic images:
    * PyCairo or PyGObject must be installed. 
    * Either Rsvg, PyGObject, or CairoSVG must also be installed. 
* Without these packages, TkinterWeb will still function properly, but SVG files will not be shown.

&nbsp;
&nbsp;
## Contributing
**The best ways to contribute to this project are by submitting a [bug report](https://github.com/Andereoo/TkinterWeb/issues/new) to report bugs or suggest new features or by submitting a [pull request](https://github.com/Andereoo/TkinterWeb/pulls) to offer fixes. Your help makes TkinterWeb become more stable and full-featured!**

Please check the [FAQs](https://github.com/Andereoo/TkinterWeb/blob/main/docs/FAQ.md) and [closed bugs](https://github.com/Andereoo/TkinterWeb/issues?q=is%3Aissue) before submitting a bug report to see if your question as already been answered.

&nbsp;
&nbsp;
## Credits
**TkinterWeb is powered by the [Tkhtml project](http://tkhtml.tcl.tk/index.html).**

Thanks to the [TkinterHtml package](https://bitbucket.org/aivarannamaa/tkinterhtml) for providing the bindings which this project is based on.

Thanks to the [BRL-CAD project](https://github.com/BRL-CAD/brlcad) for providing modifications for Tkhtml on 64-bit Windows platforms.

Thanks to [Google Fonts](https://github.com/google/fonts) for providing the font used for generating alternate text when images fail to load.

A huge thanks to everyone else who helped this project by reporting bugs, providing suggestions, and creating pull requests!

