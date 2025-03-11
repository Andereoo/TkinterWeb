Geometry Management with TkinterWeb
===================================

.. warning::
    The API changed significantly in version 4.0.0. See :doc:`upgrading` for details.

Overview
--------

**By default, Tkinter provides three geometry managers: pack, place, and grid. While these geometry managers are very powerful, achieving certain layouts, especially with scrolling, can be painful.**

**TkinterWeb provides a system for attaching Tkinter widgets onto the window, and handles layouts, images, scrolling, and much more for you.**

How-To
------

To place a Tkinter widget inside an HTML document, add the ``data=[yourwidget]`` attribute to an ``<object>`` element. For example, to add a button under some italic text, one could do:


>>> yourframe = tkinterweb.HtmlFrame(root)
>>> yourbutton = tkinter.Button(yourframe, text="Hello, world!", messages_enabled=False)
>>> source_html = f"<i>This is some text</i><br><object data={yourbutton}></object>"
>>> yourframe.load_html(source_html) # or use add_html to add onto the existing document
  
* Add the :attr:`allowscrolling` attribute to allow scrolling the document when the mouse is over the button. 
* Add the :attr:`handledelete` attribute to automatically call :meth:`~tkinter.Widget.destroy` on the widget when it is removed from the page (i.e. if another webpage is loaded).
* Add the :attr:`allowstyling` attribute to automatically change the widget's background color, text color, and font to match the containing HTML element.

Widget position and sizing can be modified using CSS styling on the widget's associated ``<object>`` element.

Widget Handling
---------------

Use the methods outlined in :doc:`dom` (new since version 3.25) and in the :doc:`api/htmlframe` to dynamically change the location of Tkinter widgets in the document after loading.

Example
-------

This code will display a blue button on the left, an image in the center, and an orange button on the right. Clicking a button will flip its location with the other button:

>>> from tkinterweb import HtmlFrame
>>> import tkinter as tk
>>> 
>>> root = tk.Tk()
>>> myhtmlframe = HtmlFrame(root)
>>> 
>>> mybutton1 = tk.Button(myhtmlframe, text="clickme!", bg="blue")
>>> mybutton2 = tk.Button(myhtmlframe, text="clickme!", bg="orange")
>>> 
>>> def mybutton1click():
>>>   myhtmlframe.replace_widget(mybutton1, mybutton2)
>>> def mybutton2click():
>>>   myhtmlframe.replace_widget(mybutton2, mybutton1)
>>>  
>>> mybutton1.config(command=mybutton1click)
>>> mybutton2.config(command=mybutton2click)
>>> 
>>> myhtmlframe.load_html(f"""<html><body>
>>>   <object widgetid={mybutton1} style="float:left"></object>
>>>   <object widgetid={mybutton2} style="float:right"></object>
>>>   <div style="margin:0 auto;width:100px;"><img src="https://wiki.tcl-lang.org/image/Tcl%2FTk+Core+Logo+520" style="width:84px; height:124px"></img></div>
>>>   </body></html>""")
>>> 
>>> myhtmlframe.pack(fill="both", expand=True)
>>> root.mainloop()

The equivalent code in pure Tkinter is certainly less straightfoward:

>>> import tkinter as tk
>>> from urllib.request import Request, urlopen
>>> except ImportError
>>> from io import BytesIO
>>> from PIL import Image, ImageTk
>>> 
>>> root = tk.Tk()
>>> container = tk.Frame(root, bg="white")
>>> mybutton1 = tk.Button(container, text="clickme!", bg="blue")
>>> mybutton2 = tk.Button(container, text="clickme!", bg="orange")
>>> 
>>> with urlopen(Request("https://wiki.tcl-lang.org/image/Tcl%2FTk+Core+Logo+520", headers={'User-Agent': 'Mozilla/5.1'})) as handle:
>>>     data = handle.read()
>>> 
>>> img = Image.open(BytesIO(data)).resize((84, 124))
>>> img = ImageTk.PhotoImage(img)
>>> 
>>> image = tk.Label(container, image=img, bd=0)
>>> loc = True
>>> def mybuttonclick():
>>>   global loc
>>>   if loc:
>>>       mybutton1.grid_forget()
>>>       mybutton2.grid_forget()
>>>       mybutton1.grid(row=0, column=4, sticky="n")
>>>       mybutton2.grid(row=0, column=0, sticky="n")
>>>       loc = False
>>>   else:
>>>       mybutton1.grid_forget()
>>>       mybutton2.grid_forget()
>>>       mybutton1.grid(row=0, column=0, sticky="n")
>>>       mybutton2.grid(row=0, column=4, sticky="n")
>>>       loc = True
>>>  
>>> mybutton1.config(command=mybuttonclick)
>>> mybutton2.config(command=mybuttonclick)
>>> 
>>> container.columnconfigure(1, weight=1)
>>> container.columnconfigure(3, weight=1)
>>> mybutton1.grid(row=0, column=0, sticky="n")
>>> image.grid(row=0, column=2)
>>> mybutton2.grid(row=0, column=4, sticky="n")
>>> 
>>> container.pack(expand=True, fill="both")
>>> root.mainloop()

Please report bugs or request new features on the `issues page <https://github.com/Andereoo/TkinterWeb/issues>`_.