"""
Generate Tk images and alt text

Copyright (c) 2021-2025 Andereoo
"""

from tkinter import PhotoImage as TkPhotoImage
from sys import modules
from io import BytesIO

# Some folks only use TkinterWeb as a fancy label widget and don't need to load images
# Or, if they do load images, they don't need support for images not supported by Tk
# We only import PIL if/when needed
# On my machine this reduces initial load time by up to a third
# The same applies to alt-text and image inversion imports

try:
    import cairo
    import rsvg
    rsvgimport = "rsvg"
except ImportError:
    try:
        import cairosvg
        rsvgimport = "cairosvg"
    except (ImportError, FileNotFoundError, OSError,):
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
    from PIL import Image, ImageTk, ImageDraw, ImageFont

    font = ImageFont.truetype(font_type, font_size)

    # Determine width and height based on nodebox or text size
    if len(nodebox) == 4:
        width = nodebox[2] - nodebox[0]
        height = nodebox[3] - nodebox[1]
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
    draw.text((0, 0), alt, fill=(0, 0, 0), font=font)
    photo_image = ImageTk.PhotoImage(image, name=name)
    return photo_image


def is_mostly_one_color(image, tolerance=30):
    from collections import Counter

    # Resize for performance
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
    # Import PIL modules only when needed
    from PIL import Image, ImageTk

    image = None
    if "svg" in imagetype:
        if rsvgimport == 'girsvg':
            from gi.repository import cairo, Rsvg
            handle = Rsvg.Handle()
            svg = handle.new_from_data(data.encode("utf-8"))
            dim = svg.get_dimensions()
            img = cairo.ImageSurface(cairo.FORMAT_ARGB32, dim.width, dim.height)
            ctx = cairo.Context(img)
            svg.render_cairo(ctx)
            png_io = BytesIO()
            img.write_to_png(png_io)
            svg.close()
            image = Image.open(png_io)
            photoimage = TkPhotoImage(image, name=name)
        elif rsvgimport == 'rsvg':
            import cairo  # Ensure cairo is imported
            handle = rsvg.Handle(data=data)
            svg_width = handle.props.width
            svg_height = handle.props.height
            img = cairo.ImageSurface(cairo.FORMAT_ARGB32, svg_width, svg_height)
            ctx = cairo.Context(img)
            handle.render_cairo(ctx)
            png_io = BytesIO()
            img.write_to_png(png_io)
            handle.close()
            image = Image.open(png_io)
            photoimage = TkPhotoImage(image, name=name)
        elif rsvgimport == 'cairosvg':
            import cairosvg
            image_data = cairosvg.svg2png(bytestring=data)
            image = Image.open(BytesIO(image_data))
            photoimage = TkPhotoImage(image, name=name)
        else:
            photoimage = None
    elif invert:
        from PIL import Image
        image = invert_image(Image.open(BytesIO(data)), limit)
        photoimage = TkPhotoImage(image=image, name=name)
    elif imagetype in frozenset({"image/png", "image/gif", "image/ppm", "image/pgm"}):
        # tkinter.PhotoImage has less overhead, so use it when possible
        photoimage = TkPhotoImage(name=name, data=data)
    else:
        # Fallback
        photoimage = ImageTk.PhotoImage(data=data, name=name)
    return photoimage


def blank_image(name):
    if "PIL" in modules:
        from PIL import Image, ImageTk
        return ImageTk.PhotoImage(Image.new("RGBA", (1, 1)), name=name)
    else: return TkPhotoImage(name=name)


def create_RGB_image(data, w, h):
    from PIL import Image
    image = Image.new("RGB", (w, h))
    for y, row in enumerate(data):
        for x, hexc in enumerate(row.split()):
            rgb = tuple(int(hexc[1:][i:i+2], 16) for i in (0, 2, 4))
            image.putpixel((x, y), rgb)
    return image
