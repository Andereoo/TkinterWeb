## Porting to TkinterWeb v4+

**The API changed significantly in version 4.0.0**
Changes include:
* Faster load speed
* Support for experimental Tkhtml features
* Widget behaviour is now more closely aligned with standard Tkinter widgets
* Dozens of new configuration options, including access to more settings and the ability to link a JavaScript interpreter
* More DOM improvements
* DOM behaviour is now more closely aligned with that of JavaScript
* A more intuitive API\
\
**Removed**
* `HtmlFrame.get_zoom()` - Use `HtmlFrame.cget("zoom")`
* `HtmlFrame.set_zoom()` - Use `HtmlFrame.configure(zoom=)`
* `HtmlFrame.get_fontscale()` - Use `HtmlFrame.cget("fontscale")`
* `HtmlFrame.set_fontscale()` - Use `HtmlFrame.configure(fontscale=)`
* `HtmlFrame.get_parsemode()` - Use `HtmlFrame.cget("parsemode")`
* `HtmlFrame.set_parsemode()` - Use `HtmlFrame.configure(parsemode=)`
* `HtmlFrame.set_message_func()` - Use `HtmlFrame.configure(message_func=)`
* `HtmlFrame.set_broken_webpage_message()` - Use `HtmlFrame.configure(on_navigate_fail=)`. Note that the latter accepts a function instead.
* `HtmlFrame.set_maximum_thread_count()` - Use `HtmlFrame.configure(threading_enabled=)`
* `HtmlFrame.set_recursive_hover_depth()`
* `HtmlFrame.add_visited_links()` - Use `HtmlFrame.configure(visited_links=)`
* `HtmlFrame.clear_visited_links()` - Use `HtmlFrame.configure(visited_links=)`
* `HtmlFrame.enable_stylesheets()` - Use `HtmlFrame.configure(stylesheets_enabled=)`
* `HtmlFrame.enable_images()` - Use `HtmlFrame.configure(images_enabled=)`
* `HtmlFrame.enable_forms()` - Use `HtmlFrame.configure(forms_enabled=)`
* `HtmlFrame.enable_objects()` - Use `HtmlFrame.configure(objects_enabled=)`
* `HtmlFrame.enable_caches()` - Use `HtmlFrame.configure(caches_enabled=)`
* `HtmlFrame.enable_dark_theme()` - Use `HtmlFrame.configure(dark_theme_enabled=, image_inversion_enabled=)`
* `HtmlFrame.on_image_setup()`
* `HtmlFrame.on_downloading_resource()` - Bind to `<<DownloadingResource>>`
* `HtmlFrame.on_done_loading()` - Bind to `<<DoneLoading>>`
* `HtmlFrame.on_url_change()` - Bind to `<<UrlChanged>>` and Use `HtmlFrame.current_url`
* `HtmlFrame.on_icon_change()` - Bind to `<<IconChanged>>` and Use `HtmlFrame.icon`
* `HtmlFrame.on_title_change()` - Bind to `<<TitleChanged>>` and Use `HtmlFrame.title`
* `HtmlFrame.on_form_submit()` - Use `HtmlFrame.configure(on_form_submit=)`
* `HtmlFrame.on_link_click()` - Use `HtmlFrame.configure(on_link_click=)`
* `HtmlFrame.yview_towidget()` - Use `HTMLElement.scrollIntoView()`
* `HtmlFrame.get_currently_hovered_node_text()` - Use `HtmlFrame.get_currently_hovered_element()`
* `HtmlFrame.get_currently_hovered_node_tag()` - Use `HtmlFrame.get_currently_hovered_element()`
* `HtmlFrame.get_currently_hovered_node_attribute()` - Use `HtmlFrame.get_currently_hovered_element()`
* `HtmlFrame.get_current_link()` - Use `HtmlFrame.get_currently_hovered_element()`\
\
**Renamed**
* `HtmlFrame.get_currently_selected_text()` -> `HtmlFrame.get_selection()`\
\
* `TkwDocumentObjectModel` -> `HTMLDocument`
* `HTMLElement` -> `HTMLElement`\
\
* `HTMLElement.style()` -> `HTMLElement.style`
* `HTMLElement.innerHTML()` -> `HTMLElement.innerHTML`
* `HTMLElement.textContent()` -> `HTMLElement.textContent`
* `HTMLElement.attributes()` -> `HTMLElement.attributes`
* `HTMLElement.tagName()` -> `HTMLElement.tagName`
* `HTMLElement.parentElement()` -> `HTMLElement.parentElement`
* `HTMLElement.children()` -> `HTMLElement.children`\
\
**Added**
* `HtmlFrame.clear_selection()`
* `HtmlFrame.get_currently_hovered_element()`
* `HtmlFrame.save_page()`
* `HtmlFrame.snapshot_page()`
* `HtmlFrame.show_error_page()`
* `HtmlFrame.print_page()`
* `HtmlFrame.screenshot_page()`
* `HtmlFrame.base_url`
* `HtmlFrame.icon`
* `HtmlFrame.title`\
\
* `HTMLElement.getElementById()`
* `HTMLElement.getElementsByClassName()`
* `HTMLElement.getElementsByName()`
* `HTMLElement.getElementsByTagName()`
* `HTMLElement.querySelector()`
* `HTMLElement.querySelectorAll()`
* `HTMLElement.scrollIntoView()`\
\
* `CSSStyleDeclaration`
* `CSSStyleDeclaration.* `(any camel-case CSS property)
* `CSSStyleDeclaration.cssText`
* `CSSStyleDeclaration.length`
* `CSSStyleDeclaration.cssProperties`
* `CSSStyleDeclaration.cssInlineProperties`\
\
* `TkinterWeb.enable_imagecache()`
* `TkinterWeb.destroy_node()`
* `TkinterWeb.get_node_properties()`
* `TkinterWeb.override_node_properties()`
* `TkinterWeb.update_tags()`\
\
* `utilities.DOWNLOADING_RESOURCE_EVENT` (equivalent to `<<DownloadingResource>>`)
* `utilities.DONE_LOADING_EVENT` (equivalent to `<<DoneLoading>>`)
* `utilities.URL_CHANGED_EVENT` (equivalent to `<<UrlChanged>>`)
* `utilities.ICON_CHANGED_EVENT` (equivalent to `<<IconChanged>>`)
* `utilities.TITLE_CHANGED_EVENT` (equivalent to `<<TitleChanged>>`)\
\
* Many new configuration options were added. See the [HtmlFrame docs](/docs/HTMLFRAME.md#key-methods) for a complete list.\
\
* The `tkinterweb-full-page` attribute can now be added to elements to make them the same height as the viewport. This can be used for vertical alignment of page content. See the TkinterWeb Demo class in [__init__.py](../tkinterweb/__init__.py) for example usage.\
\
**Changed**
* `HtmlFrame.configure()`, `.config()`, `.cget()`, and `.__init__()` now supports more configuration options.
* `HtmlFrame.load_website()`, `.load_file()`, and `.load_url()` no longer accept the `insecure` parameter. Use `HTMLElement.configure(insecure=).\
\
* Some callbacks have been replaced by Tkinter events.\
\
* Enabling/disabling caches now enables/disables the Tkhtml image cache.
* Threading now cannot be enabled if the Tcl/Tk build does not support it.\
\
* `HTMLElement.remove()` now raises a TclError when invoked on <html> or <body> elements, which previously caused segmentation faults.
* `HTMLElement.innerHTML` and `.textContent` now raise a TclError when invoked on <html> elements, which previously caused segmentation faults.\
\
* The appearance of some input elements was improved.
* Text elements now emit the `<<Modified>>` event *after* the content updates.\
\
* The `widgetid` attribute no longer embeds widgets. Use `<object data=name_of_your_widget></object>` instead. This improves load speeds and allows for widget style handling.
* The `scroll-x` attribute was changed to the `tkinterweb-scroll-x` attribute. Valid options are now "auto", "visible", "clip", "scroll", and "hidden".\
\
* Many internal methods and variables of the HtmlFrame and TkinterWeb widgets were renamed.
* The TkinterWeb demo and some of the built-in pages have been updated.