import numpy as np

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
        self.xvalues = np.arange(xmin, xmax, len(self.pass_array) + 1)
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
