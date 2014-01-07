from tagperf import tagschema

import numpy as np
import h5py
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

from os.path import isdir
import os

def make_plots(in_file_name, out_dir, ext): 
    with h5py.File(in_file_name, 'r') as in_file: 
        draw_btag_roc(in_file, out_dir, ext=ext)

def draw_btag_roc(in_file, out_dir, min_eff=0.5, ext='.pdf'): 
    fig = Figure(figsize=(8,6))
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(1,1,1)
    ax.set_yscale('log')
    ax.grid(which='both')
    for tagger in tagschema.get_taggers(in_file): 
        b_ds = in_file['B/btag/all/{}'.format(tagger)]
        u_ds = in_file['U/btag/all/{}'.format(tagger)]
        x_pts, y_pts = _get_roc_xy(eff_ds=b_ds, rej_ds=u_ds)
        valid_eff = x_pts > min_eff
        with tagschema.ColorScheme('colors.yml') as colors: 
            ax.plot(x_pts[valid_eff], y_pts[valid_eff], '-', label=tagger, 
                    color=colors[tagger])
    if not isdir(out_dir): 
        os.mkdir(out_dir)
    ax.legend()
    ax.set_xlim(min_eff, 1.0)
    ax.set_xlabel('$\epsilon_{b}$', x=0.98, ha='right')
    ax.set_ylabel('$1/\epsilon_{u}$', y=0.98, ha='right')
    canvas.print_figure('{}/roc{}'.format(out_dir, ext))

def _get_roc_xy(eff_ds, rej_ds): 
    eff_array = np.array(eff_ds)[::-1].cumsum()
    eff_array /= eff_array.max()
    rej_array = np.array(rej_ds)[::-1].cumsum()
    zero_mask = rej_array == 0
    nonzero_mask = np.logical_not(zero_mask)
    rej_array[nonzero_mask] = rej_array.max() / rej_array[nonzero_mask]
    rej_array[zero_mask] = np.Inf
    return eff_array, rej_array
    
