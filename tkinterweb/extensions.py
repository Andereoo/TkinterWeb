"""
Extensions to Tkhtml3

Copyright (c) 2021-2025 Andrew Clarke
"""

from tkinter import Frame, Event
from .utilities import EVENT_MAP, UNHANDLED_EVENT_WHITELIST

class BlinkyFrame(Frame):
    # A blinking caret-style frame
    def __init__(self, master, *args, blink_delay=600, **kwargs):
        Frame.__init__(self, master, *args, **kwargs)
        self.blink_delay = blink_delay

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
            self.pending = self.after(self.blink_delay, self._blink)

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
        else:
            self.place(self._x, self._y, _internal=True)
        
        self.update()
        self._is_placed = not(self._is_placed)
        self.pending = self.after(self.blink_delay, self._blink)


class CaretManager:
    """An extension to manage the caret's state. Largely internal. 
    
    Only interact with this object if the convenience methods provided elsewhere are insufficient.

    This object can be accessed through the :attr:`~tkinterweb.TkinterWeb.caret_manager` property of the :class:`~tkinterweb.TkinterWeb` widget.

    :ivar html: The associated :class:`~tkinterweb.TkinterWeb` instance.
    :ivar node: The node the caret is in.
    :ivar offset: The caret's offset within the node.
    :ivar index: The document text index of the start of the node; fallback if the node is deleted.
    :ivar caret_frame: The blinky widget.
    :ivar target_offset: The text offset used for traversing up/down.
    :ivar blink_delay: The caret's blink delay, in milliseconds. 
    :ivar caret_colour: The caret's colour. If None, the text colour under it will be matched.
    :ivar scrolling_threshold: If the distance between the visible part of the page and the caret is nonzero but is less than this number, a scrolling animation will play.
    :ivar scrolling_teleport: If the distance between the visible part of the page and the caret is nonzero but is greater than :attr:`scrolling_threshold`, the page is scrolled to this number before the scrolling animation plays.
    
    New in version 4.8."""
    
    def __init__(self, html):
        self.html = html

        self.node = None
        self.offset = None
        self.index = None
        self.caret_frame = None
        #self.target_node = None
        self.target_offset = None

        self.blink_delay = 600
        self.caret_colour = None
        self.scrolling_threshold = 300 
        self.scrolling_teleport = 75

    def __repr__(self):
        return f"{self.html._w}::{self.__class__.__name__.lower()}"

    def set(self, node, offset, recalculate=False):
        "Set the caret's position."
        if not node and not recalculate: return
        if self.html._caret_browsing_enabled:
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
                if not self.html.selection_start_node:
                    self.html.selection_start_node = self.node
                    self.html.selection_start_offset = self.offset
                self.node, self.offset = node, offset
                self.html.selection_end_node = self.node
                self.html.selection_end_offset = self.offset
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

        self.register_nodes_from_index(event, index)
        self.update(event)

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

        self.register_nodes_from_index(event, index)
        self.update(event)

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
        
        self.register_nodes_from_index(event, index, update_caret_start)
        self.update(event)

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

        self.register_nodes_from_index(event, index, update_caret_start)
        self.update(event, fallback=self.shift_right)

    def update(self, event=None, auto_scroll=True, fallback=None):
        "Refresh the caret or update its position."
        if not fallback:
            fallback = self.shift_left

        if self.html._caret_browsing_enabled and self.node:
            self.html.update() # Particularly important when this method runs after the document is scrolled
            if not self.caret_frame:
                self.caret_frame = BlinkyFrame(self.html, blink_delay=self.blink_delay, width=1)
                
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
                self.caret_frame.config(height=d-b, bg=bg)
                self.caret_frame.place(x=a-xoffset, y=b-yoffset)
            
                if self.html.selection_enabled and event:
                    if ((event.state & 0x1) != 0):
                        self.html.update_selection()
                    else:
                        self.html.clear_selection()

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

class EventManager:
    """An extension to manage custom node bindings. Largely internal. 
    
    Only interact with this object if the convenience methods provided elsewhere are insufficient.

    This object can be accessed through the :attr:`~tkinterweb.TkinterWeb.event_manager` property of the :class:`~tkinterweb.TkinterWeb` widget.

    :ivar html: The associated :class:`~tkinterweb.TkinterWeb` instance.
    :ivar bindings: A dictionary of bindings. You shouldn't need to touch this.

    New in version 4.10."""

    ### We use the JavaScript event system to handle some element bindings
    ### If a binding is requested but isn't handled by TkinterWeb by default, we create a new binding to deal with it
    
    def __init__(self, html):
        self.html = html
        
        self.bindings = {}

    def __repr__(self):
        return f"{self.html._w}::{self.__class__.__name__.lower()}"
    
    def reset(self):
        "Reset all bindings."

        for event in self.bindings:
            if event not in EVENT_MAP:
                self.html.unbind_class(self.html.tkinterweb_tag, event)
            
        self.bindings = {}

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
        if event in EVENT_MAP:
            return False
        
        for sequence in UNHANDLED_EVENT_WHITELIST:
            if sequence in event:
                return True
            
        raise KeyError(f"the event {event} is either unsupported or invalid")

    def bind(self, node, event, callback, add=None):
        "Add a binding."        
        if self._check_binding_name(event):
            if event not in self.bindings:
                self.html.bind_class(self.html.tkinterweb_tag, event, lambda event, name=event: self._on_demand_binding_callback(event, name))
        else:
            event = EVENT_MAP[event]

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
            if event not in EVENT_MAP:
                self.html.unbind_class(self.html.tkinterweb_tag, event)
