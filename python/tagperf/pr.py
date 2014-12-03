"""
Functions to add offical ATLAS labels
"""

def add_atlas(ax, x, y, size=16, external=False):
    ax.text(x, y, 'ATLAS', weight='bold', style='italic',
            horizontalalignment='right',
            transform=ax.transAxes, size=size)
    if not external:
        ax.text(x, y, ' Internal',
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
