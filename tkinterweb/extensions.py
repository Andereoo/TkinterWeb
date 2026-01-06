"""
Extensions to Tkhtml3

Copyright (c) 2021-2025 Andrew Clarke
"""

from re import IGNORECASE, MULTILINE, finditer

from tkinter import Frame, Event, TclError
from . import utilities

class BlinkyFrame(Frame):
    # A blinking caret-style frame
    def __init__(self, master, *args, blink_delays=[600, 300], **kwargs):
        Frame.__init__(self, master, *args, **kwargs)
        self.blink_delays = blink_delays

        self._is_placed = False
        self._x = 0
        self._y = 0
        self.pending = None

    def place(self, x, y, *args, _internal=False, **kwargs):
        if _internal:
            super().place(*args, x=x, y=y, **kwargs)
        else:
            if self.pending:
                self.after_cancel(self.pending)
            self._is_placed = True
            self._x = x
            self._y = y
            super().place(*args, x=x, y=y, **kwargs)
            self.pending = self.after(self.blink_delays[0], self._blink)

    def place_forget(self, _internal=False):
        if not _internal:
            if self.pending:
                self.after_cancel(self.pending)
            self.pending = None
            self._is_placed = False
        super().place_forget()

    def _blink(self):
        if self._is_placed:
            self.place_forget(True)
            delay = self.blink_delays[1]
        else:
            self.place(self._x, self._y, _internal=True)
            delay = self.blink_delays[0]
        
        self.update()
        self._is_placed = not(self._is_placed)
        self.pending = self.after(delay, self._blink)


