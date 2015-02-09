from os.path import isfile, isdir
import numpy as np
import h5py
import math
import warnings
import os, sys

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.colorbar import Colorbar
from matplotlib.ticker import FuncFormatter
from matplotlib.lines import Line2D
from matplotlib.legend import Legend

from tagperf.tagschema import long_particle_names
from tagperf.tagschema import leg_labels_colors, mv1uc_name, mv1uc_disp
from tagperf.pr import add_atlas, add_official_garbage, log_formatting

_text_size = 12
_fig_edge = 5.0
_fig_size = (_fig_edge, _fig_edge * 3/4)
_square_fig_size = (_fig_edge, _fig_edge)
_line_width = 1.8


# __________________________________________________________________________
# top level functions

def make_plots(in_file_name, cache_name, out_dir, ext):
    """
    Top level routine to make plots from tagger output distributions
    """
    with h5py.File(in_file_name, 'r') as in_file:
        with h5py.File(cache_name, 'a') as out_file:
            make_rejrej(in_file, out_file, tagger='gaia')
            make_rejrej(in_file, out_file, tagger='jfc')
            make_rejrej(in_file, out_file, tagger='jfit')
            make_rejrej(in_file, out_file, tagger=mv1uc_name)

    if not isdir(out_dir):
        os.mkdir(out_dir)

    with h5py.File(cache_name, 'r') as cache:
        draw_ctag_rejrej(cache, out_dir, ext)
        draw_contour_rejrej(cache, out_dir, ext)
        draw_ctag_ratio(cache, out_dir, ext)
        draw_ctag_ratio(cache, out_dir, ext, tagger='jfit',
                        tagger_disp='COMBNN', vmax=1.9)
        draw_ctag_ratio(cache, out_dir, ext, tagger=mv1uc_name,
                        tagger_disp=mv1uc_disp, vmax=1.9)
        draw_ctag_ratio(
            cache, out_dir, ext, tagger=mv1uc_name,
            tagger_disp=mv1uc_disp,
            num_tagger='jfc',num_tagger_disp='JetFitterCharm', vmax=1.9)
        draw_simple_rejrej(cache, out_dir, ext)
        draw_xkcd_rejrej(cache, out_dir, ext)
        with h5py.File(in_file_name, 'r') as in_file:
            draw_cprob_rejrej(cache, in_file, out_dir, ext)

def make_1d_plots(in_file_name, out_dir, ext, b_eff=0.1, reject='U'):
    textsize=_text_size
    taggers = {}
    with h5py.File(in_file_name, 'r') as in_file:
        for tag in ['gaia', mv1uc_name, 'jfc', 'jfit']:
            taggers[tag] = get_c_vs_u_const_beff(
                in_file, tag, b_eff=b_eff, reject=reject)

    fig = Figure(figsize=_fig_size)
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(1,1,1)
    for tname, (vc, vu) in taggers.items():
        label, color = leg_labels_colors.get(tname, (tname, 'k'))
        ax.plot(vc, vu, label=label, color=color, linewidth=_line_width)
    leg = ax.legend(title='$b$-rejection = {}'.format(1/b_eff),
                    prop={'size':textsize})
    leg.get_title().set_fontsize(textsize)

    setup_1d_ctag_legs(ax, textsize, reject=reject)

    fig.tight_layout(pad=0, h_pad=0, w_pad=0)
    if not isdir(out_dir):
        os.mkdir(out_dir)
    file_name = '{}/{rej}Rej-vs-cEff-brej{}{}'.format(
        out_dir, int(1.0/b_eff), ext, rej=reject.lower())
    canvas.print_figure(file_name, bbox_inches='tight')

