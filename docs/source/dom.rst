DOM Manipulation with TkinterWeb
================================

.. warning::
    The API changed significantly in version 4.0.0. See :doc:`../upgrading` for details.

Overview
--------

**TkinterWeb provides a handful of functions that allow for manipulation of the webpage. They are fashioned after common JavaScript functions.**


How-To
--------

To manipulate the Document Object Model, use the :attr:`~tkinterweb.HtmlFrame.document` property of your :class:`~tkinterweb.HtmlFrame` or :class:`~tkinterweb.HtmlLabel` widget. For example, to create a heading with blue text inside of an element with the id "container", one can use the following:

>>> yourhtmlframe = tkinterweb.HtmlFrame(root)
>>> yourhtmlframe.load_html("<div id='container'><p>Test</p></div>")
>>> container = yourhtmlframe.document.getElementById("container")
>>> new_header = yourhtmlframe.document.createElement("h1")
>>> new_header.textContent = "Hello, world!"
>>> new_header.style.color = "blue"
>>> container.appendChild(new_header)

See the :doc:`api/htmldocument` for an exhaustive list of supported commands.

See :doc:`javascript` for information on manipulating the DOM through JavaScript.

Please report bugs or request new features on the `issues page <https://github.com/Andereoo/TkinterWeb/issues>`_.