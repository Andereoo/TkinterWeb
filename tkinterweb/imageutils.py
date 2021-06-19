from PIL import Image
from PIL.ImageTk import PhotoImage

try:
    from tkinter import PhotoImage as TkinterPhotoImage
except ImportError:
    from Tkinter import PhotoImage as TkinterPhotoImage

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
    if rsvgimport:
        try:
            from io import BytesIO
        except ImportError:
            import BytesIO


def newimage(data, name, imagetype):
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
    elif imagetype == "image/png" or imagetype == "image/gif" or imagetype == "image/ppm" or imagetype == "image/bmp":
        image = TkinterPhotoImage(name=name, data=data)
    else:
        image = PhotoImage(name=name, data=data)

    return image, error

def blankimage(name):
    image = Image.new("RGBA", (1, 1))
    image = PhotoImage(image, name=name)
    return image
