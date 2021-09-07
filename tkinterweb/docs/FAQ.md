## Frequently Asked Questions

**How do I load websites or files?**

* Use the `load_website` or `load_file` commands. As always, check out [the docs](https://github.com/Andereoo/TkinterWeb/blob/main/tkinterweb/docs/HTMLFRAME.md) for more information

**TkinterWeb is crashing. Help?**

* That is defenitely not normal. Make sure your are using the most up-to-date TkinterWeb version and have crash protection enabled.
* If you are using a ttk.Notebook in your app, see the question below.
* If all else fails, [file a bug report](https://github.com/Andereoo/TkinterWeb/issues/new). Post your operating system, Python version, and TkinterWeb version, as well as any error codes or instructions for reproducing the crash.

**My app crashes when I open the tab with an HtmlFrame in it?**

* Tkhtml (which powers TkinterWeb) and the ttk.Notebook widget aren't compatable on some platforms, namely 64-bit Windows, causing crashes.
* This is a known issue with an easy fix.
* Instead of using ttk.Notebook, use tkinterweb.Notebook. This is a wrapper around ttk.Notebook that is designed to be a drop-in replacement for the ttk.Notebook widget. It should look and behave exactly like a ttk.Notebook widget, but without the crashes. See [Bug #19](https://github.com/Andereoo/TkinterWeb/issues/19) for more information.
* If TkinterWeb's Notebook widget isn't working properly, [file a bug report](https://github.com/Andereoo/TkinterWeb/issues/new) so that it can be fixed!

**I get a ModuleNotFoundError after compiling my code.**

* On older TkinterWeb versions, when compiling your code, you might get an error such as `ModuleNotFoundError: No module named 'bindings'`
* Newer versions should present a popup saying `ModuleNotFoundError: The files required to run TkinterWeb could not be found`
* This occurs when your Python script bundler isn't finding all the files nessessary for running TkinterWeb. You need to force it to get all the TkinterWeb files.
* On PyInstaller: add the flag `--collect-all tkinterweb` when bundling your app.
* On py2app / py2exe: Add `'packages': ['tkinterweb']` to the OPTIONS variable in your setup file.
