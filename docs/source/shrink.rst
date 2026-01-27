Creating a label widget
=======================

.. note::
    This API changed in version 4.17. See :doc:`the changelog <upgrading>` for details.

Overview
--------

**Shrink makes HTML widgets behave like label widgets, automatically resizing to match their content.**

How-to
------

Use the :class:`.HtmlLabel` widget or add the parameter ``shrink=True`` to the :class:`.HtmlFrame` widget.

Your widget will now shrink to match its content!

.. tip::
    Use the :class:`.HtmlLabel` widget if you want an HTML widget that looks and behaves like a ttk Label. Use the :class:`.HtmlFrame` widget if you want full control.

Tips and tricks
---------------

Word wrapping
~~~~~~~~~~~~~

By default, word wrapping is disabled when shrink is enabled. This forces text to keep inline, which is generally expected from label-like widgets, and prevents a number of bugs that cause the widget to shake or wrap when it shouldn't.

.. note::

    Full shrink word wrapping support is currently only rolled out to 64-bit Windows and Linux users. Ensure you installed TkinterWeb via ``pip install tkinterweb[recommended]`` or ``pip install tkinterweb[full]`` to prevent bugs when using shrink.

    If you are encountering issues on an unsupported platform, either submit a feature request or compile and install Tkhtml 3.1 by visiting and cloning https://github.com/Andereoo/TkinterWeb-Tkhtml. Then run ``python compile.py --install``.

If you need word wrapping, you can re-enable it by using ``HtmlFrame(..., textwrap=True)``. 

It is a known issue that when word wrapping is enabled and the widget is shrunk it will often not re-expand. You will need to signal to the geometry manager that the widget should expand, or use the experimental ``HtmlFrame.unshrink = True`` (not recommended).

Height and width
~~~~~~~~~~~~~~~~

Since the purpose of shrink is to automatically resize the widget according to its content, height and width have little effect.

If you need to set the height and width, simply disable shrink.

Scrollbars
~~~~~~~~~~

Scrollbars are disabled by default when shrink is enabled. Use ``HtmlFrame(..., vertical_scrollbar="auto", horizontal_scrollbar="auto")`` to enable them.

-------------------

Please report bugs or request new features on the `issues page <https://github.com/Andereoo/TkinterWeb/issues>`_.