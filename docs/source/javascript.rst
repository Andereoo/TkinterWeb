Using JavaScript
================

.. warning::
    JavaScript support is new in version 4.1. Make sure you are using the latest version of TkinterWeb.

Overview
--------

**JavaScript is fully supported through Mozilla's SpiderMonkey engine, but not all DOM commands are supported.**

See the :doc:`api/htmldocument` for an exhaustive list of supported DOM commands.

Only enable JavaScript on documents with code you know and trust and that only uses supported commands.

Setup
------

To enable JavaScript support in TkinterWeb, first install PythonMonkey using pip:

.. code-block:: console

   $ pip install pythonmonkey

Then add the parameter :attr:`javascript_enabled=True` when creating your :class:`~tkinterweb.HtmlFrame` or :class:`~tkinterweb.HtmlLabel` widget.

How-To
------

To change the color and text of a ``<p>`` element when clicked, you could use the following:

>>> yourhtmlframe = tkinterweb.HtmlFrame(root, javascript_enabled=True)
>>> yourhtmlframe.load_html("""
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

To register new JavaScript object, use :meth:`.HtmlFrame.register_JS_object`. This can be used to access Python variables, functions, and classes from JavaScript. For instance, to add a callback for the JavaScript ``alert()`` function:

>>> yourhtmlframe = tkinterweb.HtmlFrame(root, javascript_enabled=True)
>>> def open_alert_window(text):
>>>     ## Do stuff
>>> yourhtmlframe.register_JS_object("alert", open_alert_window)
>>> yourhtmlframe.load_html("<script>alert('Hello, world!')</script><p>Hello, world!</p>")

Using your own interpreter
--------------------------

Alternatively, you can register your own callback for ``<script>`` elements using the :attr:`on_script` parameter. This allows you to use your own interpreter or even simply embed Python code in your document instead:

>>> yourhtmlframe = tkinterweb.HtmlFrame(root)
>>> def handle_scripts(attributes, tagcontents):
>>>     ## Do stuff
>>> yourhtmlframe.configure(javascript_enabled=True, on_script=handle_scripts)
>>> yourhtmlframe.load_html("<div id='container'><script>// Do stuff</script><p>Test</p></div>")


You can also use the the :attr:`on_element_script` parameter to handle event scripts (i.e. handle an element's ``onclick`` attribute). The element's corresponding Tkhtml node, relevant event, and code to execute will be passed as parameters.

If needed you can always then create an :class:`~tkinterweb.dom.HTMLElement` instance from a Tkhtml node:

>>> from tkinterweb.dom import HTMLElement
>>> ...
>>> yourhtmlelement = HTMLElement(yourhtmlframe.document, yourtkhtmlnode)


It is also possible to interact with the document through Python instead. See :doc:`dom`.

Please report bugs or request new features on the `issues page <https://github.com/Andereoo/TkinterWeb/issues>`_.