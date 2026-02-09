"""
A simple JavaScript-Tkhtml bridge.
Copyright (c) 2021-2025 Andrew Clarke
"""

from . import dom, utilities

from textwrap import dedent
from traceback import format_exc

# JavaScript is experimental and not used by everyone
# We only import PythonMonkey if/when needed
pm = None

class JSEngine:
    """Access this class via the :attr:`~tkinterweb.HtmlFrame.javascript` property of the :class:`~tkinterweb.HtmlFrame` and :class:`~tkinterweb.HtmlLabel` widgets.

    New in version 4.12.
    
    :ivar html: The associated :class:`.TkinterWeb` instance.
    :ivar document: The associated :class:`.HTMLDocument` instance."""
    def __init__(self, html, document, backend):
        self.html = html
        self.document = document
        self.backend = backend

        if backend not in {"pythonmonkey", "python"}: 
            raise RuntimeError(f"Unknown backend {backend}")

    def __repr__(self):
        return f"{self.html._w}::{self.__class__.__name__.lower()}"

    def register(self, name, obj):
        """Register new JavaScript object. This can be used to access Python variables, functions, and classes from JavaScript (eg. to add a callback for the JavaScript ``alert()`` function or add a ``window`` API). 
        
        JavaScript must be enabled.
        
        :param name: The name of the new JavaScript object.
        :type name: str
        :param obj: The Python object to pass.
        :type obj: anything
        :raise RuntimeError: If JavaScript is not enabled."""
        # TODO: it would be nice to make name optional
        if self.html.javascript_enabled:
            if self.backend == "pythonmonkey":
                self._initialize_javascript()
                pm.eval(f"(function(pyObj) {{globalThis.{name} = pyObj}})")(obj)
            elif self.backend == "python":
                self._initialize_exec_context()
                self._globals[name] = obj
        else:
            raise RuntimeError("JavaScript support must be enabled to register a JavaScript object")
        
    def eval(self, expr, _locals=None):
        """Evaluate JavaScript code.
        
        JavaScript must be enabled.
        
        :param expr: The JavaScript code to evaluate.
        :type expr: str
        :raise RuntimeError: If JavaScript is not enabled."""
        if self.html.javascript_enabled:
            if self.backend == "pythonmonkey":
                self._initialize_javascript()
                return pm.eval(expr)
            elif self.backend == "python":
                self._initialize_exec_context()
                if _locals is None: _locals = {}
                # Pass _locals. This is used to copy JavaScript 'this' behaviour.
                _exec_locals = _locals.copy()
                exec(expr, self._globals, _exec_locals)
                for name in _exec_locals.keys() - _locals.keys():
                    self._globals[name] = _exec_locals[name]
                return
        else:
            raise RuntimeError("JavaScript support must be enabled to run JavaScript")
        
    def _initialize_javascript(self):
        global pm
        if pm is None:
            try:
                import pythonmonkey as pm
                self.register("document", self.document)
            except ModuleNotFoundError:
                raise ModuleNotFoundError("PythonMonkey is required to run JavaScript files but is not installed.")
            
    def _initialize_exec_context(self):
        if not hasattr(self, "_globals"):
            self._globals = {
                # Full builtins are intentionally exposed. Execution is trusted.
                "__builtins__": __builtins__,
                "document": self.document,
            }

    def _on_script(self, attributes, tag_contents):
        try:
            tag_contents = dedent(tag_contents).strip()
            self.eval(tag_contents)
        except Exception as error:
            if self.backend == "python": error = format_exc()
            if "src" in attributes:
                self.html.post_message(f"ERROR: the JavaScript interpreter encountered an error while running the script from {attributes['src']}: {error}")
            else:
                self.html.post_message(f"ERROR: the JavaScript interpreter encountered an error while running the script \n\"{utilities.shorten(tag_contents)}\":\n{error}")

    def _on_element_script(self, node_handle, attribute, attr_contents):
        try:
            element = dom.HTMLElement(self.document, node_handle)
            if self.backend == "pythonmonkey":
                # Note: if anyone tries to run a function named TkinterWeb_JSEngine_run (unlikely); this will throw up.
                self.eval(f"(element) => {{function TkinterWeb_JSEngine_run() {{ {attr_contents} }}; TkinterWeb_JSEngine_run.bind(element)()}}")(element)
            elif self.backend == "python":
                self.eval(attr_contents, {"this": element})
        except Exception as error:
            if self.backend == "python": error = format_exc()
            self.html.post_message(f"ERROR: the JavaScript interpreter encountered an error while running an {attribute} script: {error}")