class SelectionManager(utilities.BaseManager):
    """An extension to manage the selection's state. Largely internal. 
    
    Only interact with this object if the convenience methods provided elsewhere are insufficient.

    This object can be accessed through the :attr:`~tkinterweb.TkinterWeb.selection_manager` property of the :class:`~tkinterweb.TkinterWeb` widget.

    :ivar html: The associated :class:`~tkinterweb.TkinterWeb` instance.
    :ivar node: The node the caret is in.
    :ivar selection_type: The state of the selection (0, 1, or 2), used when double-clicking.
    :ivar selection_start_node: The node containing the start of the selection.
    :ivar selection_start_offset: The selection's offset within the node.
    :ivar selection_end_node: The node containing the end of the selection.
    :ivar selection_end_offset: The selection's offset within the node.

    New in version 4.11."""
    
    def __init__(self, html):
        super().__init__(html)

        self.selection_type = 0
        self.selection_start_node = None
        self.selection_start_offset = None
        self.selection_end_node = None
        self.selection_end_offset = None

    def __repr__(self):
        return f"{self.html._w}::{self.__class__.__name__.lower()}"
    
    def begin_selection(self, node, offset):
        "Begin selecting."
        self.selection_start_node = node
        self.selection_start_offset = offset

    def reset(self):
        self.selection_end_node = None
        self.selection_end_offset = None

    def reset_selection_type(self):
        "Reset the selection type."
        self.selection_type = 0

    def clear_selection(self):
        "Clear the current selection."
        self.html.tag("delete", "selection")
        self.selection_start_node = None
        self.selection_end_node = None

    def update_tags(self):
        "Update selection and find tag colours."
        self.html.tag("configure", "findtext", "-bg", self.html.find_match_highlight_color, "-fg", self.html.find_match_text_color)
        self.html.tag("configure", "findtextselected", "-bg", self.html.find_current_highlight_color, "-fg", self.html.find_current_text_color)
        self.html.tag("configure", "selection", "-bg", self.html.selected_text_highlight_color, "-fg", self.html.selected_text_color)

    def select_all(self):
        "Select all text in the document."
        if not self.html.selection_enabled:
            return
        
        self.clear_selection()
        beginning = self.html.text("index", 0)
        end = self.html.text("index", len(self.html.text("text")))
        self.selection_start_node = beginning[0]
        self.selection_start_offset = beginning[1]
        self.selection_end_node = end[0]
        self.selection_end_offset = end[1]
        self.update_selection()

    def _word_in_node(self, node, offset):
        text = self.html.get_node_text(node)
        letters = list(text)

        beg = 0
        end = 0
        for index, letter in enumerate(reversed(letters[:offset])):
            beg = index + 1
            if letter == " ":
                beg = index
                break
        for index, letter in enumerate(letters[offset:]):
            end = index + 1
            if letter == " ":
                end = index
                break

        pre = len(letters[:offset])
        return pre - beg, pre + end

    def double_click_selection(self):
        "Stimulate a double-click on the selection."
        if not self.selection_start_node:
            return
        
        if self.selection_type == 1:
            text = self.html.get_node_text(self.selection_start_node)
            self.selection_start_offset = 0
            self.selection_end_node = self.selection_start_node
            self.selection_end_offset = len(text)
            self.update_selection()
            self.selection_type = 2

        elif self.selection_type == 2:
            self.clear_selection()
            self.selection_type = 0

        else:
            start_offset, end_offset = self._word_in_node(self.selection_start_node, self.selection_start_offset)
            self.selection_end_node = self.selection_start_node
            self.selection_start_offset = start_offset
            self.selection_end_offset = end_offset
            self.update_selection()
            self.selection_type = 1

    def extend_selection(self, node, offset):
        "Extend the selection."
        self.selection_end_node = node
        self.selection_end_offset = offset
        if self.selection_type == 1:
            start_offset, end_offset = self._word_in_node(self.selection_start_node, self.selection_start_offset)
            start_offset2, end_offset2 = self._word_in_node(self.selection_end_node, self.selection_end_offset)
            start_index = self.html.text("offset", self.selection_start_node, self.selection_start_offset)
            end_index = self.html.text("offset", self.selection_end_node, self.selection_end_offset)
            if start_index > end_index:
                self.selection_start_offset = end_offset
                self.selection_end_offset = start_offset2
            else:
                self.selection_start_offset = start_offset
                self.selection_end_offset = end_offset2

        elif self.selection_type == 2:
            start_index = self.html.text("offset", self.selection_start_node, self.selection_start_offset)
            end_index = self.html.text("offset", self.selection_end_node, self.selection_end_offset)
            if start_index > end_index:
                text = self.html.get_node_text(self.selection_start_node)
                self.selection_start_offset = len(text)
                self.selection_end_offset = 0
            else:
                text = self.html.get_node_text(self.selection_end_node)
                self.selection_start_offset = 0
                self.selection_end_offset = len(text)
            
        self.update_selection()

    def update_selection(self):
        "Update the current selection."
        self.html.tag("delete", "selection")
        self.html.tag(
            "add",
            "selection",
            self.selection_start_node,
            self.selection_start_offset,
            self.selection_end_node,
            self.selection_end_offset,
        )
        self.html.tag(
            "configure",
            "selection",
            "-bg",
            self.html.selected_text_highlight_color,
            "-fg",
            self.html.selected_text_color,
        )
    
    def get_selection(self):
        "Return any selected text."
        if self.selection_start_node is None or self.selection_end_node is None:
            return
        if self.selection_type == 1:
            start_offset, end_offset = self._word_in_node(self.selection_start_node, self.selection_start_offset)
            start_offset2, end_offset2 = self._word_in_node(self.selection_end_node, self.selection_end_offset)
            start_index = self.html.text(
                "offset", self.selection_start_node, start_offset
            )
            end_index = self.html.text(
                "offset", self.selection_end_node, end_offset2
            )
            if start_index > end_index:
                start_index = self.html.text(
                    "offset", self.selection_end_node, start_offset2
                )
                end_index = self.html.text(
                    "offset", self.selection_start_node, end_offset
                )

        elif self.selection_type == 2:
            text = self.html.get_node_text(self.selection_start_node)
            text2 = self.html.get_node_text(self.selection_end_node)
            start_index = self.html.text(
                "offset", self.selection_start_node, 0
            )
            end_index = self.html.text(
                "offset", self.selection_end_node, len(text2)
            )
            if start_index > end_index:
                start_index = self.html.text(
                    "offset", self.selection_end_node, 0
                )
                end_index = self.html.text(
                    "offset", self.selection_start_node, len(text)
                )
        else:
            start_index = self.html.text(
                "offset", self.selection_start_node, self.selection_start_offset
            )
            end_index = self.html.text(
                "offset", self.selection_end_node, self.selection_end_offset
            )
            if start_index > end_index:
                start_index, end_index = end_index, start_index
                
        whole_text = self.html.text("text")
        return whole_text[start_index:end_index]

    def copy_selection(self):
        "Copy the selected text to the clipboard."
        selected_text = self.get_selection()
        self.html.clipboard_clear()
        self.html.clipboard_append(selected_text)
        self.html.post_message(f"The text '{selected_text}' has been copied to the clipboard")


