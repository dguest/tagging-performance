from os.path import isfile, isdir
import numpy as np
import h5py
import math
import warnings
import os

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib.colorbar import Colorbar

def make_plots(in_file_name, cache_name, out_dir, ext): 
    with h5py.File(in_file_name, 'r') as in_file: 
        with h5py.File(cache_name, 'a') as out_file: 
            make_rejrej(in_file, out_file)

    if not isdir(out_dir): 
        os.mkdir(out_dir)

    with h5py.File(cache_name, 'r') as cache: 
        # print('slow')
        # draw_ctag_rejrej_slow(cache, out_dir, ext)
        draw_ctag_rejrej(cache, out_dir, ext)

def draw_ctag_rejrej_slow(in_file, out_dir, ext='.pdf'): 
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
    xmin = ds.attrs.get('x_min', 1.0)
    ymin = ds.attrs.get('y_min', 1.0)
    xmax = ds.attrs['x_max']
    ymax = ds.attrs['y_max']

    eff_array = _maximize_efficiency(np.array(ds))
    im = ax.imshow(eff_array.T, extent=(xmin, xmax, ymin, ymax), 
              origin='lower', aspect='auto')
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.grid(which='both')

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    cb = Colorbar(ax=cax, mappable=im)

    out_name = '{}/rejrej{}'.format(out_dir, ext)
    # ignore complaints about not being able to scale images
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        canvas.print_figure(out_name, bbox_inches='tight')

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
    rej_array = rej_builder.get_rej_array(
        eff=_get_eff_hist(int_flavor_arrays['C']), 
        xrej=_get_rej_hist(int_flavor_arrays['B']), 
        yrej=_get_rej_hist(int_flavor_arrays['U']))

    saved_ds = out_file[tagger].create_dataset(binning, data=rej_array)
    saved_ds.attrs['x_max'] = rej_builder.x_max
    saved_ds.attrs['y_max'] = rej_builder.y_max

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
        for binn, (x, y, z) in enumerate(zip(x_bins, y_bins, z_vals)): 
            if binn % 10000 == 0: 
                print('going:', binn, x, y, z)
            out_array[x, y] = max(z, out_array[x, y])
        return out_array


def _maximize_efficiency(eff_array): 
    """
    It's not reasonable to take less than the efficiency 
    """
    temp = np.maximum.accumulate(eff_array[::-1,:], 0)[::-1,:]
    temp = np.maximum.accumulate(temp[:,::-1], 1)[:,::-1]
    return temp
