from tagperf import tagschema

import numpy as np
import h5py
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import MaxNLocator
import matplotlib.pyplot as plt

from os.path import isdir
import os

def make_plots(in_file_name, out_dir, ext, propaganda=False, subset=None):
    bl = 'mv1' if propaganda else 'gaiaGr1'
    ext_args = dict(
        propaganda=propaganda, baseline=bl, ext=ext, out_dir=out_dir,
        subset=subset)
    with h5py.File(in_file_name, 'r') as in_file:
        draw_btag_roc(in_file, flavor='U', **ext_args)
        draw_btag_roc(in_file, flavor='C', **ext_args)

def _get_datasets(in_file, tagger, flavor='B'):
    b_ds = in_file['B/btag/all/{}'.format(tagger)]
    u_ds = in_file['{}/btag/all/{}'.format(flavor, tagger)]
    return b_ds, u_ds

def _setup_ax(ax):
    ax.set_yscale('log')
    ax.grid(which='both')

def _setup_ratio(ra):
    locator = MaxNLocator(5, prune='upper')
    ra.get_yaxis().set_major_locator(locator)
    ra.set_xlabel('$\epsilon_{b}$', x=0.98, ha='right')
    ra.axhline(y=1, linestyle='-.', color='k')
    ra.set_ylim(0.4, 1.6)
    ra.grid(axis='y')

def draw_btag_roc(in_file, out_dir, min_eff=0.5, ext='.pdf',
                  baseline=None, flavor='U', propaganda=False, subset=None):
    fig = Figure(figsize=(8,6))
    canvas = FigureCanvas(fig)
    grid = GridSpec(2,1, height_ratios=[3,1])
    ax = fig.add_subplot(grid[0])
    ra = fig.add_subplot(grid[1],sharex=ax)

    _setup_ax(ax)
    _setup_ratio(ra)
    bname = tagschema.display_name(baseline) if propaganda else baseline
    ra.set_ylabel('X / {}'.format(bname))

    taggers = tagschema.get_taggers(in_file, subset)
    base_x = None

    def get_xy(tagger):
        return _get_roc_xy(*_get_datasets(in_file, tagger, flavor=flavor))

    if baseline and baseline in taggers:
        base_x, base_y = get_xy(baseline)
    for tagger in taggers:
        x_pts, y_pts = get_xy(tagger)
        valid_eff = x_pts > min_eff
        tname = tagschema.display_name(tagger) if propaganda else tagger
        with tagschema.ColorScheme('colors.yml') as colors:
            color = colors[tname]
        valid_x = x_pts[valid_eff]
        valid_y = y_pts[valid_eff]
        ax.plot(valid_x, valid_y, '-', label=tname, color=color)
        if base_x is not None and tagger != baseline:
            interp_y = np.interp(valid_x, base_x, base_y)
            ra.plot(valid_x, valid_y / interp_y, color=color)
    if not isdir(out_dir):
        os.mkdir(out_dir)
    ax.legend()
    ax.set_xlim(min_eff, 1.0)
    ax.set_ylabel('$1/\epsilon_{{ {} }}$'.format(flavor.lower()),
                  y=0.98, ha='right')
    plt.setp(ax.get_xticklabels(), visible=False)
    fig.tight_layout(pad=0, h_pad=0, w_pad=0)
    file_name = '{}/{}RejRoc{}'.format(out_dir, flavor.lower(), ext)
    canvas.print_figure(file_name, bbox_inches='tight')

def _get_roc_xy(eff_ds, rej_ds):
    eff_array = np.array(eff_ds)[::-1].cumsum()
    eff_array /= eff_array.max()
    rej_array = np.array(rej_ds)[::-1].cumsum()
    zero_mask = rej_array == 0
    nonzero_mask = np.logical_not(zero_mask)
    rej_array[nonzero_mask] = rej_array.max() / rej_array[nonzero_mask]
    rej_array[zero_mask] = np.Inf
    return eff_array, rej_array

