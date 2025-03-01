> [!IMPORTANT]
> The TkinterWeb documentation has moved to https://tkinterweb.readthedocs.io/en/latest/index.html. See you there!

## Porting to TkinterWeb v4+

**The API changed significantly in version 4.0.0**

### Changes include:
* Faster load speed
* A more intuitive API
* Support for experimental Tkhtml features, such as page printing
* Widget behaviour and API is now more closely aligned with standard Tkinter widgets
* The DOM API now more closely mirrors its JavaScript counterparts
* Dozens of new configuration options, including access to more settings and the ability to link a JavaScript interpreter
* More DOM improvements

### Removed:
* `HtmlFrame.get_zoom()` - use `HtmlFrame.cget("zoom")`
* `HtmlFrame.set_zoom()` - use `HtmlFrame.configure(zoom=)`
* `HtmlFrame.get_fontscale()` - use `HtmlFrame.cget("fontscale")`
* `HtmlFrame.set_fontscale()` - use `HtmlFrame.configure(fontscale=)`
* `HtmlFrame.get_parsemode()` - use `HtmlFrame.cget("parsemode")`
* `HtmlFrame.set_parsemode()` - use `HtmlFrame.configure(parsemode=)`
* `HtmlFrame.set_message_func()` - use `HtmlFrame.configure(message_func=)`
* `HtmlFrame.set_broken_webpage_message()` - use `HtmlFrame.configure(on_navigate_fail=)`. Note that `on_navigate_fail` latter requires a function instead.
* `HtmlFrame.set_maximum_thread_count()` - use `HtmlFrame.configure(threading_enabled=)`
* `HtmlFrame.set_recursive_hover_depth()` - use `HtmlFrame.html.recursive_hover_depth=`
* `HtmlFrame.add_visited_links()` - use `HtmlFrame.configure(visited_links=)`
* `HtmlFrame.clear_visited_links()` - use `HtmlFrame.configure(visited_links=)`
* `HtmlFrame.enable_stylesheets()` - use `HtmlFrame.configure(stylesheets_enabled=)`
* `HtmlFrame.enable_images()` - use `HtmlFrame.configure(images_enabled=)`
* `HtmlFrame.enable_forms()` - use `HtmlFrame.configure(forms_enabled=)`
* `HtmlFrame.enable_objects()` - use `HtmlFrame.configure(objects_enabled=)`
* `HtmlFrame.enable_caches()` - use `HtmlFrame.configure(caches_enabled=)`
* `HtmlFrame.enable_dark_theme()` - use `HtmlFrame.configure(dark_theme_enabled=, image_inversion_enabled=)`
* `HtmlFrame.on_image_setup()` - use `HtmlFrame.configure(on_resource_setup=)`
* `HtmlFrame.on_downloading_resource()` - bind to `<<DownloadingResource>>`
* `HtmlFrame.on_done_loading()` - bind to `<<DoneLoading>>`
* `HtmlFrame.on_url_change()` - bind to `<<UrlChanged>>` and use `HtmlFrame.current_url`
* `HtmlFrame.on_icon_change()` - bind to `<<IconChanged>>` and use `HtmlFrame.icon`
* `HtmlFrame.on_title_change()` - bind to `<<TitleChanged>>` and use `HtmlFrame.title`
* `HtmlFrame.on_form_submit()` - use `HtmlFrame.configure(on_form_submit=)`
* `HtmlFrame.on_link_click()` - use `HtmlFrame.configure(on_link_click=)`
* `HtmlFrame.yview_towidget()` - use `HTMLElement.scrollIntoView()`
* `HtmlFrame.get_currently_hovered_node_text()` - use `HtmlFrame.get_currently_hovered_element()`
* `HtmlFrame.get_currently_hovered_node_tag()` - use `HtmlFrame.get_currently_hovered_element()`
* `HtmlFrame.get_currently_hovered_node_attribute()` - use `HtmlFrame.get_currently_hovered_element()`
* `HtmlFrame.get_current_link()` - use `HtmlFrame.get_currently_hovered_element()`
    
* The `widgetid` attribute no longer embeds widgets. Use `<object data=name_of_your_widget></object>` instead. This improves load speeds and allows for widget style handling.

