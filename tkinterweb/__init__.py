"""
TkinterWeb v4.4
This is a wrapper for the Tkhtml3 widget from http://tkhtml.tcl.tk/tkhtml.html, 
which displays styled HTML documents in Tkinter.

Copyright (c) 2021-2025 Andereoo
"""


try:
    from .htmlwidgets import HtmlFrame, HtmlLabel, HtmlParse, Notebook, TkHtmlParsedURI, TkinterWeb
    # We keep this stuff in utilities.py so that about:tkinterweb can access it
    from .utilities import __title__, __author__, __copyright__, __license__, __version__
except (ImportError, ModuleNotFoundError):
    import traceback, sys
    import tkinter as tk
    from tkinter import messagebox
    # Give useful troubleshooting information as a popup, as most bundled applications don't have a visible console
    # Also print the message in case something is also wrong with the Tkinter installation
    error_message = "Error: The files required to run TkinterWeb could not be found. \
This typically occurs when bundling TkinterWeb into an app without forcing the application maker to include all nessessary files or when some of TkinterWeb's dependencies are not installed or bundled. \
See https://tkinterweb.readthedocs.io/en/latest/faq.html for more information. \n\n\
{}".format(traceback.format_exc())
    sys.stdout.write(error_message)

    root = tk.Tk()
    root.withdraw()
    # For older versions of pyinstaller, windowed app may crash without any message of any kind
    message = messagebox.showerror("Fatal Error Encountered", error_message)
    sys.exit()


__all__ = ['Demo' 'HtmlParse', 'HtmlFrame', 'HtmlLabel', 'Notebook', 'TkHtmlParsedURI', 'TkinterWeb']


class Demo():
    "A simple example of TkinterWeb in action displaying the Tkinter Wiki."

    def __init__(self):
        import tkinter as tk

        self.root = root = tk.Tk()
        self.frame = HtmlFrame(root, on_navigate_fail=self.on_error)
        self.frame2 = frame2 = HtmlFrame(root, messages_enabled=False)
        self.button = tk.Button(root, cursor="hand2")

        self.afters = []
        
        self.load()
        frame2.bind("<<TitleChanged>>", lambda event: self.root.title(frame2.title))
        frame2.pack(expand=True, fill="both")
        root.mainloop()

    def load(self, url="https://wiki.python.org/moin/TkInter"):
        self.button.configure(text="Continue", command=self.change_button)
        self.frame.load_html(f"""<html><head><style>td {{text-align:center;vertical-align:middle}} html,body,table,tr{{width:100%;height:100%;margin:0}}</style></head><body><table><tr><td tkinterweb-full-page id="container">
        <code>Still waiting for response from <a href="https://wiki.python.org/moin/TkInter">wiki.python.org</a>...</code></td></tr></table></body></html>""")
        self.frame.load_url(url)
        self.frame2.load_html(f"""<html><head><title>TkinterWeb Demo</title><style>#viewer {{width:100%; height: 300px}} td {{text-align:center;vertical-align:middle;padding: 10px}} h3{{margin:0 0 10px 0;padding:0;font-weight:normal}} html,body,table,tr{{background-color:{self.frame["about_page_background"]};color:{self.frame["about_page_foreground"]};width:100%;height:100%;margin:0}}</style></head>
        <body><table><tr><td tkinterweb-full-page id="container">
        <h3 id="heading">Welcome to TkinterWeb!</h3><object id="button" data={self.button}></object>
        </td></tr></table></body></html>""")

    def on_error(self, url, error, code):
        for after in self.afters:
            self.root.after_cancel(after)
        self.button.configure(text="Try Again", command=lambda url=self.frame.current_url: self.load(url))
        html = f"""<html><head><title>TkinterWeb Demo - Error {code}</title><style>td {{text-align:center;vertical-align:middle}} h3{{margin:0 0 10px 0;padding:0;font-weight:normal}} html,body,table,tr{{background-color:{self.frame["about_page_background"]};color:{self.frame["about_page_foreground"]};width:100%;height:100%;margin:0}}</style></head>
        <body><table><tr><td tkinterweb-full-page>
        <h3>Error {code}</h3><h3>An internet connection is required to display the TkinterWeb demo :(</h3><object id="button" data={self.button}></object>
        </td></tr></table></body></html>"""
        if self.frame2.winfo_ismapped():
            self.frame2.load_html(html)
        else:
            self.frame.load_html(html)

    def change_button(self):
        self.button.configure(text="Please don't press this button again", command=self.change_page)
    
    def change_page(self):
        heading = self.frame2.document.getElementById("heading")
        self.frame2.document.getElementById("button").widget = None
        def page1():
            heading.textContent = "Enjoy this website written about Tkinter, displayed in Tkinter:"
        def page2():
            self.frame2.pack_forget()
            self.frame.pack(expand=True, fill="both")
            if self.frame.title: self.root.title(f"TkinterWeb Demo - {self.frame.title}")
        self.afters = [self.root.after(3000, page1), self.root.after(5500, page2)]