_b_eff_styles = ['solid','dashed','dotted']
def make_1d_overlay(in_file_name, out_dir, ext, b_effs=[0.1, 0.2]):
    textsize = _text_size
    b_eff_styles = _b_eff_styles

    taggers = {x:{} for x in b_effs}
    with h5py.File(in_file_name, 'r') as in_file:
        for b_eff in taggers:
            for tag in ['gaia', mv1uc_name]:
                taggers[b_eff][tag] = get_c_vs_u_const_beff(
                    in_file, tag, b_eff=b_eff)

    fig = Figure(figsize=_fig_size)
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(1,1,1)
    for b_eff, linestyle in zip(b_effs, b_eff_styles):
        for tname, (vc, vu) in taggers[b_eff].items():
            label, color = leg_labels_colors.get(tname, (tname, 'k'))
            lab = '$1 / \epsilon_{{ b }} = $ {rej:.0f}, {tname}'.format(
                rej=1/b_eff, tname=label)
            ax.plot(vc, vu, label=lab, color=color, linewidth=_line_width,
                    linestyle=linestyle)
    legprops = {'size':textsize}
    leg = ax.legend(prop=legprops)
    leg.get_title().set_fontsize(textsize)

    setup_1d_ctag_legs(ax, textsize)

    fig.tight_layout(pad=0, h_pad=0, w_pad=0)
    if not isdir(out_dir):
        os.mkdir(out_dir)
    file_name = '{}/ctag-1d-brej-overlay{}'.format(
        out_dir, ext)
    canvas.print_figure(file_name, bbox_inches='tight')

# _________________________________________________________________________
# common utility functions

def setup_1d_ctag_legs(ax, textsize, reject='U', official=False,
                        approval='Internal'):
    ax.set_yscale('log')
    formatter = FuncFormatter(log_formatting)
    ax.yaxis.set_major_formatter(formatter)
    ax.set_xlabel('$c$-jet efficiency', x=0.98, ha='right', size=textsize)
    ylab = '{rej}-jet rejection'.format(rej=long_particle_names[reject])
    ax.set_ylabel(ylab, y=0.98, ha='right', size=textsize)
    ax.tick_params(labelsize=textsize)
    ax.grid(which='both', alpha=0.05, ls='-')
    if official:
        x = 0.5
        size = 12
        ysp = 0.1 * size / 16
        add_atlas(ax, x + 0.13, 0.9, size=size, approval=approval)
        add_official_garbage(ax, x, 0.9 - ysp, size=size, ysp=ysp)


def _get_hist_name(flavor, tagger, binning):
    return '{}/ctag/{}/{}'.format(flavor, binning, tagger)

def _get_rej_hist(int_counts):
    """
    Convert integrated counts (from tagger output distributions) to
    1 / efficiency (without warnings).
    """
    rej = np.zeros(int_counts.shape)
    valid = int_counts != 0
    rej[valid] = int_counts.max() / int_counts[valid]
    invalid = np.logical_not(valid)
    rej[invalid] = np.inf
    return rej

def _get_eff_hist(int_counts):
    return int_counts / int_counts.max()

# __________________________________________________________________________
# 'plumbing' level routines to calculate the things we'll later plot

def make_rejrej(in_file, out_file, tagger='gaia', binning='all',
                 lookup=_get_hist_name):
    """
    Builds 2d efficiency arrays, binned by rejection.
    """
    def get_flavor(flavor):
        try:
            lookup_str = lookup(flavor, tagger=tagger, binning=binning)
            return in_file[lookup_str]
        except KeyError as err:
            raise KeyError(err.args[0] + ' -- looking for ' + lookup_str)

    if not tagger in out_file:
        out_file.create_group(tagger)
    if binning in out_file[tagger]:
        print('using cached tagger {}, binning {}'.format(tagger, binning))
        return

    rej_builder = RejRejComp('BUC', 50.0, 400.0)
    rej_builder.calculate(get_flavor)
    rej_builder.save(out_file, tagger, binning)

class ProgBar(object):
    """
    Generic progress "bar".
    """
    def __init__(self, total, prefix=''):
        self.total = total
        self.prefix = prefix
    def __enter__(self):
        return self
    def __exit__(self, ex_type, ex_message, tr):
        sys.stdout.write('\n')
    def update(self, entry):
        if self.prefix:
            outstr = '\r{prefix}: {} of {} ({:.0%})'
        else:
            outstr = '\r{} of {} ({:.0%})'
        sys.stdout.write(outstr.format(
                entry, self.total, float(entry) / self.total,
                prefix=self.prefix))
        sys.stdout.flush()

