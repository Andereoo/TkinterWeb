"""
TkinterWeb v3.25
This is a wrapper for the Tkhtml3 widget from http://tkhtml.tcl.tk/tkhtml.html, 
which displays styled HTML documents in Tkinter.

Copyright (c) 2025 Andereoo
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

try:
    from bindings import TkinterWeb
    from htmlwidgets import HtmlFrame, HtmlLabel
    from utilities import Notebook
except (ImportError, ModuleNotFoundError):
    import traceback

    # Give useful troubleshooting information as a popup, as most bundled applications don't have a visible console
    # Also print the message in case something is also wrong with the Tkinter installation
    error_message = "Error: The files required to run TkinterWeb could not be found. \
This typically occurs when bundling TkinterWeb into an app without forcing the application maker to include all nessessary files or when some of TkinterWeb's dependencies are not installed. \
See https://github.com/Andereoo/TkinterWeb/blob/main/tkinterweb/docs/FAQ.md for more information. \n\n\
{}".format(traceback.format_exc())
    sys.stdout.write(error_message)

    import tkinter as tk
    from tkinter import messagebox

    root = tk.Tk()
    root.withdraw()
    message = messagebox.showerror("Fatal Error Encountered", error_message) #for older versions of pyinstaller, windowed app may crash without any message of any kind
    sys.exit()


__title__ = 'TkinterWeb'
___author__ = "Andereoo"
__copyright__ = "Copyright (c) 2025 Andereoo"
__license__ = "MIT"
__version__ = '3.25'
__all__ = ['HtmlFrame', 'HtmlLabel', 'TkinterWeb', 'Demo']


class Demo():
    "TkinterWeb Demo"

    def __init__(self):
        import tkinter as tk

        self.root = root = tk.Tk()

        frame = HtmlFrame(root)

        frame.on_title_change(self.change_title)
        frame.load_url("https://wiki.python.org/moin/TkInter")

        frame.pack(expand=True, fill="both")
        root.mainloop()

    def change_title(self, title):
        self.root.title(title)


if __name__ == "__main__":
    Demo()