class CaretManager(utilities.BaseManager):
    """An extension to manage the caret's state. Largely internal. 
    
    Only interact with this object if the convenience methods provided elsewhere are insufficient.

    This object can be accessed through the :attr:`~tkinterweb.TkinterWeb.caret_manager` property of the :class:`~tkinterweb.TkinterWeb` widget.

    :ivar html: The associated :class:`~tkinterweb.TkinterWeb` instance.
    :ivar node: The node the caret is in.
    :ivar offset: The caret's offset within the node.
    :ivar index: The document text index of the start of the node; fallback if the node is deleted.
    :ivar caret_frame: The blinky widget.
    :ivar target_offset: The text offset used for traversing up/down.
    :ivar blink_delay: The caret's blink delay, in milliseconds. Updated in version 4.11.
    :ivar caret_width: The caret's width, in pixels. New in version 4.11.
    :ivar caret_colour: The caret's colour. If None, the text colour under it will be matched.
    :ivar scrolling_threshold: If the distance between the visible part of the page and the caret is nonzero but is less than this number, a scrolling animation will play.
    :ivar scrolling_teleport: If the distance between the visible part of the page and the caret is nonzero but is greater than :attr:`scrolling_threshold`, the page is scrolled to this number before the scrolling animation plays.
    
    New in version 4.8."""
    
    def __init__(self, html):
        super().__init__(html)

        self.node = None
        self.offset = None
        self.index = None
        self.caret_frame = None
        #self.target_node = None
        self.target_offset = None

        self.blink_delays = [600, 300]
        self.caret_width = 1
        self.caret_colour = None
        self.scrolling_threshold = 300 
        self.scrolling_teleport = 75

    def __repr__(self):
        return f"{self.html._w}::{self.__class__.__name__.lower()}"

    def set(self, node, offset, recalculate=False):
        "Set the caret's position."
        if not node and not recalculate: return

        if not node:
            self.index = offset
            self.node, self.offset = self.html.text("index", offset)
            self.target_offset = self.offset
            fallback = self.shift_left
        elif recalculate:
            # If the caret's position is being set by the user, determine the node and offset using the document text
            # This allows for shifting before and past the node
            self.index = self.html.text("offset", node, 0)
            self.node, self.offset = self.html.text("index", self.index + offset)
            self.target_offset = self.offset
            if offset > 0:
                fallback = self.shift_left
            else:
                fallback = self.shift_right
        else:
            self.node = node #self.target_node = node
            self.offset = self.target_offset = offset
            self.index = self.html.text("offset", node, 0)
            fallback = self.shift_left
        self.update(fallback=fallback)

    def is_placed(self):
        "Check if the caret has been placed onto the document."
        return True if self.node else False

    def register_nodes_from_index(self, event, index, update_caret_start=False):
        "Update the caret's internal state."
        node, offset = self.html.text("index", index)
        self.index = self.html.text("offset", node, 0)

        if event:
            if (event.state & 0x1) != 0:
                if not self.html.selection_manager.selection_start_node:
                    self.html.selection_manager.selection_start_node = self.node
                    self.html.selection_manager.selection_start_offset = self.offset
                self.node, self.offset = node, offset
                self.html.selection_manager.selection_end_node = self.node
                self.html.selection_manager.selection_end_offset = self.offset
            else:
                self.node, self.offset = node, offset
        else:
            self.node, self.offset = node, offset
        
        if update_caret_start:
            #self.target_node = self.node
            self.target_offset = self.offset

    def shift_up(self, event=None):     
        "Shift the caret up."   
        if not self.node:
            return
        
        index = self.html.text("offset", self.node, self.offset)
        text = self.html.text("text")

        if type(index) == str: index = self.index

        # Get the previous newline
        index = text.rfind("\n", 0, index)

        if index == -1:
            index = 0
        else:
            # Ensure that the index we land on is not blank or a newline
            while index > 0 and text[index] in {" ", "\n"}:
                index -= 1

            # Get the beginning of the line
            beginning_index = text.rfind("\n", 0, index)
            if beginning_index != -1:
                index += 1
                # Attempt to go to the offset in that line corresponding to self.target_offset
                # If the line is too short, go to the end of the line
                ideal_index = beginning_index + self.target_offset + 1

                if ideal_index < index:
                    index = ideal_index

        try:
            # in case `node, offset = self.html.text("index", index)` fails
            self.register_nodes_from_index(event, index)
            self.update(event)
        except TclError:
            pass

    def shift_down(self, event=None):
        "Shift the caret down."
        if not self.node:
            return
    
        index = self.html.text("offset", self.node, self.offset)
        text = self.html.text("text").rstrip("\n") + "\n"
        text_length = len(text) - 1

        if type(index) == str: index = self.index

        # Get the next newline
        index = text.find("\n", index)
        if index == -1:
            index = text_length
        else:
            # Ensure that the index we land on is not blank or a newline
            while index < text_length and text[index] in {" ", "\n"}:
                index += 1

            # Attempt to go to the offset in that line corresponding to self.target_offset
            # If the line is too short, go to the end of the line
            ideal_index = index + self.target_offset

            if ideal_index < text_length:
                newline_pos = text.find("\n", index, ideal_index)
                if newline_pos != -1:
                    index = newline_pos
                else:
                    index = ideal_index

        try:
            self.register_nodes_from_index(event, index)
            self.update(event)
        except TclError:
            pass

    def shift_left(self, event=None, update_caret_start=True):
        "Shift the caret left."
        if not self.node:
            return
        
        index = self.html.text("offset", self.node, self.offset)
        text = self.html.text("text")
        if type(index) == str: index = self.index
        if index > len(text): index = len(text)
        
        # Shift left one letter
        index -= 1

        # If Ctrl is pressed, shift to the end of the previous space or newline
        if event and ((event.state & 0x4) != 0):
            index = max(text.rfind(" ", 0, index), text.rfind("\n", 0, index))
            if index == -1: 
                index = 0
            else:
                index += 1
        else:
            # Ensure that the index we land on is not a newline
            changed = False
            while index > 0 and text[index] == "\n":
                index -= 1
                changed = True
            if changed:
                index += 1
        
        try:
            self.register_nodes_from_index(event, index, update_caret_start)
            self.update(event)
        except TclError:
            pass

    def shift_right(self, event=None, update_caret_start=True):
        "Shift the caret right."
        if not self.node:
            return
        
        index = self.html.text("offset", self.node, self.offset)
        text = self.html.text("text").rstrip("\n") + "\n"
        text_length = len(text) - 1

        if type(index) == str: index = self.index

        if event and ((event.state & 0x4) != 0):
            # If Ctrl is pressed, shift to the start of the next space or newline
            next_positions = [i for i in (text.find(" ", index + 1), text.find("\n", index + 1)) if i != -1]
            index = min(next_positions) if next_positions else text_length
        else:
            # Ensure that the index we land on is not a newline
            changed = False
            while index < text_length and text[index] == "\n":
                index += 1
                changed = True
            # Otherwise, shift right one letter
            if not changed and index < text_length:
                index += 1
        
        try:
            self.register_nodes_from_index(event, index, update_caret_start)
            self.update(event, fallback=self.shift_right)
        except TclError:
            pass

    def update(self, event=None, auto_scroll=True, fallback=None):
        "Refresh the caret or update its position."
        if not fallback:
            fallback = self.shift_left

        if not self.node:
            return
    
        self.html.update() # Particularly important when this method runs after the document is scrolled
        if not self.caret_frame:
            self.caret_frame = BlinkyFrame(self.html, blink_delays=self.blink_delays, width=self.caret_width)
            
        try:
            a, b, c, d = self.html.text("bbox", self.node, self.offset, self.node, self.offset)
        except ValueError:
            # A newline doesn't belong to the node
            # If the caret is at the end of a line of text, the node returned will be different from the node we want to actually put the caret beside
            # For some reason, when scrolling, the y values from bbox() of content that doesn't move with the document are sometimes wrong
            # text("bbox") is more accurate
            # However, offset is not defined for a node's end
            # So we get the end of the previous character instead
            try:
                a2, b, c2, d = self.html.text("bbox", self.node, self.offset-1, self.node, self.offset-1)
                a = c2
                c = c2 + (c2-a2)
            except ValueError:
                return fallback(event, update_caret_start=False)
                            
        x1, y1, x2, y2 = self.html.bbox()
        yoffset = self._scroll_if_needed(b, d, y1, y2, auto_scroll)
        xoffset = self._scroll_if_needed(a, c, x1, x2, auto_scroll, 1)

        if (xoffset != None) and (yoffset != None): # Otherwise, yview/xview automatically re-calls this function, so we exit
            if self.caret_colour:
                bg = self.caret_colour
            else:
                bg = self.html.get_node_property(self.html.get_node_parent(self.node), "color")
            self.caret_frame.config(height=d-b, bg=bg, width=self.caret_width)
            self.caret_frame.place(x=a-xoffset, y=b-yoffset)
        
            if self.html.selection_enabled and event:
                if ((event.state & 0x1) != 0):
                    self.html.selection_manager.update_selection()
                else:
                    self.html.selection_manager.clear_selection()

    def hide(self):
        "Hide the caret. Show the caret again by calling :meth:`.CaretManager.update`."
        if self.node:
            self.caret_frame.place_forget()

    def reset(self):
        "Hide the caret and reset its position."
        if self.node:
            self.node = None
            self.offset = None
            self.caret_frame.place_forget()

    def _scroll_if_needed(self, node_start, node_end, viewport_start, viewport_end, auto_scroll, direction=0):
        """Scroll the caret into view if needed.
        We could scroll directly to the correct position,
        But it's easier to let Tkhtml do the work of detecting lines.
        Using yview_moveto, for instance, can be used to scroll to the top of the node,
        But then a node on the same line that is taller would be cut off.
        So we use moveto to get close if needed and use scroll to do the rest.
        As a side effect, this gives us a bit of a scrolling animation, which I think is a good thing if anything."""
        if direction: 
            command = self.html.xview
        else:
            command = self.html.yview

        start, end = command()
        top_offset = start * (viewport_end - viewport_start)
        bottom_offset = end * (viewport_end - viewport_start)

        if auto_scroll:
            if node_end >= 0 and (node_end - self.scrolling_threshold) > bottom_offset:
                command("moveto", (node_end - self.html.winfo_height() - self.scrolling_teleport) / viewport_end, auto_scroll=True)
                return None
            elif node_end >= 0 and node_end > bottom_offset:
                command("scroll", 1, "units", auto_scroll=True)
                return None
            elif node_start >= 0 and (node_start + self.scrolling_threshold) < top_offset:
                command("moveto", (node_start + self.scrolling_teleport) / viewport_end, auto_scroll=True)
                return None
            elif node_start >= 0 and node_start < top_offset:
                command("scroll", -1, "units", auto_scroll=True)
                return None
        return top_offset


