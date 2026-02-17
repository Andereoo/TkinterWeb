HTML Widgets Documentation
==========================

.. note::
    The API changed significantly in version 4. See :doc:`the changelog <../upgrading>` for details.

The :class:`~tkinterweb.HtmlFrame` widget is a Tkinter frame that provides additional functionality to the :class:`~tkinterweb.TkinterWeb` widget by adding automatic scrollbars, error handling, and many convenience methods into one embeddable and easy to use widget.

The :class:`~tkinterweb.HtmlFrame` widget is also capable managing other Tkinter widgets, making it easy to combine Tkinter widgets and HTML elements.


.. autoclass:: tkinterweb.HtmlFrame
   :members:

This widget also emits the following Tkinter virtual events that can be bound to:

* ``<<DownloadingResource>>``/:py:attr:`utilities.DOWNLOADING_RESOURCE_EVENT`: Generated whenever a new resource is being downloaded.
* ``<<DoneLoading>>``/:py:attr:`utilities.DONE_LOADING_EVENT`: Generated whenever all outstanding resources have been downloaded. This is generally a good indicator as to when the website is done loading, but may be generated multiple times while loading a page.
* ``<<DOMContentLoaded>>``/:py:attr:`utilities.DOM_CONTENT_LOADED_EVENT`: Generated once the page content has loaded. The page may not be done loading, but at this point it is possible to interact with the DOM.
* ``<<UrlChanged>>``/:py:attr:`utilities.URL_CHANGED_EVENT`: Generated whenever the url the widget is navigating to changes. Use :attr:`.HtmlFrame.current_url` to get the url.
* ``<<IconChanged>>``/:py:attr:`utilities.ICON_CHANGED_EVENT`: Generated whenever the icon of a webpage changes. Use :attr:`.HtmlFrame.icon` to get the icon.
* ``<<TitleChanged>>``/:py:attr:`utilities.TITLE_CHANGED_EVENT`: Generated whenever the title of a website or file has changed. Use :attr:`.HtmlFrame.title` to get the title.
* ``<<Modified>>```/:py:attr:`utilities.FIELD_CHANGED_EVENT`: Generated whenever the content of an interactive element changes.

.. autoclass:: tkinterweb.HtmlLabel
   :members:

.. autoclass:: tkinterweb.HtmlText
   :members:

.. autoclass:: tkinterweb.HtmlParse
   :members: