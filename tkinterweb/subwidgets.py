"""
Various constants and utilities used by TkinterWeb

Some of the CSS code in this file is modified from the Tkhtml/Hv3 project. See tkinterweb-tkhtml/COPYRIGHT.

Copyright (c) 2021-2025 Andereoo
"""

import mimetypes
import os

import tkinter as tk
from tkinter import colorchooser, filedialog, ttk

from .utilities import ROOT_DIR

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
    def __init__(self, *args, scroll=2, **kwargs):
        ttk.Scrollbar.__init__(self, *args, **kwargs)
        self.scroll = scroll
        self.visible = True

    def set(self, lo, hi):
        if self.visible and (self.scroll == 0):
            self.tk.call("grid", "remove", self)
            self.visible = False
        elif (self.visible == False) and (self.scroll == 1):
            self.grid()
            self.visible = True
        elif self.scroll == 2:
            if float(lo) <= 0.0 and float(hi) >= 1.0:
                self.tk.call("grid", "remove", self)
                self.visible = False
            else:
                self.grid()
                self.visible = True
        ttk.Scrollbar.set(self, lo, hi)
    
    def set_type(self, scroll):
        if self.scroll != scroll:
            self.scroll = scroll
            lo, hi = self.get()
            self.set(lo, hi)

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
                                    **kwargs)
        tbox.grid(row=0, column=0, sticky="nsew")

        tbox.insert("1.0", content)
    
        self.vsb = vsb = AutoScrollbar(self, command=tbox.yview)
        vsb.grid(row=0, column=1, sticky="nsew")
        tbox.configure(yscrollcommand=vsb.set)

        tbox.bind("<MouseWheel>", self.scroll)
        tbox.bind("<Button-4>", self.scroll_x11)
        tbox.bind("<Button-5>", self.scroll_x11)
        tbox.bind("<Control-Key-a>", self.select_all)
        tbox.bind('<KeyRelease>', lambda event: onchangecommand(self) if onchangecommand else None)

    def select_all(self, event):
        self.tbox.tag_add("sel", "1.0", "end")
        self.tbox.mark_set("insert", "1.0")
        self.tbox.see("insert")
        return "break"

    def scroll(self, event):
        yview = self.tbox.yview()
        if yview[0] == 0 and event.delta > 0:
            self.parent.scroll(event)
        elif yview[1] == 1 and event.delta < 0:
            self.parent.scroll(event)

    def scroll_x11(self, event):
        yview = self.tbox.yview()
        if event.num == 4 and yview[0] == 0:
            self.parent.scroll_x11(event, self.parent)
        elif event.num == 5 and yview[1] == 1:
            self.parent.scroll_x11(event, self.parent)

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
    def __init__(self, parent, value="", entry_type="", onchangecommand=None, **kwargs):
        tk.Entry.__init__(self, parent, borderwidth=0, highlightthickness=0, **kwargs)
        self.insert(0, value)

        self.bind("<KeyRelease>", lambda event: onchangecommand(self) if onchangecommand else None)
        if entry_type == "password":
            self.configure(show="*")
            
    def set(self, value):
        self.delete(0, "end")
        self.insert(0, value)

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
        self.from_ = from_ = self._check_value(from_, 0)
        self.to = to = self._check_value(to, 100)
        self.onchangecommand = onchangecommand
        self.decimal_places = len(step_str.split('.')[-1]) if '.' in step_str else 0
        self.variable = variable = tk.DoubleVar(parent, value=self._check_value(value, (to - from_) / 2))

        ttk.Scale.__init__(self, parent, variable=variable, from_=from_, to=to)

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
            
        super().configure(**kwargs)
        
    def set(self, value):
        super().set(self._check_value(value, (self.to - self.from_) / 2))

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
                # the HTML spec specifies these three wildcard cases only:
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

class TkHtmlParseURL:
    def __init__(self, uri, html=None):
        if html is None:
            master = tk.Tk()
            master.withdraw()
            self._html = TkinterWeb(master)
        self.parsed = self.uri("::tkhtml::uri", uri)

    def resolve(self, uri):
        return self._html.uri_resolve(self.parsed, uri)

    def load(self, uri):
        return self._html.uri_load(self.parsed, uri)

    @property
    def defrag(self):
        return self._html.uri_defrag(self.parsed)

    @property
    def scheme(self):
        return self._html.uri_scheme(self.parsed)

    @property
    def authority(self):
        return self._html.uri_authority(self.parsed)

    @property
    def path(self):
        return self._html.uri_path(self.parsed)

    @property
    def query(self):
        return self._html.uri_query(self.parsed)

    @property
    def fragment(self):
        return self._html.uri_fragment(self.parsed)

    @property
    def splitfrag(self):
        return SplitFrag(self.defrag, self.fragment)

    def __str__(self):
        return self._html.uri_get(self.parsed)

    def __del__(self):
        self._html.uri_destroy(self.parsed)
