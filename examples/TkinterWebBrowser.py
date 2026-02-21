"""
A proof-of-concept web browser using TkinterWeb

Note that TkinterWeb is not necessarily intended to be a full-blown modern web browser
These already exist and are generally resource-hungry and not highly integratable with Tkinter
Being based on Tkhtml, TkinterWeb is intended to be fast, lightweight, and highly integrated with Tkinter while providing far more control over layouts and styling than is feasible than Tkinter
TkinterWeb displays older or simpler websites well but may be found lacking on more modern websites

This code was created for testing TkinterWeb and is a bit of a mess, but nonetheless is a great example of some of the things that can be done with the software, including:
 - loading pages
 - searching pages
 - embedding Tkinter widgets
 - managing input elements
 - embedding Python code
 - manipulating the DOM
 - making round buttons
 - and more
 
Copyright (c) 2026 Andrew Clarke
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))


import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

from tkinterweb import HtmlFrame, Notebook, __version__
from tkinterweb.utilities import BUILTIN_PAGES, DONE_LOADING_EVENT, URL_CHANGED_EVENT, TITLE_CHANGED_EVENT, DOWNLOADING_RESOURCE_EVENT, download
from tkinterweb.subwidgets import ScrolledTextBox, FormEntry

import os


if os.name == "nt":
	from ctypes import windll
	windll.shcore.SetProcessDpiAwareness(1)

version = []
for letter in __version__.split("."):
    version.append(int(letter))
if tuple(version) < (4, 19, 0):
    raise RuntimeError("This demo needs TkinterWeb version 4.19.0 or higher.")

if len(sys.argv) > 1:
    NEW_TAB = sys.argv[1]
else:
    NEW_TAB = "about:tkinterweb"


def check_url(entry):
    url = entry.get()
    if not any((url.startswith("file:"), url.startswith("http:"), url.startswith("about:"), url.startswith("view-source:"), url.startswith("https:"), url.startswith("data:"))):
        if os.path.exists(url):
            url = f"file://{url}"
        else:
            url = "http://{}".format(url)
            entry.delete(0, "end")
            entry.insert(0, url)
    return url


class HTMLPlayground(ttk.PanedWindow):
    def __init__(self, master):
        ttk.PanedWindow.__init__(self, master, orient=tk.HORIZONTAL)

        self.master = master

        text_frame = ttk.Frame(self)
        html_frame = ttk.Frame(self)
        text_frame._scroll = lambda *a: None
        text_frame._xscroll = lambda *a: None
        text_frame._scroll_x11 = lambda *a: None
        text_frame._xscroll_x11 = lambda *a: None
        self.textarea = textarea = ScrolledTextBox(text_frame, content="Type HTML code here", padx=8, pady=8, wrap=tk.NONE)
        self.iframe = iframe = HtmlFrame(html_frame,
            messages_enabled=False,
            message_func = master.html.message_func,
            images_enabled = master.html.images_enabled,
            forms_enabled = master.html.forms_enabled,
            objects_enabled = master.html.objects_enabled,
            ignore_invalid_images = master.html.ignore_invalid_images,
            crash_prevention_enabled = master.html.crash_prevention_enabled,
            dark_theme_enabled = master.html.dark_theme_enabled,
            image_inversion_enabled = master.html.image_inversion_enabled,
            caches_enabled = master.html.caches_enabled,
            threading_enabled = master.html.threading_enabled,
            image_alternate_text_enabled = master.html.image_alternate_text_enabled,
            selection_enabled = master.html.selection_enabled,
            find_match_highlight_color = master.html.find_match_highlight_color,
            find_match_text_color = master.html.find_match_text_color,
            find_current_highlight_color = master.html.find_current_highlight_color,
            find_current_text_color = master.html.find_current_text_color,
            selected_text_highlight_color = master.html.selected_text_highlight_color,
            selected_text_color = master.html.selected_text_color,
            caret_browsing_enabled = master.html.caret_browsing_enabled)
        iframe.html.text_mode = False
        iframe.load_html("HTML output shows here")
        iframe.config(messages_enabled=True)

        self.urlbar = urlbar = FormEntry(text_frame, placeholder="https://")
        urlbar.bind("<Return>", self._load_url)
        go_button = ttk.Button(text_frame, text="Go", cursor="hand2", command=self._load_url)

        self.base_title = "HTML Playground"
        master.add_html(f"<title>{self.base_title}</title>")

        # Make a round button
        # Quite unnecessary, but very fun
        s = ttk.Style()
        run_button = HtmlFrame(textarea.tbox, messages_enabled=False, shrink=True, javascript_enabled=True, javascript_backend="python", selection_enabled=False)
        run_button.load_html(f"""<body>
                                <style>
                                    body{{margin:0;background-color:white}}
                                    button{{color:{s.lookup("TButton", "foreground")};background-color:{s.lookup("TButton", "background")};border-radius:5px;padding:6px 11px;border-width:0}}
                                    button:hover{{background-color:{s.lookup("TButton", "background", state=("active",))}}}
                                    button:active{{background-color:{s.lookup("TButton", "background")}}}
                                </style>
                                <button onclick='update_iframe()'>&gt;</button>
                                </body>""")
        run_button.javascript.register("update_iframe", self._update_iframe)
        run_button.place(relx=1.0, rely=1.0, anchor="se")

        self.iframe.bind("<<DOMContentLoaded>>", self._on_page_loaded)
        self.iframe.bind("<<TitleChanged>>", self._on_title_change)

        text_frame.grid_rowconfigure(1, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)
        urlbar.grid(row=0, column=0, sticky="nsew", padx=(5,0))
        go_button.grid(row=0, column=1, padx=(5,0))
        textarea.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(5,0), padx=(5,0))
        iframe.pack(expand=True, fill="both", padx=(0,5))

        self.add(text_frame)
        self.add(html_frame)

    def _load_url(self, event=None):
        url = check_url(self.urlbar)
        self.iframe.load_url(url)

    def _on_title_change(self, event, addendum=None):
        if addendum is None:
            addendum = f" - {self.iframe.title}"
        self.master.add_html(f"<title>{self.base_title}{addendum}</title>")

    def _on_page_loaded(self, event):
        html = self.iframe.save_page()
        self.textarea.delete("0.0", "end")
        self.textarea.insert("1.0", html)

    def _update_iframe(self, event=None):
        self.iframe.unbind("<<DOMContentLoaded>>")
        self.master.add_html(f"<title>{self.base_title}</title>")
        self.iframe.load_html(self.textarea.get(), self.iframe.base_url)
        self.iframe.bind("<<DOMContentLoaded>>", self._on_page_loaded)


HTML_TEST_PAGE = """
<head>
    <style>
        html, body {{margin:0;overflow: hidden}}
        object {{width:100%}}
    </style>
