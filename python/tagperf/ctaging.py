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

def make_plots(in_file_name, cache_name, out_dir, ext): 
    with h5py.File(in_file_name, 'r') as in_file: 
        with h5py.File(cache_name, 'a') as out_file: 
            make_rejrej(in_file, out_file, tagger='gaia')
            make_rejrej(in_file, out_file, tagger='jfc')
            make_rejrej(in_file, out_file, tagger='jfit')

    if not isdir(out_dir): 
        os.mkdir(out_dir)

    with h5py.File(cache_name, 'r') as cache: 
        draw_ctag_rejrej(cache, out_dir, ext)
        draw_contour_rejrej(cache, out_dir, ext)
        draw_ctag_ratio(cache, out_dir, ext)
        draw_ctag_ratio(cache, out_dir, ext, tagger='jfit', 
                        tagger_disp='COMBNN', vmax=1.9)
        draw_simple_rejrej(cache, out_dir, ext)
        with h5py.File(in_file_name, 'r') as in_file: 
            draw_cprob_rejrej(cache, in_file, out_dir, ext)

def _get_hist_name(flavor, tagger, binning): 
    return '{}/ctag/{}/{}'.format(flavor, binning, tagger)

def _get_rej_hist(int_counts): 
    rej = np.zeros(int_counts.shape)
    valid = int_counts != 0
    rej[valid] = int_counts.max() / int_counts[valid]
    invalid = np.logical_not(valid)
    rej[invalid] = np.inf
    return rej

def _get_eff_hist(int_counts): 
    return int_counts / int_counts.max()

def make_rejrej(in_file, out_file, tagger='gaia', binning='all'): 
    def make_int_flavor(flavor): 
        ds = in_file[_get_hist_name(flavor, tagger=tagger, binning=binning)]
        return np.array(ds)[::-1,::-1].cumsum(axis=0).cumsum(axis=1)

    if not tagger in out_file: 
        out_file.create_group(tagger)
    if binning in out_file[tagger]: 
        print('using cached tagger {}, binning {}'.format(tagger, binning))
        return 

    int_flavor_arrays = {
        flav: make_int_flavor(flav) for flav in 'BCU'}
    
    rej_builder = RejRejComp()
    rej_builder.x_max = 50.0
    rej_builder.y_max = 400.0
    rej_array = rej_builder.get_rej_array(
        eff=_get_eff_hist(int_flavor_arrays['C']), 
        xrej=_get_rej_hist(int_flavor_arrays['B']), 
        yrej=_get_rej_hist(int_flavor_arrays['U']))

    saved_ds = out_file[tagger].create_dataset(binning, data=rej_array)
    saved_ds.attrs['x_max'] = rej_builder.x_max
    saved_ds.attrs['y_max'] = rej_builder.y_max
    saved_ds.attrs['xyz'] = 'BUC'

class ProgBar: 
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
                entry, self.total, entry / self.total, prefix=self.prefix))
        sys.stdout.flush()
    
class RejRejComp: 
    def __init__(self): 
        self.n_bins = 100
        self.x_max = 200.0
        self.y_max = 1000.0

    def get_rej_array(self, eff, xrej, yrej): 
        valid_rej = np.isfinite(xrej) & np.isfinite(yrej)
        x_bin_edges = np.logspace(0, math.log10(self.x_max), self.n_bins)
        y_bin_edges = np.logspace(0, math.log10(self.y_max), self.n_bins)

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


# ============= drawing routines ===========

