"""
Generate Tk images and alt text

Copyright (c) 2025 Andereoo
"""

from PIL import Image, ImageOps, ImageFont, ImageDraw
from PIL.ImageTk import PhotoImage
from io import BytesIO

from tkinter import PhotoImage as TkinterPhotoImage
from tkinter import Label


try:
    import cairo
    cairoimport = True
except ImportError:
    try:
        import gi
        gi.require_version('cairo', '1.0')
        from gi.repository import cairo
        cairoimport = True
    except ImportError:
        cairoimport = False
        rsvgimport = None

if cairoimport:
    try:
        import rsvg
        rsvgimport = "rsvg"
    except ImportError:
        try:
            import cairosvg
            rsvgimport = "cairosvg"
        except (ImportError, FileNotFoundError):
            try:
                import gi
                try:
                    gi.require_version('Rsvg', '1.0')
                except:
                    gi.require_version('Rsvg', '2.0')
                from gi.repository import Rsvg
                rsvgimport = "girsvg"
            except Exception:
                rsvgimport = None

def textimage(name, alt, nodebox, font_type, font_size, threshold):
    font = ImageFont.truetype(font_type, font_size)
    if len(nodebox) == 4:
        width = nodebox[2]-nodebox[0]
        height = nodebox[3]-nodebox[1]
        if (width < threshold) or (height < threshold):
            try:
                width, height = font.getsize(alt)
            except AttributeError:
                left, top, right, bottom = font.getbbox(alt)
                width = right - left
                height = bottom
    else:
        try:
            width, height = font.getsize(alt)
        except AttributeError:
            left, top, right, bottom = font.getbbox(alt)
            width = right - left
            height = bottom
            
    image = Image.new('RGBA', (width, height))
    draw = ImageDraw.Draw(image)
    draw.text((0,0), alt, fill=(0, 0, 0), font=font)
    image = PhotoImage(image, name=name)
    return image

def newimage(data, name, imagetype, invert, return_image=False):
    image = None
    error = None
    if "svg" in imagetype:
        if not cairoimport:
            photoimage = None
            error = "no_pycairo"
        elif not rsvgimport:
            photoimage = None
            error = "no_rsvg"
        elif rsvgimport == 'girsvg':
            handle = Rsvg.Handle()
            svg = handle.new_from_data(data.encode("utf-8"))
            dim = svg.get_dimensions()
            img = cairo.ImageSurface(
                cairo.FORMAT_ARGB32, dim.width, dim.height)
            ctx = cairo.Context(img)
            svg.render_cairo(ctx)
            png_io = BytesIO()
            img.write_to_png(png_io)
            svg.close()
            image = Image.open(png_io)
            photoimage = PhotoImage(image, name=name)
        elif rsvgimport == 'rsvg':
            svg = rsvg.Handle(data=data)
            img = cairo.ImageSurface(
                cairo.FORMAT_ARGB32, svg.props.width, svg.props.height)
            ctx = cairo.Context(img)
            svg.render_cairo(ctx)
            png_io = BytesIO()
            img.write_to_png(png_io)
            svg.close()
            image = Image.open(png_io)
            photoimage = PhotoImage(image, name=name)
        elif rsvgimport == 'cairosvg':
            image_data = cairosvg.svg2png(bytestring=data)
            image = Image.open(BytesIO(image_data))
            photoimage = PhotoImage(image, name=name)
        else:
            photoimage = None
            error = "corrupt"
    elif invert:
        image = Image.open(BytesIO(data))
        if image.mode == 'RGBA':
            r,g,b,a = image.split()
            image = Image.merge('RGB', (r,g,b))
            image = ImageOps.invert(image)
            r2,g2,b2 = image.split()
            image = Image.merge('RGBA', (r2,g2,b2,a))
        else:
            image = image.convert("RGB")
            image = ImageOps.invert(image)
        photoimage = PhotoImage(image=image, name=name)
    elif return_image:
        image = Image.open(BytesIO(data))
        photoimage = PhotoImage(image=image, name=name)
    elif imagetype == "image/png" or imagetype == "image/gif" or imagetype == "image/ppm" or imagetype == "image/bmp":
        photoimage = TkinterPhotoImage(name=name, data=data)
    else:
        photoimage = PhotoImage(data=data, name=name)

    if return_image:
        return photoimage, error, image
    else:
        return photoimage, error

def blankimage(name):
    image = Image.new("RGBA", (1, 1))
    image = PhotoImage(image, name=name)
    return image

class ImageLabel(Label):
    def __init__(self, parent, error_func, *args, **kwargs):
        Label.__init__(self, parent, *args, **kwargs)

        self.html = parent
        self.original_image = None
        self.old_height = 0
        self.old_width = 0
        self.page_zoom = 1.0
        self.error_func = error_func

        self.image_padding = 10
    
    def set_zoom(self, multiplier):
        self.page_zoom = multiplier
        self.handle_resize(None, self.html.winfo_width(), self.html.winfo_height(), True)

    def load_image(self, newurl, data, filetype):
        try:
            self.image, error, self.current_image = newimage(data, None, filetype, self.html.image_inversion_enabled, True)
            if not self.image: # because load_image is called using after() to ensure thread safety, exceptions aren't caught
                self.error_func(newurl, "The image requested is either corrupt or not supported", "")
                return
            self.original_image = self.current_image
            self.original_width, self.original_height = self.original_image.size
            self.current_width, self.current_height = self.original_image.size

            self.config(image=self.image)
            self.handle_resize(None, self.html.winfo_width(), self.html.winfo_height(), True)
            self.html.bind("<Configure>", self.handle_resize)
        except Exception:
            self.error_func(newurl, "The image requested is either corrupt or not supported", "")

    def reset(self):
        if self.original_image:
            self.original_image = None
            self.html.unbind("<Configure>")

    def handle_resize(self, event, width=None, height=None, force=False):
        if not width:
            width = event.width
        if not height:
            height = event.height

        if height > self.image_padding+5 and width > self.image_padding+5 and self.original_image:
            if force or height != self.old_height or width != self.old_width:
                self.configure(height=height)
                self.configure(width=width)
                self.old_height = height
                self.old_width = width

                if self.old_width < self.original_width * self.page_zoom or self.old_height < self.original_height * self.page_zoom:
                    scale_factor = min(self.old_width / self.original_width, self.old_height / self.original_height)
                    new_width = int(float(self.original_width) * scale_factor)
                    new_height = int(float(self.original_height) * scale_factor)
                    current_image = self.original_image.resize((new_width - self.image_padding, new_height - self.image_padding), Image.NEAREST)
                    self.current_width = new_width
                    self.current_height = new_height
                    self.image = PhotoImage(current_image)
                    self.config(image=self.image)
                elif force or self.current_width != self.original_width or self.current_height != self.original_height:
                    new_width = int(float(self.original_width) * self.page_zoom)
                    new_height = int(float(self.original_height) * self.page_zoom)
                    current_image = self.original_image.resize((new_width - self.image_padding, new_height - self.image_padding), Image.NEAREST)
                    self.current_width = self.original_width
                    self.current_height = self.original_height
                    self.image = PhotoImage(current_image)
                    self.config(image=self.image)