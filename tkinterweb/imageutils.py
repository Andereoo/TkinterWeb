"""
Generate Tk images and alt text

Copyright (c) 2025 Andereoo
"""

from PIL import Image
from PIL.ImageTk import PhotoImage
from tkinter import PhotoImage as TkinterPhotoImage
from io import BytesIO

try:
    import cairo
    cairoimport = True
except ImportError:
    try:
        import gi
        gi.require_version('cairo', '1.0')
        from gi.repository import cairo
        cairoimport = True
    except (ValueError, ImportError,):
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
            except (ValueError, ImportError,):
                rsvgimport = None

def text_to_image(name, alt, nodebox, font_type, font_size, threshold):
    from PIL import ImageFont, ImageDraw
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

def invert_image(image):
    from PIL import ImageOps
    if image.mode == 'RGBA':
        r,g,b,a = image.split()
        image = Image.merge('RGB', (r,g,b))
        image = ImageOps.invert(image)
        r2,g2,b2 = image.split()
        image = Image.merge('RGBA', (r2,g2,b2,a))
    else:
        image = image.convert("RGB")
        image = ImageOps.invert(image)
    return image

def data_to_image(data, name, imagetype, invert, return_image=False):
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
        image = invert_image(Image.open(BytesIO(data)))
        photoimage = PhotoImage(image=image, name=name)
    elif return_image:
        image = Image.open(BytesIO(data))
        photoimage = PhotoImage(image=image, name=name)
    elif imagetype in ("image/png", "image/gif", "image/ppm", "image/pgm",):
        # tkinter.PhotoImage has less overhead, so use it when possible
        photoimage = TkinterPhotoImage(name=name, data=data)
    else:
        photoimage = PhotoImage(data=data, name=name)

    if return_image:
        return photoimage, error, image
    else:
        return photoimage, error

def blank_image(name):
    image = Image.new("RGBA", (1, 1))
    image = PhotoImage(image, name=name)
    return image

def create_RGB_image(data, w, h):
    image = Image.new("RGB", (w, h))
    for y, row in enumerate(data):
        for x, hexc in enumerate(row.split()):
            rgb = tuple(int(hexc[1:][i:i+2], 16) for i in (0, 2, 4))
            image.putpixel((x, y), rgb)
    return image