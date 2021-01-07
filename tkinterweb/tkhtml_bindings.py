import sys
import os.path
import platform
import traceback

from PIL import ImageTk, Image

try:
    from urllib.request import Request, urlopen
except ImportError: # Python 2
    from urllib2 import urlopen, Request
try:
    from urllib.parse import urlparse, urljoin
except ImportError: # Python 2
    from urlparse import urlparse, urljoin
try:
    import tkinter as tk
    from tkinter import ttk
except ImportError: # Python 2
    import Tkinter as tk
    import ttk



try:
    import cairo
    cairoimport = True
except ImportError:
    cairoimport = False
try:
    import rsvg
    rsvgimport = "rsvg"
except ImportError:
    try:
        import cairosvg
        rsvgimport = "cairosvg"
    except ImportError:
        try:
            import gi
            try:
                gi.require_version('Rsvg', '1.0')
            except:
                gi.require_version('Rsvg', '2.0')
            from gi.repository import Rsvg
            rsvgimport = "girsvg"
        except:
            rsvgimport = None
if cairoimport and rsvgimport:
    try:
        from io import BytesIO
    except ImportError:
        import BytesIO


_tkhtml_loaded = False


def load_tkhtml(master, location=None):
    """Load nessessary Tkhtml files"""
    global _tkhtml_loaded
    if not _tkhtml_loaded:
        if location:
            master.tk.eval("global auto_path; lappend auto_path {%s}" % location)
        master.tk.eval("package require Tkhtml")
        _tkhtml_loaded = True

def get_tkhtml_folder():
    """Fetch the Tkhtml3 folder for the current platform"""
    return os.path.join (os.path.abspath(os.path.dirname(__file__)),"tkhtml",
                         platform.system().replace("Darwin", "MacOSX"),
                         "64-bit" if sys.maxsize > 2**32 else "32-bit")