</head>
<body><object tkinterweb-full-page data={}></object></body>
</html>"""


class Page(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        ttk.Frame.__init__(self, master, *args, **kwargs)

        self.master = master
        self.back_history = []
        self.forward_history = []

        self.style = ttk.Style(self)
        self.style.theme_use("default")

        topbar = ttk.Frame(self)
        self.bottombar = bottombar = ttk.Frame(self)
        self.findbar = findbar = ttk.Frame(self)

        self.html_playground = None
        
        self.linklabel = linklabel = ttk.Label(bottombar, text="Welcome to TkinterWeb!", cursor="hand2")

        self.backbutton = backbutton = ttk.Button(topbar, text="Back", command=self.back, state="disabled")
        self.forwardbutton = forwardbutton = ttk.Button(topbar, text="Forward", command=self.forward, state="disabled")
        self.reloadbutton = reloadbutton = ttk.Button(topbar, text="Reload", command=self.reload, cursor="hand2")
        self.urlbar = urlbar = ttk.Entry(topbar, width=100)
        newbutton = ttk.Button(topbar, text="New tab", command=self.open_new_tab, cursor="hand2")
        closebutton = ttk.Button(topbar, text="Close", command=self.close_current_tab, cursor="hand2")
        self.findbutton = findbutton = ttk.Button(topbar, text="Find",  command=self.open_findbar, cursor="hand2")
        self.settingsbutton = settingsbutton = ttk.Button(topbar, text="Settings", command=self.open_sidebar, cursor="hand2")

        self.message_box = tk.Text(self, height=8)

        self.find_select_num = 1
        self.find_match_num = 0
        
        self.findbox_var = findbox_var = tk.StringVar()
        self.find_box = find_box = ttk.Entry(findbar, textvariable=findbox_var)
        self.find_previous = find_previous = ttk.Button(findbar, text="Prevous", command=self.previous_and_find, state="disabled")
        self.find_next = find_next = ttk.Button(findbar, text="Next", command=self.next_and_find, state="disabled")
        self.ignore_case_var = ignore_case_var = tk.IntVar(value=1)
        ignore_case = ttk.Checkbutton(findbar, text="Ignore Cases", variable=ignore_case_var, command=self.search_in_page, cursor="hand2")
        self.highlight_all_var = highlight_all_var = tk.IntVar(value=1)
        highlight_all = ttk.Checkbutton(findbar, text="Highlight All", variable=highlight_all_var, command=lambda change=False: self.search_in_page(change=change), cursor="hand2")
        self.find_bar_caption = find_bar_caption = ttk.Label(findbar, text="")
        find_close = ttk.Button(findbar, text="Close", command=self.open_findbar, cursor="hand2")

        self.frame = frame = HtmlFrame(self, message_func=self.add_message, on_link_click=self.link_click, on_form_submit=self.form_submit)
        
        self.sidebar = sidebar = HtmlFrame(frame, width=250, fontscale=0.8, selection_enabled=False, messages_enabled=False, javascript_enabled=True, javascript_backend="python")

        self.images_var = images_var = tk.IntVar(value=self.frame["images_enabled"])
        images_enabled = ttk.Checkbutton(sidebar, text="Enable images", variable=images_var, command=self.toggle_images)
        self.styles_var = styles_var = tk.IntVar(value=self.frame["stylesheets_enabled"])
        styles_enabled = ttk.Checkbutton(sidebar, text="Enable stylesheets", variable=styles_var, command=self.toggle_styles)
        self.forms_var = forms_var = tk.IntVar(value=self.frame["forms_enabled"])
        forms_enabled = ttk.Checkbutton(sidebar, text="Enable forms", variable=forms_var, command=self.toggle_forms)
        self.objects_var = objects_var = tk.IntVar(value=self.frame["objects_enabled"])
        objects_enabled = ttk.Checkbutton(sidebar, text="Enable objects", variable=objects_var, command=self.toggle_objects)
        self.caches_var = caches_var = tk.IntVar(value=self.frame["caches_enabled"])
        caches_enabled = ttk.Checkbutton(sidebar, text="Enable caches", variable=caches_var, command=self.toggle_caches)
        self.crashes_var = crashes_var = tk.IntVar(value=self.frame["crash_prevention_enabled"])
        emojis_enabled = ttk.Checkbutton(sidebar, text="Enable crash prevention", variable=crashes_var, command=self.toggle_emojis)
        self.threads_var = threads_var = tk.IntVar(value=self.frame["threading_enabled"])
        threads_enabled = ttk.Checkbutton(sidebar, text="Enable threading", variable=threads_var, command=self.toggle_threads)
        self.invert_page_var = invert_page_var = tk.IntVar(value=self.frame["dark_theme_enabled"])
        self.js_var = js_var = tk.IntVar(value=self.frame["javascript_enabled"])
        js_enabled = ttk.Checkbutton(sidebar, text="Enable javascript", variable=js_var, command=self.toggle_js)
        invert_page_enabled = ttk.Checkbutton(sidebar, text="Dark theme", variable=invert_page_var, command=self.toggle_theme)
        self.invert_images_var = invert_images_var = tk.IntVar(value=self.frame["image_inversion_enabled"])
        invert_images_enabled = ttk.Checkbutton(sidebar, text="Image inverter", variable=invert_images_var, command=self.toggle_inverter)
        self.selection_var = selection_var = tk.IntVar(value=self.frame["selection_enabled"])
        selection_enabled = ttk.Checkbutton(sidebar, text="Text selection enabled", variable=selection_var, command=self.toggle_selection)
        self.caret_browsing_var = caret_browsing_var = tk.IntVar(value=self.frame["caret_browsing_enabled"])
        caret_browsing_enabled = ttk.Checkbutton(sidebar, text="Caret browsing enabled", variable=caret_browsing_var, command=self.toggle_caret_browsing)
        
        self.view_source_button = view_source_button = ttk.Button(sidebar, text="View page source", command=self.view_source)
        about_button = ttk.Button(sidebar, text="About TkinterWeb", command=lambda: self.open_new_tab("about:tkinterweb"))
        html_button = ttk.Button(sidebar, text="HTML playground", command=lambda: self.open_new_tab("about:html"))
        style_button = ttk.Button(sidebar, text="Style report", command=self.style_report)
        
        frame.bind(TITLE_CHANGED_EVENT, self.change_title)
        frame.bind(URL_CHANGED_EVENT, self.url_change)
        frame.bind(DONE_LOADING_EVENT, self.done_loading)
        frame.bind(DOWNLOADING_RESOURCE_EVENT, self.on_downloading)

        for i in {"<Up>", "<Down>", "<Left>", "<Right>", "<Prior>", "<Next>", "<Home>", "<End>"}:
            frame.unbind(i)

        linklabel.bind("<Button-1>", self.hide_messsage_box)
        urlbar.bind("<Return>", self.load_site)
        #frame.bind("<Motion>", self.on_motion)
        frame.bind("<Leave>", lambda event: linklabel.config(text="Done"))

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        topbar.grid(column=0, row=0, sticky="ew")
        frame.grid(column=0, row=1, sticky="nsew")
        bottombar.grid(column=0, row=4, sticky="ew")

        self.sidebar.javascript.register("frame", frame)

        self.sidebar.load_html(f"""<html>
  <body>
    <style>
      body p, span {{ margin-top: 5px; margin-bottom: 5px; cursor: default; }}
      object {{ width: 100%; cursor: pointer; }}
      input[type="color"] {{ height: 15px; width: 30px; border: 1px solid black; padding: 0; margin: 5px; background-color: transparent; }}
      label {{ margin-left: 5px; }}
    </style>

    <object allowscrolling data={images_enabled}></object><br>
    <object allowscrolling data={styles_enabled}></object><br>
    <object allowscrolling data={forms_enabled}></object><br>
    <object allowscrolling data={objects_enabled}></object><br>
    <object allowscrolling data={caches_enabled}></object><br>
    <object allowscrolling data={emojis_enabled}></object><br>
    <object allowscrolling data={threads_enabled}></object><br>
    <object allowscrolling data={js_enabled}></object><hr>
    <object allowscrolling data={selection_enabled}></object>
    <object allowscrolling data={caret_browsing_enabled}></object><hr>
    
    <object allowscrolling data={invert_page_enabled}></object><br>
    <object allowscrolling data={invert_images_enabled}></object><hr>

    <div>
      <p style="float:left">Zoom:</p>
      <span style="float:right" id="zoom">{frame['zoom']}</span>
      <input onchange="document.getElementById('zoom').textContent = this.value; frame.config(zoom=this.value)" style="width: 100%" type="range" min="0.1" max="10" step="0.1" value="{self.frame['zoom']}">
    </div>
    
    <div>
      <p style="float:left">Font scale:</p>
      <span style="float:right" id="fontscale">{frame['fontscale']}</span>
      <input onchange="document.getElementById('fontscale').textContent = this.value; frame.config(fontscale=this.value)" style="width: 100%" type="range" min="0.1" max="10" step="0.1" value="{self.frame['fontscale']}">
    </div>
    
    <hr style="margin-bottom:10px;margin-top:10px">
    
    <p>User agent:</p>
    <input onchange="frame['headers']['User-Agent'] = this.value" style="padding: 5px 0px 3px 0px; width: 100%; color:black" type="text" value="{frame['headers']['User-Agent']}">
    <hr style="margin-bottom:10px;margin-top:0">
    
    <p>Parse mode:</p>
    <select onchange="frame.config(parsemode=this.value)" style="padding: 3px 0px 1px 0px; width:100%; color:black">
      <option value="xml">xml</option>
      <option value="xhtml">xhtml</option>
      <option value="html">html</option>
    </select>
    <hr style="margin-bottom:10px;margin-top:0">

    <input type="color" onchange="frame.config(find_match_highlight_color=this.value)" value="{frame['find_match_highlight_color']}">
    <input type="color" onchange="frame.config(find_match_text_color=this.value)" value="{frame['find_match_text_color']}"><label>Find matches</label><br>
    <input type="color" onchange="frame.config(find_current_highlight_color=this.value)" value="{frame['find_current_highlight_color']}">
    <input type="color" onchange="frame.config(find_current_text_color=this.value)" value="{frame['find_current_text_color']}"><label>Current match</label><br>
    <input type="color" onchange="frame.config(selected_text_highlight_color=this.value)" value="{frame['selected_text_highlight_color']}">
    <input type="color" onchange="frame.config(selected_text_color=this.value)" value="{frame['selected_text_color']}"><label>Selected text</label><br>

    <hr>
    
    <div style="margin-top: 20px">
      <object allowscrolling data={view_source_button}></object>
      <object allowscrolling data={style_button}></object>
      <object allowscrolling data={html_button}></object>
      <object allowscrolling data={about_button}></object>
    </div>
  </body>