def draw_ctag_rejrej_slow(in_file, out_dir, ext='.pdf'): 
    """
    Slow because it uses pcolormesh. 
    """
    fig = Figure(figsize=(8,6))
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
    fig = Figure(figsize=(8,6))
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(1,1,1)
    ds = in_file['gaia/all']

    eff_array, extent = _get_arr_extent(ds)
    im = ax.imshow(eff_array.T, extent=extent, 
                   origin='lower', aspect='auto')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.grid(which='both')
    _label_axes(ax, ds)

    # _add_contour(ax,ds)

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
    misc options: 
      tagger
      tagger_disp (for display)
      vmax
    """
    options = {'tagger':'jfc', 'tagger_disp':'JetFitterCharm', 'vmax':1.2}
    for key, val in opts.items(): 
        if not key in options: 
            raise TypeError("{} not a valid arg".format(key))
        options[key] = val

    fig = Figure(figsize=(8,6))
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(1,1,1)
    ds = in_file['gaia/all']
    ds_denom = in_file['{}/all'.format(options['tagger'])]

    eff_array, extent = _get_arr_extent(ds)
    denom_array, denom_extent = _get_arr_extent(ds_denom)
    ratio_array = eff_array / denom_array
    im = ax.imshow(ratio_array.T, extent=extent, 
                   origin='lower', aspect='auto', 
                   vmin=1.0, vmax=options['vmax'])
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.grid(which='both')

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    cb = Colorbar(ax=cax, mappable=im)
    cb.set_label('$\epsilon_{{c}}$ ratio (GAIA / {})'.format(
            options['tagger_disp']))

    _label_axes(ax, ds)
    _add_eq_contour(ax, ds, ds_denom, colorbar=cb)
    _add_contour(ax,ds)

    out_name = '{}/rejrej-ratio-{}{}'.format(
        out_dir, options['tagger'], ext)
    # ignore complaints about not being able to log scale images
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        canvas.print_figure(out_name, bbox_inches='tight')

def draw_contour_rejrej(in_file, out_dir, ext='.pdf'): 
    fig = Figure(figsize=(8,6))
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(1,1,1)
    ds = in_file['gaia/all']
    ds_denom = in_file['jfc/all']
    
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.grid(which='both')
    _add_eq_contour(ax, ds, ds_denom, levels=[1.05, 1.10, 1.15], smooth=1.0)
    _add_contour(ax, ds)
    _label_axes(ax, ds)

    out_name = '{}/rejrej-cont{}'.format(out_dir, ext)
    canvas.print_figure(out_name, bbox_inches='tight')

def draw_simple_rejrej(in_file, out_dir, ext='.pdf'): 
    fig = Figure(figsize=(8,6))
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(1,1,1)
    ds = in_file['gaia/all']
    ds_denom = in_file['jfc/all']
    
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.grid(which='both')
    _add_contour(ax, ds, opts=dict(levels=np.arange(0.1, 0.8, 0.05)))
    _label_axes(ax, ds)

    out_name = '{}/rejrej-simple{}'.format(out_dir, ext)
    canvas.print_figure(out_name, bbox_inches='tight')

def draw_cprob_rejrej(in_file, in_file_up, out_dir, ext='.pdf'): 
    fig = Figure(figsize=(8,6))
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(1,1,1)
    ds = in_file['gaia/all']
    ds_denom = in_file['jfc/all']
    
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.grid(which='both')
    levels = np.arange(0.1, 0.8, 0.1)
    _add_contour(ax, ds, opts=dict(levels=levels))
    _add_cprob_curve(ax, in_file_up, levels=levels)
    _label_axes(ax, ds)

    out_name = '{}/rejrej-cprob{}'.format(out_dir, ext)
    canvas.print_figure(out_name, bbox_inches='tight')

# =========== draw utilities ===========

def _add_cprob_curve(ax, in_file, levels): 
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
    ax.plot(b_rej, u_rej, '--r', linewidth=2, label='gaia 1D $p_{c}$')
    b_rej_pts = []
    u_rej_pts = []
    for eff in levels: 
        idx_above, *throw_away = np.nonzero(c_eff > eff)
        first_above = idx_above.min()
        b_pt = b_rej[first_above]
        b_rej_pts.append(b_pt)
        u_pt = u_rej[first_above]
        u_rej_pts.append(u_pt)
        ax.text(b_pt, u_pt, str(eff), color='r', ha='left', va='bottom')
    ax.plot(b_rej_pts, u_rej_pts, 'or')
    handles, labels = ax.get_legend_handles_labels()
    handles.append(Line2D([0,1],[0,0], linewidth=2, color='k'))
    labels.append('gaia 2D, iso-eff')
    ax.legend(reversed(handles), reversed(labels), numpoints=1)

def _add_contour(ax, ds, opts={}): 
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
        linewidths = 2, 
        levels = opts.get('levels',c_lines),
        colors = opts.get('color','k'), 
        label = 'iso-eff 2D cuts'
        )
    ax.clabel(ct, fontsize=12, inline=True, fmt = '%.2f')

def _smooth(ratio_array, sigma): 
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
        linewidths = 2, 
        levels = [1.0] if not levels else levels,
        colors = ['r','orange','y','green'], 
        )
    def fmt(value): 
        if value == 1.0: 
            return 'equal'
        return '{:+.0%}'.format(value - 1.0)
    ax.clabel(ct, fontsize=12, inline=True, fmt=fmt)
    if colorbar: 
        colorbar.add_lines(ct)

def _tick_format(x, pos): 
    base = math.floor(math.log10(x)) 
    if x / 10**base > 5: 
        return ''
    else:
        return '{:.0f}'.format(x)

def _label_axes(ax, ds): 
    x, y, z = ds.attrs['xyz']
    formatter = FuncFormatter(_tick_format)
    ax.xaxis.set_minor_formatter(formatter)
    ax.xaxis.set_major_formatter(formatter)
    ax.yaxis.set_minor_formatter(formatter)
    ax.yaxis.set_major_formatter(formatter)
    ax.set_xlabel('$1 / \epsilon_{{ {} }}$'.format(x.lower()), 
                  x=0.98, ha='right')
    ax.set_ylabel('$1 / \epsilon_{{ {} }}$'.format(y.lower()), 
                  y=0.98, ha='right')

def _get_arr_extent(ds): 
    xmin = ds.attrs.get('x_min', 1.0)
    ymin = ds.attrs.get('y_min', 1.0)
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
