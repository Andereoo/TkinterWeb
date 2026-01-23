Changelog
=========

**The API changed significantly in version 4.**

.. dropdown:: Key Changes
    :open:
    :color: primary

    * Faster load speed
    * A more intuitive API
    * Support for experimental Tkhtml features, such as page printing
    * Widget behaviour and API is now more closely aligned with standard Tkinter widgets
    * Many DOM improvements. The DOM API now more closely mirrors its JavaScript counterpart.
    * Dozens of new configuration options, including access to more settings and the ability to link a JavaScript interpreter

    * Basic JavaScript support (new in version 4.1)
    * Improved embedded widget handling (new in version 4.2)
    * SVG support on Windows and ``border-radius`` support on Windows and Linux (new in version 4.4)
    * Support for Tcl 9 (new in version 4.5)
    * Caret browsing functionality (new in version 4.8)
    * Improved thread safety (new in version 4.9)
    * Ability to bind to HTML elements (new in version 4.10)

.. dropdown:: Removed

    Version 4.0:

    * ``HtmlFrame.get_zoom()`` - use ``HtmlFrame.cget("zoom")``
    * ``HtmlFrame.set_zoom()`` - use ``HtmlFrame.configure(zoom=)``
    * ``HtmlFrame.get_fontscale()`` - use ``HtmlFrame.cget("fontscale")``
    * ``HtmlFrame.set_fontscale()`` - use ``HtmlFrame.configure(fontscale=)``
    * ``HtmlFrame.get_parsemode()`` - use ``HtmlFrame.cget("parsemode")``
    * ``HtmlFrame.set_parsemode()`` - use ``HtmlFrame.configure(parsemode=)``
    * ``HtmlFrame.set_message_func()`` - use ``HtmlFrame.configure(message_func=)``
    * ``HtmlFrame.set_broken_webpage_message()`` - use ``HtmlFrame.configure(on_navigate_fail=)``. Note that :attr:`on_navigate_fail` requires a function instead.
    * ``HtmlFrame.set_maximum_thread_count()`` - use ``HtmlFrame.configure(threading_enabled=)``
    * ``HtmlFrame.set_recursive_hover_depth()`` - use ``HtmlFrame.html.recursive_hover_depth=``
    * ``HtmlFrame.add_visited_links()`` - use ``HtmlFrame.configure(visited_links=)``
    * ``HtmlFrame.clear_visited_links()`` - use ``HtmlFrame.configure(visited_links=)``
    * ``HtmlFrame.enable_stylesheets()`` - use ``HtmlFrame.configure(stylesheets_enabled=)``
    * ``HtmlFrame.enable_images()`` - use ``HtmlFrame.configure(images_enabled=)``
    * ``HtmlFrame.enable_forms()`` - use ``HtmlFrame.configure(forms_enabled=)``
    * ``HtmlFrame.enable_objects()`` - use ``HtmlFrame.configure(objects_enabled=)``
    * ``HtmlFrame.enable_caches()`` - use ``HtmlFrame.configure(caches_enabled=)``
    * ``HtmlFrame.enable_dark_theme()`` - use ``HtmlFrame.configure(dark_theme_enabled=, image_inversion_enabled=)``
    * ``HtmlFrame.on_image_setup()`` - use ``HtmlFrame.configure(on_resource_setup=)``
    * ``HtmlFrame.on_downloading_resource()`` - bind to ``<<DownloadingResource>>``
    * ``HtmlFrame.on_done_loading()`` - bind to ``<<DoneLoading>>``
    * ``HtmlFrame.on_url_change()`` - bind to ``<<UrlChanged>>`` and use :attr:`.HtmlFrame.current_url`
    * ``HtmlFrame.on_icon_change()`` - bind to ``<<IconChanged>>`` and use :attr:`.HtmlFrame.title`
    * ``HtmlFrame.on_title_change()`` - bind to ``<<TitleChanged>>`` and use :attr:`.HtmlFrame.title`
    * ``HtmlFrame.on_form_submit()`` - use ``HtmlFrame.configure(on_form_submit=)``
    * ``HtmlFrame.on_link_click()`` - use ``HtmlFrame.configure(on_link_click=)``
    * ``HtmlFrame.yview_toelement()`` - use :meth:`.HTMLElement.scrollIntoView`
    * ``HtmlFrame.get_currently_hovered_node_text()`` - :meth:`.HtmlFrame.get_currently_hovered_element`
    * ``HtmlFrame.get_currently_hovered_node_tag()`` - :meth:`.HtmlFrame.get_currently_hovered_element`
    * ``HtmlFrame.get_currently_hovered_node_attribute()`` - :meth:`.HtmlFrame.get_currently_hovered_element`
    * ``HtmlFrame.get_current_link()`` - use :meth:`.HtmlFrame.get_currently_hovered_element`

    * The ``widgetid`` attribute no longer embeds widgets. Use ``<object data=name_of_your_widget></object>`` or :attr:`.HTMLElement.widget` instead. This improves load speeds and allows for widget style handling.

    Version 4.2:

    * ``TkinterWeb.replace_widget()``
    * ``TkinterWeb.replace_element()``
    * ``TkinterWeb.remove_widget()``

    Version 4.8

    * ``HtmlFrame.replace_widget()`` (deprecated in version 4.0) - use :meth:`.HtmlFrame.widget_to_element` and :attr:`.HTMLElement.widget`
    * ``HtmlFrame.replace_element()`` (deprecated in version 4.0) - use :attr:`.HTMLElement.widget`
    * ``HtmlFrame.remove_widget()`` (deprecated in version 4.0) - use :meth:`.HTMLElement.remove`

    Version 4.14:

    * The ``style`` configuration option no longer sets the CSS style of :class:`.HtmlLabel` widgets. See `bug #145 <https://github.com/Andereoo/TkinterWeb/issues/145>`_.

