Document Object Model Documentation
===================================

.. warning::
    The API changed significantly in version 4.0.0. See Porting to TkinterWeb v4+ for details.

.. autoclass:: tkinterweb.dom.HTMLDocument
   :members:

.. autoclass:: tkinterweb.dom.HTMLElement
   :members:

.. autoclass:: tkinterweb.dom.CSSStyleDeclaration
   :members:

   All camel-cased supported CSS properties are also valid properties. Examples include ``color``, ``backgroundColor``, and ``fontFamily``.

   CSS properties can also be returned or set as key-value pairs (eg. ``CSSStyleDeclaration["background-color"]``)


All classes listed in this page have an ``html`` property corresponding to the element's :class:`~tkinterweb.TkinterWeb` instance and a ``node`` property corresponding to the Tkhtml node associated with the element.
