TkinterWeb Documentation
========================

The :class:`TkinterWeb` class is the low-level widget that bridges the gap between the underlying Tkhtml3 widget and Tkinter. 

Do not use this widget unless absolutely nessessary. Instead use the :class:`HtmlFrame` widget.

This widget can be accessed through the :attr:`~tkinterweb.HtmlFrame.html` property of the :class:`HtmlFrame` and :class:`HtmlLabel` widgets to access underlying settings and commands that are not a part of the :class:`HtmlFrame` API.

.. autoclass:: tkinterweb.TkinterWeb
   :members: