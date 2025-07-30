Porting to TkinterWeb 4+
========================


**The API changed significantly in version 4.0.0**

Summary of changes
------------------

* Faster load speed
* A more intuitive API
* Support for experimental Tkhtml features, such as page printing and ``border-radius``
* Widget behaviour and API is now more closely aligned with standard Tkinter widgets
* The DOM API now more closely mirrors its JavaScript counterparts
* Dozens of new configuration options, including access to more settings and the ability to link a JavaScript interpreter
* Basic JavaScript support (new in version 4.1)
* Improved embedded widget handling (new in version 4.2)
* More DOM improvements

Removed
-------

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
* ``HtmlFrame.replace_widget()`` (deprecated in version 4.2) - use :meth:`.HtmlFrame.widget_to_element` and :attr:`.HTMLElement.widget`
* ``HtmlFrame.replace_element()`` (deprecated in version 4.2) - use :attr:`.HTMLElement.widget`
* ``HtmlFrame.remove_widget()`` (deprecated in version 4.2) - use :meth:`.HTMLElement.remove`
* ``TkinterWeb.replace_widget()`` (removed in version 4.2)
* ``TkinterWeb.replace_element()`` (removed in version 4.2)
* ``TkinterWeb.remove_widget()`` (removed in version 4.2)

* The ``widgetid`` attribute no longer embeds widgets. Use ``<object data=name_of_your_widget></object>`` or :attr:`.HTMLElement.widget` instead. This improves load speeds and allows for widget style handling.

Renamed
-------

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

* :class:`.HtmlParse` (new in version 4.4)
* :class:`.TkHtmlParsedURI` (new in version 4.4)
* :class:`.HTMLCollection` (new in version 4.4)

* :meth:`.HtmlFrame.clear_selection`
* :meth:`.HtmlFrame.get_currently_hovered_element`
* :meth:`.HtmlFrame.widget_to_element` (new in version 4.2)
* :meth:`.HtmlFrame.save_page`
* :meth:`.HtmlFrame.snapshot_page`
* :meth:`.HtmlFrame.show_error_page`
* :meth:`.HtmlFrame.print_page`
* :meth:`.HtmlFrame.screenshot_page`
* :meth:`.HtmlFrame.insert_html` (new in version 4.4)
* :meth:`.HtmlFrame.register_JS_object`` (new in version 4.1)
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
* :attr:`.HTMLElement.widget` (new in version 4.1, updated in version 4.2)
* :attr:`.HTMLElement.value` (new in version 4.1)
* :attr:`.HTMLElement.checked` (new in version 4.1)
* :attr:`.HTMLElement.onchange` (new in version 4.1)
* :attr:`.HTMLElement.onload` (new in version 4.1)
* :attr:`.HTMLElement.onclick` (new in version 4.1)
* :attr:`.HTMLElement.oncontextmenu` (new in version 4.1)
* :attr:`.HTMLElement.ondblclick` (new in version 4.1)
* :attr:`.HTMLElement.onmousedown` (new in version 4.1)
* :attr:`.HTMLElement.onmouseenter` (new in version 4.1)
* :attr:`.HTMLElement.onmouseleave` (new in version 4.1)
* :attr:`.HTMLElement.onmousemove` (new in version 4.1)
* :attr:`.HTMLElement.onmouseout` (new in version 4.1)
* :attr:`.HTMLElement.onmouseover` (new in version 4.1)
* :attr:`.HTMLElement.onmouseup` (new in version 4.1)
* :attr:`.HTMLElement.id` (new in version 4.4)
* :attr:`.HTMLElement.class` (new in version 4.4)


* :class:`.CSSStyleDeclaration`
* :attr:`.CSSStyleDeclaration.*` (any camel-case CSS property)
* :attr:`.CSSStyleDeclaration.cssText`
* :attr:`.CSSStyleDeclaration.length`
* :attr:`.CSSStyleDeclaration.cssProperties`
* :attr:`.CSSStyleDeclaration.cssInlineProperties`
* :attr:`.CSSStyleDeclaration.setProperty` (new in version 4.1)
* :attr:`.CSSStyleDeclaration.getPropertyValue` (new in version 4.1)
* :attr:`.CSSStyleDeclaration.removeProperty` (new in version 4.1)

* :meth:`.TkinterWeb.enable_imagecache`
* :meth:`.TkinterWeb.destroy_node`
* :meth:`.TkinterWeb.get_node_properties`
* :meth:`.TkinterWeb.override_node_properties`
* :meth:`.TkinterWeb.update_tags`
* :meth:`.TkinterWeb.send_onload` (new in version 4.1)
* :meth:`.TkinterWeb.replace_node_contents` (new in version 4.2)
* :meth:`.TkinterWeb.map_node` (new in version 4.2)
* :meth:`.TkinterWeb.replace_node_with_widget` (new in version 4.2)
* :meth:`.TkinterWeb.get_node_stacking` (new in version 4.2)
* :meth:`.TkinterWeb.override_node_CSS` (new in version 4.4)
* :meth:`.TkinterWeb.write` (new in version 4.4)
* :meth:`.TkinterWeb.get_child_text` (new in version 4.4)
* :meth:`.TkinterWeb.safe_tk_eval` (new in version 4.4)
* :meth:`.TkinterWeb.serialize_node` (new in version 4.4)
* :meth:`.TkinterWeb.serialize_node_style` (new in version 4.4)

* ``utilities.DOWNLOADING_RESOURCE_EVENT`` (equivalent to ``<<DownloadingResource>>``)
* ``utilities.DONE_LOADING_EVENT`` (equivalent to ``<<DoneLoading>>``)
* ``utilities.URL_CHANGED_EVENT`` (equivalent to ``<<UrlChanged>>``)
* ``utilities.ICON_CHANGED_EVENT`` (equivalent to ``<<IconChanged>>``)
* ``utilities.TITLE_CHANGED_EVENT`` (equivalent to ``<<TitleChanged>>``)

* Many new configuration options were added. See the :doc:`api/htmlframe` for a complete list.
* Support for many JavaScript events was added in version 4.1.

* The ``tkinterweb-full-page`` attribute can now be added to elements to make them the same height as the viewport. This can be used for vertical alignment of page content. See the TkinterWeb Demo class in `__init__.py <https://github.com/Andereoo/TkinterWeb/blob/main/tkinterweb/__init__.py>`_ for example usage.

* Support for the HTML number input was added in version 4.4.

Changed
-------

* :meth:`.HtmlFrame.configure`, :meth:`.HtmlFrame.config`, :meth:`.HtmlFrame.cget`, and :meth:`.HtmlFrame.__init__` now support more configuration options.
* :meth:`.HtmlFrame.load_website`, :meth:`.HtmlFrame.load_file`, and :meth:`.HtmlFrame.load_url` no longer accept the ``insecure`` parameter. use ``HTMLElement.configure(insecure=)``.

* Enabling/disabling caches now enables/disables the Tkhtml image cache.
* Threading now cannot be enabled if the Tcl/Tk build does not support it.

* :meth:`.HTMLElement.remove` now raises a TclError when invoked on ``<html>`` or ``<body>`` elements, which previously caused segmentation faults.
* :attr:`.HTMLElement.innerHTML` and :attr:`.HTMLElement.textContent` now raise a TclError when invoked on ``<html>`` elements, which previously caused segmentation faults.

* Shorthand CSS properties can now be set and returned after the document is loaded.

  
* The ability to style color selector inputs was improved.
* The ability to access form elements has improved.
* Text elements now emit the ``<<Modified>>`` event *after* the content updates.

* As of version 4.1, :meth:`.HtmlFrame.screenshot_page` is now partially supported on Windows and now accepts the additional parameter ``show``. 
* As of version 4.1, the default selection and find text colors are less abrupt.

* As of version 4.2, widgets embedded in the document can now be removed without removing the containing element. 

* The TkinterWeb demo and some of the built-in pages have been updated. Many internal methods and variables have been renamed, removed, or modified.

* As of version 4.3, prebuilt Tkhtml binaries have been split off into a new package, TkinterWeb-Tkhtml. This has been done to work towards `bug #52 <https://github.com/Andereoo/TkinterWeb/issues/52>`_ and reduce the download size of the TkinterWeb package when updating.

* As of version 4.4, :meth:`.HtmlFrame.add_html` is now accepts the additional parameter ``return_element``. 

* As of version 4.4, it is possible to choose specific Tkhtml versions if supplied. It is now only possible to enable experimental mode if an experimental Tkhtml release is detected.