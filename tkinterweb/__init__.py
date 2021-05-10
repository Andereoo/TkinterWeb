"""
TkinterWeb v3.5

This is a wrapper for the Tkhtml3 widget from http://tkhtml.tcl.tk/tkhtml.html, 
which displays styled HTML documents in Tkinter.
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from bindings import TkinterWeb
from htmlwidgets import HtmlFrame, HtmlLabel


__title__ = 'TkinterWeb'
__version__ = '3.5'
__all__ = ['HtmlFrame', 'HtmlLabel', 'TkinterWeb', 'Demo']


class Demo():
    "TkinterWeb Demo"

    def __init__(self):

        try:
            import tkinter as tk
        except ImportError:
            import Tkinter as tk

        self.root = root = tk.Tk()

        frame = HtmlFrame(root)

        frame.on_title_change(self.change_title)
        frame.load_website("http://tkhtml.tcl.tk")

        frame.pack(expand=True, fill="both")
        root.mainloop()

    def change_title(self, title):
        self.root.title(title)


if __name__ == "__main__":
    Demo()
