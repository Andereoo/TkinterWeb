Porting to TkinterWeb 4+
========================


**The API changed significantly in version 4.0.0**

Summary of changes
------------------

* Faster load speed
* A more intuitive API
* Support for experimental Tkhtml features, such as page printing
* Widget behaviour and API is now more closely aligned with standard Tkinter widgets
* The DOM API now more closely mirrors its JavaScript counterparts
* Dozens of new configuration options, including access to more settings and the ability to link a JavaScript interpreter
* Basic JavaScript support (new in version 4.1)
* Improved embedded widget handling (new in version 4.2)
* More DOM improvements
* SVG support on Windows and ``border-radius`` support on Windows and Linux (new in version 4.4)
* Support for Tcl 9 (new in version 4.5)

Removed
-------

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

* ``HtmlFrame.replace_widget()``- use :meth:`.HtmlFrame.widget_to_element` and :attr:`.HTMLElement.widget`
* ``HtmlFrame.replace_element()``- use :attr:`.HTMLElement.widget`
* ``HtmlFrame.remove_widget()``- use :meth:`.HTMLElement.remove`
* ``TkinterWeb.replace_widget()``
* ``TkinterWeb.replace_element()``
* ``TkinterWeb.remove_widget()``

Renamed
-------

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

Added
-----

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
* :attr:`.HTMLElement.class`

* :meth:`.TkinterWeb.override_node_CSS`
* :meth:`.TkinterWeb.write`
* :meth:`.TkinterWeb.get_child_text`
* :meth:`.TkinterWeb.safe_tk_eval`
* :meth:`.TkinterWeb.serialize_node`
* :meth:`.TkinterWeb.serialize_node_style`

* Added support for the HTML number input.

* The new configuration option ``tkhtml_version`` can be used to choose a specific Tkhtml version to load.

Version 4.5:

* The new configuration option ``ssl_cafile`` can be used to provide a path to a CA Certificate file. See  `bug #28 <https://github.com/Andereoo/TkinterWeb/issues/28>`_ .

Version 4.6:

* The new configuration option ``request_timeout`` can be used to specify the number of seconds to wait before a request times out.

Version 4.7:
* The new ``<<DOMContentLoaded>>`` event will be generated once the page DOM content has loaded. The page may not be done loading, but at this point it is possible to interact with the DOM.

Changed/Fixed
-------------

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

Version 4.7

* Fixed flickering when moving the mouse over scrollbars in ``<iframe>`` elements
* :meth:`.HtmlFrame.bind` now binds `<Enter>` and `<Leave>` directly. All other events are still bound to the associated :class:`~tkinterweb.TkinterWeb` instance.
