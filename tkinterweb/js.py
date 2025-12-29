"""
A simple JavaScript-Tkhtml bridge.
Copyright (c) 2021-2025 Andrew Clarke
"""

from . import dom

# JavaScript is experimental and not used by everyone
# We only import PythonMonkey if/when needed
pythonmonkey = None

class JSEngine:
    """Access this class via the :attr:`~tkinterweb.HtmlFrame.javascript` property of the :class:`~tkinterweb.HtmlFrame` and :class:`~tkinterweb.HtmlLabel` widgets.

    New in version 4.12.
    
    :ivar html: The associated :class:`.TkinterWeb` instance.
    :ivar document: The associated :class:`.HTMLDocument` instance."""
    def __init__(self, html, document):
        self.html = html
        self.document = document

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
        if self.html.javascript_enabled:
            if not pythonmonkey:
                self._initialize_javascript()
            pythonmonkey.eval(f"(function(pyObj) {{globalThis.{name} = pyObj}})")(obj)
        else:
            raise RuntimeError("JavaScript support must be enabled to register a JavaScript object")
        
    def eval(self, expr):
        """Evaluate JavaScript code.
        
        JavaScript must be enabled.
        
        :param expr: The JavaScript code to evaluate.
        :type expr: str
        :raise RuntimeError: If JavaScript is not enabled."""
        if self.html.javascript_enabled:
            if not pythonmonkey:
                self._initialize_javascript()
            return pythonmonkey.eval(expr)
        else:
            raise RuntimeError("JavaScript support must be enabled to run JavaScript")
        
    def _initialize_javascript(self):
        global pythonmonkey
        try:
            import pythonmonkey
            self.register("document", self.document)
        except ModuleNotFoundError:
            raise ModuleNotFoundError("PythonMonkey is required to run JavaScript files but is not installed.")

    def _on_script(self, attributes, tag_contents):
        if self.html.javascript_enabled and not pythonmonkey:
            self._initialize_javascript()
        try:
            pythonmonkey.eval(tag_contents)
        except Exception as error:
            if "src" in attributes:
                self.html.post_message(f"ERROR: the JavaScript interpreter encountered an error while running the script from {attributes['src']}: {error}")
            else:
                self.html.post_message(f"ERROR: the JavaScript interpreter encountered an error while running a script: {error}")

    def _on_element_script(self, node_handle, attribute, attr_contents):
        if self.html.javascript_enabled and not pythonmonkey:
            self._initialize_javascript()
        try:
            element = dom.HTMLElement(self.document, node_handle)
            pythonmonkey.eval(f"(element) => {{function run() {{ {attr_contents} }}; run.bind(element)()}}")(element)
        except Exception as error:
            self.html.post_message(f"ERROR: the JavaScript interpreter encountered an error while running an {attribute} script: {error}")