class RejRejComp(object):
    """
    Class to convert three arrays (one efficiency and two rejection) into
    a 2D efficiency array binned by rejection.
    """
    def __init__(self, xyz='BUC', xmax=50.0, ymax=400.0):
        self.n_bins = 100
        self.x_min = 1.0
        self.y_min = 1.0
        self.x_max = float(xmax)
        self.y_max = float(ymax)
        self.xyz = xyz
        self.rej_array = None

    def calculate(self, get_flavor):
        """get_flavor is a function that returns array given a flavor"""
        int_arr = {}
        for flavor in self.xyz:
            arr = np.asarray(get_flavor(flavor))
            int_arr[flavor] = arr[::-1,::-1].cumsum(axis=0).cumsum(axis=1)

        x, y, z = self.xyz
        get_eff, get_rej = _get_eff_hist, _get_rej_hist
        self.rej_array = self.get_rej_array(
            eff=get_eff(int_arr[z]),
            xrej=get_rej(int_arr[x]),
            yrej=get_rej(int_arr[y]))

    def save(self, out_file, tagger, binning):
        assert self.rej_array is not None, 'need to load an array first'

        if not tagger in out_file:
            out_file.create_group(tagger)
        saved_ds = out_file[tagger].create_dataset(
            binning, data=self.rej_array)

        saved_ds.attrs['x_max'] = self.x_max
        saved_ds.attrs['y_max'] = self.y_max
        saved_ds.attrs['x_min'] = self.x_min
        saved_ds.attrs['y_min'] = self.y_min
        saved_ds.attrs['xyz'] = self.xyz

    def _logspace(self, low, high):
        return np.logspace(math.log10(low), math.log10(high), self.n_bins)

    def get_rej_array(self, eff, xrej, yrej):
        valid_rej = np.isfinite(xrej) & np.isfinite(yrej)
        x_bin_edges = self._logspace(self.x_min, self.x_max)
        y_bin_edges = self._logspace(self.y_min, self.y_max)

        x_bins = np.digitize(xrej[valid_rej], bins=x_bin_edges) - 1
        y_bins = np.digitize(yrej[valid_rej], bins=y_bin_edges) - 1
        z_vals = eff[valid_rej]

        out_array = np.ones((self.n_bins, self.n_bins)) * -1
        with ProgBar(z_vals.size, 'making rejrej') as pbar:
            for binn, (x, y, z) in enumerate(zip(x_bins, y_bins, z_vals)):
                if binn % 20000 == 0:
                    pbar.update(binn)
                out_array[x, y] = max(z, out_array[x, y])
        return out_array

def get_c_vs_u_const_beff(in_file, tagger, b_eff=0.1, binning='all',
                               reject='U', lookup=_get_hist_name):
    """
    Returns (c efficiency, X rejection) tuple for a given b-tagging
    efficiency. By default reject 'U', but can set this.
    """
    def make_int_flavor(flavor):
        ds = in_file[lookup(flavor, tagger=tagger, binning=binning)]
        return np.array(ds)[::-1,::-1].cumsum(axis=0).cumsum(axis=1)

    flavs = 'BC' + reject
    eff_flavor = {
        flav: _get_eff_hist(make_int_flavor(flav)) for flav in flavs}

    # --- Here be the meat ---
    # the 'anti-b' cut is along the second axis. The index of the first
    # passing value above the efficiency threshold is the same as the
    # number of points that are below the threshold.
    first_passing_index = np.sum(eff_flavor['B'] < b_eff, axis=1)
    ll, lb = eff_flavor['B'].shape
    u_idx = np.arange(ll)
    b_idx = np.minimum(first_passing_index, lb - 1)
    beffs = eff_flavor['B'][u_idx, b_idx]
    ceffs = eff_flavor['C'][u_idx, b_idx]
    leffs = eff_flavor[reject][u_idx, b_idx]
    # to remove points with lower efficiency than the previous point
    c_max = np.maximum.accumulate(ceffs)
    valid = (np.abs(beffs - b_eff) / b_eff < 0.01) & (ceffs == c_max)
    return ceffs[valid], 1 / leffs[valid]

# __________________________________________________________________________
# drawing routines

def draw_ctag_rejrej_slow(in_file, out_dir, ext='.pdf'):
    """
    Slow because it uses pcolormesh.
    """
    fig = Figure(figsize=_fig_size)
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(1,1,1)
    ds = in_file['gaia/all']
    xmin = ds.attrs.get('x_min', 1.0)
    ymin = ds.attrs.get('y_min', 1.0)
    xmax = ds.attrs['x_max']
    ymax = ds.attrs['y_max']

    xvals = np.logspace(math.log10(xmin), math.log10(xmax), ds.shape[0])
    yvals = np.logspace(math.log10(ymin), math.log10(ymax), ds.shape[1])
    xgrid, ygrid = np.meshgrid(xvals, yvals)

    ax.pcolormesh(xgrid, ygrid, np.array(ds))
    ax.set_xscale('log')
    ax.set_yscale('log')
    out_name = '{}/rejrej{}'.format(out_dir, ext)
    canvas.print_figure(out_name, bbox_inches='tight')