class EventManager(utilities.BaseManager):
    """An extension to manage custom node bindings and JavaScript events. Largely internal. 
    
    Only interact with this object if the convenience methods provided elsewhere are insufficient.

    This object can be accessed through the :attr:`~tkinterweb.TkinterWeb.event_manager` property of the :class:`~tkinterweb.TkinterWeb` widget.

    :ivar html: The associated :class:`~tkinterweb.TkinterWeb` instance.
    :ivar bindings: A dictionary of bindings. You shouldn't need to touch this.
    :ivar loaded_elements: A list storing loaded elements.

    New in version 4.10."""

    ### We use the JavaScript event system to handle some element bindings
    ### If a binding is requested but isn't handled by TkinterWeb by default, we create a new binding to deal with it
    
    def __init__(self, html):
        super().__init__(html)
        
        self.bindings = {}
        self.loaded_elements = []

    def __repr__(self):
        return f"{self.html._w}::{self.__class__.__name__.lower()}"
    
    # --- Tk events -----------------------------------------------------------

    def reset(self):
        "Reset all bindings."

        for event in self.bindings:
            if event not in utilities.EVENT_MAP:
                self.html.unbind_class(self.html.tkinterweb_tag, event)
            
        self.bindings.clear()
        self.loaded_elements.clear()

    def post_event(self, node, JS_event_name, event=None, Tk_event_name=None):
        """Given a CSS node and JavaScript event name, trigger any related bindings.

        If  :attr:`event` is provided, the event generated will be modified from the given event.
        If  :attr:`Tk_event_name` is provided, an event will be created using the given name.

        All generated events have the additional ``node`` property, representing the corresponding Tkhtml node. """
        if JS_event_name not in self.bindings:
            return

        node_callbacks = self.bindings[JS_event_name].get(node)
        if not node_callbacks:
            return

        for callback in node_callbacks:
            if event:
                new_event = self.create_modified_event(node, event, Tk_event_name)
            else:
                new_event = self.create_new_event(node, Tk_event_name)
                
            self.html.after(0, callback, new_event)
    
    def create_modified_event(self, node, event, Tk_event_name=None):
        "Create a new event using details from :attr:`event`."
        new_event = Event()
        new_event.widget = self,
        new_event.node = node,
        new_event.delta = event.delta
        new_event.num = event.num
        new_event.state = event.state

        if Tk_event_name:
            new_event.type = Tk_event_name
        else:
            new_event.type = event.type
            
        new_event.char = event.char
        new_event.x = event.x
        new_event.y = event.y
        return new_event
    
    def create_new_event(self, node, Tk_event_name):
        "Create a new event."
        new_event = Event()
        new_event.widget = self,
        new_event.node = node,
        new_event.type = Tk_event_name
        new_event.char = 0
        new_event.state = 0
        new_event.delta = 0
        return new_event
    
    def _on_demand_binding_callback(self, event, name):
        if not self.html.events_enabled:
            return
        
        if name not in self.bindings:
            return
        
        bindings = self.bindings[name]
        
        if not self.html.current_node:
            self.html._on_mouse_motion(event)

        for node_handle in self.html.hovered_nodes:
            if node_handle in bindings: 
                callbacks = bindings[node_handle]
                for callback in callbacks:
                    event = self.create_modified_event(node_handle, event)
                    self.html.after(0, callback, event)  

    def _check_binding_name(self, event):
        if event in utilities.EVENT_MAP:
            return False
        
        for sequence in utilities.UNHANDLED_EVENT_WHITELIST:
            if sequence in event:
                return True
            
        raise KeyError(f"the event {event} is either unsupported or invalid")

    def bind(self, node, event, callback, add=None):
        "Add a binding."        
        if self._check_binding_name(event):
            if event not in self.bindings:
                self.html.bind_class(self.html.tkinterweb_tag, event, lambda event, name=event: self._on_demand_binding_callback(event, name))
        else:
            event = utilities.EVENT_MAP[event]

        event_bindings = self.bindings.setdefault(event, {})
        if add:
            callbacks = event_bindings.setdefault(node, [])
            callbacks.append(callback)
        else:
            callbacks = [callback]
        self.bindings[event][node] = callbacks

    def unbind(self, node, event, funcid=None):
        "Remove a binding."
        if event not in self.bindings or node not in self.bindings[event]:
            raise KeyError("the requested binding does not exist")
        
        if funcid:
            callbacks = self.bindings[event][node]           
            try:
                callbacks.remove(funcid)
            except ValueError:
                raise KeyError("the requested binding does not exist")
            if not callbacks:
                del self.bindings[event][node]
        else:
            del self.bindings[event][node]

        if not self.bindings[event]:
            del self.bindings[event]
            if event not in utilities.EVENT_MAP:
                self.html.unbind_class(self.html.tkinterweb_tag, event)

    # --- JavaScript/Tk events ------------------------------------------------

    def post_element_event(self, node_handle, attribute, event=None, event_name=None):
        """Post an element event.
        
        New in version 4.11."""
        
        # Post the JavaScript event first if needed
        if self.html.javascript_enabled:
            if attribute == "onload":
                if node_handle in self.loaded_elements:
                    # Don't run the onload script twice
                    return
                else:
                    self.loaded_elements.append(node_handle)
            if attribute in utilities.JS_EVENT_MAP:
                # If the event is a non-standard event (i.e. onscrollup), convert it
                attribute = utilities.JS_EVENT_MAP[attribute]
            if attribute:
                mouse = self.html.get_node_attribute(node_handle, attribute)
                if mouse:
                    self.html.on_element_script(node_handle, attribute, mouse)
        
        # Then post the Tkinter event
        if self.html.events_enabled and (event or event_name):
            self.post_event(node_handle, attribute, event, event_name)

    def send_onload(self, root=None, children=None):
        """Send the onload signal for nodes that aren't handled at runtime.
        We keep this a seperate command so that it can be run after inserting elements or changing the innerHTML.

        New in version 4.11."""
        # Don't bother worring about element bindings...they can't be set if the element doesn't exist
        if not self.html.javascript_enabled:
            return
        if children:
            for node in children:
                if self.html.get_node_tag(node) not in {"img", "object", "link"}:
                    self.post_element_event(node, "onload")
        else:
            for node in self.html.search("[onload]", root=root):
                if self.html.get_node_tag(node) not in {"img", "object", "link"}:
                    self.post_element_event(node, "onload")
                

