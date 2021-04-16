## *Geometry Magement with TkinterWeb*

## Overview
By default, Tkinter provides three geometry managers: `pack`, `place`, and `grid`. While these geometry managers are very powerful, achieving certain layouts, especially with scrolling, can be very time-consuming. TkinterWeb provides it's own way to attach Tkinter widgets onto a screen, and handles layouts, images, scrolling, and much more for you. 

**TkinterWeb not only lets you put HTML inside Tkinter widgets, but it also lets you put Tkinter widgets inside HTML. This means that all the dirty work is done for you, meaning that you can focus on building your app instead fighting with layouts and looks.**

## How-To
To place a Tkinter widget inside an HTML document, add the `widgetid=[yourwidget]` attribute to any HTML element. For example, to add a button under some italic text, one could do:

```
mybutton = tkinter.Button(myframe)
myframe.load_html("<i>This is some text</i><div widgetid="+str(mybutton)+"></div>")
```
The above code will replace the `<div>` element with the `mybutton` Button. This `<div>` element will still behave as it would normally. This means that it is very easy to set the location of the button, the size, and much more using CSS. For example, `<div style="width:50px" widgetid="+str(mybutton)+"></div>` would make the button exactly 50 pixels wide.
  
Add the attribute `allowscrolling="yes"` to allow scrolling the document when the mouse is over the button. Note that this has no effect on the HtmlLabel widget.

## Widget Handling
Currently, the [HtmlFrame](HTMLFRAME.md) and [HtmlLabel](HTMLLABEL.md) widgets provide three commands to dynamically change the location of Tkinter widgets inside the HTML document after it has been loaded:

---

#### **replace_widget**(oldwidget, newwidget)
Removes the `oldwidget` from the document, and replaces it with the `newwidget`. Note that if both `oldwidget` and `newwidget` are currently shown in the document, their locations will be swapped.

Parameters
* **oldwidget** *(tkinter.Widget)* - Specifies the Tkinter widget to replace. This must be a valid Tkinter widget that is currently managed by TkinterWeb.
* **newwidget** *(tkinter.Widget)* - Specifies the new Tkinter widget to show. This may be any Tkinter widget.

---

#### **replace_element**(cssselector, newwidget)
Replaces the content of the element matching the specified CSS selector with the `newwidget`. This command will scan the document for any elements that match the specified CSS selector. If multiple elements match the specified selector, only the first element will be replaced. For example, the following code will replace the 'myparagraph' HTML element with a button. 
```
mybutton = tkinter.Button(myframe)
myframe.load_html("<p id='myparagraph'>some text</p>")
myframe.replace_element("#myparagraph", mybutton)
```
Parameters
* **cssselector** *(string)* - Specifies the CSS selector to search for.
* **newwidget** *(tkinter.Widget)* - Specifies the new Tkinter widget to show. This may be any Tkinter widget.

---

#### **remove_widget**(oldwidget)
Removes the `oldwidget` from the document. 
This method is experimental and may cause issues. If you encounter any issues, please [report them](https://github.com/Andereoo/TkinterWeb/issues).

Parameters
* **oldwidget** *(tkinter.Widget)* - Specifies the Tkinter widget to remove. This must be a valid Tkinter widget that is currently managed by TkinterWeb.

---

#### **add_html**(html_source)
Adds HTML onto the end of the current document. Tkinter widgets may be added in the `html_source` using the `widgetid` attribute (see above). This may be used to add widgets to the end of the currently displayed document.

Parameters
* **html_source** *(string)* - Specifies the code to parse and add to the end of the document. Must be valid HTML code.

---

## Example
This code will display a blue button on the left, an image in the center, and an orange button on the right. Clicking a button will flip it's location with the other button:
```
from tkinterweb import HtmlFrame
try:
  import tkinter as tk #python3
except ImportError:
  import Tkinter as tk #python2
root = tk.Tk()
myhtmlframe = HtmlFrame(root)

mybutton1 = tk.Button(myhtmlframe, text="clickme!", bg="blue")
mybutton2 = tk.Button(myhtmlframe, text="clickme!", bg="orange")

def mybutton1click():
  myhtmlframe.replace_widget(mybutton1, mybutton2)
def mybutton2click():
  myhtmlframe.replace_widget(mybutton2, mybutton1)
 
mybutton1.config(command=mybutton1click)
mybutton2.config(command=mybutton2click)

myhtmlframe.load_html("""<html><body>
  <div widgetid="""+str(mybutton1)+""" style="float:left"></div>
  <div widgetid="""+str(mybutton2)+""" style="float:right"></div>
  <div style="margin:0 auto;width:100px;"><img src="https://wiki.tcl-lang.org/image/Tcl%2FTk+Core+Logo+520" style="width:84px; height:124px"></img></div>
  </body></html>""")

myhtmlframe.pack(fill="both", expand=True)
root.mainloop()
```
The equivelent code in pure Tkinter is much less straightfoward:

```
try:
  import tkinter as tk #python3
except ImportError:
  import Tkinter as tk #python2
try:
    from urllib.request import Request, urlopen
except ImportError: # Python 2
    from urllib2 import urlopen, Request
try:
    from io import BytesIO
except ImportError: # Python 2
    import BytesIO
from PIL import Image, ImageTk

root = tk.Tk()
container = tk.Frame(root, bg="white")
mybutton1 = tk.Button(container, text="clickme!", bg="blue")
mybutton2 = tk.Button(container, text="clickme!", bg="orange")

with urlopen(Request("https://wiki.tcl-lang.org/image/Tcl%2FTk+Core+Logo+520", headers={'User-Agent': 'Mozilla/5.1'})) as handle:
    data = handle.read()

img = Image.open(BytesIO(data)).resize((84, 124))
img = ImageTk.PhotoImage(img)

image = tk.Label(container, image=img, bd=0)
loc = True
def mybuttonclick():
  global loc
  if loc:
      mybutton1.grid_forget()
      mybutton2.grid_forget()
      mybutton1.grid(row=0, column=4, sticky="n")
      mybutton2.grid(row=0, column=0, sticky="n")
      loc = False
  else:
      mybutton1.grid_forget()
      mybutton2.grid_forget()
      mybutton1.grid(row=0, column=0, sticky="n")
      mybutton2.grid(row=0, column=4, sticky="n")
      loc = True
 
mybutton1.config(command=mybuttonclick)
mybutton2.config(command=mybuttonclick)

container.columnconfigure(1, weight=1)
container.columnconfigure(3, weight=1)
mybutton1.grid(row=0, column=0, sticky="n")
image.grid(row=0, column=2)
mybutton2.grid(row=0, column=4, sticky="n")

container.pack(expand=True, fill="both")
root.mainloop()
```

## Questions, bugs, and features
Please report bugs or request new features in the [issues page](https://github.com/Andereoo/TkinterWeb/issues).

If you need some help using TkinterWeb in your app, also feel free to head over to the issues page.
