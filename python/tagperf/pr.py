"""
Functions to add offical ATLAS labels
"""
import math

def log_formatting(value, pos):
    roundval = round(value)
    if roundval == 1:
        base = 1
        exp = ''
    elif roundval == 10:
        base = 10
        exp = ''
    else:
        base = 10
        exp = round(math.log(value,10))
    return r'{}$^{{\mathdefault{{ {} }} }}$'.format(base, exp)

def add_atlas(ax, x, y, size=16, approval='Internal'):
    ax.text(x, y, 'ATLAS', weight='bold', style='italic',
            horizontalalignment='right',
            transform=ax.transAxes, size=size)
    if approval:
        ax.text(x, y, ' ' + approval,
                horizontalalignment='left',
                transform=ax.transAxes, size=size)

def add_official_garbage(ax, x, y, size=16, ysp=0.1, ha='left'):
    tricks = dict(
        ha=ha, transform=ax.transAxes, size=size)
    first_line = r'$t\bar{t}$ Simulation, $\sqrt{s}$ = 8 TeV'
    ax.text(x, y, first_line, **tricks)
    pt = r'$p_{\rm T}^{\rm jet} > $ 20 GeV'
    eta = r' $|\eta^{\rm jet}| < $ 2.5'
    ax.text(x, y - 1*ysp, pt + ', ' + eta, **tricks)
    ax.text(x, y - 2*ysp, 'JetFitterCharm', **tricks)