.. dropdown:: Deprecated

    Version 4.11:

    * ``TkinterWeb.update_tags()`` - use :meth:`.SelectionManager.update_tags`
    * ``TkinterWeb.select_all()`` - use :meth:`.SelectionManager.select_all`
    * ``TkinterWeb.clear_selection()`` - use :meth:`.SelectionManager.clear_selection`
    * ``TkinterWeb.update_selection()`` - use :meth:`.SelectionManager.update_selection`
    * ``TkinterWeb.get_selection()`` - use :meth:`.SelectionManager.get_selection`
    * ``TkinterWeb.copy_selection()`` - use :meth:`.SelectionManager.copy_selection`
    * ``TkinterWeb.allocate_image_name()`` - use :meth:`.ImageManager.allocate_image_name`
    * ``TkinterWeb.handle_node_replacement()`` - use :meth:`.WidgetManager.handle_node_replacement`
    * ``TkinterWeb.map_node()`` - use :meth:`.WidgetManager.map_node`
    * ``TkinterWeb.find_text()`` - use :meth:`.SearchManager.find_text`
    * ``TkinterWeb.send_onload()`` - use :meth:`.EventManager.send_onload`

    Version 4.12:

    * ``Htmlframe.register_JS_object()`` - use :meth:`.JSEngine.register`

    Version 4.14:

    * The configuration option ``default_style`` - use ``tkinterweb.utilities.DEFAULT_STYLE`` or the ``defaultstyle`` configuration option.
    * The configuration option ``dark_style`` - use ``tkinterweb.utilities.DARK_STYLE`` or the ``defaultstyle`` configuration option.
    * The configuration option ``about_page_background`` - use ``ttk.Style().configure("TFrame", background=)``.
    * The configuration option ``about_page_foreground`` - use ``ttk.Style().configure("TFrame", foreground=)``.

    Version 4.16:

    * :meth:`.HtmlFrame.get_caret_page_position` - use  :meth:`HtmlFrame.get_caret_position(return_element=False) <.HtmlFrame.get_caret_position>`
    * :meth:`.HtmlFrame.set_caret_page_position` - use :meth:`HtmlFrame.set_caret_position(index=) <.HtmlFrame.set_caret_position>`
    * :meth:`.HtmlFrame.get_selection_page_position` - use :meth:`HtmlFrame.get_selection_position(return_elements=False) <.HtmlFrame.get_selection_position>`
    * :meth:`.HtmlFrame.set_selection_page_position` - use :meth:`HtmlFrame.set_selection_position(start_index=, end_index=) <.HtmlFrame.set_selection_position>`