def draw_ctag_rejrej(in_file, out_dir, ext='.pdf'):
    """
    Basic heatmap of efficiency vs two rejections.
    """
    fig = Figure(figsize=_fig_size)
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(1,1,1)
    ds = in_file['gaia/all']

    eff_array, extent = _get_arr_extent(ds)
    label_rejrej_axes(ax, ds)
    im = ax.imshow(eff_array.T, extent=extent,
                   origin='lower', aspect='auto')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.grid(which='both')

    # add_contour(ax,ds)

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    cb = Colorbar(ax=cax, mappable=im)

    out_name = '{}/rejrej{}'.format(out_dir, ext)
    # ignore complaints about not being able to log scale images
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        canvas.print_figure(out_name, bbox_inches='tight')

def draw_ctag_ratio(in_file, out_dir, ext='.pdf', **opts):
    """
    Heat map showing efficiency ratio gaia and some other tagger.
    Makes iso-efficiency contours for gaia.

    misc options:
      tagger
      tagger_disp (for display)
      vmax
    """
    options = {'tagger':'jfc', 'tagger_disp':'JetFitterCharm', 'vmax':1.2,
               'num_tagger':'gaia', 'num_tagger_disp':None,
               'textsize':_text_size}
    for key, val in opts.items():
        if not key in options:
            raise TypeError("{} not a valid arg".format(key))
        options[key] = val

    fig = Figure(figsize=_fig_size)
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(1,1,1)
    ds = in_file['{}/all'.format(options['num_tagger'])]
    ds_denom = in_file['{}/all'.format(options['tagger'])]

    eff_array, extent = _get_arr_extent(ds)
    denom_array, denom_extent = _get_arr_extent(ds_denom)
    ratio_array = eff_array / denom_array
    im = ax.imshow(ratio_array.T, extent=extent,
                   origin='lower', aspect='auto',
                   vmin=1.0, vmax=options['vmax'])

    textsize = options['textsize']
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    cb = Colorbar(ax=cax, mappable=im)
    cb.set_label('$\epsilon_{{c}}$ ratio ({} / {})'.format(
            options['num_tagger_disp'] or options['num_tagger'].upper(),
            options['tagger_disp']), size=textsize)
    cb.ax.tick_params(labelsize=textsize, which='both')

    label_rejrej_axes(ax, ds, textsize=textsize)
    _add_eq_contour(ax, ds, ds_denom, colorbar=cb)
    add_contour(ax,ds, opts=dict(textsize=textsize))

    out_name = '{}/ctag-2d-{}-vs-{}{}'.format(
        out_dir, options['num_tagger'], options['tagger'], ext)
    # ignore complaints about not being able to log scale images
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        canvas.print_figure(out_name, bbox_inches='tight')

def draw_contour_rejrej(in_file, out_dir, ext='.pdf'):
    """
    Compare efficiency of two taggers. Draw one set of contours for the
    numerator tagger, another set for the ratio between the two taggers.
    """
    fig = Figure(figsize=_fig_size)
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(1,1,1)
    ds = in_file['gaia/all']
    ds_denom = in_file['jfc/all']

    label_rejrej_axes(ax, ds)
    _add_eq_contour(ax, ds, ds_denom, levels=[1.05, 1.10, 1.15], smooth=1.0)
    add_contour(ax, ds)

    out_name = '{}/rejrej-cont{}'.format(out_dir, ext)
    canvas.print_figure(out_name, bbox_inches='tight')

