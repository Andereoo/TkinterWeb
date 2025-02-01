## Geometry Management with TkinterWeb

## Overview
By default, Tkinter provides three geometry managers: `pack`, `place`, and `grid`. While these geometry managers are very powerful, achieving certain layouts, especially with scrolling, can be very time-consuming. TkinterWeb provides its own way to attach Tkinter widgets onto a screen, and handles layouts, images, scrolling, and much more for you. 

## How-To
To place a Tkinter widget inside an HTML document, add the `widgetid=[yourwidget]` attribute to any HTML element. 


**New since version 3.25.9:** Consider creating an `<object>` element with the `data=[yourwidget]` attribute instead. This improves load speed and allows the widget to match it's container's styling in real-time. For example, to add a button under some italic text, one could do:

```
yourframe = tkinterweb.HtmlFrame(root)
yourbutton = tkinter.Button(yourframe, text="Hello, world!", messages_enabled=False)
source_html = f"<i>This is some text</i><br><object handledelete data={str(yourbutton)}></object>"
yourframe.load_html(source_html) # or use add_html to add onto the existing document
```
  
- Add the `allowscrolling` attribute to allow scrolling the document when the mouse is over the button. Note that this has no effect on the HtmlLabel widget.

- Add the `handledelete` attribute to automatically call `destroy()` on the widget when it is removed from the page (i.e. if another webpage is loaded).

- Add the `allowstyling` attribute to automatically change the widget's background color, text color, and font to match the HTML element containing it. Note that this has no effect on widgets inserted using the `widgetid` attribute.

Widget position and sizing can be modified through CSS styling on the containing element.

## Widget Handling
Alongside the methods above and those outlined in [DOM Manipulation with TkinterWeb](/docs/DOM.md), the [HtmlFrame](HTMLFRAME.md) and [HtmlLabel](HTMLLABEL.md) widgets also provide three other commands to dynamically change the location of Tkinter widgets inside the HTML document after loading:

---

#### **replace_widget**(oldwidget, newwidget)
Removes the `oldwidget` from the document, and replaces it with the `newwidget`. Note that if both `oldwidget` and `newwidget` are currently shown in the document, their locations will be swapped.

Parameters
* **oldwidget** *(tkinter.Widget)* - Specifies the Tkinter widget to replace. This must be a valid Tkinter widget that is currently managed by TkinterWeb.
* **newwidget** *(tkinter.Widget)* - Specifies the new Tkinter widget to show. This may be any Tkinter widget.

---

#### **replace_element**(cssselector, newwidget)
Replaces the content of the element matching the specified CSS selector with the specified widget. This command will scan the document for any elements that match the specified CSS selector. If multiple elements match the specified selector, only the first element will be replaced. For example, the following code will replace the 'text' HTML element with a button. 
```
yourbutton = tkinter.Button(yourframe)
yourframe.load_html("<p id='text'>some text</p>")
yourframe.replace_element("#text", yourbutton)
```
Parameters
* **cssselector** *(string)* - Specifies the CSS selector to search for.
* **newwidget** *(tkinter.Widget)* - Specifies the new Tkinter widget to show. This may be any Tkinter widget.

---

#### **remove_widget**(oldwidget)
Removes the specified widget from the document. 

Parameters
* **oldwidget** *(tkinter.Widget)* - Specifies the Tkinter widget to remove. This must be a valid Tkinter widget that is currently managed by TkinterWeb.

---

## Example
This code will display a blue button on the left, an image in the center, and an orange button on the right. Clicking a button will flip it's location with the other button:
```
from tkinterweb import HtmlFrame
import tkinter as tk

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

myhtmlframe.load_html(f"""<html><body>
  <div widgetid={str(mybutton1)} style="float:left"></div>
  <div widgetid={str(mybutton2)} style="float:right"></div>
  <div style="margin:0 auto;width:100px;"><img src="https://wiki.tcl-lang.org/image/Tcl%2FTk+Core+Logo+520" style="width:84px; height:124px"></img></div>
  </body></html>""")

myhtmlframe.pack(fill="both", expand=True)
root.mainloop()
```
The equivalent code in pure Tkinter is certainly less straightfoward:

```
import tkinter as tk
from urllib.request import Request, urlopen
except ImportError
from io import BytesIO
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

---

Please report bugs or request new features on the [issues page](https://github.com/Andereoo/TkinterWeb/issues).
