import sys

try:
    import tkinter as tk
    from tkinter import ttk
except ImportError:
    import Tkinter as tk
    import ttk

class _AutoScrollbar(ttk.Scrollbar):
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.tk.call("grid", "remove", self)
        else:
            self.grid()
        ttk.Scrollbar.set(self, lo, hi)
        
    def pack(self, **kw):
        raise tk.TclError("cannot use pack with this widget")
    
    def place(self, **kw):
        raise tk.TclError("cannot use place with this widget")

def notifier(main, sub, cap=True):
    "Notifications printer."
    try:
        sys.stderr.write(("UserNotification: "+str(main))+"\n")
        sub = str(sub)
        if cap:
            if len(sub) > 200:
                sub = sub[:200] + "..."
        sys.stdout.write(str(sub)+"\n\n")
    except Exception:
        "sys.stderr.write doesn't work in .pyw files."
        "Since .pyw files have no console, we can simply not bother printing messages."