.. dropdown:: Renamed

    Version 4.0:

    * ``HtmlFrame.get_currently_selected_text()`` -> :meth:`.HtmlFrame.get_selection`

    * ``TkwDocumentObjectModel`` -> :class:`.HTMLDocument`
    * ``HtmlElement`` -> :class:`.HTMLElement`

    * ``HtmlElement.style()`` -> :attr:`.HTMLElement.style`
    * ``HtmlElement.innerHTML()`` -> :attr:`.HTMLElement.innerHTML`
    * ``HtmlElement.textContent()`` -> :attr:`.HTMLElement.textContent`
    * ``HtmlElement.attributes()`` -> :attr:`.HTMLElement.attributes`
    * ``HtmlElement.tagName()`` -> :attr:`.HTMLElement.tagName`
    * ``HtmlElement.parentElement()`` -> :attr:`.HTMLElement.parentElement`
    * ``HtmlElement.children()`` -> :attr:`.HTMLElement.children`

    * The ``scroll-x`` attribute was changed to the ``tkinterweb-scroll-x`` attribute. Like the ``overflow`` CSS property, valid options are now "auto", "visible", "clip", "scroll", and "hidden".

.. dropdown:: Added

    Version 4.0:

    * :meth:`.HtmlFrame.clear_selection`
    * :meth:`.HtmlFrame.get_currently_hovered_element`
    * :meth:`.HtmlFrame.save_page`
    * :meth:`.HtmlFrame.snapshot_page`
    * :meth:`.HtmlFrame.show_error_page`
    * :meth:`.HtmlFrame.print_page`
    * :meth:`.HtmlFrame.screenshot_page`

    * :attr:`.HtmlFrame.base_url`
    * :attr:`.HtmlFrame.icon`
    * :attr:`.HtmlFrame.title`

    * :meth:`.HTMLElement.getElementById`
    * :meth:`.HTMLElement.getElementsByClassName`
    * :meth:`.HTMLElement.getElementsByName`
    * :meth:`.HTMLElement.getElementsByTagName`
    * :meth:`.HTMLElement.querySelector`
    * :meth:`.HTMLElement.querySelectorAll`
    * :meth:`.HTMLElement.scrollIntoView`

    * :class:`.CSSStyleDeclaration`
    * :attr:`.CSSStyleDeclaration.*` (any camel-case CSS property)
    * :attr:`.CSSStyleDeclaration.cssText`
    * :attr:`.CSSStyleDeclaration.length`
    * :attr:`.CSSStyleDeclaration.cssProperties`
    * :attr:`.CSSStyleDeclaration.cssInlineProperties`

    * :meth:`.TkinterWeb.enable_imagecache`
    * :meth:`.TkinterWeb.destroy_node`
    * :meth:`.TkinterWeb.get_node_properties`
    * :meth:`.TkinterWeb.override_node_properties`
    * :meth:`.TkinterWeb.update_tags`

    * ``utilities.DOWNLOADING_RESOURCE_EVENT`` (equivalent to ``<<DownloadingResource>>``)
    * ``utilities.DONE_LOADING_EVENT`` (equivalent to ``<<DoneLoading>>``)
    * ``utilities.URL_CHANGED_EVENT`` (equivalent to ``<<UrlChanged>>``)
    * ``utilities.ICON_CHANGED_EVENT`` (equivalent to ``<<IconChanged>>``)
    * ``utilities.TITLE_CHANGED_EVENT`` (equivalent to ``<<TitleChanged>>``)

    * Many new configuration options were added. See the :doc:`api/htmlframe` for a complete list.

    * The ``tkinterweb-full-page`` attribute can now be added to elements to make them the same height as the viewport. This can be used for vertical alignment of page content. See the TkinterWeb Demo class in `__init__.py <https://github.com/Andereoo/TkinterWeb/blob/main/tkinterweb/__init__.py>`_ for example usage.

    Version 4.1:

    * :meth:`.HtmlFrame.register_JS_object``

    * :attr:`.HTMLElement.widget` (updated again in version 4.2)
    * :attr:`.HTMLElement.value`
    * :attr:`.HTMLElement.checked`
    * :attr:`.HTMLElement.onchange`
    * :attr:`.HTMLElement.onload`
    * :attr:`.HTMLElement.onclick`
    * :attr:`.HTMLElement.oncontextmenu`
    * :attr:`.HTMLElement.ondblclick`
    * :attr:`.HTMLElement.onmousedown`
    * :attr:`.HTMLElement.onmouseenter`
    * :attr:`.HTMLElement.onmouseleave`
    * :attr:`.HTMLElement.onmousemove`
    * :attr:`.HTMLElement.onmouseout`
    * :attr:`.HTMLElement.onmouseover`
    * :attr:`.HTMLElement.onmouseup`

    * :attr:`.CSSStyleDeclaration.setProperty`
    * :attr:`.CSSStyleDeclaration.getPropertyValue`
    * :attr:`.CSSStyleDeclaration.removeProperty`

    * :meth:`.TkinterWeb.send_onload`

    * Added support for many JavaScript events.

    * The new configuration option ``on_element_script`` can be used to add a callback to run when a JavaScript event attribute on an element is encountered.
    * The new configuration option ``javascript_enabled`` can be used to enable JavaScript support.

    Version 4.2:

    * :meth:`.HtmlFrame.widget_to_element`

    * :meth:`.TkinterWeb.replace_node_contents`
    * :meth:`.TkinterWeb.map_node`
    * :meth:`.TkinterWeb.replace_node_with_widget`
    * :meth:`.TkinterWeb.get_node_stacking`

    Version 4.4:

    * :class:`.HtmlParse`
    * :class:`.TkHtmlParsedURI`
    * :class:`.HTMLCollection`

    * :meth:`.HtmlFrame.insert_html`

    * :attr:`.HTMLElement.id`
    * :attr:`.HTMLElement.className`

    * :meth:`.TkinterWeb.override_node_CSS`
    * :meth:`.TkinterWeb.write`
    * :meth:`.TkinterWeb.get_child_text`
    * :meth:`.TkinterWeb.safe_tk_eval`
    * :meth:`.TkinterWeb.serialize_node`
    * :meth:`.TkinterWeb.serialize_node_style`

    * Added support for the HTML number input.

    * The new configuration option ``tkhtml_version`` can be used to choose a specific Tkhtml version to load.

    Version 4.5:

    * The new configuration option ``ssl_cafile`` can be used to provide a path to a CA Certificate file. See  `bug #28 <https://github.com/Andereoo/TkinterWeb/issues/28>`_.

    Version 4.6:

    * The new configuration option ``request_timeout`` can be used to specify the number of seconds to wait before a request times out.

    Version 4.7:

    * The new ``<<DOMContentLoaded>>`` event will be generated once the page DOM content has loaded. The page may not be done loading, but at this point it is possible to interact with the DOM.

    Version 4.8:

    * :meth:`.HtmlFrame.get_page_text`
    * :meth:`.HtmlFrame.get_caret_position`
    * :meth:`.HtmlFrame.get_caret_page_position` (deprecated in version 4.16)
    * :meth:`.HtmlFrame.set_caret_position`
    * :meth:`.HtmlFrame.set_caret_page_position` (deprecated in version 4.16)
    * :meth:`.HtmlFrame.shift_caret_left`
    * :meth:`.HtmlFrame.shift_caret_right`
    * :meth:`.HtmlFrame.get_selection_position`
    * :meth:`.HtmlFrame.get_selection_page_position` (deprecated in version 4.16)
    * :meth:`.HtmlFrame.set_selection_position`
    * :meth:`.HtmlFrame.set_selection_page_position` (deprecated in version 4.16)

    * :attr:`.HTMLElement.previousSibling`
    * :attr:`.HTMLElement.nextSibling`

    * :attr:`.TkinterWeb.caret_manager`

    * :meth:`.TkinterWeb.update_selection`
    * :meth:`.TkinterWeb.tkhtml_offset_to_text_index`

    * :class:`.CaretManager`

    * The new configuration option ``caret_browsing_enabled`` can be used to enable or disable caret browsing mode.

    Version 4.9:

    * :meth:`.TkinterWeb.post_to_queue`
    * :meth:`.TkinterWeb.allocate_image_name`
    * :meth:`.TkinterWeb.check_images`

    Version 4.10:

    * :meth:`.HTMLElement.bind`
    * :meth:`.HTMLElement.unbind`

    * :attr:`.TkinterWeb.event_manager`

    * :class:`.EventManager`

    * You can now set ``allowstyling="deep"`` on elements with embedded widgets to also style their subwidgets.

    Version 4.11:

    * :meth:`.HtmlFrame.unbind`

    * :class:`.HtmlText`

    * :attr:`.TkinterWeb.selection_manager`
    * :attr:`.TkinterWeb.widget_manager`
    * :attr:`.TkinterWeb.search_manager`
    * :attr:`.TkinterWeb.script_manager`
    * :attr:`.TkinterWeb.style_manager`
    * :attr:`.TkinterWeb.image_manager`
    * :attr:`.TkinterWeb.object_manager`
    * :attr:`.TkinterWeb.form_manager`
    * :attr:`.TkinterWeb.node_manager`

    * :class:`.SelectionManager`
    * :class:`.WidgetManager`

    Version 4.12:

    * :class:`.JSEngine`

    Version 4.13:

    * :meth:`.TkinterWeb.get_node_replacement`

    Version 4.14:

    * :attr:`.HTMLElement.innerText`

    * The new configuration option ``request_func`` can be used to set a custom script to use to download resources.
    * The new configuration option ``defaultstyle`` can be used to set the default stylesheet to use when parsing HTML.

    Version 4.15:

    * :meth:`.HtmlFrame.add_css` now accepts the additional parameter ``priority``. 
    * :meth:`.CaretManager.shift_left`, :meth:`.CaretManager.shift_right`, :meth:`.CaretManager.shift_up`, :meth:`.CaretManager.shift_down`, and :meth:`.CaretManager.shift_update` now accept the additional parameter ``update``.

    * The :class:`.HtmlText` widget now supports the ``background``, ``foreground``, ``bg``, and ``fg`` keywords.

    Version 4.16:

    * :meth:`.HtmlFrame.get_caret_position` now accepts the additional parameter ``return_element``. 
    * :meth:`.HtmlFrame.get_selection_position` now accepts the additional parameter ``return_elements``. 

    * :attr:`.HtmlText.insert`
    * :attr:`.HtmlText.delete`

    * The :class:`.HtmlText` widget now supports the ``state`` keyword.

    * Added introductory support for :class:`.HtmlLabel` and :class:`.HtmlFrame(shrink=True)` widget resizing. This feature is experimental and may change at any time. Set ``HtmlFrame.unshrink = True`` to enable it and let me know how it works!

