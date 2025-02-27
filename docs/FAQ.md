## Frequently Asked Questions

**How do I load websites or files?**

* Use the `load_website` or `load_file` commands. Alternatively, use the `load_url` command to load any generic url, but keep in mind that the url must be properly formatted, because the url scheme will not be automatically applied. As always, check out [the docs](https://github.com/Andereoo/TkinterWeb/blob/main/tkinterweb/docs/HTMLFRAME.md) for more information

**How do I manage clicks and use custom bindings?**

* The `on_link_click` configuration option can be used to assign a custom function to link clicks. Likewise the `on_form_submit` configuration option can be used for form submits. See the [API reference](https://github.com/Andereoo/TkinterWeb/blob/main/tkinterweb/docs/HTMLFRAME.md) for more information
* Like any other Tkinter widget, mouse and keyboard events can be bound to the HtmlFrame widget. See the [Tips and Tricks](https://github.com/Andereoo/TkinterWeb/blob/main/tkinterweb/docs/HTMLFRAME.md#tips-and-tricks) page for examples of binding navigation keys and opening menus on right-clicks.
 
**TkinterWeb is crashing. Help?**

* That is defenitely not normal. Make sure your are using the most up-to-date TkinterWeb version and have crash protection enabled.
* If you are using a ttk.Notebook in your app, see the question below.
* If all else fails, [file a bug report](https://github.com/Andereoo/TkinterWeb/issues/new). Post your operating system, Python version, and TkinterWeb version, as well as any error codes or instructions for reproducing the crash.

**My app crashes when I open a tab with an HtmlFrame in it.**

* Tkhtml (the underlying HTML engine) and the `ttk.Notebook` widget aren't compatable on 64-bit Windows.
* This is a known issue. Fixing this is beyond the scope of this project, but working around it is easy.
* Instead of using `ttk.Notebook`, use `tkinterweb.Notebook`. This is a wrapper around ttk.Notebook that is designed to be a drop-in replacement for the `ttk.Notebook` widget. It should look and behave exactly like a `ttk.Notebook` widget, but without the crashes. See [Bug #19](https://github.com/Andereoo/TkinterWeb/issues/19) for more information.
* Please note that after adding a widget to the Notebook (eg. `mynotebook.add(mywidget)`) there is no need to `pack` or `grid` the widget. This may raise errors. TkinterWeb's Notebook widget handles all this on its own.

**I get a ModuleNotFoundError after compiling my code.**

* On older TkinterWeb versions, when compiling your code, you might get an error such as `ModuleNotFoundError: No module named 'bindings'`
* Newer versions should present a popup saying `ModuleNotFoundError: The files required to run TkinterWeb could not be found`
* This occurs when your Python script bundler isn't finding all the files nessessary for running TkinterWeb. You need to force it to get all the TkinterWeb files.
* On PyInstaller: add the flag `--collect-all tkinterweb` when bundling your app.
* On py2app / py2exe: Add `'packages': ['tkinterweb']` to the OPTIONS variable in your setup file.

&nbsp;
&nbsp;
## A Note on Tkhtml Binaries
TkinterWeb supports all platforms but only ships with precompiled Tkhtml binaries for the most common platforms:
* x86_64 Windows, Linux, and macOS
* i686 Windows and Linux
* ARM64 Macos and Linux
* ARMv71 Linux

If you are encountering issues on your system or are are using an unsupported system, feel free to submit a bug report or feature request. You may need to compile Tkhtml on your system. See https://github.com/Andereoo/TkinterWeb-Tkhtml/.
