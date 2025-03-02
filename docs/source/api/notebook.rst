Notebook Documentation
=======================

The TkinterWeb :class:`Notebook` widget should be used in place of :py:class:`ttk.Notebook`, which is incompatable with Tkhtml on some platforms and crashes when selecting tabs. See https://docs.python.org/3/library/tkinter.ttk.html#notebook for the full API.

.. autoclass:: tkinterweb.Notebook
   :members:

This widget also emits the following Tkinter virtual events that can be bound to:

* ``<<NotebookTabChanged>>``: Generated whenever the selected tab changes.
