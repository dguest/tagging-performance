import numpy as np
import h5py
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

from os.path import isdir
import os

def get_taggers(in_file): 
    return in_file['B/btag/all/'].keys()

def make_plots(in_file_name, out_dir): 
    with h5py.File(in_file_name, 'r') as in_file: 
        draw_btag_roc(in_file, out_dir)

def draw_btag_roc(in_file, out_dir): 
    fig = Figure(figsize=(8,6))
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(1,1,1)
    ax.set_yscale('log')
    for tagger in get_taggers(in_file): 
        b_ds = in_file['B/btag/all/{}'.format(tagger)]
        u_ds = in_file['U/btag/all/{}'.format(tagger)]
        x_pts, y_pts = _get_roc_xy(eff_ds=b_ds, rej_ds=u_ds)
        ax.plot(x_pts, y_pts, '-', label=tagger)
    if not isdir(out_dir): 
        os.mkdir(out_dir)
    ax.legend()
    canvas.print_figure('{}/roc.pdf'.format(out_dir))

def _get_roc_xy(eff_ds, rej_ds): 
    eff_array = np.array(eff_ds)[::-1].cumsum()
    eff_array /= eff_array.max()
    rej_array = np.array(rej_ds)[::-1].cumsum()
    rej_array = rej_array.max() / rej_array
    return eff_array, rej_array
    
