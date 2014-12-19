import os
import numpy as np
import h5py

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Patch

from tagperf.tagschema import long_particle_names

ANTI_LIGHT_RANGE = (-4.5, 5.0)
ANTI_B_RANGE = (-7.0, 3.5)
ANTI_B_CUT = -0.9
ANTI_LIGHT_CUT = 0.95

def draw_cut_plane(hdf_file, out_dir, ext, tagger='jfc', maxcut=0.5):
    with h5py.File(hdf_file) as in_file:
        planes = {x: CountPlane(in_file[x][tagger]) for x in 'BUC'}
    xlims = ANTI_LIGHT_RANGE
    ylims = ANTI_B_RANGE
    rgb = np.dstack([planes[x].subplane(xlims, ylims) for x in 'BCU'])
    rgb = np.log(rgb + 1)
    for iii in range(rgb.shape[2]):
        maxval = (rgb[:,:,iii].max() * maxcut)
        rgb[:,:,iii] = np.minimum(rgb[:,:,iii] / maxval, 1.0)
    fig = Figure(figsize=(5.0,5.0*3/4))
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(1,1,1)
    imextent = list(xlims) + list(ylims)
    ax.imshow(rgb, origin='lower', extent=imextent, aspect='auto')
    ax.set_xlim(*xlims)
    ax.set_ylim(*ylims)
    _label_axes(ax)
    _add_legend(ax)
    _add_atlas(ax, 0.02, 0.98)
    _add_sim_info(ax, 0.02, 0.38, size=10)
    xcut, ycut = ANTI_LIGHT_CUT, ANTI_B_CUT
    cutcolor = 'DarkGreen'
    _add_cut(ax, xcut, ycut, color=cutcolor)
    _annotate_cut(ax, xy=(3.5, ycut), xyt=(0.95, 0.05), color=cutcolor)
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)
    canvas.print_figure('{}/2d-cut{}'.format(out_dir, ext),
                        bbox_inches='tight')

def _label_axes(ax, size=14):
    ax.set_xlabel(r'$\log(P_{c} / P_{\rm light})$',
                  x=0.98, ha='right', size=size)
    ax.set_ylabel(r'$\log(P_{c} / P_{b})$',
                  y=0.98, ha='right', size=size)

def _add_legend(ax):
    rgb_patch = [Patch(color=x) for x in 'rgb']
    bcl_names = [r'$b$', r'$c$', r'$\rm light$']
    title = 'Jet Flavor'
    ax.legend(rgb_patch, bcl_names, loc='lower left', fancybox=True,
              borderaxespad=0.2, title=title,
              labelspacing=0.2, handlelength=1.0)

def _add_atlas(ax, x, y, size=16):
    props = dict(boxstyle='round', facecolor='w')
    ax.text(x, y, 'ATLAS Internal', weight='bold', style='italic',
            transform=ax.transAxes, bbox=props, va='top', ha='left')

def _add_cut(ax, x, y, color='Purple'):
    ym = ax.get_ylim()[1]
    xm = ax.get_xlim()[1]
    xv = [x, x, xm]
    yv = [ym, y, y]
    ax.plot(xv, yv, color=color, lw=3)

def _annotate_cut(ax, xy, xyt, size=12, color='Purple'):
    text = (
        'JetFitterCharm\n'
        "medium tag")
    bbox_style = dict(boxstyle="round", fc='w', ec=color)
    arrowprops = dict(arrowstyle='simple', color=color)
    textprops = dict(ha='right', va='bottom')
    ax.annotate(text, size=size, xy=xy, xytext=xyt, arrowprops=arrowprops,
                textcoords=ax.transAxes, bbox=bbox_style, **textprops)

def _add_sim_info(ax, x, y, size=16):
    props = dict(boxstyle='round', facecolor='w')
    text = (
        r'$t\bar{t}$ Simulation' + '\n'
        r'$\sqrt{s} =$ 8 TeV' + '\n'
        r'$p_{\rm T}^{\rm jet} > $ 20 GeV' + '\n'
        r'$|\eta| < $ 2.5' + '\n'
        r'JetFitterCharm')
    ax.text(x, y, text, size=size,
            transform=ax.transAxes, bbox=props, va='bottom', ha='left')

class CountPlane:
    def __init__(self, ds):
        ar = np.array(ds)[1:-1,1:-1]
        xextent = [ds.attrs[x][1] for x in ['min', 'max']]
        yextent = [ds.attrs[x][0] for x in ['min', 'max']]
        self.xvalues = np.linspace(*xextent, num=(ar.shape[1] + 1))
        self.yvalues = np.linspace(*yextent, num=(ar.shape[0] + 1))
        self.array = ar.T
    def subplane(self, xlims=ANTI_LIGHT_RANGE, ylims=ANTI_B_RANGE):
        xv, yv = self.xvalues, self.yvalues
        xvalid_idx = np.nonzero((xlims[0] <= xv) & (xv <= xlims[1]))[0]
        xlow, xhigh = xvalid_idx[0], xvalid_idx[-1]
        yvalid_idx = np.nonzero((ylims[0] <= yv) & (yv <= ylims[1]))[0]
        ylow, yhigh = yvalid_idx[0], yvalid_idx[-1]
        subarray = self.array[ylow:yhigh, xlow:xhigh]
        return subarray
    def project(self, axis, lims=(-10,10)):
        """return x, y plottable values"""
        assert axis.lower() in 'xy', 'must project along x or y'
        vals = self.xvalues if axis == 'x' else self.yvalues
        valid_idx = np.nonzero((lims[0] <= vals) & (vals <= lims[1]))[0]
        rng = slice(valid_idx[0], valid_idx[-1])
        if axis == 'x':
            yvals = self.array[:, rng].sum(0)
        elif axis == 'y':
            yvals = self.array[rng, :].sum(1)
        return vals[rng], yvals
