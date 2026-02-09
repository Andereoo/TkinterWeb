Using JavaScript
================

.. note::
    JavaScript support is new in version 4.1. Embedded Python support is new in version 4.19. Make sure you are using the latest version of TkinterWeb.

Overview
--------

**JavaScript support makes it easy to embed JavaScript or Python code in your document. JavaScript is fully supported through Mozilla's SpiderMonkey engine, but not all DOM commands are supported.**  See the :doc:`api/htmldocument` for an exhaustive list of supported DOM commands.

Setup
------

To enable JavaScript support in TkinterWeb, first install `PythonMonkey <http://pythonmonkey.io/>`_ using pip:

.. code-block:: console

   $ pip install pythonmonkey

Skip this step if you are embedding Python code in your document.

Or when installing TkinterWeb, use:

.. code-block:: console

   $ pip install tkinterweb[javascript]

Then add ``yourhtmlframe.configure(javascript_enabled=True)`` to your script or add the parameter ``javascript_enabled=True`` when creating your :class:`~tkinterweb.HtmlFrame`, :class:`~tkinterweb.HtmlLabel`, or :class:`~tkinterweb.HtmlText` widget.

**Only enable JavaScript in documents with code you know and trust.**

How-to
------

To change the color and text of a ``<p>`` element when clicked, you could use the following:

.. code-block:: python
    
    yourhtmlframe = tkinterweb.HtmlFrame(root, javascript_enabled=True)
    yourhtmlframe.load_html("""
        <script>
        function changeColor(element) {
            element.style.color = "blue"
            element.textContent = "I've been clicked!"
        }
        </script>
        <div id='container'><p onclick="changeColor(this)">Hello, world!</p></div>
        """)

Add the ``defer`` attribute to the relevant ``<script>`` element if you want it to run after the page loads. Otherwise, the script will be executed as soon as it is encountered in the document.

The following JavaScript event attributes are supported: ``onchange`` (``<input>`` elements only), ``onload``, ``onclick``, ``oncontextmenu``, ``ondblclick``, ``onmousedown``, ``onmouseenter``, ``onmouseleave``, ``onmousemove``, ``onmouseout``, ``onmouseover``, and ``onmouseup``.

Registering new JavaScript objects
----------------------------------

To register new JavaScript object, use :meth:`.JSEngine.register`. This can be used to access Python variables, functions, and classes from JavaScript. This, for instance, can be used to implement a ``window`` API or to add a callback for the JavaScript ``alert()`` function:

.. code-block:: python

    yourhtmlframe = tkinterweb.HtmlFrame(root, javascript_enabled=True)
    def open_alert_window(text):
        ## Do stuff
    yourhtmlframe.javascript.register("alert", open_alert_window)
    yourhtmlframe.load_html("<script>alert('Hello, world!')</script><p>Hello, world!</p>")

Embedding Python in your document
---------------------------------

To run embedded scripts as Python code instead of JavaScript, simply use the parameters ``javascript_enabled=True`` and ``javascript_backend="python"`` when creating your HTML widget. Ensure you are running code you trust.

Like normal JavaScript code, by default scripts can access the ``document`` property and events can also access the ``this`` property. You will still need to register objects if you want the document's scripts to be able to access other functions, classes or variables.

That's it!

Using your own interpreter
--------------------------

Alternatively, you can register your own callback for ``<script>`` elements using the :attr:`on_script` parameter:

.. code-block:: python

    yourhtmlframe = tkinterweb.HtmlFrame(root)
    def handle_scripts(attributes, tagcontents):
        ## Do stuff
    yourhtmlframe.configure(javascript_enabled=True, on_script=handle_scripts)
    yourhtmlframe.load_html("<div id='container'><script>// Do stuff</script><p>Test</p></div>")


You can also use the :attr:`on_element_script` parameter to handle event scripts (i.e. handle an element's ``onclick`` attribute). The element's corresponding Tkhtml node, relevant event, and code to execute will be passed as parameters.

If needed you can always then create an :class:`~tkinterweb.dom.HTMLElement` instance from a Tkhtml node:

.. code-block:: python
    
    from tkinterweb.dom import HTMLElement
    ...
    yourhtmlelement = HTMLElement(yourhtmlframe.document, yourtkhtmlnode)

-------------------

It is also possible to interact with the document through Python instead. See :doc:`dom`.

Please report bugs or request new features on the `issues page <https://github.com/Andereoo/TkinterWeb/issues>`_.