System and Webpage Compatibility
================================

Webpage Compatibility
---------------------

**HTML/CSS:**

* TkinterWeb supports HTML 4.01 and CSS 2.1. A full list of supported CSS declarations can be found at http://tkhtml.tcl.tk/support.html. 
* Most CSS pseudo-elements, such as ``:hover`` and ``:active`` are also supported. 

**JavaScript:**

* JavaScript partly supported at the moment. See :doc:`javascript` for more information.

  * To use JavaScript, :py:mod:`PythonMonkey`  must be installed.

* It is also possible for the user to connect a JavaScript interpreter and then manipulate the document through Python. See :doc:`javascript` and :doc:`dom` for more information.

**Images:**

* TkinterWeb supports nearly 50 different image types through :py:mod:`PIL`.

  * To load Scalable Vector Graphic images, :py:mod:`CairoSVG`, both :py:mod:`PyCairo` and :py:mod:`PyGObject`, or both :py:mod:`PyCairo` and :py:mod:`Rsvg` must also be installed. 
  
* Without these packages, TkinterWeb will still function properly, but SVG files will not be shown.


A Note on Tkhtml Binaries
-------------------------

**TkinterWeb supports all platforms but only ships with precompiled Tkhtml binaries for the most common platforms:**

* x86_64 Windows, Linux, and macOS
* i686 Windows and Linux
* ARM64 Macos and Linux
* ARMv71 Linux

Alternatively, you can install Tkhtml system-wide (i.e. through your system package manager) and then add the parameter :attr:`use_prebuilt_tkhtml=False` when creating your :class:`~tkinterweb.HtmlFrame` or :class:`~tkinterweb.HtmlLabel` widget to use the system's Tkhtml. Keep in mind that some crash protection features will no longer work.

If you are encountering issues on your system or are are using an unsupported system, feel free to submit a bug report or feature request. You may need to compile Tkhtml on your system. See https://github.com/Andereoo/TkinterWeb-Tkhtml/.
