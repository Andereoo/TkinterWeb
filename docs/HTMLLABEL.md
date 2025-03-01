> [!WARNING]
> The API changed significantly in version 4.0.0. See [Porting to TkinterWeb v4+](UPGRADING.md) for details.

> [!IMPORTANT]
> The TkinterWeb documentation has moved to https://tkinterweb.readthedocs.io/en/latest/index.html. See you there!

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
* `master` Parent (Tkinter widget)
* `text` Set the content of the widget (string) **Default: ""**
* `**kwargs` Any other optional `HtmlFrame` arguments

The HtmlLabel class inherits from the HtmlFrame. For a complete list of avaliable methods, configuration options, generated events, and state variables, see the [HtmlFrame docs](HTMLFRAME.md#useful-methods).
