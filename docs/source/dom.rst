DOM Manipulation with TkinterWeb
================================

.. warning::
    The API changed significantly in version 4.0.0. See :doc:`upgrading` for details.

Overview
--------

**TkinterWeb provides a handful of functions that allow for manipulation of the webpage. They are fashioned after common JavaScript functions.**


How-To
--------

To manipulate the Document Object Model, use the :attr:`HtmlFrame.document` property of your :class:`HtmlFrame` or :class:`HtmlLabel` widget (new since version 3.25). For example, to create a heading with blue text inside of an element with the id "container", one can use the following:

>>> yourhtmlframe = tkinterweb.HtmlFrame(root)
>>> yourhtmlframe.load_html("<div id='container'><p>Test</p></div>")
>>> container = yourhtmlframe.document.getElementById("container")
>>> new_header = yourhtmlframe.document.createElement("h1")
>>> new_header.textContent = "Hello, world!"
>>> new_header.style.color = "blue"
>>> container.appendChild(new_header)

To register a callback for ``<script>`` elements, use the :attr:`on_script` parameter:

>>> yourhtmlframe = tkinterweb.HtmlFrame(root)
>>> yourhtmlframe.load_html("<div id='container'><script>// Do stuff</script><p>Test</p></div>")
>>> def handle_scripts(attributes, tagcontents):
>>>     ## Do stuff
>>> yourhtmlframe.configure(on_script=handle_scripts)

See the :doc:`api/htmldocument` for a complete list of commands.

Please report bugs or request new features on the `issues page <https://github.com/Andereoo/TkinterWeb/issues>`_.