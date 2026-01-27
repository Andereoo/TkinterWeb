![PyPi Downloads](https://static.pepy.tech/badge/tkinterweb/month)
![MIT Licence](https://img.shields.io/pypi/l/tkinterweb) 
![Python 3](https://img.shields.io/pypi/pyversions/tkinterweb)
![Made in Canada](https://img.shields.io/badge/%F0%9F%87%A8%F0%9F%87%A6%20made%20in%20Canada-grey)

<div style="margin-bottom: 0px"><a href="https://www.buymeacoffee.com/andereoo" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-violet.png" alt="Buy Me A Coffee" style="height: 36px; width: 146px;" ></a></div>

<p align="center"><img src="./docs/source/_static/banner.png" style="width: 425px"/></p>

**<p align="center">Fast and lightweight web browser, rich text, and app design widgets for Tkinter.</p>**

## Overview
**TkinterWeb offers bindings and extensions to a modified version of the Tkhtml3 widget from [http://tkhtml.tcl.tk](https://web.archive.org/web/20250219233338/http://tkhtml.tcl.tk/), which enables the display of HTML and CSS code in Tkinter applications.** 

Some of TkinterWeb's uses include:
* Displaying and editing websites, feeds, help files, and other styled HTML
* Displaying images, including SVG images
* Creating a rich text or HTML editor
* Designing apps using HTML templates
* Creating prettier apps, with rounded buttons and more!

All [major operating systems](https://tkinterweb.readthedocs.io/en/latest/compatibility.html#a-note-on-tkhtml-binaries) running Python 3.2+ are supported. 

## Usage

**TkinterWeb provides:**
* A [frame widget](https://tkinterweb.readthedocs.io/en/latest/api/htmlframe.html) to display and edit websites, help files, RSS feeds, and any other styled HTML in Tkinter.
* A [label widget](https://tkinterweb.readthedocs.io/en/latest/api/htmlframe.html#tkinterweb.HtmlLabel) that can display styled HTML.
* A [text widget](https://tkinterweb.readthedocs.io/en/latest/api/htmlframe.html#tkinterweb.HtmlText) that allows the user to edit styled HTML.

**TkinterWeb can be used in any Tkinter application to display and edit websites, help pages, documentation, and much more! Here is an example:**
```
import tkinter as tk
from tkinterweb import HtmlFrame # import the HtmlFrame widget

root = tk.Tk() # create the Tkinter window
frame = HtmlFrame(root) # create the HtmlFrame widget
frame.load_website("https://tkinterweb.readthedocs.io/en/latest/index.html") # load a website
frame.pack(fill="both", expand=True) # attach the HtmlFrame widget to the window
root.mainloop()
```
![TkinterWeb](/images/tkinterweb-demo.png)

See [Getting Started](https://tkinterweb.readthedocs.io/en/latest/usage.html) for more tips and tricks.

## Installation
To install TkinterWeb, simply type `pip install tkinterweb[recommended]` in the command prompt or terminal. That's it!

Or, you can also choose from the following extras: `pip install tkinterweb[html,images,svg,javascript,requests]`. You can also use `pip install tkinterweb[full]` to install all optional dependencies or ``pip install tkinterweb`` to install the bare minimum.

## Dependencies
**In order to load webpages and show images, TkinterWeb requires the following packages:**
* Tkinter
* TkinterWeb-Tkhtml

I also **strongly** recommended installing the following:
* TkinterWeb-Tkhtml-Extras
* PIL
* PIL.ImageTk

You can also choose from the following list for extra functionality:
* Brotli (for faster page loads on some sites)
* PythonMonkey (for basic JavaScript support)
* CairoSVG or PyGObject (for SVG support)

Pip will automatically install dependencies when installing TkinterWeb. PIL.ImageTk should be automatically installed with PIL but might need to installed separately on some systems.

## API Documentation

> [!WARNING]
> The API changed significantly in version 4.0.0. See [the changelog](https://tkinterweb.readthedocs.io/en/latest/upgrading.html) for details.

**Documentation and additional information on built-in classes can be found in the corresponding API reference pages:**
* [`tkinterweb.Demo`](https://tkinterweb.readthedocs.io/en/latest/usage.html#installation)
* [`tkinterweb.HtmlFrame`](https://tkinterweb.readthedocs.io/en/latest/api/htmlframe.html)
* [`tkinterweb.HtmlLabel`](https://tkinterweb.readthedocs.io/en/latest/api/htmlframe.html#tkinterweb.HtmlLabel)
* [`tkinterweb.HtmlText`](https://tkinterweb.readthedocs.io/en/latest/api/htmlframe.html#tkinterweb.HtmlText)
* [`tkinterweb.HtmlParse`](https://tkinterweb.readthedocs.io/en/latest/api/htmlframe.html#tkinterweb.HtmlParse)
* [`tkinterweb.TkinterWeb`](https://tkinterweb.readthedocs.io/en/latest/api/tkinterweb.html)
* [`tkinterweb.Notebook`](https://tkinterweb.readthedocs.io/en/latest/api/notebook.html) (a Tkhtml-compatible drop-in replacement for `ttk.Notebook`)

## FAQs
See [Frequently Asked Questions](https://tkinterweb.readthedocs.io/en/latest/faq.html).

## Webpage Compatability
**HTML/CSS:**
* TkinterWeb supports HTML 4.01 and CSS 2.1. A full list of supported CSS declarations can be found at [http://tkhtml.tcl.tk/support.html](https://web.archive.org/web/20250325123206/http://tkhtml.tcl.tk/support.html).
* Most CSS pseudo-elements, such as `:hover` and `:active` are also supported. 
* On 64-bit Windows and Linux, if the TkinterWeb-Tkhtml-Extras package is installed, ``border-radius`` and more cursor options are also supported.

**JavaScript:**
* Javascript only partly supported at the moment.
   * To use JavaScript, PythonMonkey must be installed.
* It is also possible for the user to connect their own JavaScript interpreter or manipulate the document through Python.
* See [Using JavaScript](https://tkinterweb.readthedocs.io/en/latest/javascript.html) for more information and [DOM Manipulation with TkinterWeb](https://tkinterweb.readthedocs.io/en/latest/dom.html) for information on manipulating the document through Python.

**Images:**
* TkinterWeb supports nearly 50 different image types through PIL.
* In order to load Scalable Vector Graphic images, CairoSVG, both PyCairo and PyGObject, or both PyCairo and Rsvg must also be installed. 

## Support & Donations

This project is released under the MIT License and is free to use, including for commercial purposes.

☕ If you’d like to support ongoing development and maintenance, please consider supporting this project by [buying me a coffee](https://buymeacoffee.com/andereoo) — any amount is hugely appreciated!

If you use this project in a commercial product or derive financial benefit from it, please kindly consider supporting its development with a donation. This helps cover maintenance time and ongoing improvements, which in turn will improve your own software!

## Contributing
**The best ways to contribute to this project are by submitting a [bug report](https://github.com/Andereoo/TkinterWeb/issues/new) to report bugs or suggest new features, or by submitting a [pull request](https://github.com/Andereoo/TkinterWeb/pulls) to offer fixes. Your help makes TkinterWeb become more stable and full-featured!**

Please check the [FAQs](https://tkinterweb.readthedocs.io/en/latest/faq.html) and [closed bugs](https://github.com/Andereoo/TkinterWeb/issues?q=is%3Aissue) before submitting a bug report to see if your question as already been answered.

## Credits
**TkinterWeb is powered by the [Tkhtml project](https://web.archive.org/web/20250219233338/http://tkhtml.tcl.tk/).**

Special thanks to [Christopher Chavez](https://github.com/chrstphrchvz), [Zamy846692](https://github.com/Zamy846692), [Jośe Fernando Moyano](https://github.com/jofemodo), [Bumshakalaka](https://github.com/Bumshakalaka), [Trov5](https://github.com/TRVRStash), [Mark Mayo](https://github.com/marksmayo), [Jaedson Silva](https://github.com/jaedsonpys), [Nick Moore](https://github.com/nickzoic), [Leonardo Saurwein](https://github.com/Sau1707), and [Hbregalad](https://github.com/hbregalad) for their code suggestions and pull requests.

Special thanks to [Christopher Chavez](https://github.com/chrstphrchvz), Jan Nijtmans, and everyone else in the tcl-core mailing list for the help making border rounding work on Windows and MacOSX, and to [Zamy846692](https://github.com/Zamy846692) for spearheading experimental Tkhtml development.

Thanks to the [TkinterHtml package](https://bitbucket.org/aivarannamaa/tkinterhtml) for providing the bindings on which this project is based and the [BRL-CAD project](https://github.com/BRL-CAD/brlcad) for providing modifications for Tkhtml on 64-bit Windows.

A huge thanks to everyone else who supported this project by reporting bugs and providing suggestions!
