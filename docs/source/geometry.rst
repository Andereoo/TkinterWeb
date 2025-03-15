Embedding Widgets
=================

.. warning::
    The API changed significantly in version 4.0.0. See :doc:`upgrading` for details.

Overview
--------

By default, Tkinter provides three geometry managers: pack, place, and grid. While these geometry managers are very powerful, achieving certain layouts, especially with scrolling, can be painful.

**TkinterWeb provides a system for attaching Tkinter widgets onto the window, and handles layouts, images, selection, scrolling, and much more for you.**

How-To
------

To place a Tkinter widget inside an HTML document, add the ``data=[yourwidget]`` attribute to an ``<object>`` element. For example, to add a button under some italic text, one could do:

.. code-block:: python

    yourframe = tkinterweb.HtmlFrame(root)
    yourbutton = tkinter.Button(yourframe, text="Hello, world!")
    source_html = f"<i>This is some text</i><br><object data={yourbutton}></object>"
    yourframe.load_html(source_html) # or use add_html to add onto the existing document
  
* Add the :attr:`allowscrolling` attribute to allow scrolling the document when the mouse is over the button. 
* Add the :attr:`handledelete` attribute to automatically call :meth:`~tkinter.Widget.destroy` on the widget when it is removed from the page (i.e. if another webpage is loaded).
* Add the :attr:`allowstyling` attribute to automatically change the widget's background color, text color, and font to match the containing HTML element.

Widget position and sizing can be modified using CSS styling on the widget's associated ``<object>`` element.

To get the element containing your widget, either use :meth:`.HtmlFrame.widget_to_element`.

Widget Handling
---------------

You can also set, remove, or change the widget in any element later (new since version 4.1.4):

.. code-block:: python

    yourbutton = tkinter.Button(yourframe, text="Hello, world!")
    ...
    yourelement = yourframe.document.getElementById("#container") # get the element to fill
    yourelement.widget = yourbutton # set the element's widget

The widget can be removed from the element via ``yourelement.widget = None``.

See :doc:`dom` (new since version 3.25) for more details.

Please report bugs or request new features on the `issues page <https://github.com/Andereoo/TkinterWeb/issues>`_.