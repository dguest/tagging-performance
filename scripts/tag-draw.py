#!/usr/bin/env python3

import argparse
import sys

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('hdf_file')
    parser.add_argument(
        '-o', '--out-dir', help='output dir (default %(default)s)',
        default='plots')
    parser.add_argument(
        '-e', '--ext', help='plot extension (default %(default)s)',
        default='.pdf')

    fdict = {f.name: f for f in [ctag, roc, pt, c1d, btag2d]}
    parser.add_argument(
        '-p', '--plots', help='plots to make (default %(default)s)',
        choices=fdict.keys(), default='all')
    parser.add_argument(
        '-t', '--taggers', help='only plot a subset of b-taggers', nargs='+')
    parser.add_argument('--propaganda', action='store_true')
    args = parser.parse_args(sys.argv[1:])

    if args.plots == 'all':
        plots = fdict.keys()
    else:
        plots = [args.plots]
    for plt in plots:
        fdict[plt](args)

def name(name):
    def named(function):
        function.name = name
        return function
    return named

@name('btag2d')
def btag2d(args):
    from tagperf import b2d
    b2d.make_b2d(args.hdf_file, 'BTAG_CACHE.h5', args.out_dir, args.ext)

@name('ctag')
def ctag(args):
    from tagperf import ctaging
    print('making ctag plots')
    ctaging.make_plots(args.hdf_file, 'REJREJ_CACHE.h5', args.out_dir,
                        args.ext)

@name('c1d')
def c1d(args):
    from tagperf import ctaging
    print('making ctag 1d plots')
    b_effs = [0.125, 0.2]
    ctaging.make_1d_overlay(args.hdf_file, args.out_dir, args.ext,
                            b_effs=b_effs, subset=args.taggers)
    for ef in b_effs:
        ctaging.make_1d_plots(args.hdf_file, args.out_dir, args.ext,
                              b_eff=ef)
        ctaging.make_1d_plots(args.hdf_file, args.out_dir, args.ext,
                              b_eff=ef, reject='T')

@name('roc')
def roc(args):
    from tagperf import tagroc
    print('making roc plots')
    tagroc.make_plots(args.hdf_file, args.out_dir, args.ext,
                      propaganda=args.propaganda, subset=args.taggers)

@name('pt')
def pt(args):
    from tagperf import tagpt
    print('making pt plots')
    tagpt.make_plots(args.hdf_file, args.out_dir, args.ext,
                     subset=args.taggers, propaganda=args.propaganda)

if __name__ == '__main__':
    run()