def draw_simple_rejrej(in_file, out_dir, ext='.pdf', tagger='gaia',
                       official=False, approval='Internal'):
    """
    Draw iso-efficiency contours for one tagger (no colors).
    """
    fig = Figure(figsize=_fig_size)
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(1,1,1)
    ds = in_file[tagger + '/all']

    label_rejrej_axes(ax, ds)
    levels = np.linspace(0.2, 0.5, 7)
    add_contour(ax, ds, opts=dict(levels=levels, textsize=10))
    if official:
        size = 10
        ysp = 0.1*size/16
        add_official_garbage(ax, 0.97, 0.93, size=size, ysp=ysp, ha='right')
        add_atlas(ax, 0.2, 0.92, size=size*1.2, approval=approval)
        z = long_particle_names[ds.attrs['xyz'][2]]
        zlab = '{}-jet efficiency'.format(z)
        ax.text(0.97, 0.90 - ysp*4, 'Contours give \n ' + zlab,
                transform=ax.transAxes, size=size, ha='right')

    out_name = '{}/rejrej-simple{}'.format(out_dir, ext)
    canvas.print_figure(out_name, bbox_inches='tight')

def draw_xkcd_rejrej(in_file, out_dir, ext='.pdf'):
    """
    Draw iso-efficiency contours 'sketch'.
    """
    import matplotlib.pyplot as plt
    with plt.xkcd():
        fig = Figure(figsize=_fig_size)
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(1,1,1)
        ds = in_file['gaia/all']
        ds_denom = in_file['jfc/all']

        label_rejrej_axes(ax, ds)
        add_contour(ax, ds, opts=dict(levels=np.arange(0.1, 0.8, 0.05)))

        out_name = '{}/rejrej-xkcd{}'.format(out_dir, ext)
        canvas.print_figure(out_name, bbox_inches='tight')


def draw_cprob_rejrej(in_file, in_file_up, out_dir, ext='.pdf'):
    """
    Map of iso-efficiency contours, with an overlay for the rejections
    of a 1d cut.
    """
    fig = Figure(figsize=_fig_size)
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(1,1,1)
    ds = in_file['gaia/all']
    ds_denom = in_file['jfc/all']

    levels = np.arange(0.1, 0.8, 0.1)
    label_rejrej_axes(ax, ds)
    add_contour(ax, ds, opts=dict(levels=levels))
    _add_cprob_curve(ax, in_file_up, levels=levels)

    out_name = '{}/rejrej-cprob{}'.format(out_dir, ext)
    canvas.print_figure(out_name, bbox_inches='tight')

# __________________________________________________________________________
# draw utilities

def _add_cprob_curve(ax, in_file, levels):
    """
    Add a curve indicating the possible rejections for a 1D discriminator
    cut. Also add points at various efficiency levels.
    """
    def getint(flavor):
        name = '{}/ctag/all/gaiaC'.format(flavor)
        return np.array(in_file[name])[::-1].cumsum()
    c_int = getint('C')
    b_int = getint('B')
    u_int = getint('U')

    c_eff_all = c_int / c_int.max()
    useful_eff = c_eff_all > 0.2
    c_eff = c_eff_all[useful_eff]
    b_rej = b_int.max() / b_int[useful_eff]
    u_rej = u_int.max() / u_int[useful_eff]
    ax.plot(b_rej, u_rej, '--r', linewidth=_line_width,
            label='gaia 1D $p_{c}$')
    b_rej_pts = []
    u_rej_pts = []
    for eff in levels:
        idx_above, = np.nonzero(c_eff > eff)
        first_above = idx_above.min()
        b_pt = b_rej[first_above]
        b_rej_pts.append(b_pt)
        u_pt = u_rej[first_above]
        u_rej_pts.append(u_pt)
        ax.text(b_pt, u_pt, str(eff), color='r', ha='left', va='bottom')
    ax.plot(b_rej_pts, u_rej_pts, 'or')
    handles, labels = ax.get_legend_handles_labels()
    handles.append(Line2D([0,1],[0,0], linewidth=_line_width, color='k'))
    labels.append('gaia 2D, iso-eff')
    ax.legend(reversed(handles), reversed(labels), numpoints=1)

