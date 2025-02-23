"""
A proof-of-concept web browser using TkinterWeb

Note that TkinterWeb is not necessarily intended to be a full-blown modern web browser
These already exist and are generally resource-hungry and not highly integratable with Tkinter
Being based on Tkhtml, TkinterWeb is intended to be fast, lightweight, and highly integrated with Tkinter while providing far more control over layouts and styling than is feasible than Tkinter
TkinterWeb displays older or simpler websites well but may be found lacking on more modern websites

This file was originally created for testing TkinterWeb and could be cleaned up a bit, but nonetheless is a great example of some of the things that can be done with the software, including:
 - loading pages
 - searching pages
 - embedding Tkinter widgets
 - manipulating the DOM
 - and others
 
Copyright (c) 2025 Andereoo
"""

import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

from tkinterweb import HtmlFrame, Notebook, __version__
from tkinterweb.utilities import BUILTIN_PAGES, DONE_LOADING_EVENT, URL_CHANGED_EVENT, TITLE_CHANGED_EVENT, DOWNLOADING_RESOURCE_EVENT

import os


if os.name == "nt":
	from ctypes import windll
	windll.shcore.SetProcessDpiAwareness(1)

version = []
for letter in __version__.split("."):
    version.append(int(letter))
if tuple(version) < (3, 25, 12):
    raise RuntimeError("This demo needs TkinterWeb version 3.25.12 or higher.")


NEW_TAB = "http://tkhtml.tcl.tk"#https://wiki.python.org/moin/TkInter"


