"""
TkinterWeb v4
This is a wrapper for the Tkhtml3 widget from http://tkhtml.tcl.tk/tkhtml.html, 
which displays styled HTML documents in Tkinter.

Copyright (c) 2021-2025 Andrew Clarke
"""


try:
    from .htmlwidgets import HtmlFrame, HtmlLabel, HtmlText, HtmlParse
    from .subwidgets import Notebook
    from .bindings import TkHtmlParsedURI, TkinterWeb
    from .utilities import __title__, __author__, __copyright__, __license__, __version__
except (ImportError, ModuleNotFoundError) as error:
    import sys
    import tkinter as tk
    from tkinter import messagebox
    # Give useful troubleshooting information as a popup, as most bundled applications don't have a visible console
    # Also print the message in case something is also wrong with the Tkinter installation
    error_message = f"Error: {error} \n\n\
This may occur when bundling TkinterWeb into an app without forcing the application maker to include all nessessary files or when some of TkinterWeb's dependencies are not installed or bundled.\n\n\
See https://tkinterweb.readthedocs.io/en/latest/faq.html for more information."
    sys.stdout.write(error_message)
    root = tk.Tk()
    root.withdraw()
    # For older versions of pyinstaller, windowed app may crash without any message of any kind
    message = messagebox.showerror("Fatal Error Encountered", error_message)
    sys.exit()


__all__ = ['Demo', 'HtmlFrame', 'HtmlLabel', 'HtmlText', 'HtmlParse', 'Notebook', 'TkHtmlParsedURI', 'TkinterWeb']


class Demo():
    "A simple example of TkinterWeb in action displaying the Tkinter Wiki."

    def __init__(self):
        import tkinter as tk

        self.root = root = tk.Tk()
        self.frame = frame = HtmlFrame(root, on_navigate_fail=self.on_error, on_link_click=self.navigate, selected_text_highlight_color="#e6eee6")
        self.button = tk.Button(root, cursor="hand2")
        
        frame.load_url("https://tkinterweb.readthedocs.io/en/latest/")
        frame.bind("<<TitleChanged>>", lambda event: self.root.title(frame.title))
        frame.bind("<<DOMContentLoaded>>", self.done_loading)
        frame.pack(expand=True, fill="both")

        root.mainloop()

    def HTML_to_text(self, text, start, end):
        "Make HTML code bwtween two strings display as plain text"
        import re
        pattern = re.compile(re.escape(start) + r'(.*?)' + re.escape(end), re.DOTALL)
        def replacer(match):
            inner = match.group(1)
            escaped = inner.replace("<", "&lt;").replace(">", "&gt;").replace("&gt;", ">", 1)
            return start + escaped + end
        return pattern.sub(replacer, text)
    
    def navigate(self, url):
        "Only display files from the docs page or from tkhtml.tcl.tk"
        from urllib.parse import urlparse
        if urlparse(self.frame.current_url).netloc == urlparse(url).netloc or "tkhtml.tcl.tk" in url:
            self.frame.load_url(url)
        else:
            import webbrowser
            webbrowser.open(url)

    def done_loading(self, event):
        "Remove the search bar and display code blocks in iframes to allow horizontal scrolling when the page loads"
        from tkinter import TclError
        try:
            self.frame.document.querySelector("div[role=\"search\"]").remove()
            head = self.frame.document.getElementsByTagName("head")[0].innerHTML
            for code_block in self.frame.document.getElementsByClassName("highlight"):
                iframe = HtmlFrame(self.frame, messages_enabled=False, horizontal_scrollbar="auto", shrink=True, overflow_scroll_frame=self.frame.html)
                text = self.HTML_to_text(code_block.innerHTML, "<span", "</span>")
                iframe.load_html(f"{head}<div class='highlight'>{text}</div>", base_url=self.frame.base_url)
                code_block.widget = iframe
        except TclError:
            pass

    def on_error(self, url, error, code):
        "Show an error page if the page fails to load"
        self.button.configure(text="Try Again", command=lambda url=self.frame.current_url: self.frame.load_url(url))
        html = f"""<html><head><title>TkinterWeb Demo - Error {code}</title><style>td {{text-align:center;vertical-align:middle}} h3{{margin:0 0 10px 0;padding:0;font-weight:normal}} html,body,table,tr{{background-color:{self.frame["about_page_background"]};color:{self.frame["about_page_foreground"]};width:100%;height:100%;margin:0}}</style></head>
        <body><table><tr><td tkinterweb-full-page>
        <h3>Error {code}</h3><h3>An internet connection is required to display the TkinterWeb demo :(</h3><object id="button" data={self.button}></object>
        </td></tr></table></body></html>"""
        self.frame.load_html(html)