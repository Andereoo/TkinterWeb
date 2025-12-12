Getting Started
===============

.. note::
    The API changed significantly in version 4. See :doc:`the changelog <upgrading>` for details.

Installation
------------

To use TkinterWeb, first install it using pip:

.. code-block:: console

   $ pip install tkinterweb[recommended]

.. tip::
    
    You can also choose from the following extras:

    .. code-block:: console

        $ pip install tkinterweb[html, images, svg, javascript, requests]
    
    Run ``pip install tkinterweb[full]`` to install all optional dependencies or ``pip install tkinterweb`` to install the bare minimum.

Run the TkinterWeb demo to see if it worked!

>>> from tkinterweb import Demo
>>> Demo()

.. image:: ../../images/tkinterweb-demo.png

TkinterWeb requires :py:mod:`Tkinter`, :py:mod:`TkinterWeb-Tkhtml`, :py:mod:`PIL`, and :py:class:`PIL.ImageTk`. All dependencies should be installed when installing TkinterWeb, but on some systems :py:class:`PIL.ImageTk` may need to be installed seperately in order to load most image types.

Getting started
----------------

TkinterWeb is very easy to use! Here is an example:

.. code-block:: python

    import tkinter as tk
    from tkinterweb import HtmlFrame # import the HtmlFrame widget
    
    root = tk.Tk() # create the Tkinter window
    
    yourhtmlframe = HtmlFrame(root) # create the HtmlFrame widget
    yourhtmlframe.load_html("<h1>Hello, World!</h1>") # load some HTML code
    yourhtmlframe.pack(fill="both", expand=True) # attach the HtmlFrame widget to the window
    
    root.mainloop()

.. tip::
    To load a website, call ``yourhtmlframe.load_website("www.yourwebsite.com")``.
    
    To load a file, call ``yourhtmlframe.load_file("/path/to/your/file.html")``.
    
    To load any generic url, call ``yourhtmlframe.load_url(yourwebsiteorfile)``. Keep in mind that the url must be properly formatted and include the url scheme.

The :class:`~tkinterweb.HtmlFrame` widget behaves like any other Tkinter widget and supports bindings. It also supports link clicks, form submittions, website title changes, and much, much more! Refer below for more tips and tricks!

Tips and tricks
---------------

Creating bindings
~~~~~~~~~~~~~~~~~

Like any other Tkinter widget, mouse and keyboard events can be bound to the :class:`~tkinterweb.HtmlFrame` widget.

The following is an example of the usage of bingings to show a menu:

.. code-block:: python

    def on_right_click(event):
        # Get the element under the mouse and its url
        element = yourhtmlframe.get_currently_hovered_element()
        url = element.getAttribute("href")

        if url:
            # Resolve the url to ensure it is a full url
            url = yourhtmlframe.resolve_url(url)

            # Create the menu and add a button with the url
            menu = tk.Menu(root, tearoff=0)
            menu.add_command(label="Open %s" % url, 
                command=lambda url=url: yourhtmlframe.load_url(url))

            # Show the menu
            menu.tk_popup(event.x_root, event.y_root, 0)

    yourhtmlframe.bind("<Button-3>", on_right_click)

This will make a popup open when the user right-clicks on a link. Clicking the link shown in the popup would load the website.

Note that some keypress events are automatically bound to the widget. If you notice a feature unintentionally stops working after adding a binding, consider using ``bind(event, callback, add="+")`` to add your binding instead of replacing the default one.

.. tip::
    Since version 4.10, you can also bind to a specific HTML element! See :ref:`binding-to-an-element` for more details.

Changing the title
~~~~~~~~~~~~~~~~~~

To change the title of the window every time the title of a website changes, use the following:

.. code-block:: python

    def change_title(event):
        root.title(yourhtmlframe.title) # change the title
        
    yourhtmlframe.bind("<<TitleChanged>>", change_title)

Similarily, the ``<<IconChanged>>`` event fires when the website's icon changes.

Handling url changes
~~~~~~~~~~~~~~~~~~~~

Normally, a website's url may change when it is loaded. For example, "https://github.com" will redirect to "https://www.github.com". This can be handled with a binding to ``<<UrlChanged>>``:

