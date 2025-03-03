TkinterWeb Documentation
========================

The :class:`~tkinterweb.TkinterWeb` class is the low-level widget that bridges the gap between the underlying Tkhtml3 widget and Tkinter. 

Do not use this widget unless absolutely nessessary. Instead use the :class:`~tkinterweb.HtmlFrame` widget.

This widget can be accessed through the :attr:`~tkinterweb.HtmlFrame.html` property of the :class:`~tkinterweb.HtmlFrame` and :class:`~tkinterweb.HtmlLabel` widgets to access underlying settings and commands that are not a part of the :class:`~tkinterweb.HtmlFrame` API.

.. autoclass:: tkinterweb.TkinterWeb
   :members:


The :class:`~tkinterweb.TkinterWeb` class also includes dozens of variables that can be used to change the widget's behaviour or to get the its state (eg. access embedded input widgets or the nodes under the mouse). If this widget is being used through the :class:`~tkinterweb.HtmlFrame` or :class:`~tkinterweb.HtmlLabel` widget, many of these variables are exposed as properties or as configuration options, but many more are unique and could be useful in certain cases. 

Please see the source code for more details.