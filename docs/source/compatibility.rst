System and Webpage Compatability
================================

Webpage Compatability
---------------------

**HTML/CSS:**

* TkinterWeb supports HTML 4.01 and CSS 2.1. A full list of supported CSS declarations can be found at http://tkhtml.tcl.tk/support.html. 
* Most CSS pseudo-elements, such as ``:hover`` and ``:active`` are also supported. 

**JavaScript:**

* Javascript is not supported at the moment. It is up to the user to connect a JavaScript interpreter by registering a callback for scripts and manipulating the document through Python. See :doc:`dom`.

**Images:**

* TkinterWeb supports nearly 50 different image types through :py:mod:`PIL`. However, in order to load Scalable Vector Graphic images:
    * :py:mod:`PyCairo` or :py:mod:`PyGObject` must be installed. 
    * Either :py:mod:`Rsvg`, :py:mod:`PyGObject`, or :py:mod:`CairoSVG` must also be installed. 
* Without these packages, TkinterWeb will still function properly, but SVG files will not be shown.


A Note on Tkhtml Binaries
-------------------------

**TkinterWeb supports all platforms but only ships with precompiled Tkhtml binaries for the most common platforms:**

* x86_64 Windows, Linux, and macOS
* i686 Windows and Linux
* ARM64 Macos and Linux
* ARMv71 Linux

If you are encountering issues on your system or are are using an unsupported system, feel free to submit a bug report or feature request. You may need to compile Tkhtml on your system. See https://github.com/Andereoo/TkinterWeb-Tkhtml/.