</html>""")
        
        frame.config = self.html_config

        linklabel.pack(expand=True, fill="both")
        topbar.columnconfigure(4, weight=1)
        backbutton.grid(row=0, column=1, pady=5, padx=5)
        forwardbutton.grid(row=0, column=2, pady=5)
        reloadbutton.grid(row=0, column=3, pady=5, padx=5)
        urlbar.grid(row=0, column=4, pady=5, padx=20, sticky="NS")
        newbutton.grid(row=0, column=5, pady=5, padx=(5,0))
        closebutton.grid(row=0, column=6, pady=5, padx=5)
        findbutton.grid(row=0, column=7, pady=5)
        settingsbutton.grid(row=0, column=8, pady=5, padx=5)

        findbar.columnconfigure(6, weight=1)
        find_box.grid(row=0, column=0, padx=5)
        find_previous.grid(row=0, column=1)
        find_next.grid(row=0, column=2)
        ttk.Separator(findbar, orient="vertical").grid(row=0, column=3, sticky="ns", pady=4, padx=8)
        ignore_case.grid(row=0, column=4, sticky="ns")
        highlight_all.grid(row=0, column=5, sticky="ns", padx=5)
        find_bar_caption.grid(row=0, column=7)
        find_close.grid(row=0, column=8, sticky="ns", padx=5)
        ttk.Separator(findbar).grid(row=1, column=0, columnspan=9, sticky="ew", pady=4, padx=8)

        findbox_var.trace("w", self.search_in_page)

        frame.bind("<Button-3>", self.on_right_click)
        for widget in [urlbar, find_box]:
            widget.bind("<Control-a>", lambda e: self.after(50, self.select_all_in_entry, e.widget))

        for child in findbar.winfo_children():
            child.bind("<Escape>", lambda x: self.open_findbar())
        for child in sidebar.winfo_children():
            child.bind("<Escape>", lambda x: self.close_sidebar())
        settingsbutton.bind("<Escape>", lambda x: self.close_sidebar())

        self.toggle_theme(False)

    def html_config(self, **kwargs):
        self.frame.configure(**kwargs)
        if self.html_playground is not None: 
            self.html_playground.iframe.configure(**kwargs)

    def style_report(self):
        if self.frame.base_url == "about:html":
            self.html_playground.iframe.generate_style_report().grab_set()
        else:
            self.frame.generate_style_report().grab_set()

    def apply_dark_theme(self):
        self.style.configure(".", background="#2b2b2b", foreground="#FFFFFF")
        self.style.configure("TButton",
            background="#444444",
            foreground="#FFFFFF")
        self.style.map("TButton",
            background=[("active", "#666666"),
                ("!active", "#444444")])
        self.style.configure("TLabel",
            background="#2b2b2b",
            foreground="#FFFFFF")
        self.style.configure("TEntry",
            fieldbackground="#555555",
            foreground="#FFFFFF")    
        self.style.map('TScale',
          background=[('active', '#2b2b2b'),
                      ('!active', '#2b2b2b')])  
        self.style.configure("TFrame",
            background="#2b2b2b")
        self.style.configure("TScrollbar",
            background="#444444",
            troughcolor="#2b2b2b",
            arrowcolor="#FFFFFF")
        self.style.map("TScrollbar",
            background=[("active", "#666666"),
                ("!active", "#444444")])
        self.style.configure("TCheckbutton",
            foreground="#FFFFFF")
        self.style.map("TCheckbutton",
            background=[("active", "#666666"),
                ("!active", "#2b2b2b")])
        self.style.configure("TNotebook",
            background="#2b2b2b")
        self.style.configure("TNotebook.Tab",
            background="#444444",
            foreground="#FFFFFF")
        self.style.map("TNotebook.Tab", 
            background=[("selected", "#444444"), 
                ("!selected", "#2b2b2b")],
            foreground=[("selected", "#FFFFFF"),
                ("!selected", "#FFFFFF")])
        self.sidebar.document.body.style.backgroundColor = "#2b2b2b"
        self.sidebar.document.body.style.color = "#FFFFFF"
        
    def apply_light_theme(self):
        self.style.configure(".", background="#F0F0F0", foreground="#000000",)
        self.style.configure("TButton",
            background="#DDDDDD",
            foreground="#000000",
            font=("Arial", 10),
            relief="flat")
        self.style.map("TButton",
            background=[("active", "#CCCCCC"),
                ("!active", "#DDDDDD")])
        self.style.configure("TLabel",
            background="#F0F0F0",
            foreground="#000000",
            font=("Arial", 10))
        self.style.configure("TEntry",
            fieldbackground="#FFFFFF",
            foreground="#000000",
            insertcolor="black",
            borderwidth=0,
            font=("Arial", 10))
        self.style.configure("TScale",
            troughcolor="white",)
        self.style.map('TScale',
          background=[('active', '#F0F0F0'),
                      ('!active', '#F0F0F0')])
        self.style.configure("TFrame",
            background="#F0F0F0",)
        self.style.configure("TScrollbar",
            background="#DDDDDD",
            troughcolor="#F0F0F0",
            arrowcolor="#000000")
        self.style.map("TScrollbar",
            background=[("active", "#CCCCCC"),
                ("!active", "#DDDDDD")])
        self.style.configure("TCheckbutton",
            background="#F0F0F0",
            foreground="#000000",
            font=("Arial", 10))
        self.style.map("TCheckbutton",
            background=[("active", "#DDDDDD"),
                ("!active", "#F0F0F0")])
        self.style.configure("TNotebook",
            background="#F0F0F0",
            relief="flat",
            borderwidth=0,
            tabmargins=(5, 5, 5, 0),
            padding=0)
        self.style.configure("TNotebook.Tab",
            background="#DDDDDD",
            foreground="#000000",
            padding=(10, 5),
            relief="flat",
            borderwidth=0,
            font=("Arial", 10))
        self.style.map("TNotebook.Tab", 
            background=[("selected", "#DDDDDD"),
                ("!selected", "#F0F0F0")],
            foreground=[("selected", "#000000"),
                ("!selected", "#000000")])
        # this only works on the non-experimental version of tkhtml
        self.sidebar.document.body.style.backgroundColor = "#F0F0F0"
        self.sidebar.document.body.style.color = "#000000"

    def select_all_in_entry(self, widget):
        widget.select_range(0, 'end')
        widget.icursor('end')
    
    def select_all_in_text(self, widget):
        widget.tag_add(tk.SEL, "1.0", tk.END)
        widget.mark_set(tk.INSERT, "1.0")
        widget.see(tk.INSERT)

    def on_right_click(self, event):
        url = self.frame.get_currently_hovered_element().getAttribute("href")
        if url:
            url = self.frame.resolve_url(url)
        selection = self.frame.get_selection()
        menu = tk.Menu(self, tearoff=0)
        if len(self.back_history) > 1:
            menu.add_command(label="Back", accelerator="Alt-Back", command=self.back)
        if len(self.forward_history) == 1: 
            menu.add_command(label="Forward", accelerator="Alt-Forward", command=self.forward)
        menu.add_command(label="Reload", accelerator="Ctrl-R", command=self.reload)
        menu.add_separator()
        if url:
            menu.add_command(label="Open link", command=lambda url=url: self.link_click(url))
            menu.add_command(label="Open link in new tab", command=lambda url=url: self.open_new_tab(url))
            menu.add_separator()
        menu.add_command(label="Select all", accelerator="Ctrl-A", command=self.frame.select_all)
        if selection:
            menu.add_command(label="Copy", accelerator="Ctrl-C", command=self.frame.html.copy_selection)
        menu.add_separator()
        if self.frame["experimental"] or not os.name == "nt":
            menu.add_command(label="Take screenshot", command=self.screenshot)
        else:
            menu.add_command(label="Take screenshot", state="disabled", command=self.screenshot)
        menu.add_command(label="Snapshot page", command=self.snapshot)
        if self.frame["experimental"]:
            menu.add_command(label="Print page", accelerator="Ctrl-P", command=self.print)
        else:
            menu.add_command(label="Print page", accelerator="Ctrl-P", state="disabled", command=self.print)
        menu.add_command(label="Save page", accelerator="Ctrl-S", command=self.save)
        menu.add_separator()
        menu.add_command(label="Find in page", accelerator="Ctrl-F", command=lambda: self.open_findbar(True))
        if str(self.view_source_button.cget("state")) == "normal":
            menu.add_command(label="View page source", accelerator="Ctrl-U", command=self.view_source)
        menu.tk_popup(event.x_root, event.y_root, 0)

    def screenshot(self):
        file_path = filedialog.asksaveasfilename(
            filetypes=[("JPG files", "*.jpg"), ("PNG files", "*.png"), ("All files", "*.*")],
            title="Save Screenshot As"
        )
        if file_path:
            self.frame.screenshot_page(file_path)

    def snapshot(self):
        file_path = filedialog.asksaveasfilename(
            filetypes=[("HTML files", "*.html"), ("XHTML files", "*.xhtml"), ("XML files", "*.xml"), ("All files", "*.*")],
            title="Snapshot Page As"
        )
        if file_path:
            self.frame.snapshot_page(file_path)

    def print(self):
        if self.frame["experimental"]:
            file_path = filedialog.asksaveasfilename(
                filetypes=[("Postscript files", "*.ps"), ("All files", "*.*")],
                title="Print Page As"
            )
            if file_path:
                self.frame.print_page()

    def save(self):
        file_path = filedialog.asksaveasfilename(
            filetypes=[("HTML files", "*.html"), ("XHTML files", "*.xhtml"), ("XML files", "*.xml"), ("All files", "*.*")],
            title="Save Page As"
        )
        if file_path:
            self.frame.save_page(file_path)

    def urlbar_focus(self):
        self.urlbar.focus()
        self.urlbar.select_range(0, 'end')
        self.urlbar.icursor('end')

    def previous_and_find(self):
        self.find_select_num -= 1
        if self.find_select_num == 0:
            self.find_select_num = self.find_match_num
        self.search_in_page(change=False)

    def next_and_find(self):
        self.find_select_num += 1
        if self.find_select_num == self.find_match_num+1:
            self.find_select_num = 1
        self.search_in_page(change=False)

    def search_in_page(self, x=None, y=None, change=True):
        if self.frame.base_url == "about:html":
            frame = self.html_playground.iframe
        else:
            frame = self.frame
        if change:
            self.find_select_num = 1
        self.find_match_num = frame.find_text(self.findbox_var.get(), self.find_select_num, self.ignore_case_var.get(), self.highlight_all_var.get())
        if self.find_match_num > 0:
            self.find_bar_caption.configure(text="Selected {} of {} matches.".format(self.find_select_num, self.find_match_num))
        else:
            self.find_bar_caption.configure(text="No matches")

        if self.find_match_num > 1:
            self.find_previous.config(state="normal", cursor="hand2")
            self.find_next.config(state="normal", cursor="hand2")
        else:
            self.find_previous.config(state="disabled", cursor="arrow")
            self.find_next.config(state="disabled", cursor="arrow")

    def hide_messsage_box(self, event):
        if self.message_box.winfo_ismapped():
            self.message_box.grid_forget()
        else:
            self.message_box.grid(column=0, row=5, sticky="ew", padx=4, pady=(0, 4,))

    def add_message(self, message):
        self.message_box.insert("end", message+"\n\n")
        self.message_box.yview("end")
        if f"Error loading {self.urlbar.get()}" in message:
            self.handle_view_source_button("about:error")
        self.linklabel.config(text=self.cut_text(message, 80))

    def toggle_images(self):
        self.frame.config(images_enabled= self.images_var.get())
        self.reload()

    def toggle_styles(self):
        self.frame.config(stylesheets_enabled = self.styles_var.get())
        self.reload()

    def toggle_forms(self):
        self.frame.config(forms_enabled = self.forms_var.get())
        self.reload()

    def toggle_js(self):
        try:
            val = self.js_var.get()
            self.frame.config(javascript_enabled = val)
            self.reload()
        except ModuleNotFoundError:
            self.js_var.set(0)
            tk.messagebox.showerror("Error", "PythonMonkey must be installed to enable JavaScript.")

    def toggle_objects(self):
        self.frame.config(objects_enabled = self.objects_var.get())
        self.reload()

    def toggle_caches(self):
        self.frame.config(caches_enabled = self.caches_var.get())
        self.reload()

    def toggle_emojis(self):
        self.frame.config(crash_prevention_enabled = self.crashes_var.get())
        self.reload()

    def toggle_threads(self):
        self.frame.config(threading_enabled = self.threads_var.get())
        self.reload()

    def toggle_theme(self, update_page=True):
        value = self.invert_page_var.get()
        if value:
            self.apply_dark_theme()
        else:
            self.apply_light_theme()

        self.frame.config(dark_theme_enabled = value)
        if update_page:
            self.reload()

    def toggle_inverter(self):
        self.frame.config(image_inversion_enabled = self.invert_images_var.get())
        self.reload()

    def toggle_selection(self):
        self.frame.config(selection_enabled = self.selection_var.get())

    def toggle_caret_browsing(self):
        self.frame.config(caret_browsing_enabled = self.caret_browsing_var.get())

    def open_sidebar(self, keep_open=False):
        if self.sidebar.winfo_ismapped() and not keep_open:
            self.close_sidebar()
        else:
            self.sidebar.grid(row=0, column=2, sticky="nsew")
            self.sidebar.update()
            self.settingsbutton.state(['pressed'])
            
    def close_sidebar(self):
        if self.sidebar.winfo_ismapped():
            self.sidebar.grid_forget()
            self.settingsbutton.state(['!pressed'])

    def open_findbar(self, keep_open=False):
        if self.findbar.winfo_ismapped() and not keep_open:
            self.findbar.grid_forget()
            self.frame.find_text("")
            self.findbutton.state(['!pressed'])
        else:
            self.findbar.grid(column=0, row=2, sticky="ew", pady=(4,0,))
            self.find_box.focus()
            self.findbutton.state(['pressed'])

    def on_motion(self, event):
        text = self.frame.get_currently_hovered_node_text()
        link = self.frame.get_currently_hovered_node_attribute("href")
        if link:
            self.linklabel.config(text=self.cut_text("Hyper-link: "+link, 80))
        elif text:
            self.linklabel.config(text=self.cut_text("Text: "+text, 80))
        else:
            elm = self.frame.get_currently_hovered_node_tag()
            self.linklabel.config(text=self.cut_text("Element: "+elm, 80))

    def back(self):
        if len(self.back_history) == 1:
            return
        self.forwardbutton.config(state="normal", cursor="hand2")
        self.forward_history.append(self.back_history[-1])
        url = self.back_history[-2]
        self.back_history = self.back_history[:-1]
        self.load_url(url)
        if len(self.back_history) <= 1:
            self.backbutton.config(state="disabled", cursor="arrow")
        self.url_change(url)

    def on_downloading(self, event):
        self.reloadbutton.config(text="Stop", command=self.frame.stop)

    def load_url(self, url, decode=None, force=False):
        if url == "about:html":
            if self.html_playground is None: self.html_playground = HTMLPlayground(self.frame)
            self.frame.load_html(HTML_TEST_PAGE.format(self.html_playground), url)
        else:
            self.frame.load_url(url, decode, force)

    def forward(self):
        if len(self.forward_history) == 0:
            return
        url = self.forward_history[-1]
        self.forward_history = self.forward_history[:-1]
        if self.forward_history == []:
            self.forwardbutton.config(state="disabled", cursor="arrow")
        self.backbutton.config(state="normal", cursor="hand2")
        self.back_history.append(url)
        self.load_url(url)
        self.url_change(url)

    def cut_text(self, text, limit):
        if (len(text) > limit):
            text = text[:limit] + "..."
        return text

    def focus_on_url(self):
        self.urlbar.focus()
        self.urlbar.select_range(0, 'end')

    def open_new_tab(self, url=NEW_TAB):
        page = Page(self.master)
        self.master.add(page, text='')
        self.master.select(page)
        page.invert_page_var.set(self.invert_page_var.get())
        page.toggle_theme(False)
        page.link_click(url, history=False)

    def close_current_tab(self):
        self.master.forget(self)

    def done_loading(self, event):
        self.linklabel.config(text="Done")
        self.reloadbutton.config(text="Reload", command=self.reload)

        self.search_in_page()

    def handle_view_source_button(self, url):
        if url in BUILTIN_PAGES or url.startswith("view-source:") or url == "about:html":
            self.view_source_button.config(state="disabled", cursor="arrow")
        else:
            self.view_source_button.config(state="normal", cursor="hand2")

    def url_change(self, url=None):
        if not isinstance(url, str): url = self.frame.current_url;
        self.master.tab(self, text=self.cut_text(url, 40))
        self.urlbar.delete(0, "end")
        self.urlbar.insert(0, url)
        self.handle_view_source_button(url)

    def addtohist(self, url):
        self.back_history.append(url)
        self.forward_history = []
        self.forwardbutton.config(state="disabled", cursor="arrow")
        self.backbutton.config(state="normal", cursor="hand2")

    def form_submit(self, url, data, method):
        if method == "GET":
            self.addtohist(url+data)
        else:
            self.addtohist(url)
        self.frame.load_form_data(url, data, method)

    def load_site(self, event):
        url = check_url(self.urlbar)
        self.addtohist(url)
        self.load_url(url, force=True)
        self.handle_view_source_button(url)

    def link_click(self, url, history=True):
        self.addtohist(url)
        self.master.tab(self, text=self.cut_text(url, 40))
        if not history:
            self.backbutton.config(state="disabled", cursor="arrow")
        self.urlbar.delete(0, "end")
        self.urlbar.insert(0, url)
        self.load_url(url)
        self.handle_view_source_button(url)

    def reload(self):
        if self.frame.base_url == "about:html": 
            self.html_playground.iframe.reload()
        else:
            self.frame.reload()

    def change_title(self, event):
        self.master.tab(self, text=self.cut_text(self.frame.title, 40))  
    
    def select_all(self):
        if self.focus_get() not in (self.urlbar, self.find_box):
            if self.frame.base_url == "about:html":
                self.html_playground.iframe.select_all()
            else:
                self.frame.select_all()

    def view_source(self):
        if str(self.view_source_button.cget("state")) == "normal":
            self.open_new_tab("view-source:"+self.urlbar.get())
        
class Browser(tk.Tk):
    "TkinterWeb Browser"

    def __init__(self):

        tk.Tk.__init__(self)
        self.title("TkinterWebBrowser")
        self.minsize(800, 500)
        self.main_frame = main_frame = tk.Frame(self, highlightthickness=0, bd=0)

        self.frame = frame = Notebook(main_frame)
        frame.enable_traversal()
        frame.bind("<<NotebookTabChanged>>", self.on_tab_change)

        page = Page(frame)
 
        self.bind_all("<Up>", lambda e: frame.select().frame.html._on_up(e))
        self.bind_all("<Down>", lambda e: frame.select().frame.html._on_down(e))
        self.bind_all("<Left>", lambda e: frame.select().frame.html._on_left(e))
        self.bind_all("<Right>", lambda e: frame.select().frame.html._on_right(e))
        self.bind_all("<Prior>", lambda e: frame.select().frame.html._on_prior(e))
        self.bind_all("<Next>", lambda e: frame.select().frame.html._on_next(e))
        self.bind_all("<Home>", lambda e: frame.select().frame.html._on_home(e))
        self.bind_all("<End>", lambda e: frame.select().frame.html._on_end(e))
        self.bind_all("<Control-w>", lambda e: frame.select().close_current_tab())
        self.bind_all("<Control-t>", lambda e: frame.select().open_new_tab())
        self.bind_all("<Control-f>", lambda e: frame.select().open_findbar(True))
        self.bind_all("<Control-b>",  lambda e: frame.select().open_sidebar(True))
        self.bind_all("<Control-l>", lambda e: frame.select().urlbar_focus())
        self.bind_all("<Control-i>", lambda e: frame.select().hide_messsage_box(e))
        self.bind_all("<Control-r>", lambda e: frame.select().reloadbutton.invoke())
        self.bind_all("<Control-n>", lambda e: Browser())
        self.bind_all("<Control-q>", lambda e: self.destroy())
        self.bind_all("<Control-a>", lambda e: frame.select().select_all())
        self.bind_all("<Control-u>", lambda e: frame.select().view_source())
        self.bind_all("<Control-p>", lambda e: frame.select().print())
        self.bind_all("<Control-s>", lambda e: frame.select().save())
        self.bind_all("<Alt-Left>", lambda e: frame.select().back())
        self.bind_all("<Alt-Right>", lambda e: frame.select().forward())

        frame.pack(expand=True, fill="both")
        main_frame.pack(expand=True, fill="both")
        frame.add(page, text='')

        page.link_click(NEW_TAB, history=False)

        self.mainloop()
    
    def on_tab_change(self, event):
        if self.frame.pages:
            self.frame.select().toggle_theme(False)
        else:
            self.destroy()

if __name__ == "__main__":   
    Browser()