class TkinterWeb(tk.Widget):
    "Tkhtml3 widget bindings"
    def __init__(self, master, message_func, cfg={}, **kw):
        # widget settings
        self.stylesheets_enabled = True
        self.images_enabled = True
        self._base_url = ""
        self.currently_hovered_node = ""
        self.visited_links = []
        self._recursive_hovering_count = 15
        self._recursive_link_count = 15
        self._message_func = message_func
        self._title_change_func = lambda title:None
        self._cursor_change_func = lambda url:None
        self._link_click_func = lambda url:None
        self.cursors = {
          "crosshair": "crosshair",
          "default": "",
          "pointer": "hand2",
          "move": "fleur",
          "text": "xterm",
          "wait": "watch",
          "progress": "box_spiral",
          "help": "question_arrow",
          "none": "none",
        }
        
        # widget status variables
        self._style_count = 0
        self._prev_hovered_nodes = []
        self._prev_active_node = [None, True]
        self._prev_cursor = ""
        
        # handle image loading        
        img=Image.open((os.path.dirname(__file__)+'/images/broken_image.png'))
        self._broken_image = img.resize((25,30))
        
        if "imagecmd" not in kw:
            kw["imagecmd"] = master.register(self._fetch_image)
            
        # load the Tkhtml3 widget
        self._message_func(("Fetching Tkhtml3 for %s %s with Python %s." % ("64-bit" if sys.maxsize > 2**32 else "32-bit", platform.system().replace("Darwin", "MacOSX"), str(sys.version_info[0:3]).replace(", ", ".").replace(")", "").replace("(", ""))),
                   "Tkhtml found in %s." % get_tkhtml_folder())
        load_tkhtml(master, get_tkhtml_folder())
        tk.Widget.__init__(self, master, "html", cfg, kw)
        
        # enable text selection, image loading, and pseudo-element flagging
        self._selection_start_node = None
        self._selection_start_offset = None
        self._selection_end_node = None
        self._selection_end_offset = None
        self.bind("<B1-Motion>", self._extend_selection, True)
        self.bind("<<Copy>>", self.copy_selection_to_clipboard, True)
        self.bind("<Button-1>", self._on_click, True)
        self.bind("<ButtonRelease-1>", self._on_click_release, True)
        self.bind("<Motion>", self._mouse_motion, True)
        self._image_name_prefix = str(id(self)) + "_img_"
        self._images = set() # to avoid python garbage collector from stealing images
        
        # handle tags
        self.tk.call(self._w, "handler", "script", "script", self.register(self._on_script))
        self.tk.call(self._w, "handler", "script", "style", self.register(self._on_style))
        self.tk.call(self._w, "handler", "node", "link", self.register(self._on_link))
        self.tk.call(self._w, "handler", "node", "title", self.register(self._on_title))
        self.tk.call(self._w, "handler", "node", "a", self.register(self._on_a))
        self.tk.call(self._w, "handler", "node", "base", self.register(self._on_base))

    def node(self, *arguments):
        """Retrieve one or more document
        node handles from the current document."""
        return self.tk.call(self._w, "node", *arguments)

    def parse(self, *args):
        """Parse HTML code"""
        self._prev_hovered_nodes = []
        self.tk.call(self._w, "parse", *args)
        if self.stylesheets_enabled:
            self.parse_css("a:active{color:red; cursor:pointer;}")

    def parse_css(self, *args):
        """Parse CSS code"""
        self.tk.call(self._w, "style", *args)
        
    def reset(self):
        """Reset the widget"""
        self._link_ids = {}
        return self.tk.call(self._w, "reset")

    def tag(self, subcommand, tag_name, *arguments):
        """Return the name of the Html tag that generated this
        document node, or an empty string if the node is a text node. """
        return self.tk.call(self._w, "tag", subcommand, tag_name, *arguments)

    def search(self, selector):
        """Search the document for the specified CSS
        selector; return a Tkhtml3 node if found."""
        return self.tk.call(self._w, "search", selector)

    def text(self, *args):
        """Enable interaction with the text of the HTML document."""
        return self.tk.call(self._w, "text", *args)

    def xview(self, *args):
        """Used to control horizontal scrolling."""
        if args: return self.tk.call(self._w, "xview", *args)
        coords = map(float, self.tk.call(self._w, "xview").split())
        return tuple(coords)

    def xview_moveto(self, fraction):
        """Adjusts horizontal position of the widget so that fraction
        of the horizontal span of the document is off-screen to the left.
        """
        return self.xview("moveto", fraction)

    def xview_scroll(self, number, what):
        """Shifts the view in the window according to number and what;
        number is an integer, and what is either "units" or "pages".
        """
        return self.xview("scroll", number, what)

    def yview(self, *args):
        """Used to control the vertical position of the document."""
        if args: return self.tk.call(self._w, "yview", *args)
        coords = map(float, self.tk.call(self._w, "yview").split())
        return tuple(coords)

    def yview_name(self, name):
        """Adjust the vertical position of the document so that the tag
        <a name=NAME...> is visible and preferably near the top of the window.
        """
        return self.yview(name)

    def yview_moveto(self, fraction):
        """Adjust the vertical position of the document so that fraction of
        the document is off-screen above the visible region.
        """
        return self.yview("moveto", fraction)

    def yview_scroll(self, number, what):
        """Shifts the view in the window up or down, according to number and
        what. "number" is an integer, and "what" is either "units" or "pages".
        """
        return self.yview("scroll", number, what)

    def _on_script(self, *args):
        """Currently just ignoring script"""
        
    def _on_style(self, attributes, tagcontents):
        """Handle <style> elements"""
        if not self.stylesheets_enabled:
            return
        self._style_count += 1
        ids = "author."+ str(self._style_count).zfill(4)
        handler_proc = self.register(lambda new_url, parent_url=self._base_url: self._on_at_import(parent_url, new_url))
        self.parse_css("-id", ids+".9999", "-importcmd", handler_proc, tagcontents)
        self._message_func("Finished loading <style> element.", "")

    def _on_link(self, node):
        """Load <link> elements"""
        if not self.stylesheets_enabled:
            return
        try:
            rel = self._get_node_attr(node, "rel")
        except tk.TclError:
            return
        if rel == "stylesheet":
            try:
                url = urljoin(self._base_url, self._get_node_attr(node, "href"))
                urldata = urlopen(Request(url, headers={"User-Agent": "Mozilla"})).read().decode()
                self._style_count += 1
                ids = "author."+ str(self._style_count).zfill(4)
                handler_proc = self.register(lambda new_url, parent_url=url: self._on_at_import(parent_url, new_url))
                self.parse_css("-id", ids+".9999", "-importcmd", handler_proc, urldata)
                self._message_func("Finished loading stylesheet.", "Sheet found at "+url+".")
            except Exception as e:
                self._message_func("Error reading stylesheet.", "Url: "+self._get_node_attr(node, "href")+".")

    def _on_at_import(self, parent_url, new_url):
        """Load @import scripts"""
        try:
            self._style_count += 1
            url = urljoin(parent_url, new_url)
            urldata = urlopen(Request(url, headers={"User-Agent": "Mozilla"})).read().decode()
            ids = "author."+ str(self._style_count).zfill(4)
            handler_proc = self.register(lambda new_url, parent_url=url: self._on_at_import(parent_url, new_url))             
            self.parse_css("-id", ids+".9999", "-importcmd", handler_proc, urldata)
            self._message_func("Finished loading stylesheet.", "Sheet found at "+url+".")
        except Exception:
            self._message_func("Error reading stylesheet.", "Url: "+new_url+".")

    def _on_title(self, node):
        """Handle <title> elements"""
        for child in (self.tk.call(node, "children")):
            self._title_change_func(self.tk.call(child, "text"))

    def _on_base(self, node):
        """Handle <base> elements"""
        try:
            href = self._get_node_attr(node, "href")
            self._base_url = href
        except Exception:
            self._message_func("Error setting base url.", "A <base> element has been found without an href attribute.")

    def _on_a(self, node):
        """Handle <a> elements"""
        self.tk.call(node, "dynamic", "set", "link")
        try:
            href = self._get_node_attr(node, "href")
            url = urljoin(self._base_url, href)
            if url in self.visited_links:
                self.tk.call(node, "dynamic", "set", "visited")
        except tk.TclError:
            pass

    def _attach_broken_image(self, name):
        """Attach the broken image icon"""
        self._message_func("File is not supported yet.", "")
        self._images.add(ImageTk.PhotoImage(self._broken_image, name=name))

    def _attach_image(self, url, name, urltype):
        """Attach images using the specified url"""
        path=urlparse(url).path
        self._message_func(("Fetching image data."), ("Pasting image: %s" % url))
        if path.endswith('.svg') == True: 
            if not cairoimport:
                self._message_func(('TKhtml requires Pycairo to parse .svg files.'), ('Consider installing it as it is not found on your path.'))
            if not rsvgimport:
                self._message_func(('TKhtml requires some version of rsvg to parse .svg files.'), ('Consider installing it as it is not found on your path.'))
            try:
                code=urlopen(Request(url, headers={"User-Agent": "Mozilla"})).read().decode()
                if rsvgimport== 'girsvg':
                    handle = Rsvg.Handle()
                    svg = handle.new_from_data(code.encode("utf-8"))
                    dim = svg.get_dimensions()
                    img = cairo.ImageSurface(cairo.FORMAT_ARGB32, dim.width, dim.height)
                    ctx = cairo.Context(img)
                    svg.render_cairo(ctx)
                    png_io = BytesIO()
                    img.write_to_png(png_io)
                    svg.close()
                    self._images.add(ImageTk.PhotoImage(name=name, data=png_io.getvalue()))
                elif rsvgimport == 'rsvg':
                    svg = rsvg.Handle(data=code)
                    img = cairo.ImageSurface(cairo.FORMAT_ARGB32,svg.props.width,svg.props.height)
                    ctx = cairo.Context(img)
                    svg.render_cairo(ctx)
                    png_io = BytesIO()
                    img.write_to_png(png_io)
                    svg.close()
                    self._images.add(ImageTk.PhotoImage(name=name, data=png_io.getvalue()))
                elif rsvgimport == 'cairosvg':
                    image_data = cairosvg.svg2png(bytestring=code)
                    image = Image.open(BytesIO(image_data))
                    tk_image = ImageTk.PhotoImage(image)                    
                    self._images.add(tk_image)
                else:
                    self._attach_broken_image(name)
            except Exception as e:
                self._attach_broken_image(name)
        else:
            try:
                with urlopen(Request(url, headers={"User-Agent": "Mozilla"})) as handle:
                    data = handle.read()
                self._images.add(ImageTk.PhotoImage(name=name, data=data))
            except Exception:
                self._attach_broken_image(name)


    def _fetch_image(self, *args):
        """Fetch images"""
        if not self.images_enabled:
            return
        assert len(args) == 1
        url = args[0]
        url = urljoin(self._base_url, url)
        name = self._image_name_prefix + str(len(self._images))
        self._attach_image(url, name, url)
        return name

    def _get_node_text(self, node_handle):
        """Get the text content of the given node_handle"""
        return self.tk.call(node_handle, "text")

    def _get_node_tag(self, node_handle):
        """Get the HTML tag of the given node_handle"""
        return self.tk.call(node_handle, "tag")

    def _get_node_parent(self, node_handle):
        """Get the parent of the given node_handle"""
        return self.tk.call(node_handle, "parent")

    def _get_node_attr(self, node_handle, attribute):
        """Get the specified attribute of the given node_handle"""
        return self.tk.call(node_handle, "attribute", attribute)

    def _on_click(self, event):
        """Set active element flags"""
        self._start_selection(event)
        try:
            node_handle, offset = self.node(True, event.x, event.y)
        except ValueError:
            self._selection_start_node = None
            return

        if self.stylesheets_enabled:
            try:
                self.tk.call(node_handle, "dynamic", "set", "active")
                self._prev_active_node = [node_handle, True]
            except Exception:
                try:
                    node_handle = self._get_node_parent(node_handle)
                    self.tk.call(node_handle, "dynamic", "set", "active")
                    self._prev_active_node = [node_handle, False]
                except Exception:
                    pass

    def _handle_link_click(self, node_handle):
        """Handle link clicks"""
        href = self._get_node_attr(node_handle, "href")
        url = urljoin(self._base_url, href)
        self._message_func(('Link clicked.'), ('Url: '+url+'.'))
        self.visited_links.append(url)
        self._link_click_func(url)

    def _on_click_release(self, event):
        """Handle click releases on <a> nodes"""
        if self._prev_active_node is not None:
            if self.stylesheets_enabled:
                self.tk.call(self._prev_active_node[0], "dynamic", "clear", "active")
        try:
            node_handle, offset = self.node(True, event.x, event.y)

            if self.stylesheets_enabled:
                done = False
                if self._get_node_tag(node_handle) == "a":
                    if node_handle == self._prev_active_node[0]:
                        self._handle_link_click(node_handle)
                        done = True
                elif self._get_node_parent(node_handle) == self._prev_active_node[0]:
                    if self._get_node_tag(self._get_node_parent(node_handle)) == "a":
                        self._handle_link_click(self._get_node_parent(node_handle))
                        done = True
                if not done:                
                    count = 0
                    for i in self._prev_hovered_nodes:
                        if self._get_node_tag(i) == "a":
                            self._handle_link_click(i)
                            break
                        elif count >= 10:
                            #If the tenth parent of the clicked element still isn't an <a> element,
                            #we will likely not ever find one. Time to quit checking.
                            break
            else:
                if self._get_node_tag(node_handle) == "a":
                    self._handle_link_click(node_handle)
                elif self._get_node_tag(self._get_node_parent(node_handle)) == "a":
                    self._handle_link_click(self._get_node_parent(node_handle))
        except Exception:
            pass

        if self._prev_active_node is not None:
            if self.stylesheets_enabled:
                self._prev_active_node = [None, True]

    def _change_cursor(self, node_handle):
        """Handle CSS 'cursor' property"""
        try:
            cursor = self.tk.call(node_handle, "property", "cursor")
            cursor = self.cursors[cursor]
            if self._prev_cursor != cursor:
                self._cursor_change_func(cursor=cursor)
                self._prev_cursor = cursor
        except KeyError:
            try:
                cursor = self.tk.call(self._get_node_parent(node_handle), "property", "cursor")
                cursor = self.cursors[cursor]
                if self._prev_cursor != cursor:
                    self._cursor_change_func(cursor=cursor)
                    self._prev_cursor = cursor
            except KeyError:
                if self._get_node_tag(node_handle) == "":
                    if self._prev_cursor != "text":
                        cursor = self.cursors["text"]
                        self._cursor_change_func(cursor=cursor)
                        self._prev_cursor = cursor
                else:
                    if self._prev_cursor != "":
                        self._cursor_change_func(cursor="")
                        self._prev_cursor = ""
        
    def _mouse_motion(self, event):
        """Set hover flags and handle the CSS 'cursor' property"""
        try:
            node_handle, offset = self.node(True, event.x, event.y)
        except ValueError:
            return

        self.currently_hovered_node = node_handle

        self._change_cursor(node_handle)        

        if self.stylesheets_enabled:
            try:
                if node_handle != self._prev_hovered_nodes[0]:
                    if self._prev_hovered_nodes != []:
                        for node in self._prev_hovered_nodes:
                            self.tk.call(node, "dynamic", "clear", "hover")
                    self.tk.call(node_handle, "dynamic", "set", "hover")
                    self._prev_hovered_nodes = node_handle
            except Exception:
                try:
                    node_handle = self._get_node_parent(node_handle)
                    if node_handle != self._prev_hovered_nodes[0]:
                        if self._prev_hovered_nodes != []:
                            for node in self._prev_hovered_nodes:
                                self.tk.call(node, "dynamic", "clear", "hover")
                        self.tk.call(node_handle, "dynamic", "set", "hover")
                        self._prev_hovered_nodes.append(node_handle)
                except Exception:
                    pass

            try:
                self._set_hover_recursively(self._get_node_parent(node_handle), self._recursive_hovering_count)
            except Exception:
                pass

    def _set_hover_recursively(self, node_handle, count):
        """Set hover flags to the parents of
        the hovered element as well"""
        try:
            self.tk.call(node_handle, "dynamic", "set", "hover")
            self._prev_hovered_nodes.append(node_handle)
        except Exception:
            pass
        try:
            if count >= 1:
                self._set_hover_recursively(self._get_node_parent(node_handle), count-1)
        except Exception:
            pass
                
    def _start_selection(self, event):
        """Make selection possible"""
        self.focus_set()
        self.tag("delete", "selection")
        try:
            self._selection_start_node, self._selection_start_offset = self.node(True, event.x, event.y)
        except ValueError:
            self._selection_start_node = None

    def _extend_selection(self, event):
        """Alter selection and HTML element states based on mouse movement"""
        self.tag("delete", "selection")
        if self._selection_start_node is None:
            return
        try:
            self._selection_end_node, self._selection_end_offset = self.node(True, event.x, event.y)
            self.tag("add", "selection", self._selection_start_node, self._selection_start_offset, self._selection_end_node, self._selection_end_offset)
            self.tag("configure", "selection", "-background", "#ff7043")
            if self.stylesheets_enabled:
                if self._prev_active_node[0] is not None:
                    if self._prev_active_node[-1]:
                        if self._prev_active_node[0] != self._selection_end_node:
                            self.tk.call(self._prev_active_node[0], "dynamic", "clear", "active")
                            if self._get_node_tag(self._selection_end_node) == "":
                                if self._prev_cursor != "text":
                                    cursor = self.cursors["text"]
                                    self._cursor_change_func(cursor=cursor)
                                    self._prev_cursor = cursor
                            else:
                                if self._prev_cursor != "":
                                    self._cursor_change_func(cursor="")
                                    self._prev_cursor = ""
                        else:
                            self.tk.call(self._prev_active_node[0], "dynamic", "set", "active")
                            self._change_cursor(self._prev_active_node[0])
                    else:
                        if self._prev_active_node[0] != self._get_node_parent(self._selection_end_node):
                            self.tk.call(self._prev_active_node[0], "dynamic", "clear", "active")
                            if self._get_node_tag(self._selection_end_node) == "":
                                if self._prev_cursor != "text":
                                    cursor = self.cursors["text"]
                                    self._cursor_change_func(cursor=cursor)
                                    self._prev_cursor = cursor
                            else:
                                if self._prev_cursor != "":
                                    self._cursor_change_func(cursor="")
                                    self._prev_cursor = ""
                        else:
                            self.tk.call(self._prev_active_node[0], "dynamic", "set", "active")
                            self._change_cursor(self._prev_active_node[0])                      
        except ValueError:
            self._selection_end_node = None

    def _ctrl_c(self, event):
        if self.focus_get() == self:
            self.copy_selection_to_clipboard()

    def _get_selected_text(self):
        """Return the text currently selected/highlighted"""
        if self._selection_start_node is None or self._selection_end_node is None:
            return
        start_index = self.text("offset", self._selection_start_node, self._selection_start_offset)
        end_index = self.text("offset", self._selection_end_node, self._selection_end_offset)
        if start_index > end_index:
            start_index, end_index = end_index, start_index
        whole_text = self.text("text")
        return whole_text[start_index:end_index]

    def copy_selection_to_clipboard(self, event=None):
        """Copy the selected text to the clipboard"""
        selected_text = self._get_selected_text()
        self.clipboard_clear()
        self.clipboard_append(selected_text)
        self._message_func('Text copied to clipboard.', selected_text)
