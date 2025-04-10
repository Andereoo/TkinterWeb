Frequently Asked Questions
==========================

**How do I load websites or files?**

* Use the :meth:`~tkinterweb.HtmlFrame.load_website` or :meth:`~tkinterweb.HtmlFrame.load_file` commands. Alternatively, use the :meth:`~tkinterweb.HtmlFrame.load_url` command to load any generic url, but keep in mind that the url must be properly formatted, because the url scheme will not be automatically applied. As always, check out the :doc:`api/htmlframe` for more information.

**How do I manage clicks and use custom bindings?**

* The :attr:`on_link_click` configuration option can be used to assign a custom function to link clicks. Likewise :attr:`on_form_submit` can be used to handle form submissions. See the :doc:`api/htmlframe` for more information.
* Like any other Tkinter widget, mouse and keyboard events can be bound to the :class:`~tkinterweb.HtmlFrame` widget. See the :doc:`usage` page for examples of binding navigation keys and opening menus on right-clicks.
 
**TkinterWeb is crashing. Help?**

* That is defenitely not normal. Make sure your are using the most up-to-date TkinterWeb version and have crash protection enabled.
* If you are using a :py:class:`ttk.Notebook` in your app, see the question below.
* If all else fails, `file a bug report <https://github.com/Andereoo/TkinterWeb/issues/new>`_. Post your operating system, Python version, and TkinterWeb version, as well as any error codes or instructions for reproducing the crash.

**My app crashes when I open a tab with an HtmlFrame in it.**

* Tkhtml (the underlying HTML engine) and the :py:class:`ttk.Notebook` widget aren't compatable on 64-bit Windows.
* This is a known issue. Fixing this is beyond the scope of this project, but working around it is easy.
* Instead of using :py:class:`ttk.Notebook`, use :class:`tkinterweb.Notebook`. This is a wrapper around ttk.Notebook that is designed to be a drop-in replacement for the :py:class:`ttk.Notebook` widget. It should look and behave exactly like a :py:class:`ttk.Notebook` widget, but without the crashes. See `bug #19 <https://github.com/Andereoo/TkinterWeb/issues/19>`_ for more information.
* Please note that after adding a widget to the Notebook (eg. ``mynotebook.add(mywidget)``) there is no need to call :py:func:`~tkinterweb.Widget.pack` or :py:func:`~tkinterweb.Widget.grid` the widget. This may raise errors. TkinterWeb's Notebook widget handles all this on its own.

**I get a ModuleNotFoundError after compiling my code.**

* When compiling your code, you might get an error popup saying ``ModuleNotFoundError: The files required to run TkinterWeb could not be found``
* Your app might also fail quietly if TkinterWeb's dependencies are not installed
* This occurs when your Python script bundler isn't finding all the files nessessary for running TkinterWeb. You need to force it to get all of TkinterWeb's files and dependencies.
* On PyInstaller: add the flag ``--collect-all tkinterweb --collect-all tkinterweb-tkhtml`` when bundling your app.
* On py2app / py2exe: Add ``'packages': ['tkinterweb', 'tkinterweb-tkhtml']`` to the ``OPTIONS`` variable in your setup file.