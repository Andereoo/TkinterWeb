"""
TkinterWeb v3.10
This is a wrapper for the Tkhtml3 widget from http://tkhtml.tcl.tk/tkhtml.html, 
which displays styled HTML documents in Tkinter.

Copyright (c) 2021 Andereoo

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

try:
    from bindings import TkinterWeb
    from htmlwidgets import HtmlFrame, HtmlLabel
    from utilities import Notebook
except (ImportError, ModuleNotFoundError):
    # Give useful troubleshooting information as a popup, as most bundled applications don't have a visible console
    # Also print the message in case something is wrong with the Tkinter installation as well
    error_message = "ModuleNotFoundError: The files required to run TkinterWeb could not be found. \
This usually occurs when bundling TkinterWeb into an app without forcing the application maker to include all nessessary files. \
See https://github.com/Andereoo/TkinterWeb/blob/main/tkinterweb/docs/FAQ.md for more information."
    sys.stdout.write(error_message+"\n\n")
    try:
        import tkinter as tk
        from tkinter import messagebox
    except ImportError as e:
        import Tkinter as tk
        import tkMessageBox as messagebox
    root = tk.Tk()
    root.withdraw()
    message = messagebox.showerror("Fatal Error Encountered", error_message)
    sys.exit()


__title__ = 'TkinterWeb'
___author__ = "Andereoo"
__version__ = '3.10'
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
        frame.load_website("https://wiki.python.org/moin/TkInter")

        frame.pack(expand=True, fill="both")
        root.mainloop()

    def change_title(self, title):
        self.root.title(title)


if __name__ == "__main__":
    Demo()
