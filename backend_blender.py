try:
    import bpy
except:
    print("bpy not found")

from collections import OrderedDict
import six
import os
import numpy as np
from matplotlib import __version__, cbook
from matplotlib.backend_bases import FigureCanvasBase, FigureManagerBase, _Backend
from matplotlib.backends.backend_agg import FigureCanvasAgg, RendererAgg

def write_png(renderer, fh, dpi, metadata):

    # get filename and close file (open later)
    if hasattr(fh, "name"):
        filename = fh.name
        fh.close()
    else:
        print(fh)
        raise ValueError("Failed to determine filename.")
    nparray = renderer2nparray(renderer)

    nparray2blender(nparray, filename)

    # reopen file
    fh = cbook.open_file_cm(filename, "ab")
    return fh


def renderer2nparray(renderer):
    height, width = map(int,(renderer.height, renderer.width))

    buffer = renderer.buffer_rgba()
    nparray = np.frombuffer(buffer, dtype = np.uint8)/255
    channels = nparray.size//(width*height)
    nparray = nparray.reshape(height, width, channels)

    return nparray

def nparray2blender(nparray, filename):
    h, w, c = nparray.shape
    alpha = False if c == 3 else True
    b_img = bpy.data.images.new(filename+"saved", alpha=alpha, width = w,height = h)

    nparray = np.flip(nparray, axis = 0).flatten()
    b_img.pixels = nparray
    if os.path.isabs(filename):
        b_img.filepath_raw = filename
    else:
        b_img.filepath_raw = "//" + bpy.path.basename(filename)

    b_img.file_format = "PNG"
    b_img.save()
    bpy.data.images.remove(b_img)


class FigureCanvasBlender(FigureCanvasAgg):
    def print_png(self, filename_or_obj, *args, **kwargs):
        FigureCanvasAgg.draw(self)
        renderer = self.get_renderer()
        original_dpi = renderer.dpi
        renderer.dpi = self.figure.dpi

        version_str = 'matplotlib version ' + __version__ + \
            ', http://matplotlib.org/'
        metadata = OrderedDict({'Software': version_str})
        user_metadata = kwargs.pop("metadata", None)
        if user_metadata is not None:
            metadata.update(user_metadata)

        try:
            with cbook.open_file_cm(filename_or_obj, "wb") as fh:
                fh = write_png(renderer, fh,
                               self.figure.dpi, metadata=metadata)
        finally:
            renderer.dpi = original_dpi

@_Backend.export
class _BackendAgg(_Backend):
    FigureCanvas = FigureCanvasBlender
    FigureManager = FigureManagerBase
