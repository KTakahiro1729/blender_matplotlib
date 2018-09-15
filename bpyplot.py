from matplotlib.pyplot import imsave as original_imsave
from matplotlib.pyplot import *
from matplotlib.image import AxesImage
import os, six
import backend_blender

def _doc_copy(from_func):
    def result(to_func):
        to_func.__doc__ = "copy of: " + from_func.__doc__
        return to_func
    return result

class _AxesImage(AxesImage):
    @_doc_copy(AxesImage.write_png)
    def write_png(self, fname):
        im = self.to_rgba(self._A[::-1] if self.origin == 'lower' else self._A,
                          bytes=True, norm=True)
        backend_blender.write_png(im, fname)

@_doc_copy(original_imsave)
def imsave(fname, arr, vmin=None, vmax=None, cmap=None, format=None,
           origin=None, dpi=100):

    if isinstance(fname, getattr(os, "PathLike", ())):
        fname = os.fspath(fname)
    if (format == 'png'
        or (format is None
            and isinstance(fname, six.string_types)
            and fname.lower().endswith('.png'))):
        image = _AxesImage(None, cmap=cmap, origin=origin)
        image.set_data(arr)
        image.set_clim(vmin, vmax)
        image.write_png(fname)
    else:
        fig = Figure(dpi=dpi, frameon=False)
        FigureCanvas(fig)
        fig.figimage(arr, cmap=cmap, vmin=vmin, vmax=vmax, origin=origin,
                     resize=True)
        fig.savefig(fname, dpi=dpi, format=format, transparent=True)