class WidgetManager(utilities.BaseManager):
    """An extension to manage stored widgets. Largely internal. 
    
    Only interact with this object if the convenience methods provided elsewhere are insufficient.

    This object can be accessed through the :attr:`~tkinterweb.TkinterWeb.widget_manager` property of the :class:`~tkinterweb.TkinterWeb` widget.

    :ivar html: The associated :class:`~tkinterweb.TkinterWeb` instance.
    :ivar widget_container_attr: The HTML attribute given to elements containing a widget.
    :ivar hovered_embedded_node: True if the mouse is over a widget in the document, otherwise False.

    New in version 4.11."""
    
    def __init__(self, html):
        super().__init__(html)

        ### TODO: see if there's a way we can avoid setting an attribute on replaced nodes
        self.widget_container_attr = "-tkinterweb-widget-container"
        self.hovered_embedded_node = None

    def __repr__(self):
        return f"{self.html._w}::{self.__class__.__name__.lower()}"
    
    def reset(self):
        self.hovered_embedded_node = None

    def get_node_widget(self, node):
        "Get the widget associated with the given node."
        widget = self.html.get_node_replacement(node)
        
        if widget == node or not widget:
            return None
        
        return self.html.nametowidget(widget)

    def handle_node_replacement(self, node, widgetid, deletecmd, stylecmd=None, allowscrolling=True, handledelete=True):
        """Replace a Tkhtml3 node with a Tkinter widget. 
        
        This method is used internally by :meth:`~tkinterweb.extensions.WidgetManager.set_node_widget` and offers more control.
         
        I don't recommend using it unless absolutely needed."""
        self.html.set_node_attribute(node, self.widget_container_attr, widgetid)
        if stylecmd:
            if handledelete:
                self.html.replace_node_contents(
                    node, widgetid,
                    "-deletecmd", self.html.register(deletecmd),
                    "-stylecmd", self.html.register(stylecmd),
                )
            else:
                self.html.replace_node_contents(
                    node, widgetid, "-stylecmd", self.html.register(stylecmd)
                )
        else:
            if handledelete:
                self.html.replace_node_contents(
                    node, widgetid, "-deletecmd", self.html.register(deletecmd)
                )
            else:
                self.html.replace_node_contents(node, widgetid)

        self.html._add_bindtags(widgetid, allowscrolling)
        for child in widgetid.winfo_children():
            self.html._add_bindtags(child, allowscrolling)
            
        widgetid.bind(
            "<Enter>",
            lambda event, node_handle=node: self._on_embedded_mouse_enter(
                event, node_handle=node_handle
            ),
        )
        widgetid.bind(
            "<Leave>",
            lambda event, node_handle=None: self._on_embedded_mouse_leave(
                event, node_handle=node_handle
            ),
        )

    def _handle_node_removal(self, widgetid):
        widgetid.destroy()

    def _handle_node_style(self, node, widgetid, widgettype="button"):
        if widgettype == "button":
            bg = "transparent"
            while bg == "transparent" and node != "":
                bg = self.html.get_node_property(node, "background-color")
                node = self.html.get_node_parent(node)
            if bg == "transparent":
                bg = "white"
            widgetid.configure(
                background=bg,
                highlightbackground=bg,
                highlightcolor=bg,
                activebackground=bg,
            )
        elif widgettype == "range":
            bg = "transparent"
            while bg == "transparent" and node != "":
                bg = self.html.get_node_property(node, "background-color")
                node = self.html.get_node_parent(node)
            if bg == "transparent":
                bg = "white"
            widgetid.configure(background=bg)
        elif widgettype == "text":
            bg = self.html.get_node_property(node, "background-color")
            fg = self.html.get_node_property(node, "color")
            font = self.html.get_node_property(node, "font")
            if bg == "transparent":
                bg = "white"
            if fg == "transparent":
                fg = "white"
            try:
                widgetid.configure(background=bg, foreground=fg, font=font)
            except (TclError, ValueError, ):
                widgetid.configure(background=bg)
        elif widgettype == "auto":
            bg = self.html.get_node_property(node, "background-color")
            fg = self.html.get_node_property(node, "color")
            font = self.html.get_node_property(node, "font")
            if bg == "transparent":
                bg = "white"
            if fg == "transparent":
                fg = "white"
            widgets = [widgetid] + [widget for widget in widgetid.winfo_children()]
            for widget in widgets:
                try:
                    widget.configure(background=bg, foreground=fg, font=font)
                except (TclError, ValueError, ):
                    widget.configure(background=bg)

    def map_node(self, node, force=False):
        "Redraw a node if it currently contains a Tk widget."
        if force or (self.get_node_widget(node)):
            self.html.replace_node_contents(node, node)

    def set_node_widget(self, node, widgetid=None):
        "Replace a node with a Tk widget."
        if not widgetid:
            # Reset the node if a widget is not supplied
            self.map_node(node)
            return
            
        manager = widgetid.winfo_manager()
        if manager == "Tkhtml":  # Don't display the same widget twice
            for old_node in self.html.search(f"[{self.widget_container_attr}]"):
                if self.html.get_node_attribute(old_node, self.widget_container_attr) == str(widgetid):
                    # If we know where the widget is, 
                    # Replace the old node with its original contents so we can redraw the widget here
                    self.map_node(old_node)
                    break
            else:
                raise TclError(f"cannot embed widget already managed by {manager}")
        # Tkhtml seems to remove the widget from the previous geometry manager if it is not Tkhtml so I think we are fine

        handleremoval = self.html.get_node_attribute(node, "handleremoval", "false") != "false"

        # Handle scrolling
        # If set to "auto" (default), scrolling will work on the widget as long as no bindings are already set on it
        allowscrolling = self.html.get_node_attribute(node, "allowscrolling", "auto")
        if allowscrolling == "auto":
            widgets = [widgetid] + [widget for widget in widgetid.winfo_children()]
            allowscrolling = True
            events = ("<MouseWheel>", "<Button-4>", "<Button-5>")
            ignore = {".", "all"}
            def check_scrolling():
                for widget in widgets:
                    for tag in widget.bindtags():
                        if tag in ignore: continue
                        for event in events:
                            if widget.bind_class(tag, event):
                                return False
                return True
            allowscrolling = check_scrolling()
        elif allowscrolling in {"", "true"}:
            allowscrolling = True
        else:
            allowscrolling = False

        # Handle styling
        # If set to "false" (default), nothing will be done
        # If set to "deep", the widget and any children are styled
        # If set to "true" or "auto", only the widget will be styled
        allowstyling = self.html.get_node_attribute(node, "allowstyling", "false")
        if allowstyling == "deep":
            allowstyling = lambda node=node, widgetid=widgetid, widgettype="auto": self._handle_node_style(node, widgetid, widgettype)
        elif allowstyling in {"", "true", "auto"}:
            allowstyling = lambda node=node, widgetid=widgetid, widgettype="text": self._handle_node_style(node, widgetid, widgettype)
        else:
            allowstyling = None

        if handleremoval:
            # Tkhtml's -deletecmd handler is quite broken
            # I would instead give the widget an extra class and bind to <Unmap>
            # But apparently that doesn't fire at all. Oh well.
            handleremoval = lambda widgetid=widgetid: self._handle_node_removal(widgetid)
        else:
            handleremoval = None
        
        # We used to add the node to a dict but we need to be able to delete it when destroy is called on any of its parents
        # By setting an attribute we can use Tkhtml's search function to check if the widget exists elsewhere without having to invert a dict
        # I'll probably change that eventually
        self.handle_node_replacement(
            node,
            widgetid,
            handleremoval,
            allowstyling,
            allowscrolling,
            False,
        )
        self.html.event_manager.post_element_event(node, "onload", None, utilities.ELEMENT_LOADED_EVENT)

    def _on_embedded_mouse_enter(self, event, node_handle):
        self.hovered_embedded_node = node_handle
        self.html._on_mouse_motion(event)
    
    def _on_embedded_mouse_leave(self, event, node_handle):
        self.hovered_embedded_node = node_handle
        # Calling self._on_mouse_motion here seems so cause some flickering
        # event.x and event.y are relative to this node and not self
        # We could fix this but I can't find any noticeable side effects of not including it
        # Not too sure why it was originally here?