def add_contour(ax, ds, opts={}):
    """
    routine to add the iso-efficiency contours to a plot.
    """
    eff_array = _maximize_efficiency(np.array(ds))
    xmin = ds.attrs.get('x_min', 1.0)
    ymin = ds.attrs.get('y_min', 1.0)
    xmax = ds.attrs['x_max']
    ymax = ds.attrs['y_max']

    xvals = np.logspace(math.log10(xmin), math.log10(xmax), ds.shape[0])
    yvals = np.logspace(math.log10(ymin), math.log10(ymax), ds.shape[1])
    xgrid, ygrid = np.meshgrid(xvals, yvals)
    c_lines = np.arange(0.1, 0.65, 0.05)
    ct = ax.contour(xgrid, ygrid,
        eff_array.T,
        linewidths = _line_width,
        levels = opts.get('levels',c_lines),
        colors = opts.get('color','k'),
        label = 'iso-eff 2D cuts'
        )
    ax.clabel(ct, fontsize=opts.get('textsize',_text_size*0.75), inline=True,
              fmt = '%.2f')

def _smooth(ratio_array, sigma):
    """
    Gaussian smoothing function, doesn't work without scipy.
    """
    if not sigma:
        return ratio_array
    try:
        from scipy.ndimage.filters import gaussian_filter
        ratio_array = gaussian_filter(ratio_array, sigma=sigma)
    except ImportError as err:
        warnings.warn(
            'problem with scipy: {}, not smoothing'.format(err), stacklevel=2)
    return ratio_array

def _add_eq_contour(ax, ds, ds_denom, colorbar=None, levels=[], smooth=None):
    """
    Add contours where ds and ds_denom have equal efficiency (ratio = 1). The
    'levels' argument can be used to specify contours at ratios other than 1.
    """
    eff_array = _maximize_efficiency(np.array(ds))
    other_array = _maximize_efficiency(np.array(ds_denom))
    ratio_array = _smooth(eff_array / other_array, sigma=smooth)
    xmin = ds.attrs.get('x_min', 1.0)
    ymin = ds.attrs.get('y_min', 1.0)
    xmax = ds.attrs['x_max']
    ymax = ds.attrs['y_max']

    xvals = np.logspace(math.log10(xmin), math.log10(xmax), ds.shape[0])
    yvals = np.logspace(math.log10(ymin), math.log10(ymax), ds.shape[1])
    xgrid, ygrid = np.meshgrid(xvals, yvals)
    ct = ax.contour(
        xgrid, ygrid,
        ratio_array.T,
        linewidths = _line_width,
        levels = [1.0] if not levels else levels,
        colors = ['r','orange','y','green'],
        )
    def fmt(value):
        if value == 1.0:
            return 'equal'
        return '{:+.0%}'.format(value - 1.0)
    ax.clabel(ct, fontsize=_text_size*0.75, inline=True, fmt=fmt)
    if colorbar:
        colorbar.add_lines(ct)

def _tick_format(x, pos):
    base = math.floor(math.log10(x))
    if x / 10**base > 4:
        return ''
    else:
        return '{:.0f}'.format(x)

def label_rejrej_axes(ax, ds, textsize=_text_size):
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.grid(which='both', alpha=0.05, ls='-')
    x, y, z = ds.attrs['xyz']
    formatter = FuncFormatter(_tick_format)
    ax.xaxis.set_minor_formatter(formatter)
    ax.xaxis.set_major_formatter(formatter)
    ax.yaxis.set_minor_formatter(formatter)
    ax.yaxis.set_major_formatter(formatter)
    ax_tmp = '{}-jet rejection'
    ax.set_xlabel(ax_tmp.format(long_particle_names[x]),
                  x=0.98, ha='right', size=textsize)
    ax.set_ylabel(ax_tmp.format(long_particle_names[y]),
                  y=0.98, ha='right', size=textsize)
    ax.tick_params(labelsize=textsize, which='both')

def _get_arr_extent(ds):
    """
    Retreve the extent of an array stored by make_rejrej.
    """
    try:
        xmin = ds.attrs['x_min']
        ymin = ds.attrs['y_min']
    except KeyError:
        warnings.warn("no stored minimum for rejrej array, assume 1",
                      stacklevel=2)
        xmin = 1.0
        ymin = 1.0
    xmax = ds.attrs['x_max']
    ymax = ds.attrs['y_max']
    eff_array = _maximize_efficiency(np.array(ds))
    return eff_array, (xmin, xmax, ymin, ymax)

def _maximize_efficiency(eff_array):
    """
    It's not reasonable to take less than the efficiency
    """
    temp = np.maximum.accumulate(eff_array[::-1,:], 0)[::-1,:]
    temp = np.maximum.accumulate(temp[:,::-1], 1)[:,::-1]
    return temp
