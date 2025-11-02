Using Caret Browsing Mode
=========================

.. note::
    Caret browsing support is new in version 4.8. Make sure you are using the latest version of TkinterWeb.

Overview
--------

**Caret browsing can be used to turn TkinterWeb into a rich text or HTML editor.**

As the specific behaviour of rich text or HTML editors is highly variable, TkinterWeb is not intended to be a full-featured HTML editor out of the box, but it provides a useful API for developers to easily create their own what-you-see-is-what-you-get editor.

This feature is new. Please reach out to report a bug, suggest an improvement, or seek support.

Setup
------

To enable caret browsing mode in TkinterWeb, add ``yourhtmlframe.configure(caret_browsing_enabled=True)`` to your script or add the parameter ``caret_browsing_enabled=True`` when creating your :class:`~tkinterweb.HtmlFrame` or :class:`~tkinterweb.HtmlLabel` widget.

When caret browsing mode is enabled, a caret will appear once the user clicks on text in the document. Unless the default keybindings are overridden, this caret can be moved by clicking elsewhere or by using the arrow keys.

How-to
------

Use :meth:`.HtmlFrame.get_caret_position` to get the caret's position. The element returned will always be a text node. You can use the methods outlined in the `HTMLElement documentation <api/htmldocument.html#tkinterweb.dom.HTMLElement>`_ to get its parent or siblings if needed.

Use :meth:`.HtmlFrame.shift_caret_left` or :meth:`.HtmlFrame.shift_caret_right` to shift the caret left or right.

The following is a simple example showing how to handle keypresses to insert letters and numbers:

.. code-block:: python
    
    def on_keypress(event):
        # Get the caret's position
        caret_position = yourhtmlframe.get_caret_position()
        if caret_position and event.char:
            element, text, index = caret_position
            
            # Add the key's character to the element's text
            newtext = text[:index] + event.char + text[index:]

            # Set the element's text
            element.textContent = newtext

            # Shift the caret right
            yourhtmlframe.shift_caret_right()

    yourhtmlframe.bind("<Key>", on_keypress)

.. note::
    Most HTML elements collapse spaces. To insert a space into the document's text, it is usually best to use a non-breaking space (``"\xa0"`` or ``"&nbsp;"``).

Use :meth:`.HtmlFrame.set_caret_position` to set the caret's position if you know the element and index you want to place the caret at.

Some extra logic will be needed to handle other types of keypresses. 

.. tip::
    When handling backspaces at the start of a node or deletions at the end of a node, it is sometimes useful to find the previous or following text nodes, respectively. 
    
    You can get the preceeding or following text nodes by using :meth:`.HtmlFrame.shift_caret_left` or :meth:`.HtmlFrame.shift_caret_right` followed by :meth:`.HtmlFrame.get_caret_position`.

Managing selected text
----------------------

Use :meth:`.HtmlFrame.get_selection_position` to get the position of any selected text and :meth:`.HtmlFrame.clear_selection` to clear the selection. 

You will need to set the caret's position after modifying the document.

.. tip::
    :meth:`.HtmlFrame.set_caret_position` will raise an error if the element provided has been removed or is empty. 
    
    If you need to remove or empty the elements returned by :meth:`.HtmlFrame.get_selection_position`, consider also getting the selection's position relative to the page text content using :meth:`.HtmlFrame.get_selection_page_position` to avoid losing track of the selection's position.

    You can then use :meth:`.HtmlFrame.set_caret_page_position` to set the caret relative to the page text content. 


The following code can be used as a starting point on handling backspaces when text is selected:

.. code-block:: python

    def on_backspace(event):
        # Get the selection's position and deselect all selected text
        selection = yourhtmlframe.get_selection_position()

        if selection:
            start, end, middle = selection
            start_element, start_element_text, start_element_index = start
            end_element, end_element_text, end_element_index = end

            # Get the position of the selection relative to the page text and deselect all selected text
            start_pos, end_pos = yourhtmlframe.get_selection_page_position()
            yourhtmlframe.clear_selection()

            if start_element == end_element: 
                # If the selected text is only in one element, cut out the selection from the element's text
                start_element.textContent = start_element_text[:start_element_index] + start_element_text[end_element_index:]

            else:
                # Otherwise, remove the selected part of the starting element's text (the part after 'start_element_index')
                start_element.textContent = start_element_text[:start_element_index]

                # Remove the selected part of the end element's text (the part before 'end_element_index')
                end_element.textContent = end_element_text[end_element_index:]

                # Remove each element that is fully selected, and its parent if it is now empty
                for element in middle: 
                    parent = element.parentElement
                    element.remove()
                    if len(parent.children) == 0:
                        parent.remove()

            # Set the caret's position 
            yourhtmlframe.set_caret_page_position(start_pos)

    yourhtmlframe.bind("<BackSpace>", on_backspace)

You can use :meth:`.HtmlFrame.set_selection_position` to set the selection if needed.

-------------------

See the `HtmlFrame documentation <api/htmlframe.html#tkinterweb.HtmlFrame.get_caret_position>`_ for a detailed list of supported methods.

Please report bugs or request new features on the `issues page <https://github.com/Andereoo/TkinterWeb/issues>`_.