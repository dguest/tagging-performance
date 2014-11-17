import os

import numpy as np
import h5py

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

from tagperf.tagschema import long_particle_names

_fig_edge = 5.0
_fig_size = (_fig_edge, _fig_edge * 3/4)

def peters_cross_check(in_file_name, out_dir, ext):
    fig = Figure(figsize=_fig_size)
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(1,1,1)
    with h5py.File(in_file_name, 'r') as in_file:
        effs = {x:PetersEff(in_file, x) for x in 'CUB'}
    peter_colors = {'B':'r','C':'g','U':'b'}
    for flavor, eff in effs.items():
        pt, efficiency, pt_wd = eff.get_efficiency()
        pt_gev, wd_gev = [x / 1000 for x in [pt, pt_wd]]
        lab = long_particle_names[flavor]
        ax.errorbar(pt_gev, efficiency, xerr=wd_gev, label=lab,
                    linestyle='none', marker='.', color=peter_colors[flavor])
    ax.legend(numpoints=1, framealpha=0)
    ax.set_xlabel(r'Jet $p_{\rm T}$', x=0.98, ha='right')
    ax.set_ylabel(r'JetFitterCharm Efficiency', y=0.98, ha='right')
    if not os.path.isdir(out_dir):
        os.mkdir(out_dir)
    canvas.print_figure('{}/cross-check{}'.format(out_dir, ext),
                        bbox_inches='tight')

_peter_bin_vals = [20, 25, 30, 50, 80, 120, 160, 200, 300,  400, 750]
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