class Page(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        ttk.Frame.__init__(self, master, *args, **kwargs)

        self.master = master
        self.back_history = []
        self.forward_history = []

        self.style = ttk.Style(self)

        topbar = ttk.Frame(self)
        self.bottombar = bottombar = ttk.Frame(self)
        self.findbar = findbar = ttk.Frame(self)
        
        self.linklabel = linklabel = ttk.Label(bottombar, text="Welcome to TkinterWeb!", cursor="hand2")

        self.backbutton = backbutton = ttk.Button(topbar, text="Back", command=self.back, state="disabled")
        self.forwardbutton = forwardbutton = ttk.Button(topbar, text="Forward", command=self.forward, state="disabled")
        self.reloadbutton = reloadbutton = ttk.Button(topbar, text="Reload", command=self.reload, cursor="hand2")
        self.urlbar = urlbar = ttk.Entry(topbar)
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

        self.frame = frame = HtmlFrame(self, message_func=self.add_message, link_click_func=self.link_click, form_submit_func=self.form_submit)
        self.sidebar = sidebar = HtmlFrame(frame, width=250, fontscale=0.8, selection_enabled=False, messages_enabled=False)
        sidebar.grid_propagate(False)

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
        invert_page_enabled = ttk.Checkbutton(sidebar, text="Dark theme", variable=invert_page_var, command=self.toggle_theme)
        self.invert_images_var = invert_images_var = tk.IntVar(value=self.frame["image_inversion_enabled"])
        invert_images_enabled = ttk.Checkbutton(sidebar, text="Image inverter", variable=invert_images_var, command=self.toggle_inverter)
        
        self.zoom_var = zoom_var = tk.StringVar(value=self.frame["zoom"])
        self.zoom_box = zoom_box = ttk.Scale(sidebar, from_=0.1, to=5, orient="horizontal", variable=zoom_var, command=self.set_zoom)
        self.fontscale_var = fontscale_var = tk.StringVar(value=frame["fontscale"])
        self.fontscale_box = fontscale_box = ttk.Scale(sidebar, from_=0.1, to=5, orient="horizontal", variable=fontscale_var, command=self.set_fontscale)
        self.broken_page_msg_box = broken_page_msg_box = tk.Text(sidebar, wrap=tk.WORD, width=30, undo=True)
        self.view_source_button = view_source_button = ttk.Button(sidebar, text="View page source", command=self.view_source)
        about_button = ttk.Button(sidebar, text="About TkinterWeb", command=lambda url="about:tkinterweb": self.open_new_tab(url))
        
        frame.bind(TITLE_CHANGED_EVENT, self.change_title)
        frame.bind(URL_CHANGED_EVENT, self.url_change)
        frame.bind(DONE_LOADING_EVENT, self.done_loading)
        frame.bind(DOWNLOADING_RESOURCE_EVENT, self.on_downloading)

        linklabel.bind("<Button-1>", self.hide_messsage_box)
        urlbar.bind("<Return>", self.load_site)
        #frame.bind("<Motion>", self.on_motion)
        frame.bind("<Leave>", lambda event: linklabel.config(text="Done"))
        broken_page_msg_box.bind("<<Modified>>", self.broken_page_msg_update)
        broken_page_msg_box.bind('<KeyRelease>', self.broken_page_msg_change)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        topbar.grid(column=0, row=0, sticky="ew")
        frame.grid(column=0, row=1, sticky="nsew")
        bottombar.grid(column=0, row=4, sticky="ew")

        self.sidebar.load_html(f"""<html><body><style>body p, span {{margin-top: 5px; margin-bottom: 5px; cursor: default}} object {{width: 100%; cursor: pointer}}</style>
                               <div><object allowscrolling data={images_enabled}></object><br>
                               <object allowscrolling data={styles_enabled}></object><br>
                               <object allowscrolling data={forms_enabled}></object><br>
                               <object allowscrolling data={objects_enabled}></object><br>
                               <object allowscrolling data={caches_enabled}></object><br>
                               <object allowscrolling data={emojis_enabled}></object>
                               <object allowscrolling data={threads_enabled}></object><hr></hr>
                               <object allowscrolling data={invert_page_enabled}></object><br>
                               <object allowscrolling data={invert_images_enabled}></object><hr></hr>
                               <div><p style="float:left">Zoom:</p><span style="float:right" id="zoom">{zoom_var.get()}</span><object allowscrolling data={zoom_box}></object></div>
                               <div><p style="float:left">Font scale:</p><span style="float:right" id="fontscale">{fontscale_var.get()}</span><object allowscrolling data={fontscale_box}></object></div><hr></hr>
                               <p>Parse mode:</p><select style="width:100%; color:black"><option value="xml">xml</option><option value="xhtml">xhtml</option><option value="html">html</option></select><hr></hr>
                               <p>Broken page message:</p><object allowscrolling data={broken_page_msg_box}></object><hr></hr>
                               <object allowscrolling data={view_source_button}></object>
                               <object allowscrolling data={about_button}></object></div></body></html>
        """)
        sidebar.bind_all("<<Modified>>", self.on_modified)

        linklabel.pack(expand=True, fill="both")
        topbar.columnconfigure(4, weight=1)
        backbutton.grid(row=0, column=1, pady=5, padx=5)
        forwardbutton.grid(row=0, column=2, pady=5)
        reloadbutton.grid(row=0, column=3, pady=5, padx=5)
        urlbar.grid(row=0, column=4, pady=5, padx=3, sticky="NSEW")
        newbutton.grid(row=0, column=5, pady=5, padx=5)
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

        broken_page_msg_box.insert("end", BUILTIN_PAGES["about:error"].format(self.sidebar.background, self.sidebar.foreground, "").replace("</", "\n</").replace(">", ">\n").replace("\n\n", "\n").replace("</html>\n", "</html>"))

        frame.bind("<Button-3>", self.on_right_click)
        for widget in [urlbar, find_box, zoom_box, fontscale_box]:
            widget.bind("<Control-a>", lambda e: self.after(50, self.select_all_in_entry, e.widget))
        broken_page_msg_box.bind("<Control-a>", lambda e: self.after(50, self.select_all_in_text, e.widget))

        for child in findbar.winfo_children():
            child.bind("<Escape>", lambda x: self.open_findbar())
        for child in sidebar.winfo_children():
            child.bind("<Escape>", lambda x: self.close_sidebar())
        settingsbutton.bind("<Escape>", lambda x: self.close_sidebar())

        self.apply_light_theme()

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
            font=("Arial", 10))
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
            background=[("selected", "#FFFFFF"),
                ("!selected", "#DDDDDD")],
            foreground=[("selected", "#000000"),
                ("!selected", "#000000")])
        # this only works on the non-experimental version of tkhtml
        self.sidebar.document.body.style.backgroundColor = "#F0F0F0"
        self.sidebar.document.body.style.color = "#000000"

    def on_modified(self, event):
        if "combobox" in str(event.widget):
            self.frame.configure(parsemode = event.widget.get())

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
        menu.add_command(label="Take screenshot", command=self.screenshot)
        menu.add_command(label="Snapshot page", command=self.snapshot)
        menu.add_command(label="Print", accelerator="Ctrl-P", command=self.print)
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
        if change:
            self.find_select_num = 1
        self.find_match_num = self.frame.find_text(self.findbox_var.get(), self.find_select_num, self.ignore_case_var.get(), self.highlight_all_var.get())
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

    def broken_page_msg_update(self, event=None):
        height = self.broken_page_msg_box.count("1.0", "end", "displaylines")[0]
        self.broken_page_msg_box.configure(height=height)
        self.broken_page_msg_box.edit_modified(False)

    def broken_page_msg_change(self, event):
        self.frame.configure(broken_webpage_message = event.widget.get("1.0", 'end-1c'))

    def toggle_images(self):
        self.frame.configure(images_enabled= self.images_var.get())
        self.reload()

    def toggle_styles(self):
        self.frame.configure(stylesheets_enabled = self.styles_var.get())
        self.reload()

    def toggle_forms(self):
        self.frame.configure(forms_enabled = self.forms_var.get())
        self.reload()

    def toggle_objects(self):
        self.frame.configure(objects_enabled = self.objects_var.get())
        self.reload()

    def toggle_caches(self):
        self.frame.configure(caches_enabled = self.caches_var.get())
        self.reload()

    def toggle_emojis(self):
        self.frame.configure(crash_prevention_enabled = self.crashes_var.get())
        self.reload()

    def toggle_threads(self):
        self.frame.configure(threading_enabled = self.threads_var.get())
        self.reload()

    def toggle_theme(self, update_page=True):
        value = self.invert_page_var.get()
        if value:
            self.apply_dark_theme()
        else:
            self.apply_light_theme()

        self.frame.configure(dark_theme_enabled = value)
        self.frame.background = self.style.lookup('TFrame', 'background')
        self.frame.foreground = self.style.lookup('TLabel', 'foreground')
        if update_page:
            self.reload()

    def toggle_inverter(self):
        self.frame.configure(image_inversion_enabled = self.invert_images_var.get())
        self.reload()

    def open_sidebar(self, keep_open=False):
        self.sidebar.grid_propagate(False)
        if self.sidebar.winfo_ismapped() and not keep_open:
            self.close_sidebar()
        else:
            self.sidebar.grid(row=0, column=2, sticky="nsew")
            self.sidebar.update()
            self.broken_page_msg_box.update()
            self.broken_page_msg_update()
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
        self.frame.load_url(url)
        if len(self.back_history) <= 1:
            self.backbutton.config(state="disabled", cursor="arrow")
        self.url_change(url)

    def on_downloading(self, event):
        self.reloadbutton.config(text="Stop", command=self.frame.stop)

    def forward(self):
        if len(self.forward_history) == 0:
            return
        url = self.forward_history[-1]
        self.forward_history = self.forward_history[:-1]
        if self.forward_history == []:
            self.forwardbutton.config(state="disabled", cursor="arrow")
        self.backbutton.config(state="normal", cursor="hand2")
        self.back_history.append(url)
        self.frame.load_url(url)
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

    def set_zoom(self, *args):
        zoom = round(float(self.zoom_var.get()), 1)
        self.frame.configure(zoom = self.zoom_var.get())
        self.sidebar.document.getElementById("zoom").textContent = zoom

    def set_fontscale(self, *args):
        fontscale = round(float(self.fontscale_var.get()), 1)
        self.frame.configure(fontscale = fontscale)
        self.sidebar.document.getElementById("fontscale").textContent = fontscale

    def done_loading(self, event):
        self.linklabel.config(text="Done")
        self.reloadbutton.config(text="Reload", command=self.reload)

    def handle_view_source_button(self, url):
        if url in BUILTIN_PAGES or url.startswith("view-source:"):
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
        url = self.urlbar.get()
        if not any((url.startswith("file:"), url.startswith("http:"), url.startswith("about:"), url.startswith("view-source:"), url.startswith("https:"), url.startswith("data:"))):
            url = "http://{}".format(url)
        self.addtohist(url)
        self.frame.load_url(url, force=True)
        self.handle_view_source_button(url)

    def link_click(self, url, history=True):
        self.addtohist(url)
        self.master.tab(self, text=self.cut_text(url, 40))
        if not history:
            self.backbutton.config(state="disabled", cursor="arrow")
        self.urlbar.delete(0, "end")
        self.urlbar.insert(0, url)
        self.frame.load_url(url)
        self.handle_view_source_button(url)

    def reload(self):
        self.frame.load_url(self.frame.current_url, force=True)

    def change_title(self, event):
        self.master.tab(self, text=self.cut_text(self.frame.title, 40))  
    
    def select_all(self):
        if self.focus_get() not in (self.urlbar, self.find_box, self.zoom_box, self.fontscale_box, self.broken_page_msg_box):
            self.frame.select_all()

    def view_source(self):
        if str(self.view_source_button.cget("state")) == "normal":
            self.open_new_tab("view-source:"+self.urlbar.get())
        
