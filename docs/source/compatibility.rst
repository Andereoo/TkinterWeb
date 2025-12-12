System and Webpage Compatibility
================================

System compatibility
--------------------

**TkinterWeb supports all platforms but only ships with precompiled Tkhtml binaries for the most common platforms:**

* x86_64 Windows, Linux, and macOS
* i686 Windows and Linux
* ARM64 Macos and Linux
* ARMv71 Linux

If your system is unsupported, compile and install Tkhtml by visiting https://github.com/Andereoo/TkinterWeb-Tkhtml/tree/3.1-TclTk9 and running ``python compile.py --install``.

Alternatively, you can install Tkhtml system-wide (i.e. through your system package manager) and then add the parameter :attr:`use_prebuilt_tkhtml=False` when creating your :class:`~tkinterweb.HtmlFrame` or :class:`~tkinterweb.HtmlLabel` widget to use the system's Tkhtml. Keep in mind that some features will no longer work.

If you are encountering issues, feel free to submit a bug report or feature request.

The experimental Tkhtml version is not provided as a pre-built binary but can be compiled from the source code at https://github.com/Andereoo/TkinterWeb-Tkhtml/tree/experimental. This version has better cross-platform compatibility, is printable, and introduces support for some new CSS3 properties!

Webpage compatibility
---------------------

**HTML/CSS:**

* TkinterWeb supports HTML 4.01 and CSS 2.1. A full list of supported CSS declarations can be found at `http://tkhtml.tcl.tk/support.html <https://web.archive.org/web/20250325123206/http://tkhtml.tcl.tk/support.html>`_.  ``overflow-x`` is also supported on ``body`` and ``html`` elements.
* Most CSS pseudo-elements, such as ``:hover`` and ``:active`` are also supported.
* On 64-bit Windows and Linux, if the TkinterWeb-Tkhtml-Extras package is installed, ``border-radius`` and more cursor options are also supported. 

**JavaScript:**

* JavaScript partly supported at the moment. See :doc:`javascript` for more information.

  * To use JavaScript, :py:mod:`PythonMonkey`  must be installed.

* It is also possible for the user to connect their own JavaScript interpreter or manipulate the document through Python. See :doc:`javascript` and :doc:`dom` for more information.

**Images:**

* TkinterWeb supports nearly 50 different image types through :py:mod:`PIL`.

* In order to load Scalable Vector Graphic images, :py:mod:`CairoSVG`, both :py:mod:`PyCairo` and :py:mod:`PyGObject`, or both :py:mod:`PyCairo` and :py:mod:`Rsvg` must also be installed. 

-------------------

Please report bugs or request new features on the `issues page <https://github.com/Andereoo/TkinterWeb/issues>`_.