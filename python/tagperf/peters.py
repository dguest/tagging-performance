import os
from os.path import isdir
import itertools

import numpy as np
import h5py

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

from tagperf.tagschema import long_particle_names, leg_labels_colors
from tagperf.ctaging import make_rejrej, draw_simple_rejrej
from tagperf.ctaging import get_c_vs_u_const_beff, setup_1d_ctag_legs

_fig_edge = 5.0
_fig_size = (_fig_edge, _fig_edge * 3/4)
_text_size = 12
_line_width = 1.8

def _peters_lookup(flavor, tagger, binning):
    return '{}/{}'.format(flavor, tagger)

def peters_cross_check(in_file_name, out_dir, ext):
    fig = Figure(figsize=_fig_size)
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(1,1,1)
    with h5py.File(in_file_name, 'r') as in_file:
        effs = {x:PetersEff(in_file, x) for x in 'CUB'}
    peter_colors = {'B':'r','C':'g','U':'b'}
    for flavor, eff in effs.items():
        pt, efficiency, pt_wd = eff.get_efficiency(_other_bin_vals)
        pt_gev, wd_gev = [x / 1000 for x in [pt, pt_wd]]
        lab = long_particle_names[flavor]
        ax.errorbar(pt_gev, efficiency, xerr=wd_gev, label=lab,
                    linestyle='none', marker='.', color=peter_colors[flavor])
    ax.legend(numpoints=1, framealpha=0)
    ax.set_xlabel(r'Jet $p_{\rm T}$', x=0.98, ha='right')
    ax.set_ylabel(r'JetFitterCharm Efficiency', y=0.98, ha='right')
    ax.set_yscale('log')
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)
    canvas.print_figure('{}/cross-check{}'.format(out_dir, ext),
                        bbox_inches='tight')

_peter_bin_vals = [20, 25, 30, 50, 80, 120, 160, 200, 300,  400, 750]
_other_bin_vals = np.hstack([np.arange(20, 150, 2),np.arange(150, 300, 5)])
class PetersEff:
    """make binned efficinecy as a cross check for peter's plots"""
    def __init__(self, in_file, flavor):
        pass_ds = in_file[flavor + '/efficiency/pass']
        fail_ds = in_file[flavor + '/efficiency/fail']
        self.pass_array = np.array(pass_ds)[1:-1]
        self.fail_array = np.array(fail_ds)[1:-1]
        xmin, xmax = [pass_ds.attrs[x][0] for x in ['min', 'max']]
        assert pass_ds.attrs['units'] == 'MeV'
        self.xvalues = np.linspace(xmin, xmax, len(self.pass_array) )
    def get_efficiency(self, bin_vals=_peter_bin_vals):
        """return two tuple"""
        all_jets = self.pass_array + self.fail_array
        x_ctrs = []
        y_ctrs = []
        x_wd = []
        xvs = self.xvalues
        bin_vals_mev = [x * 1e3 for x in bin_vals]
        last_bin = bin_vals_mev[0]
        for bin in bin_vals_mev[1:]:
            valid_x = (last_bin < xvs) & (xvs < bin)
            bin_all = all_jets[valid_x]
            bin_pass = self.pass_array[valid_x]
            bin_eff = bin_pass.sum() / bin_all.sum()
            x_ctrs.append((bin + last_bin) / 2)
            y_ctrs.append(bin_eff)
            x_wd.append((bin - last_bin) / 2)
            last_bin = bin
        return np.array(x_ctrs), np.array(y_ctrs), np.array(x_wd)


def peters_plots(in_file_name, cache_name, out_dir, ext, approval='Internal'):
    """
    Top level routine to make peters plots
    """
    lookup = _peters_lookup
    with h5py.File(in_file_name, 'r') as in_file:
        with h5py.File(cache_name, 'a') as out_file:
            make_rejrej(in_file, out_file, tagger='jfc', lookup=lookup)
            # _make_rejrej(in_file, out_file, tagger='jfit', lookup=lookup)

    if not isdir(out_dir):
        os.mkdir(out_dir)

    with h5py.File(cache_name, 'r') as cache:
        draw_simple_rejrej(cache, out_dir, ext, tagger='jfc', official=True,
                           approval=approval)

_peters_rej = [4, 5, 6, 7, 8, 10]
def make_peters_1d(in_file_name, out_dir, ext, b_rej=_peters_rej,
                   approval='Internal'):
    tagger = 'jfc'
    textsize = _text_size

    b_effs = [1 / r for r in b_rej]

    rej_curves = {}
    with h5py.File(in_file_name, 'r') as in_file:
        for eff in b_effs:
            rej_curves[eff] = get_c_vs_u_const_beff(
                in_file, tagger, b_eff=eff, lookup=_peters_lookup)

    lines = ['-','--',':','-.', '_']
    colors = 'rgbkcm'
    style_iter = itertools.product(lines, colors)
    fig = Figure(figsize=_fig_size)
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(1,1,1)
    for b_eff, (linestyle, color) in zip(b_effs, style_iter):
        label, _ = leg_labels_colors.get(tagger, (tagger, 'k'))
        lab = '$1 / \epsilon_{{ b }} = $ {rej:.0f}'.format(
            rej=1/b_eff, tname=label)
        vc, vu = rej_curves[b_eff]
        ax.plot(vc, vu, label=lab, color=color, linewidth=_line_width,
                linestyle=linestyle)
    legprops = dict(size=textsize)
    leg = ax.legend(prop=legprops, framealpha=0, loc='lower left',
                    labelspacing=0.1, title='$b$-rejection')
    leg.get_title().set_fontsize(textsize)

    setup_1d_ctag_legs(ax, textsize, official=True, approval=approval)
    ax.set_xlim(0.10, 0.5)
    ax.set_ylim(1, 1e3)

    fig.tight_layout(pad=0, h_pad=0, w_pad=0)
    if not isdir(out_dir):
        os.mkdir(out_dir)
    file_name = '{}/{}-ctag-roc{}'.format(out_dir, tagger, ext)
    canvas.print_figure(file_name, bbox_inches='tight')
