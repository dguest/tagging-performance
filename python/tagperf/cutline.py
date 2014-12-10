import os
import numpy as np
import h5py

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter

from tagperf.tagschema import long_particle_names
from tagperf.pr import add_atlas, add_official_garbage, log_formatting
from tagperf.cutplane import CountPlane, ANTI_LIGHT_RANGE, ANTI_B_RANGE

def draw_cut_lines(hdf_file, out_dir, ext, tagger='jfc'):
    with h5py.File(hdf_file) as in_file:
        planes = {x: CountPlane(in_file[x][tagger]) for x in 'BUC'}
    for ax, disc in [('x', 'light'), ('y', 'bottom')]:
        canvas = _get_line_canvas(planes, ax)
        if not os.path.isdir(out_dir):
            os.mkdir(out_dir)
        canvas.print_figure('{}/anti-{}-discriminant{}'.format(
                out_dir, disc, ext), bbox_inches='tight')

_parts_vs_ax = {'x': 'U', 'y':'B'}
_range_vs_ax = {'x': ANTI_LIGHT_RANGE, 'y': ANTI_B_RANGE}
_peter_colors = {'B':'r','C':'g','U':'b'}
_legpos_vs_ax = {'x':'upper left', 'y':'upper right'}
_text_size = 12
def _get_line_canvas(planes, axis, axsize=14, rebin=5):
    """return the canvas with everything drawn on it"""
    fig = Figure(figsize=(5.0, 5.0*3/4))
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(1,1,1)
    for flav, plane in sorted(planes.items()):
        xv, yv = plane.project(axis)
        yv = yv.reshape(-1, rebin).sum(1)
        xv = xv.reshape(-1, rebin)[:,0]
        yv /= yv.sum()
        lab = long_particle_names[flav] + ' jets'
        color = _peter_colors[flav]
        ax.plot(xv, yv, drawstyle='steps-post', label=lab, color=color)
    discriminated = {'U':r'\mathrm{light}', 'B':'b'}[_parts_vs_ax[axis]]
    xname = r'$\log(P_{{c}} / P_{{ {} }})$'.format(discriminated)
    ax.set_xlabel(xname, x=0.98, ha='right', size=axsize)
    ax.set_xlim(_range_vs_ax[axis])
    ax.set_yscale('log')
    ax.set_ylabel('Fraction of Jets',
                  y=0.98, ha='right', size=axsize)
    ax.set_ylim(1e-4, 1.5)
    formatter = FuncFormatter(log_formatting)
    ax.yaxis.set_major_formatter(formatter)
    legprops = dict(size=_text_size)
    legloc = _legpos_vs_ax[axis]
    ax.legend(framealpha=0, loc=legloc, prop=legprops)
    off_x = 0.05 if 'right' in legloc else 0.5
    off_y = 0.93
    ysp = 0.07
    add_atlas(ax, off_x + 0.13, off_y, size=_text_size)
    add_official_garbage(ax, off_x, off_y - ysp, size=_text_size, ysp=0.07)
    fig.tight_layout(pad=0, h_pad=0, w_pad=0)
    return canvas
