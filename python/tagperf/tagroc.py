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

def make_plots(in_file_name, out_dir, ext): 
    with h5py.File(in_file_name, 'r') as in_file: 
        draw_btag_roc(in_file, out_dir, ext=ext, baseline='gaiaGr1')

def _get_datasets(in_file, tagger): 
    b_ds = in_file['B/btag/all/{}'.format(tagger)]
    u_ds = in_file['U/btag/all/{}'.format(tagger)]
    return b_ds, u_ds

def draw_btag_roc(in_file, out_dir, min_eff=0.5, ext='.pdf', baseline=None): 
    fig = Figure(figsize=(8,6))
    canvas = FigureCanvas(fig)
    grid = GridSpec(2,1, height_ratios=[3,1])
    ax = fig.add_subplot(grid[0])
    ra = fig.add_subplot(grid[1],sharex=ax)
    locator = MaxNLocator(5, prune='upper') 
    ra.get_yaxis().set_major_locator(locator)

    ax.set_yscale('log')
    ax.grid(which='both')
    taggers = tagschema.get_taggers(in_file)
    base_x = None
    if baseline and baseline in taggers: 
        base_x, base_y = _get_roc_xy(*_get_datasets(in_file, baseline))
    for tagger in taggers:
        x_pts, y_pts = _get_roc_xy(*_get_datasets(in_file, tagger))
        valid_eff = x_pts > min_eff
        with tagschema.ColorScheme('colors.yml') as colors: 
            color = colors[tagger]
        valid_x = x_pts[valid_eff]
        valid_y = y_pts[valid_eff]
        ax.plot(valid_x, valid_y, '-', label=tagger, color=color)
        if base_x is not None and tagger != baseline: 
            interp_y = np.interp(valid_x, base_x, base_y)
            ra.plot(valid_x, valid_y / interp_y, color=color)
    if not isdir(out_dir): 
        os.mkdir(out_dir)
    ax.legend()
    ax.set_xlim(min_eff, 1.0)
    ra.set_xlabel('$\epsilon_{b}$', x=0.98, ha='right')
    ra.axhline(y=1, linestyle='-.', color='k')
    ax.set_ylabel('$1/\epsilon_{u}$', y=0.98, ha='right')
    plt.setp(ax.get_xticklabels(), visible=False)
    ra.set_ylim(0.4, 1.6)
    ra.grid(axis='y')
    fig.tight_layout(pad=0, h_pad=0, w_pad=0)
    canvas.print_figure('{}/roc{}'.format(out_dir, ext), bbox_inches='tight')

def _get_roc_xy(eff_ds, rej_ds): 
    eff_array = np.array(eff_ds)[::-1].cumsum()
    eff_array /= eff_array.max()
    rej_array = np.array(rej_ds)[::-1].cumsum()
    zero_mask = rej_array == 0
    nonzero_mask = np.logical_not(zero_mask)
    rej_array[nonzero_mask] = rej_array.max() / rej_array[nonzero_mask]
    rej_array[zero_mask] = np.Inf
    return eff_array, rej_array
    
