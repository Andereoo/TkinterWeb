Bindings Documentation
======================

.. note::
   This API has changed significantly recently. See :doc:`the changelog <../upgrading>` for details.


The following objects offer the core bindings to the Tkhtml3 HTML widget and are largely internal. You will likely never need to access them, but they are described here just in case.

.. autoclass:: tkinterweb.TkinterWeb
   :members:


The :class:`~tkinterweb.TkinterWeb` class and its extensions also include many variables that can be used to change the widget's behaviour or to get the its state (eg. access embedded input widgets or the nodes under the mouse). If this widget is being used through the :class:`~tkinterweb.HtmlFrame` or :class:`~tkinterweb.HtmlLabel` widget, many of these variables are exposed as properties or as configuration options, but many more are unique and could be useful in certain cases. 

Please see the source code for more details.


.. autoclass:: tkinterweb.TkHtmlParsedURI
   :members: