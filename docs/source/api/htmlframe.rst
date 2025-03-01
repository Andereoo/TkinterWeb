HTML Widgets Documentation
==========================

.. warning::
    The API changed significantly in version 4.0.0. See :doc:`upgrading` for details.

The :class:`~tkinterweb.HtmlFrame` widget is a Tkinter frame that provides additional functionality to the :class:`~tkinterweb.TkinterWeb` widget by adding automatic scrollbars, error handling, and many convenience methods into one embeddable and easy to use widget.

The :class:`~tkinterweb.HtmlFrame` widget is also capable managing other Tkinter widgets, which enables combining Tkinter widgets and HTML elements.


.. autoclass:: tkinterweb.HtmlFrame
   :members:

This widget also emits the following Tkinter virtual events that can be bound to:

* ``<<DownloadingResource>>``/:py:attr:`utilities.DOWNLOADING_RESOURCE_EVENT`: Generated whenever a new resource is being downloaded.
* ``<<DoneLoading>>``/:py:attr:`utilities.DONE_LOADING_EVENT`: Generated whenever all outstanding resources have been downloaded. This is generally a good indicator as to when the website is done loading, but may be generated multiple times while loading a page.
* ``<<UrlChanged>>``/:py:attr:`utilities.URL_CHANGED_EVENT`: Generated whenever the url the widget is navigating to changes. Use :py:attr:`current_url` to get the url.
* ``<<IconChanged>>``/:py:attr:`utilities.ICON_CHANGED_EVENT`: Generated whenever the icon of a webpage changes. Use :py:attr:`icon` to get the icon.
* ``<<TitleChanged>>``/:py:attr:`utilities.TITLE_CHANGED_EVENT`: Generated whenever the title of a website or file has changed. Use :py:attr:`title` to get the title.
* ``<<Modified>>``: Generated whenever the content of any ``<input>`` element changes.

.. autoclass:: tkinterweb.HtmlLabel
   :members: