"""
TkinterWeb v3.23
This is a wrapper for the Tkhtml3 widget from http://tkhtml.tcl.tk/tkhtml.html, 
which displays styled HTML documents in Tkinter.

Copyright (c) 2023 Andereoo

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

from PIL import Image, ImageOps, ImageFont, ImageDraw
from PIL.ImageTk import PhotoImage

try:
    from tkinter import PhotoImage as TkinterPhotoImage
except ImportError:
    from Tkinter import PhotoImage as TkinterPhotoImage
try:
    from io import BytesIO
except ImportError:
    import BytesIO
try:
    import cairo
    cairoimport = True
except ImportError:
    cairoimport = False
    rsvgimport = None
else:
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
            width, height = font.getsize(alt)
    else:
        width, height = font.getsize(alt)
    image = Image.new('RGBA', (width, height))
    draw = ImageDraw.Draw(image)
    draw.text((0,0), alt, fill=(0, 0, 0), font=font)
    image = PhotoImage(image, name=name)
    return image

def newimage(data, name, imagetype, invert):
    image = None
    error = None
    if "svg" in imagetype:
        if not cairoimport:
            error = "pycairo"
        elif not rsvgimport:
            error = "rsvg"
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
            image = PhotoImage(name=name, data=png_io.getvalue())
        elif rsvgimport == 'rsvg':
            svg = rsvg.Handle(data=data)
            img = cairo.ImageSurface(
                cairo.FORMAT_ARGB32, svg.props.width, svg.props.height)
            ctx = cairo.Context(img)
            svg.render_cairo(ctx)
            png_io = BytesIO()
            img.write_to_png(png_io)
            svg.close()
            image = PhotoImage(name=name, data=png_io.getvalue())
        elif rsvgimport == 'cairosvg':
            image_data = cairosvg.svg2png(bytestring=data)
            image = Image.open(BytesIO(image_data))
            image = PhotoImage(image, name=name)
        else:
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
        image = PhotoImage(image=image, name=name)
    elif imagetype == "image/png" or imagetype == "image/gif" or imagetype == "image/ppm" or imagetype == "image/bmp":
        image = TkinterPhotoImage(name=name, data=data)
    else:
        image = PhotoImage(data=data, name=name)

    return image, error

def blankimage(name):
    image = Image.new("RGBA", (1, 1))
    image = PhotoImage(image, name=name)
    return image