class SearchManager(utilities.BaseManager):
    """An extension to manage search the document. Largely internal. 
    
    Only interact with this object if the convenience methods provided elsewhere are insufficient.

    This object can be accessed through the :attr:`~tkinterweb.TkinterWeb.search_manager` property of the :class:`~tkinterweb.TkinterWeb` widget.

    :ivar html: The associated :class:`~tkinterweb.TkinterWeb` instance.

    New in version 4.11."""
    
    def __init__(self, html):
        super().__init__(html)

    def __repr__(self):
        return f"{self.html._w}::{self.__class__.__name__.lower()}"
    
    def find_text(self, searchtext, select, ignore_case, highlight_all):
        "Search for and highlight specific text in the document."
        self.html.selection_manager.clear_selection()

        nmatches = 0
        matches = []
        selected = []
        match_indexes = []

        self.html.tag("delete", "findtext")
        self.html.tag("delete", "findtextselected")

        if len(searchtext) == 0 or select <= 0:
            return nmatches, selected, matches

        doctext = self.html.text("text")

        try:
            # Find matches
            if ignore_case:
                rmatches = finditer(
                    searchtext, doctext, flags=IGNORECASE | MULTILINE
                )
            else:
                rmatches = finditer(searchtext, doctext, flags=MULTILINE)

            for match in rmatches:
                match_indexes.append(
                    (
                        match.start(0),
                        match.end(0),
                    )
                )
                nmatches += 1

            if len(match_indexes) > 0:
                # Highlight matches
                self.html.post_message(f"{nmatches} results for the search key '{searchtext}' have been found")
                if highlight_all:
                    for num, match in enumerate(match_indexes):
                        match = self.html.text("index", match_indexes[num][0])
                        match += self.html.text("index", match_indexes[num][1])
                        matches.append(match)

                selected = self.html.text("index", match_indexes[select - 1][0])
                selected += self.html.text("index", match_indexes[select - 1][1])

                for match in matches:
                    node1, index1, node2, index2 = match
                    self.html.tag("add", "findtext", node1, index1, node2, index2)
                    self.html.tag(
                        "configure",
                        "findtext",
                        "-bg",
                        self.html.find_match_highlight_color,
                        "-fg",
                        self.html.find_match_text_color,
                    )

                node1, index1, node2, index2 = selected
                self.html.tag("add", "findtextselected", node1, index1, node2, index2)
                self.html.tag(
                    "configure",
                    "findtextselected",
                    "-bg",
                    self.html.find_current_highlight_color,
                    "-fg",
                    self.html.find_current_text_color,
                )

                # Scroll to node if selected match is not visible
                nodebox = self.html.text("bbox", node1, index1, node2, index2)
                docheight = float(self.html.bbox()[3])

                view_top = docheight * self.html.yview()[0]
                view_bottom = view_top + self.html.winfo_height()
                node_top = float(nodebox[1])
                node_bottom = float(nodebox[3])

                if (node_top < view_top) or (node_bottom > view_bottom):
                    self.html.yview("moveto", node_top / docheight)
            else:
                self.html.post_message(f"No results for the search key '{searchtext}' could be found")
            return nmatches, selected, matches
        except Exception as error:
            self.html.post_message(f"ERROR: an error was encountered while searching for {searchtext}: {error}")
            return nmatches, selected, matches