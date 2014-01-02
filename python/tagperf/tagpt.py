from tagperf import tagschema

import numpy as np
import h5py
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.ticker import FuncFormatter

from os.path import isdir
import os, sys
import math
import warnings

def make_plots(in_file_name, out_dir, ext): 
    with h5py.File(in_file_name, 'r') as in_file: 
        for eff in [0.6, 0.7, 0.8]: 
            for rej_flavor in 'UC': 
                draw_pt_bins(in_file, out_dir, rej_flavor=rej_flavor, 
                             eff=eff, ext=ext)

def draw_pt_bins(in_file, out_dir, eff=0.7, rej_flavor='U', ext='.pdf'): 
    fig = Figure(figsize=(8,6))
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(1,1,1)
    ax.grid(which='both')
    ax.set_xscale('log')
    for tagger in tagschema.get_taggers(in_file): 
        pt_bins = tagschema.get_pt_bins(in_file['B/btag/ptBins'])
        eff_group = in_file['B/btag/ptBins']
        rej_group = in_file['{}/btag/ptBins'.format(rej_flavor)]
        x_vals, y_vals, x_err, y_err = _get_pt_xy(
            eff_group, rej_group, pt_bins, eff, tagger=tagger)
        ax.errorbar(
            x_vals, y_vals, label=tagger, #xerr=x_err, 
            yerr=y_err)
    ax.legend(numpoints=1, loc='upper left')
    ax.set_xlim(20, np.max(x_vals) * 1.1)
    ax.set_xlabel('$p_{\mathrm{T}}$ [GeV]', x=0.98, ha='right')
    ax.set_ylabel(rej_label(rej_flavor, eff), y=0.98, ha='right')
    x_formatter = FuncFormatter(tick_format)
    ax.xaxis.set_minor_formatter(x_formatter)
    ax.xaxis.set_major_formatter(x_formatter)
    out_name = '{}/{}_rej{}_ptbins{}'.format(
        out_dir, rej_flavor, int(eff*100), ext)
    canvas.print_figure(out_name, bbox_inches='tight')

def _check_round(eff, target, warn_tolerance=0.01, err_tolerance=0.1): 
    roundoff_frac = abs((target - eff) / eff)
    if roundoff_frac > warn_tolerance: 
        prob = 'target eff {}, rounded to {} ({:.0%} off)'.format(
                target, eff, roundoff_frac)
        if roundoff_frac > err_tolerance: 
            raise RoundoffError(prob)
        warnings.warn(prob, stacklevel=3)

def _get_pt_xy(eff_group, rej_group, pt_bins, eff, tagger): 
    def bin_low_edge(bin_name): 
        return pt_bins[bin_name][0]
    pt_list = sorted(pt_bins, key=bin_low_edge)
    ud_list = [pt_bins[key] for key in pt_list]
    x_vals = np.fromiter( ( (u + d) / 2 for d,u in ud_list), dtype='d')
    x_err = np.fromiter( ( (u - d) / 2 for d,u in ud_list), dtype='d')
    y_vals = np.ones(len(pt_bins)) * np.NaN
    y_err = np.ones(len(pt_bins)) * np.NaN
    for bin_num, pt_bin in enumerate(pt_list): 
        def get_int(group): 
            return np.array(group[pt_bin][tagger])[::-1].cumsum()
        eff_array = get_int(eff_group)
        rej_counts = get_int(rej_group)
        try: 
            rej_at_eff, err_at_eff = _get_rejection(
                eff_array, rej_counts, eff)
            y_vals[bin_num] = rej_at_eff
            y_err[bin_num] = err_at_eff
        except RejectionCalcError as err: 
            prob = '{} {}: {}\n'.format(tagger, pt_bin, str(err))
            sys.stderr.write(prob)

    return x_vals, y_vals, x_err, y_err

def _get_rejection(eff_array, rej_counts, eff): 
    eff_array /= eff_array.max()
    idx_above_eff, = np.nonzero(eff_array > eff)
    first_idx_above = idx_above_eff.min()

    count_at_eff = rej_counts[first_idx_above]
    if count_at_eff == 0.0: 
        raise RejectionCalcError("infinite rejection")
    _check_round(eff_array[first_idx_above], eff)

    rej_at_eff = rej_counts.max() / count_at_eff
    err_at_eff = rej_at_eff / math.sqrt(count_at_eff)
    return rej_at_eff, err_at_eff


# ===== labeling functions =====
def tick_format(x, pos): 
    base = math.floor(math.log10(x)) 
    if x / 10**base > 5: 
        return ''
    else:
        return '{:.0f}'.format(x)

def rej_label(rej_flavor, eff): 
    pt1 = '$1/\epsilon_{{ \mathrm{{ {} }} }}$'.format(rej_flavor)
    pt2 = ' (fixed $\epsilon_{{b}}$ = {})'.format(eff)
    return pt1 + pt2

# ==== exceptions ====
class RejectionCalcError(Exception): 
    def __init__(self, *args): 
        super(RejectionCalcError, self).__init__(*args)

class RoundoffError(RejectionCalcError): 
    def __init__(self, *args): 
        super(RoundoffError, self).__init__(*args)
