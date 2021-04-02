"""
TkinterWeb v3.0

This is a wrapper for the Tkhtml3 widget from http://tkhtml.tcl.tk/tkhtml.html, which displays styled HTML documents in Tkinter.
"""

import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from htmlwidgets import HtmlFrame, HtmlLabel
from bindings import TkinterWeb
    
__title__ = 'TkinterWeb'
__version__ = '3.0'
__all__ = ['HtmlFrame', 'HtmlLabel', 'TkinterWeb', 'Demo']

class Demo():
    "TkinterWeb Demo"
    
    def __init__(self):
        
        try:
            import tkinter as tk
        except ImportError:
            import Tkinter as tk
        
        self.root = root = tk.Tk()
        
        self.frame = frame = HtmlFrame(root)
        
        frame.on_title_change(self.change_title)
        frame.on_link_click(self.load_new_page)
        frame.load_website("http://tkhtml.tcl.tk")
        
        frame.pack()
        root.mainloop()

    def change_title(self, title):
        self.root.title(title)

    def load_new_page(self, url):
        self.frame.load_website(url)
        
if __name__ == "__main__":
    Demo()