class Browser(tk.Tk):
    "TkinterWeb Browser"

    def __init__(self):

        tk.Tk.__init__(self)
        self.title("TkinterWebBrowser")
        self.main_frame = main_frame = tk.Frame(self, highlightthickness=0, bd=0)

        self.frame = frame = Notebook(main_frame)
        frame.bind("<<NotebookTabChanged>>", self.on_tab_change)

        page = Page(frame)
 
        self.bind_all("<Up>", lambda e: frame.select().frame.html.yview_scroll(-5, "units"))
        self.bind_all("<Down>", lambda e: frame.select().frame.html.yview_scroll(5, "units"))
        self.bind_all("<Prior>", lambda e: frame.select().frame.html.yview_scroll(-1, "pages"))
        self.bind_all("<Next>", lambda e: frame.select().frame.html.yview_scroll(1, "pages"))
        self.bind_all("<Home>", lambda e: frame.select().frame.html.yview_moveto(0))
        self.bind_all("<End>", lambda e: frame.select().frame.html.yview_moveto(1))
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
        self.bind_all("<Alt-Left>", lambda e: frame.select().back())
        self.bind_all("<Alt-Right>", lambda e: frame.select().forward())

        frame.pack(expand=True, fill="both")
        main_frame.pack(expand=True, fill="both")
        frame.add(page, text='')

        page.link_click(NEW_TAB, history=False)

        self.mainloop()
    
    def on_tab_change(self, event):
        self.frame.select().toggle_theme(False)
        if not self.frame.pages:
            self.destroy()

if __name__ == "__main__":   
    Browser()