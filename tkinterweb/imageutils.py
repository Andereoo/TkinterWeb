"""
Generate Tk images and alt text

Copyright (c) 2021-2025 Andrew Clarke
"""

from tkinter import PhotoImage as TkPhotoImage

# Some folks only use TkinterWeb as a fancy label widget and don't need to load images
# Or, if they do load images, they don't need support for images not supported by Tk
# We only import PIL if/when needed
# On my machine this reduces initial load time by up to a third
# The same applies to alt-text and image inversion imports

# For the same reasons as above, we only attempt to load Cairo when needed
# Additionally, CairoSVG will only detect TkinterWeb-Tkhtml's Cairo binary after Tkhtml is loaded 
rsvg_type = None


def load_cairo():
    global rsvg_type
    if rsvg_type == None:
        try:
            import cairo
            globals()['cairo'] = cairo
            import rsvg
            globals()['rsvg'] = rsvg
            rsvg_type = 1
        except ImportError:
            try:
                import cairosvg as cairo
                globals()['cairo'] = cairo
                rsvg_type = 2
            except (ImportError, FileNotFoundError, OSError,):
                import gi
                gi.require_version('Rsvg', '2.0')
                from gi.repository import Rsvg as rsvg
                globals()['rsvg'] = rsvg
                # Don't import PyGobject's Cairo if PyCairo has already been imported
                if not cairo:
                    gi.require_version('cairo', '1.0')
                    from gi.repository import cairo
                    globals()['cairo'] = cairo
                rsvg_type = 3


def photoimage_del(image):
    "Monkey-patch to quiet Photoimage error messages. I think it's a PIL bug."
    try:
        name = image.__photo.name
        image.__photo.name = None
        image.__photo.tk.call("image", "delete", name)
    except AttributeError:
        pass


def text_to_image(name, alt, nodebox, font_type, font_size, threshold):
    from PIL import Image
    from PIL.ImageTk import PhotoImage
    from PIL import ImageFont, ImageDraw

    if PhotoImage.__del__ is not photoimage_del:
        PhotoImage.__del__ = photoimage_del

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

def invert_image(image, limit):
    from PIL import Image, ImageOps
    from collections import Counter
    from io import BytesIO

    def is_mostly_one_color(image, tolerance=30):
        pixels = list(image.resize((100, 100), Image.Resampling.NEAREST).getdata())
        counter = Counter(pixels)
        dominant_color = max(counter, key=counter.get)
        def is_similar(c1, c2):
            return sum(abs(a - b) for a, b in zip(c1, c2)) < tolerance * 3
        similar_count = sum(1 for p in pixels if is_similar(p, dominant_color))
        ratio = similar_count / len(pixels)
        return ratio, dominant_color
    image = Image.open(BytesIO(image))

    if image.mode not in {'RGBA', 'LA', 'P'} or "transparent" in image.info or "transparency" in image.info:
        image = image.convert("RGBA")
        white_bg = Image.new("RGB", image.size, (255, 255, 255))
        white_bg.paste(image, mask=image.split()[3])
        ratio, dominant_color = is_mostly_one_color(white_bg)
        if ratio >= 0.5 and sum(dominant_color) > limit:
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
        if ratio >= 0.5 and sum(dominant_color) > limit:
            image = ImageOps.invert(image)
        return image


def svg_to_png(data):
    load_cairo()
    if rsvg_type == 1 or rsvg_type == 3:
        from io import BytesIO
        if rsvg_type == 1:
            svg = rsvg.Handle(data=data)
            img = cairo.ImageSurface(
                cairo.FORMAT_ARGB32, svg.props.width, svg.props.height)
        else:
            handle = rsvg.Handle()
            svg = handle.new_from_data(data.encode("utf-8"))
            dim = svg.get_dimensions()
            img = cairo.ImageSurface(
                cairo.FORMAT_ARGB32, dim.width, dim.height)
        ctx = cairo.Context(img)
        svg.render_cairo(ctx)
        png_io = BytesIO()
        img.write_to_png(png_io)
        svg.close()
        return png_io.getvalue()
    else:
        return cairo.svg2png(bytestring=data)


def data_to_image(data, name, imagetype, data_is_image):
    if data_is_image:
        from PIL import Image
        from PIL.ImageTk import PhotoImage
        
        if PhotoImage.__del__ is not photoimage_del:
            PhotoImage.__del__ = photoimage_del

        return PhotoImage(image=data, name=name)
    elif imagetype in ("image/png", "image/gif", "image/ppm", "image/pgm",):
        # tkinter.PhotoImage has less overhead, so use it when possible
        return TkPhotoImage(data=data, name=name)
    else:
        from PIL import Image
        from PIL.ImageTk import PhotoImage

        if PhotoImage.__del__ is not photoimage_del:
            PhotoImage.__del__ = photoimage_del
        
        return PhotoImage(data=data, name=name)


def blank_image(name): 
    return TkPhotoImage(name=name)


def create_RGB_image(data, w, h):
    from PIL import Image
    
    image = Image.new("RGB", (w, h))
    for y, row in enumerate(data):
        for x, hexc in enumerate(row.split()):
            rgb = tuple(int(hexc[1:][i:i+2], 16) for i in (0, 2, 4))
            image.putpixel((x, y), rgb)
    return image
