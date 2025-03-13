"""
Generate Tk images and alt text

Copyright (c) 2025 Andereoo
"""

from PIL import Image
from PIL.ImageTk import PhotoImage
from tkinter import PhotoImage as TkinterPhotoImage
from io import BytesIO

cairo = None
try:
    import cairo
    import rsvg
    rsvgimport = "rsvg"
except ImportError:
    try:
        import cairosvg
        rsvgimport = "cairosvg"
    except (ImportError, FileNotFoundError,):
        try:
            import gi
            gi.require_version('Rsvg', '2.0')
            from gi.repository import Rsvg
            if not cairo:
                gi.require_version('cairo', '1.0')
                from gi.repository import cairo
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

def is_mostly_one_color(image, tolerance=30):
    from collections import Counter

    pixels = list(image.resize((100, 100), Image.Resampling.NEAREST).getdata())
    counter = Counter(pixels)
    dominant_color = max(counter, key=counter.get)
    def is_similar(c1, c2):
        return sum(abs(a - b) for a, b in zip(c1, c2)) < tolerance * 3
    similar_count = sum(1 for p in pixels if is_similar(p, dominant_color))
    ratio = similar_count / len(pixels)

    return ratio, dominant_color

def invert_image(image, limit):
    from PIL import ImageOps

    if image.mode in {'RGBA', 'LA', 'P'}:
        image = image.convert("RGBA")
        white_bg = Image.new("RGB", image.size, (255, 255, 255))
        white_bg.paste(image, mask=image.split()[3])
        ratio, dominant_color = is_mostly_one_color(white_bg)
        if ratio >= 0.5 and all(i > limit for i in dominant_color):
            r, g, b, a = image.split()
            rgb_image = Image.merge('RGB', (r, g, b))
            ratio, dominant_color = is_mostly_one_color(rgb_image)
            inverted_rgb = ImageOps.invert(rgb_image)
            r2, g2, b2 = inverted_rgb.split()
            image = Image.merge('RGBA', (r2, g2, b2, a))
        return image
    else:
        image = image.convert("RGB")
        ratio, dominant_color = is_mostly_one_color(image)
        if ratio >= 0.5 and all(i > limit for i in dominant_color):
            image = ImageOps.invert(image)
        return image

def data_to_image(data, name, imagetype, invert, limit):
    image = None
    if "svg" in imagetype:
        if rsvgimport == 'girsvg':
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
    elif invert:
        image = invert_image(Image.open(BytesIO(data)), limit)
        photoimage = PhotoImage(image=image, name=name)
    elif imagetype in ("image/png", "image/gif", "image/ppm", "image/pgm",):
        # tkinter.PhotoImage has less overhead, so use it when possible
        photoimage = TkinterPhotoImage(name=name, data=data)
    else:
        photoimage = PhotoImage(data=data, name=name)

    return photoimage

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