### Renamed:
* `HtmlFrame.get_currently_selected_text()` -> `HtmlFrame.get_selection()`

* `TkwDocumentObjectModel` -> `HTMLDocument`
* `HtmlElement` -> `HTMLElement`

* `HtmlElement.style()` -> `HTMLElement.style`
* `HtmlElement.innerHTML()` -> `HTMLElement.innerHTML`
* `HtmlElement.textContent()` -> `HTMLElement.textContent`
* `HtmlElement.attributes()` -> `HTMLElement.attributes`
* `HtmlElement.tagName()` -> `HTMLElement.tagName`
* `HtmlElement.parentElement()` -> `HTMLElement.parentElement`
* `HtmlElement.children()` -> `HTMLElement.children`

* The `scroll-x` attribute was changed to the `tkinterweb-scroll-x` attribute. Like the `overflow` CSS property, valid options are now "auto", "visible", "clip", "scroll", and "hidden".


### Added:
* `HtmlFrame.clear_selection()`
* `HtmlFrame.get_currently_hovered_element()`
* `HtmlFrame.save_page()`
* `HtmlFrame.snapshot_page()`
* `HtmlFrame.show_error_page()`
* `HtmlFrame.print_page()`
* `HtmlFrame.screenshot_page()`
* `HtmlFrame.base_url`
* `HtmlFrame.icon`
* `HtmlFrame.title`

* `HTMLElement.getElementById()`
* `HTMLElement.getElementsByClassName()`
* `HTMLElement.getElementsByName()`
* `HTMLElement.getElementsByTagName()`
* `HTMLElement.querySelector()`
* `HTMLElement.querySelectorAll()`
* `HTMLElement.scrollIntoView()`

* `CSSStyleDeclaration`
* `CSSStyleDeclaration.* `(any camel-case CSS property)
* `CSSStyleDeclaration.cssText`
* `CSSStyleDeclaration.length`
* `CSSStyleDeclaration.cssProperties`
* `CSSStyleDeclaration.cssInlineProperties`

* `TkinterWeb.enable_imagecache()`
* `TkinterWeb.destroy_node()`
* `TkinterWeb.get_node_properties()`
* `TkinterWeb.override_node_properties()`
* `TkinterWeb.update_tags()`

* `utilities.DOWNLOADING_RESOURCE_EVENT` (equivalent to `<<DownloadingResource>>`)
* `utilities.DONE_LOADING_EVENT` (equivalent to `<<DoneLoading>>`)
* `utilities.URL_CHANGED_EVENT` (equivalent to `<<UrlChanged>>`)
* `utilities.ICON_CHANGED_EVENT` (equivalent to `<<IconChanged>>`)
* `utilities.TITLE_CHANGED_EVENT` (equivalent to `<<TitleChanged>>`)

* Many new configuration options were added. See the [HtmlFrame docs](/docs/HTMLFRAME.md#key-methods) for a complete list.

* The `tkinterweb-full-page` attribute can now be added to elements to make them the same height as the viewport. This can be used for vertical alignment of page content. See the TkinterWeb Demo class in [__init__.py](../tkinterweb/__init__.py) for example usage.

### Changed:
* `HtmlFrame.configure()`, `.config()`, `.cget()`, and `.__init__()` now supports more configuration options.
* `HtmlFrame.load_website()`, `.load_file()`, and `.load_url()` no longer accept the `insecure` parameter. use `HTMLElement.configure(insecure=)`.

* Enabling/disabling caches now enables/disables the Tkhtml image cache.
* Threading now cannot be enabled if the Tcl/Tk build does not support it.

* `HTMLElement.remove()` now raises a TclError when invoked on `<html>` or `<body>` elements, which previously caused segmentation faults.
* `HTMLElement.innerHTML` and `.textContent` now raise a TclError when invoked on `<html>` elements, which previously caused segmentation faults.

  
* The ability to style color selector inputs was improved.
* Text elements now emit the `<<Modified>>` event *after* the content updates.
  

* The TkinterWeb demo and some of the built-in pages have been updated. Many internal methods and variables of the HtmlFrame and TkinterWeb widgets were renamed or moved.


&nbsp;

Apologies for any extra trouble this overhaul might cause. It was needed.
