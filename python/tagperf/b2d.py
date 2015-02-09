from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

from tagperf.ctaging import make_rejrej_btag, add_contour
# from tagperf.ctaging import add_official_garbage, add_atlas

def make_b2d(in_file_name, cache_name, out_dir, ext):
    """
    Top level routine to make plots from tagger output distributions
    """
    with h5py.File(in_file_name, 'r') as in_file:
        with h5py.File(cache_name, 'a') as out_file:
            make_rejrej_btag(in_file, out_file, tagger='gaia')

    if not isdir(out_dir):
        os.mkdir(out_dir)

    with h5py.File(cache_name, 'r') as cache:
        _draw_btag_rejrej(cache, out_dir, ext)

def _draw_btag_rejrej(in_file, out_dir, ext='.pdf', tagger='gaia',
                      official=False, approval='Internal'):
    """
    Draw iso-efficiency contours for one tagger (no colors).
    """
    fig = Figure(figsize=_fig_size)
    canvas = FigureCanvas(fig)
    ax = fig.add_subplot(1,1,1)
    ds = in_file[tagger + '/all']

    label_rejrej_axes(ax, ds)
    levels = np.linspace(0.55, 0.95, 5)
    add_contour(ax, ds, opts=dict(levels=levels, textsize=10))

    out_name = '{}/rejrej-simple{}'.format(out_dir, ext)
    canvas.print_figure(out_name, bbox_inches='tight')
