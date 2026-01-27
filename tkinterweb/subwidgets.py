"""
Various constants and utilities used by TkinterWeb

Copyright (c) 2021-2025 Andrew Clarke

Some of the CSS code in this file is modified from the Tkhtml/Hv3 project. Tkhtml is copyright (c) 2005 Dan Kennedy.
"""

import mimetypes
import os

from decimal import Decimal, InvalidOperation

import tkinter as tk
from tkinter import colorchooser, filedialog, ttk

from .utilities import ROOT_DIR, rgb_to_hex

combobox_loaded = False

def load_combobox(master, force=False):
    "Load combobox.tcl"
    global combobox_loaded
    if not (combobox_loaded) or force:
        master.tk.call("lappend", "auto_path", ROOT_DIR)
        master.tk.call("package", "require", "combobox")
        combobox_loaded = True

class Combobox(tk.Widget):
    "Bindings for Bryan Oakley's combobox widget."

    def __init__(self, master):
        try:
            load_combobox(master)
            tk.Widget.__init__(self, master, "::combobox::combobox")
        except tk.TclError:
            load_combobox(master, force=True)
            tk.Widget.__init__(self, master, "::combobox::combobox")
        self.configure(
            highlightthickness=0,
            borderwidth=0,
            editable=False,
            takefocus=0,
            selectbackground="#6eb9ff",
            relief="flat",
            elementborderwidth=0,
            buttonbackground="white",
        )
        self.data = [""]
        self.values = [""]
        self.default = 0

    def insert(self, data, values, selected):
        for elem in reversed(data):
            self.tk.call(self._w, "list", "insert", 0, elem)
        self.data = data
        self.values = values
        if selected:
            self.default = self.values.index(selected)
        self.reset()

    def set(self, value):
        if value in self.values:
            self.tk.call(self._w, "select", self.values.index(value))

    def reset(self):
        self.tk.call(self._w, "select", self.default)

    def get(self):
        val = self.tk.call(self._w, "curselection")[0]
        return self.values[val]


class AutoScrollbar(ttk.Scrollbar):
    "Scrollbar that hides itself when not needed"
    def __init__(self, *args, **kwargs):
        ttk.Scrollbar.__init__(self, *args, **kwargs)
        self.scroll = None
        self.visible = True

    def set(self, low, high):
        if self.visible and (self.scroll == 0):
            self.tk.call("grid", "remove", self)
            self.visible = False
        elif not self.visible and (self.scroll == 1):
            self.grid()
            self.visible = True
        elif self.scroll == 2:
            if float(low) <= 0.0 and float(high) >= 1.0:
                self.tk.call("grid", "remove", self)
                self.visible = False
            else:
                self.grid()
                self.visible = True
        ttk.Scrollbar.set(self, low, high)
    
    def set_type(self, scroll, low, high):
        if self.scroll != scroll:
            self.scroll = scroll
            self.set(low, high)

    def pack(self, **kwargs):
        raise tk.TclError("cannot use pack with this widget")

    def place(self, **kwargs):
        raise tk.TclError("cannot use place with this widget")


