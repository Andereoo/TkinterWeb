import ttkbootstrap as ttk

import tkinter as tk
root = ttk.Window(themename="superhero") # create the Tkinter window

from tkinterweb import HtmlText # import the HtmlFrame widget
d = HtmlText(root,messages_enabled=False) # create the HtmlFrame widget
b = tk.Button(root, text="DSF")

#d.load_url("about:tkinterweb")

d.pack()

b1 = ttk.Button(root, text="Submit", bootstyle="success")
b1.pack(side="left", padx=5, pady=10)

b2 = ttk.Button(root, text="Submit", bootstyle="info-outline")
b2.pack(side="left", padx=5, pady=10)

root.mainloop()