.. code-block:: python

    def url_changed(event):
        updated_url = yourhtmlframe.current_url
        ### Do stuff, such as change the content of an address bar
        
    yourhtmlframe.bind("<<UrlChanged>>", url_changed)

This is highly recomended if your app includes an address bar. This event will fire on page redirects and url changes when a page stops loading.


Searching the page
~~~~~~~~~~~~~~~~~~

Use :meth:`~tkinterweb.HtmlFrame.find_text` to search the page for specific text. To search the document for the word 'python', for example, the following can be used:

.. code-block:: python

    number_of_matches = yourhtmlframe.find_text("python")

Or, to select the second match found:

.. code-block:: python

    number_of_matches = yourhtmlframe.find_text("python", 2)

Refer to the API reference for more information.

.. tip::
    
    Check out `bug 18 <https://github.com/Andereoo/TkinterWeb/issues/18#issuecomment-881649007>`_ or the `sample web browser <https://github.com/Andereoo/TkinterWeb/blob/main/examples/TkinterWebBrowser.py>`_ for a sample find bar!

Done loading?
~~~~~~~~~~~~~

The ``<<DoneLoading>>`` event fires when the document is done loading. 

When binding to ``<<DoneLoading>>`` to, for example, change a 'stop' button to a 'refresh' button, it is generally a good idea to bind to ``<<DownloadingResource>>`` to do the opposite. Otherwise, the document may show that is is done loading while it is still loading.

Stop loading
~~~~~~~~~~~~

The method :meth:`~tkinterweb.HtmlFrame.stop` can be used to stop loading a webpage. If :meth:`~tkinterweb.HtmlFrame.load_url`, :meth:`~tkinterweb.HtmlFrame.load_website`, or :meth:`~tkinterweb.HtmlFrame.load_file` was used to load the document, passing ``yourhtmlframe.current_url`` with ``force=True``  will force a page refresh.

Handling link clicks
~~~~~~~~~~~~~~~~~~~~

Link clicks can also be easily handled. By default, when a link is clicked, it will be automatically loaded.
To, for example, run some code before loading the new website, use the following: 

.. code-block:: python

    yourhtmlframe = HtmlFrame(master, on_link_click=load_new_page)
    
    def load_new_page(url):
        ### Do stuff
        yourhtmlframe.load_url(url) # load the new website    

Similarily, :attr:`on_form_submit` can be used to override the default form submission handlers.

Zooming
~~~~~~~

Setting the zoom of the :class:`~tkinterweb.HtmlFrame` widget is very easy. This can be used to improve accessibility in your application. To set the zoom to 2x magnification the following can be used: 

.. code-block:: python

    yourhtmlframe = HtmlFrame(master, zoom=2)
    ### Or yourhtmlframe.configure(zoom=2)
    ### Or yourhtmlframe["zoom"] = 2

To scale only the text, use ``fontscale=2`` instead.

Embedding a widget
~~~~~~~~~~~~~~~~~~

There are many ways to embed widgets in an :class:`~tkinterweb.HtmlFrame` widget. One way is to use ``<object>`` elements:

.. code-block:: python

    yourcanvas = tkinter.Canvas(yourhtmlframe)
    yourhtmlframe.load_html(f"<p>This is a canvas!</p><object data="{yourcanvas}"></object>")

Refer to :doc:`geometry` for more information.

Manipulating the DOM
~~~~~~~~~~~~~~~~~~~~

Refer to :doc:`dom` (new in version 3.25).

Using JavaScript
~~~~~~~~~~~~~~~~

Refer to :doc:`javascript` (new in version 4.1).

Making the page editable
~~~~~~~~~~~~~~~~~~~~~~~~

Refer to :doc:`caret` (new in version 4.8).

Using dark mode
~~~~~~~~~~~~~~~

You can set ``dark_theme_enabled=True`` when creating your :class:`~tkinterweb.HtmlFrame` or calling :meth:`~tkinterweb.HtmlFrame.configure` to turn on dark mode and automatically modify page colours.

If you set ``image_inversion_enabled=True``, an algorithm will attempt to detect and invert images with a predominantly light-coloured background. This helps make light-coloured images or pictures with a white background darker.

Refresh the page for these features to take full effect. This features may cause hangs or crashes on more complex websites.

-------------------

See the :doc:`api/htmlframe` for a complete list of available commands.
