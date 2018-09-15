try:
    import bpy
except:
    print("bpy not found")

from collections import OrderedDict
import os
import numpy as np
from matplotlib import __version__, cbook
from matplotlib.backend_bases import FigureCanvasBase, FigureManagerBase
from matplotlib.backends.backend_agg import FigureCanvasAgg, RendererAgg

from matplotlib._pylab_helpers import Gcf
from matplotlib.figure import Figure
def renderer2nparray(renderer):
    height, width = map(int,(renderer.height, renderer.width))

    buffer = renderer.buffer_rgba()
    nparray = np.frombuffer(buffer, dtype = np.uint8)/256
    channels = nparray.size//(width*height)
    nparray = nparray.reshape(height, width, channels)

    return nparray

def nparray2blenderimg(nparray, filename):
    h, w, c = nparray.shape
    alpha = False if c == 3 else True
    b_img = bpy.data.images.new(filename, alpha=alpha, width = w,height = h)

    nparray = np.flip(nparray, axis = 0).flatten()
    b_img.pixels = nparray

    return b_img

def write_png(renderer, fh, dpi=None, metadata=None):

    # get filename and close file (open later)
    if hasattr(fh, "name"):
        filename = fh.name
        fh.close()
        fh_reopen = True
    elif isinstance(fh,str):
        filename = fh
        fh_reopen = False
    else:
        print(fh)
        raise ValueError("Failed to determine filename.")

    # generate blender image

    if isinstance(renderer, np.ndarray):
        nparray = renderer
        if nparray.dtype in [np.uint8, int]:
            nparray = nparray / 256
    else:
        nparray = renderer2nparray(renderer)
    b_img = nparray2blenderimg(nparray, filename)

    # resolve filename_or_obj
    if os.path.isabs(filename):
        b_img.filepath_raw = filename
    else:
        b_img.filepath_raw = "//" + bpy.path.basename(filename)

    # set as png
    b_img.file_format = "PNG"



    # save and delete
    b_img.save()
    bpy.data.images.remove(b_img)

    # reopen file
    if fh_reopen:
        fh = cbook.open_file_cm(filename, "ab")
    return fh

def show_blender(renderer):
    nparray = renderer2nparray(renderer)
    b_img = nparray2blenderimg(nparray, "plt_show")

    # set as active image

    ## find area to set image as active
    image_area = None
    if bpy.context.area.type =="IMAGE_EDITOR":
        image_area = bpy.context.area
    else:
        for area in bpy.context.screen.areas:
            if area.type == "IMAGE_EDITOR":
                image_area = area

    if image_area is not None:
        image_area.spaces.active.image = b_img

class FigureCanvasBlender(FigureCanvasAgg):
    def show(self):
        FigureCanvasAgg.draw(self)
        show_blender(self.get_renderer())

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

class FigureManagerBlender(FigureManagerBase):
    def show(self):
        pass





def show(block=None):
    for manager in Gcf.get_all_fig_managers():
        manager.canvas.show()


def new_figure_manager(num, *args, **kwargs):
    FigureClass = kwargs.pop('FigureClass', Figure)
    thisFig = FigureClass(*args, **kwargs)
    return new_figure_manager_given_figure(num, thisFig)


def new_figure_manager_given_figure(num, figure):
    canvas = FigureCanvasBlender(figure)
    manager = FigureManagerBlender(canvas, num)
    return manager

FigureCanvas = FigureCanvasBlender
FigureManager = FigureManagerBlender