.. dropdown:: Changed/Fixed

    Version 4.0:

    * :meth:`.HtmlFrame.configure`, :meth:`.HtmlFrame.config`, :meth:`.HtmlFrame.cget`, and :meth:`.HtmlFrame.__init__` now support more configuration options.
    * :meth:`.HtmlFrame.load_website`, :meth:`.HtmlFrame.load_file`, and :meth:`.HtmlFrame.load_url` no longer accept the ``insecure`` parameter. use ``HTMLElement.configure(insecure=)``.

    * Enabling/disabling caches now enables/disables the Tkhtml image cache.
    * Threading now cannot be enabled if the Tcl/Tk build does not support it.

    * :meth:`.HTMLElement.remove` now raises a :py:class:`tkinter.TclError` when invoked on ``<html>`` or ``<body>`` elements, which previously caused segmentation faults.
    * :attr:`.HTMLElement.innerHTML` and :attr:`.HTMLElement.textContent` now raise a :py:class:`tkinter.TclError` when invoked on ``<html>`` elements, which previously caused segmentation faults.

    * Shorthand CSS properties can now be set and returned after the document is loaded.
    
    * The ability to style color selector inputs was improved.
    * The ability to access form elements has improved.
    * Text elements now emit the ``<<Modified>>`` event *after* the content updates.
    * The TkinterWeb demo and some of the built-in pages have been updated. Many internal methods and variables have been renamed, removed, or modified.

    Version 4.1:

    * :meth:`.HtmlFrame.screenshot_page` is now partially supported on Windows and now accepts the additional parameter ``show``. 
    * The default selection and find text colors are less abrupt.

    Version 4.2:

    * Widgets embedded in the document can now be removed without removing the containing element. 

    Version 4.3:

    * Prebuilt Tkhtml binaries have been split off into a new package, `TkinterWeb-Tkhtml <https://pypi.org/project/tkinterweb-tkhtml/>`_. This has been done to work towards `bug #52 <https://github.com/Andereoo/TkinterWeb/issues/52>`_ and reduce the download size of the TkinterWeb package when updating.

    Version 4.4:

    * :meth:`.HtmlFrame.add_html` is now accepts the additional parameter ``return_element``. 
    * It is now only possible to enable experimental mode if an experimental Tkhtml release is detected.
    * Some experimental HTML features were enabled in Windows and Linux. ``border-radius`` is now supported!

    Version 4.5:

    * Periods are now supported in url fragments. See  `bug #143 <https://github.com/Andereoo/TkinterWeb/issues/143>`_ .
    * Tkhtml file loading was updated in version 4.5. Some error messages have also been updated. Please submit a bug report if you notice any issues.

    Version 4.6:

    * Url fragments are now tracked as the document loads. This ensures that the fragment is still visible even after loading CSS files or images that change the layout of the document.
    * ``gzip`` and ``deflate`` content encodings are now supported. Brotli compression is also supported if the :py:mod:`brotli` module is installed. This increases page load speeds and decreases bandwidth usage in some websites.
    * Pressing Ctrl-A in an HTML number input, text input, or textarea will cause the widget's text to be selected. Pasting will now overwrite any selected text.
    * Loading local files with a query string in the url will no longer raise an error.
    * Fixed :meth:`.HTMLDocument.querySelector`.

    Version 4.7:

    * Fixed flickering when moving the mouse over scrollbars in ``<iframe>`` elements.
    * ``bind()`` calls to the :meth:`.HtmlFrame.bind` respect requests to bind ``<Enter>`` and ``<Leave>``. All other events are still bound to the associated :class:`~tkinterweb.TkinterWeb` instance. Keep in mind that overriding the default bindings to ``<Enter>`` and ``<Leave>`` may cause unwanted side effects. 

    Version 4.8:

    * All HTML widgets now bind to ``<Up>``, ``<Down>``, ``<Left>``, ``<Right>``, ``<Prior>``, ``<Next>``, ``<Home>``, and ``<End>`` by default.
    * Fixed :meth:`.HTMLElement.parentElement`.

    Version 4.9:

    * TkinterWeb is now thread-safe when loading resources. All callbacks now will run on the main thread.
    * Fixed loading of data urls.
    * Local files will now load regardless of the number of slashes before the path.
    * Fixed some dark mode and image inversion bugs.

    Version 4.10:

    * Binding button presses and motion events to the widget no longer removes internal bindings.
    * Setting ``html.maximum_thread_count = 0`` no longer disables threading. Use ``html.threading_enabled = False``.
    * :py:mod:`PIL` is now an optional dependency. I also recommend installing the new :py:mod:`tkinterweb-tkhtml-extras` package.
    * The :attr:`.HTMLElement.widget` property now returns a Tk widget when used on ``<input>``, ``<textarea>``, ``<select>``, ``<iframe>``, and some ``<object>`` elements.
    * Fixed scrollbar flashes when the widget opens.
    * DOM objects now provide more useful information when printed.
    * By default, scrolling on embedded widgets now scrolls the page if the embedded widget or subwidgets do not bind to the mousewheel.
    * If dark theme is enabled, HTML code passed to the configuration option ``dark_style`` will now be automatically appended onto the code set by ``default_style``.
    * Plain text is no longer rendered as a blank page.
    * The event queue now only runs when threading is enabled.
    * Modifying the selection when selection is disabled now raises an error.
    * Modifying the caret position when caret browsing is disabled now raises an error.
    * Local file loading now happens on the main thread.
    * Fixed a fatal scrollbar error when loading TkinterWeb on Tk 8.5 on MacOS.
    * Fixed a fatal binding error when loading TkinterWeb on MacOS.
    * Many internal changes were made in this release. If you notice any bugs, please report them.

    Version 4.11:

    * Fixed some minor bugs.
    * JavaScript events no longer fire when events are disabled.
    * The :class:`.TkinterWeb` widget was restructured in this release. If you notice any bugs, please report them.

    Version 4.12:

    * Fixed more bugs.
    * Side-scrolling is now supported.

    Version 4.13:

    * Fixed more bugs, including a segfault when inserting a widget into the page's root element.
    * ``grid_propagate(0)`` and ``pack_propagate(0)`` no longer have any effect on the widget. Requested width and height will now always be respected.

    Version 4.14:

    * Fixed more bugs.
    * The :class:`.HtmlLabel` widget now automatically matches the ttk style.
    * Alternate text for broken images is now displayed natively through Tkhtml.

    Version 4.15:

    * Fixed more bugs.
    * Improved some error messages.
    * Improved code autocompletion.
    * All HTML widgets now bind to ``<Ctrl-A>`` by default.
    * Equality checking between :class:`.HTMLElement` objects is now fully supported.
    * The :class:`.HtmlText` widget is now editable out-of-the-box!
    * The :class:`.HtmlLabel` widget now uses the ``TLabel`` style by default instead of ``TFrame``.

    Version 4.16:

    * Fixed more bugs.
    * :meth:`.HtmlFrame.set_caret_position` now sets the caret relative to the document text when no element is provided. 
    * :meth:`.HtmlFrame.set_selection_position` now sets the selection relative to the document text when no elements are provided. 
    * A ``NotImplementedError`` will now raise when changing some settings via ``HtmlFrame.configure()``. This occurs on settings that have no effect after the widget loads and on the shrink value, which has been causing segfaults when changed after the widget loads. If you absolutely need to change the shrink value on the fly use ``HtmlFrame.html.configure()``
    * Scrollbars will no longer show in :class:`.HtmlLabel` and :class:`.HtmlFrame(shrink=True)` widgets when scrollbars are set to ``"auto"``.
    * Text wrapping has been disabled by default in the :class:`.HtmlLabel` and :class:`.HtmlFrame(shrink=True)` widgets. Use CSS to override this (with caution). See `bug #147 <https://github.com/Andereoo/TkinterWeb/issues/147>`_.

-------------------

Please report bugs or request new features on the `issues page <https://github.com/Andereoo/TkinterWeb/issues>`_.