class ScrolledTextBox(tk.Frame):
    "Text widget with a scrollbar"

    def __init__(self, parent, content="", onchangecommand=None, **kwargs):
        self.parent = parent
        self.onchangecommand = onchangecommand

        tk.Frame.__init__(self, parent)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.tbox = tbox = tk.Text(self, 
                                    borderwidth=0,
                                    selectborderwidth=0,
                                    highlightthickness=0,
                                    undo=True, 
                                    maxundo=-1, 
                                    autoseparators=True,
                                    **kwargs)
        tbox.grid(row=0, column=0, sticky="nsew")

        tbox.insert("1.0", content)
    
        self.vsb = vsb = AutoScrollbar(self, command=tbox.yview)
        vsb.grid(row=0, column=1, sticky="nsew")
        tbox.configure(yscrollcommand=vsb.set)
        vsb.set_type(2, *tbox.yview())

        tbox.bind("<MouseWheel>", self.scroll)
        tbox.bind("<Button-4>", self.scroll_x11)
        tbox.bind("<Button-5>", self.scroll_x11)
        tbox.bind("<Control-Key-a>", self.select_all)
        tbox.bind('<KeyRelease>', lambda event: onchangecommand(self) if onchangecommand else None)
        tbox.bind("<<Paste>>", self._on_paste)

    def _on_paste(self, event):
        try:
            self.tbox.delete("sel.first", "sel.last")
        except tk.TclError:
            pass
        self.tbox.insert("insert", self.tbox.clipboard_get())
        return "break"

    def select_all(self, event):
        self.tbox.tag_add("sel", "1.0", "end")
        self.tbox.mark_set("insert", "1.0")
        self.tbox.see("insert")
        return "break"

    def scroll(self, event):
        yview = self.tbox.yview()
        if yview[0] == 0 and event.delta > 0:
            self.parent._scroll(event)
        elif yview[1] == 1 and event.delta < 0:
            self.parent._scroll(event)

    def scroll_x11(self, event):
        yview = self.tbox.yview()
        if event.num == 4 and yview[0] == 0:
            self.parent._scroll_x11(event, self.parent)
        elif event.num == 5 and yview[1] == 1:
            self.parent._scroll_x11(event, self.parent)

    def configure(self, *args, **kwargs):
        self.tbox.configure(*args, **kwargs)

    def insert(self, *args, **kwargs):
        return self.tbox.insert(*args, **kwargs)

    def get(self, *args, **kwargs):
        if not args and not kwargs:
            args = ("1.0", "end-1c")
        return self.tbox.get(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.tbox.delete(*args, **kwargs)

    def set(self, value):
        self.tbox.delete("0.0", "end")
        self.tbox.insert("1.0", value)
        if self.onchangecommand:
            self.onchangecommand(self)

class FormEntry(tk.Entry):
    def __init__(self, parent, value="", placeholder="", entry_type="", onchangecommand=None, insertwidth=1, **kwargs):
        if entry_type == "password":
            kwargs["show"] = "*"
        tk.Entry.__init__(self, parent, borderwidth=0, highlightthickness=0, insertwidth=insertwidth, **kwargs)

        self._placeholder = placeholder
        self.colour = self.cget("fg")

        if value:
            self.placeholder_shown = False
            self.insert(0, value)
        else:
            self.placeholder_shown = True
            self._halfway()
            self.insert(0, placeholder)

        self.bind("<KeyRelease>", lambda e: onchangecommand(self) if onchangecommand else None)
        self.bind("<KeyPress>", self._on_key_press)
        self.bind("<Control-a>", self._select_all)
        self.bind("<<Paste>>", self._on_paste)
        self.bind("<Button-1>", self._on_click)
        self.bind("<Motion>", self._on_motion)

    @property
    def placeholder(self):
        return self._placeholder
    
    @placeholder.setter
    def placeholder(self, value):
        self._placeholder = value
        if self.placeholder_shown:
            self.delete(0, "end")
            self.insert(0, self._placeholder)

    def _halfway(self, bg=None):
        fg = list(self.winfo_rgb(self.colour))
        bg = list(self.winfo_rgb(bg if bg else self.cget("bg")))
        new = [int((fg[0] + bg[0]) / 2),
               int((fg[1] + bg[1]) / 2),
               int((fg[2] + bg[2]) / 2)]
        super().config(fg=rgb_to_hex(*new))

    def _on_key_press(self, event):
        if self.placeholder_shown:
            if event.keysym in {"BackSpace", "Delete"}:
                return "break"
            elif event.char:
                self._hide_placeholder()

        if self._placeholder and (event.keysym == "BackSpace" and len(super().get()) == 1) or \
            (event.keysym == "Delete" and len(super().get()) == 1 and self.index("insert") == 0) or \
            (event.keysym in {"BackSpace", "Delete"} and self.select_present() and self.selection_get() == super().get()):
            self.delete(0, "end")
            self._show_placeholder()
            return "break"

    def _on_click(self, event):
        if self.placeholder_shown:
            self.focus_set()
            self.icursor(0)
            return "break"
    
    def _on_motion(self, event):
        if self.placeholder_shown:
            return "break"

    def _on_paste(self, event):
        try:
            self.delete("sel.first", "sel.last")
        except tk.TclError:
            pass
        self.insert("insert", self.clipboard_get())
        return "break"

    def _select_all(self, event):
        if self.placeholder_shown:
            return "break"
        else:
            self.selection_range(0, "end")
            self.icursor("end")
            return "break"

    def set(self, value):
        self.delete(0, "end")

        if value:
            if self.placeholder_shown:
                self._hide_placeholder()
            self.insert(0, value)
        elif self._placeholder:
            self._show_placeholder()

    def _show_placeholder(self):
        self._halfway()
        self.insert(0, self._placeholder)
        self.icursor(0)
        self.placeholder_shown = True

    def _hide_placeholder(self):
        self.delete(0, "end")
        super().config(fg=self.colour)
        self.placeholder_shown = False

    def get(self):
        if self.placeholder_shown:
            return ""
        else:
            return super().get()

    def configure(self, **kwargs):
        kwargs.pop("borderwidth", None)
        kwargs.pop("highlightthickness", None)

        if "bg" in kwargs: bg = kwargs["bg"]
        elif "background" in kwargs: bg = kwargs["background"]
        else: bg = None

        if "fg" in kwargs:
            kwargs["insertbackground"] = kwargs["fg"]
            if self.placeholder_shown:
                self.colour = kwargs.pop("fg")
                self._halfway(bg)
        elif "foreground" in kwargs:
            kwargs["insertbackground"] = kwargs["foreground"]
            if self.placeholder_shown:
                self.colour = kwargs.pop("foreground")
                self._halfway(bg)
        elif bg: self._halfway(bg)

        super().configure(**kwargs)
    
    def config(self, **kwargs):
        self.configure(**kwargs)

class FormCheckbox(ttk.Checkbutton):
    def __init__(self, parent, value=0, onchangecommand=None, **kwargs):
        self.variable = variable = tk.IntVar(parent, value=value)

        tk.Checkbutton.__init__(
            self,
            parent,
            borderwidth=0,
            padx=0,
            pady=0,
            highlightthickness=0,
            variable=variable,
            **kwargs
        )
        variable.trace_add("write", lambda *args: onchangecommand(self) if onchangecommand else None)

class FormRadioButton(ttk.Checkbutton):
    def __init__(self, parent, token, value=0, checked=False, variable=None, onchangecommand=None, **kwargs):
        if not variable: 
            variable = tk.StringVar(parent)
            variable.trace_add("write", lambda *args: onchangecommand(self) if onchangecommand else None)
        self.variable = variable

        tk.Radiobutton.__init__(
            self,
            parent,
            value=value,
            variable=variable,
            tristatevalue=token,
            borderwidth=0,
            padx=0,
            pady=0,
            highlightthickness=0,
            **kwargs
        )
        if checked:
            variable.set(value)

    def set(self, value):
        self.variable.set(value)
        
    def get(self):
        return self.variable.get()

class FormRange(ttk.Scale):
    def __init__(self, parent, value=50, from_=0, to=100, step=1, onchangecommand=None, **kwargs):
        step_str = str(step)
        self.step = self._check_value(step, 1)
        from_ = self._check_value(from_, 0)
        to = self._check_value(to, 100)
        self.onchangecommand = onchangecommand
        self.decimal_places = len(step_str.split('.')[-1]) if '.' in step_str else 0
        value = round(self._check_value(value, (to - from_) / 2) / self.step) * self.step
        self.variable = variable = tk.DoubleVar(parent, value=round(value, self.decimal_places))

        ttk.Scale.__init__(self, parent, variable=variable, from_=from_, to=to, **kwargs)

        variable.trace_add("write", self._update_value)

    def _update_value(self, *args):
        value = round(self.variable.get() / self.step) * self.step
        self.set(round(value, self.decimal_places))
        self.onchangecommand(self)

    def _check_value(self, value, default):
        try: 
            return float(value)
        except ValueError:
            return default
        
    def configure(self, **kwargs):
        if "bg" in kwargs:
            bg = kwargs.pop("bg")
            style = ttk.Style()
            stylename = f"Scale{self}.Horizontal.TScale"
            style.configure(stylename, troughcolor=bg)
            self.configure(style=stylename)

        if "background" in kwargs:
            bg = kwargs.pop("background")
            style = ttk.Style()
            stylename = f"Scale{self}.Horizontal.TScale"
            style.configure(stylename, troughcolor=bg)
            self.configure(style=stylename)

        if "step" in kwargs:
            self.step = step = self._check_value(kwargs.pop("step"), self.step)
            step_str = str(step)
            self.decimal_places = len(step_str.split('.')[-1]) if '.' in step_str else 0

        if "from_" in kwargs:
            kwargs["from_"] = self._check_value(kwargs["from_"], 0)
        
        if "to" in kwargs:
            kwargs["to"] = self._check_value(kwargs["to"], 100)
            
        super().configure(**kwargs)


class Tooltip:
    def __init__(self, widget, text=""):
        self.widget = widget
        self.text = text
        self.tip_window = None

        self.custom_tag = f"tkinterweb.{self}.tooltiptoplevel"
        
    def show(self, text=None):
        if text:
            self.text = text
        
        self.hide()

        x = self.widget.winfo_rootx()
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 2

        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        self.label = label = tk.Label(tw, text=self.text, background="#ffffe0",
                         relief="solid", borderwidth=1, font=("tahoma", 8))
        label.pack(ipadx=4, ipady=2)

        current_tags = self.widget.winfo_toplevel().bindtags()
        self.widget.winfo_toplevel().bindtags((self.custom_tag,) + current_tags)

        self.tip_window.focus_force()

        tw.bind("<FocusOut>", self.hide)
        self.widget.winfo_toplevel().bind_class(self.custom_tag, "<Configure>", self.hide)

    def hide(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None
            self.widget.winfo_toplevel().unbind_class(self.custom_tag, "<Configure>")
            current_tags = list(self.widget.winfo_toplevel().bindtags())
            current_tags.remove(self.custom_tag)
            self.widget.winfo_toplevel().bindtags(tuple(current_tags))
            self.widget.focus_force()


class FormNumber(tk.Spinbox):
    def __init__(self, parent, value=0, from_=0, to=100, step=1, onchangecommand=None, **kwargs):
        self.onchangecommand = onchangecommand
        self.step = self._decimalize_value(step, 1)
        from_ = self._check_value(from_, 0)
        to = self._check_value(to, 100)

        self.variable = tk.DoubleVar(parent, value=value)

        super().__init__(parent, textvariable=self.variable, from_=from_, to=to, **kwargs)

        self.variable.trace_add("write", self._update_value)

        self.tooltip = Tooltip(self)

        self.bind("<Control-a>", self._select_all)
        self.bind("<<Paste>>", self._on_paste)

    def _on_paste(self, event):
        try:
            self.delete("sel.first", "sel.last")
        except tk.TclError:
            pass
        self.insert("insert", self.clipboard_get())
        return "break"

    def _select_all(self, event):
        self.selection_range(0, "end")
        self.icursor("end")
        return "break"

    def _update_value(self, *args):
        self.onchangecommand(self)

    def check(self):
        try:
            current_value = self.variable.get()
            current_value = Decimal(str(current_value))
            from_ = Decimal(str(self.cget("from")))
            to = Decimal(str(self.cget("to")))
            
            if current_value < from_:
                if from_ == from_.to_integral_value():
                    from_ = int(from_)
                self.tooltip.show(f"Please enter a number that is larger than {from_}")
            elif current_value > to:
                if to == to.to_integral_value():
                    to = int(to)
                self.tooltip.show(f"Please enter a number that is smaller than {to}")
            elif ((current_value - from_) % self.step) != 0:
                lower = from_ + ((current_value - from_) // self.step) * self.step
                upper = lower + self.step
                if lower == lower.to_integral_value():
                    lower = int(lower)
                if upper == upper.to_integral_value():
                    upper = int(upper)
                if upper > to and lower > from_:
                    self.tooltip.show(f"Please enter a valid number. The nearest number is {lower}.")
                elif lower < from_ and upper < to:
                    self.tooltip.show(f"Please enter a valid number. The nearest number is {upper}.")
                else:
                    self.tooltip.show(f"Please enter a valid number. The nearest numbers are {lower} and {upper}.")
            else:
                return True                
        except tk.TclError:
            self.tooltip.show("Please enter a number")
        return False

    def _check_value(self, value, default):
        try:
            return float(value)
        except ValueError:
            return default
    
    def _decimalize_value(self, value, default):
        try:
            return Decimal(str(value))
        except (InvalidOperation):
            return Decimal(str(default))

    def configure(self, **kwargs):
        if "step" in kwargs:
            self.step = self._decimalize_value(kwargs.pop("step"), self.step)

        if "from_" in kwargs:
            kwargs["from_"] = self._check_value(kwargs["from_"], 0)
        
        if "to" in kwargs:
            kwargs["to"] = self._check_value(kwargs["to"], 100)

        super().configure(**kwargs)

    def set(self, value):
        self.variable.set(value)
        
    def get(self):
        try:
            return self.variable.get()
        except tk.TclError:
            return None

class FileSelector(tk.Frame):
    "File selector widget"

    def __init__(self, parent, accept, multiple, onchangecommand=None, **kwargs):
        self.multiple = multiple
        self.onchangecommand = onchangecommand
        self.files = []

        tk.Frame.__init__(self, parent)
        self.selector = selector = tk.Button(
            self, text="Browse", command=self.select_file
        )
        self.label = label = tk.Label(self, bg="red", text="No files selected.")

        selector.grid(row=0, column=1)
        label.grid(row=0, column=2, padx=5)

        self.generate_filetypes(accept)

    def generate_filetypes(self, accept):
        if accept:
            accept_list = [a.strip() for a in accept.split(",")]
            all_extensions = set()
            filetypes = []

            # First find all the MIME types
            for mimetype in [a for a in accept_list if not a.startswith(".")]:
                # The HTML spec specifies these three wildcard cases only:
                if mimetype in ("audio/*", "video/*", "image/*"):
                    extensions = [
                        k
                        for k, v in mimetypes.types_map.items()
                        if v.startswith(mimetype[:-1])
                    ]
                else:
                    extensions = mimetypes.guess_all_extensions(mimetype)
                filetypes.append((mimetype, " ".join(extensions)))
                all_extensions.update(extensions)

            # Now add any non-MIME types not already included as part of a MIME type.
            for suffix in [a for a in accept_list if a.startswith(".")]:
                if suffix not in all_extensions:
                    mimetype = mimetypes.guess_type(f" {suffix}", suffix)[0]
                    if mimetype:
                        extensions = mimetypes.guess_all_extensions(mimetype)
                        filetypes.append((mimetype, " ".join(extensions)))
                        all_extensions.update(extensions)
                    else:
                        filetypes.append((f"{suffix} files", suffix))

            if len(filetypes) > 1:
                filetypes.insert(
                    0, ("All Supported Types", " ".join(sorted(all_extensions)))
                )

            self.filetypes = filetypes
        else:
            self.filetypes = []

    def select_file(self):
        if self.multiple:
            files = filedialog.askopenfilenames(
                title="Select files", filetypes=self.filetypes
            )
            if files:
                self.files = []
                for file in files:
                    self.files.append(os.path.basename(file.replace('\\', '/')))
                files = self.files
        else:
            files = filedialog.askopenfilename(
                title="Select file", filetypes=self.filetypes
            )
            if files:
                self.files = files = (os.path.basename(files.replace('\\', '/')),)
        number = len(files)
        if number == 0:
            self.label.config(text="No files selected.")
        elif number == 1:
            files = files[0].replace("\\", "/").split("/")[-1]
            self.label.config(text=files)
        else:
            self.label.config(text=f"{number} files selected.")
        self.event_generate("<<Modified>>")
        if self.onchangecommand:
            self.onchangecommand(self)

    def set(self, value):
        self.label.config(text="No files selected.")
        self.event_generate("<<Modified>>")
        if self.onchangecommand:
            self.onchangecommand(self)

    def get(self):
        return self.files

    def configure(self, *args, **kwargs):
        self.selector.config(*args, **kwargs)
        if "activebackground" in kwargs:
            del kwargs["activebackground"]
        self.label.config(*args, **kwargs)
        if "state" in kwargs:
            del kwargs["state"]
        self.config(*args, **kwargs)


class ColourSelector(tk.Frame):
    "Colour selector widget"

    def __init__(self, parent, colour="#000000", onchangecommand=None, **kwargs):
        self.onchangecommand = onchangecommand
        colour = colour if colour else "#000000"
        tk.Button.__init__(self, parent,
            bg=colour,
            command=self.select_colour,
            activebackground=colour,
            highlightthickness=0,
            borderwidth=0,
            **kwargs
        )

    def select_colour(self):
        colour = colorchooser.askcolor(title="Choose color", initialcolor=self.cget("bg"))[1]
        if colour:
            self.set(colour)

    def set(self, colour):
        colour = colour if colour else "#000000"
        self.config(bg=colour, activebackground=colour)
        self.event_generate("<<Modified>>")
        if self.onchangecommand:
            self.onchangecommand(self)

    def get(self):
        return self.cget("bg")


class Notebook(ttk.Frame):
    "Drop-in replacement for the :py:class:`ttk.Notebook` widget."

    def __init__(self, master, takefocus=True, **kwargs):
        ttk.Frame.__init__(self, master, **kwargs)
        self.notebook = notebook = ttk.Notebook(self, takefocus=takefocus)
        self.blankframe = lambda: tk.Frame(
            notebook, height=0, bd=0, highlightthickness=0
        )

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        notebook.grid(row=0, column=0, sticky="ew")

        notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

        self.pages = []
        self.previous_page = None

    def on_tab_change(self, event):
        self.event_generate("<<NotebookTabChanged>>")
        try:
            tabId = self.notebook.index(self.notebook.select())
            newpage = self.pages[tabId]
            if self.previous_page:
                self.previous_page.grid_forget()
            newpage.grid(row=1, column=0, sticky="nsew")
            self.previous_page = newpage
        except tk.TclError:
            pass

    def add(self, child, **kwargs):
        "Adds a new tab to the notebook."
        if child in self.pages:
            raise ValueError(f"{child} is already managed by {self}.")
        frame = self.blankframe()
        self.notebook.add(frame, **kwargs)
        self.pages.append(child)

    def insert(self, where, child, **kwargs):
        "Adds a new tab at the specified position."
        if child in self.pages:
            raise ValueError(f"{child} is already managed by {self}.")
        frame = self.blankframe()
        self.notebook.insert(where, frame, **kwargs)
        self.pages.insert(where, child)

    def enable_traversal(self):
        "Enable keyboard traversal for a toplevel window containing this notebook."
        self.notebook.enable_traversal()

    def select(self, tabId=None):
        "Select the given tabId."
        if tabId in self.pages:
            tabId = self.pages.index(tabId)
            return self.notebook.select(tabId)
        else:
            self.notebook.select(tabId)
            return self.transcribe(self.notebook.select())

    def transcribe(self, item, reverse=False):
        return self.pages[self.notebook.index(item)]

    def tab(self, tabId, option=None, **kwargs):
        "Query or modify the options of the given tabId."
        if not isinstance(tabId, int) and tabId in self.pages:
            tabId = self.pages.index(tabId)
        return self.notebook.tab(tabId, option, **kwargs)

    def forget(self, tabId):
        "Removes the tab specified by tabId and unmaps the associated window."
        if isinstance(tabId, int):
            del self.pages[tabId]
            self.notebook.forget(tabId)
        else:
            index = self.pages.index(tabId)
            self.pages.remove(tabId)
            self.notebook.forget(index)

    def index(self, child):
        "Returns the numeric index of the tab specified by child, or the total number of tabs if child is the string “end”."
        try:
            return self.pages.index(child)
        except (IndexError, ValueError):
            return self.transcribe(self.notebook.index(child))

    def tabs(self):
        "Returns a list of widgets managed by the notebook."
        return self.pages
