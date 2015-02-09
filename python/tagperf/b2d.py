import h5py
import numpy as np
from os.path import isdir
import os

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

from tagperf.ctaging import add_contour, label_rejrej_axes
from tagperf.ctaging import RejRejComp

_fig_edge = 5.0
_fig_size = (_fig_edge, _fig_edge * 3/4)

def make_b2d(in_file_name, cache_name, out_dir, ext):
    """
    Top level routine to make plots from tagger output distributions
    """
    with h5py.File(in_file_name, 'r') as in_file:
        with h5py.File(cache_name, 'a') as out_file:
            _make_rejrej_btag(in_file, out_file)

    if not isdir(out_dir):
        os.mkdir(out_dir)

    with h5py.File(cache_name, 'r') as cache:
        _draw_btag_rejrej(cache, out_dir, ext)

def _make_rejrej_btag(in_file, out_file, binning='all', tagger='gaiaBtag'):
    """
    Builds 2d efficiency arrays, binned by rejection.
    """
    def get_flavor(flavor):
        try:
            lookup_str = '{}/ctag/{}/{}'.format(flavor, binning, tagger)
            return in_file[lookup_str]
        except KeyError as err:
            raise KeyError(err.args[0] + ' -- looking for ' + lookup_str)

    if not tagger in out_file:
        out_file.create_group(tagger)
    if binning in out_file[tagger]:
        print('using cached tagger {}, binning {}'.format(tagger, binning))
        return

    rej_builder = RejRejComp('CUB', 25, 1500)
    rej_builder.calculate(get_flavor)
    rej_builder.save(out_file, tagger, binning)


def _get_hist_name_btag(flavor, tagger, binning):
    return '{}/ctag/{}/{}'.format(flavor, binning, tagger)


def _draw_btag_rejrej(in_file, out_dir, ext='.pdf', tagger='gaiaBtag',
                      official=False, approval='Internal'):
    """
    Draw iso-efficiency contours for one tagger (no colors).
    """
    fig = Figure(figsize=_fig_size)
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(1,1,1)
    ds = in_file[tagger + '/all']

    label_rejrej_axes(ax, ds)
    levels = np.linspace(0.60, 0.9, 7)
    add_contour(ax, ds, opts=dict(levels=levels, textsize=10))

    out_name = '{}/rejrej-btag{}'.format(out_dir, ext)
    canvas.print_figure(out_name, bbox_inches='tight')
